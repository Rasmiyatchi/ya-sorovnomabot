from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app import texts
from app.db.repositories import candidates as candidates_repo
from app.db.repositories import channels as channels_repo
from app.db.repositories import settings_repo
from app.handlers.admin.common import safe_edit
from app.keyboards.admin import cancel_kb, settings_kb
from app.keyboards.user import candidates_kb
from app.services.deadline import format_deadline, parse_deadline
from app.states.admin import SettingsFSM
from app.utils import esc

router = Router(name="admin-settings")


async def _settings_view(session: AsyncSession):
    setting = await settings_repo.get_settings(session)
    name = esc(setting.poll_name) if setting.poll_name else texts.SUM_NONE
    description = (
        esc(setting.description) if setting.description else texts.SUM_NONE
    )
    if len(description) > 80:
        description = description[:77] + "…"
    banner = texts.SUM_SET if setting.banner_file_id else texts.SUM_UNSET
    deadline = format_deadline(setting.deadline)
    summary = "\n".join(
        [
            texts.SUM_NAME.format(v=name),
            texts.SUM_DESC.format(v=description),
            texts.SUM_BANNER.format(v=banner),
            texts.SUM_DEADLINE.format(v=deadline),
        ]
    )
    return texts.SETTINGS_TITLE.format(summary=summary), settings_kb()


@router.callback_query(F.data == "adm:settings")
async def cb_settings(callback: CallbackQuery, session: AsyncSession) -> None:
    text, markup = await _settings_view(session)
    await safe_edit(callback, text, markup)
    await callback.answer()


@router.callback_query(F.data == "set:name")
async def cb_name(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsFSM.waiting_name)
    await safe_edit(callback, texts.ASK_NAME, cancel_kb())
    await callback.answer()


@router.callback_query(F.data == "set:desc")
async def cb_desc(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsFSM.waiting_description)
    await safe_edit(callback, texts.ASK_DESC, cancel_kb())
    await callback.answer()


@router.callback_query(F.data == "set:banner")
async def cb_banner(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsFSM.waiting_banner)
    await safe_edit(callback, texts.ASK_BANNER, cancel_kb())
    await callback.answer()


@router.callback_query(F.data == "set:deadline")
async def cb_deadline(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsFSM.waiting_deadline)
    await safe_edit(callback, texts.ASK_DEADLINE, cancel_kb())
    await callback.answer()


async def _save_and_show(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    await message.answer(texts.SET_SAVED)
    text, markup = await _settings_view(session)
    await message.answer(text, reply_markup=markup)


@router.message(SettingsFSM.waiting_name, F.text)
async def on_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await settings_repo.update_settings(session, poll_name=message.text.strip())
    await _save_and_show(message, state, session)


@router.message(SettingsFSM.waiting_description, F.text)
async def on_desc(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await settings_repo.update_settings(session, description=message.text.strip())
    await _save_and_show(message, state, session)


@router.message(SettingsFSM.waiting_banner, F.photo)
async def on_banner(message: Message, state: FSMContext, session: AsyncSession) -> None:
    file_id = message.photo[-1].file_id
    await settings_repo.update_settings(session, banner_file_id=file_id)
    await _save_and_show(message, state, session)


@router.message(SettingsFSM.waiting_banner)
async def on_banner_invalid(message: Message) -> None:
    await message.answer(texts.ASK_BANNER)


@router.message(SettingsFSM.waiting_deadline, F.text)
async def on_deadline(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    raw = message.text.strip()
    if raw == "-":
        await settings_repo.set_deadline(session, None)
        await state.clear()
        await message.answer(texts.DEADLINE_CLEARED)
        text, markup = await _settings_view(session)
        await message.answer(text, reply_markup=markup)
        return

    parsed = parse_deadline(raw)
    if parsed is None:
        await message.answer(texts.BAD_DEADLINE)
        return
    await settings_repo.set_deadline(session, parsed)
    await _save_and_show(message, state, session)


@router.callback_query(F.data == "adm:post_poll")
async def cb_post_poll(callback: CallbackQuery, session: AsyncSession, bot: Bot) -> None:
    channels = await channels_repo.list_active(session)
    if not channels:
        await callback.answer(
            "Majburiy kanallar qo'shilmagan. Avval kanal qo'shing.",
            show_alert=True,
        )
        return

    setting = await settings_repo.get_settings(session)
    candidates = await candidates_repo.list_active(session)

    if not candidates:
        await callback.answer("So'rovnomada nomzodlar yo'q!", show_alert=True)
        return

    name = setting.poll_name or texts.DEFAULT_POLL_NAME
    description = setting.description or texts.DEFAULT_DESCRIPTION

    # Nomzod havolalarini matn ichiga joylash
    # (Forward qilinganda inline tugmalar yo'qoladi, lekin matn ichidagi havolalar saqlanadi)
    me = await bot.get_me()
    vote_lines = []
    for i, candidate in enumerate(candidates, start=1):
        link = f"https://t.me/{me.username}?start=vote_{candidate.id}"
        vote_lines.append(f'{i}. <a href="{link}">{esc(candidate.full_name)}</a>  —  🗳 Ovoz berish')

    caption = (
        f"<b>{esc(name)}</b>\n\n"
        f"{esc(description)}\n\n"
        f"<b>👇 Nomzodlar:</b>\n"
        + "\n".join(vote_lines)
    )

    # Inline tugma ham qo'shamiz (kanalda ko'rinishi chiroyli bo'lishi uchun)
    channel_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🗳 Ovoz berish",
            url=f"https://t.me/{me.username}?start=poll",
        )]
    ])

    # Birinchi (asosiy) kanalga yuborish
    channel = channels[0]
    try:
        if setting.banner_file_id:
            chan_caption = caption[:1021] + "..." if len(caption) > 1024 else caption
            await bot.send_photo(
                channel.chat_id,
                setting.banner_file_id,
                caption=chan_caption,
                reply_markup=channel_markup,
            )
        else:
            chan_caption = caption[:4093] + "..." if len(caption) > 4096 else caption
            await bot.send_message(
                channel.chat_id, chan_caption, reply_markup=channel_markup
            )
        ch_name = channel.title or channel.username or str(channel.chat_id)
        await callback.answer(
            f"So'rovnoma '{ch_name}' kanaliga muvaffaqiyatli yuborildi!",
            show_alert=True,
        )
    except Exception as e:
        await callback.answer(
            f"Xatolik yuz berdi: {e}",
            show_alert=True,
        )

