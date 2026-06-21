from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, MessageOriginChannel
from sqlalchemy.ext.asyncio import AsyncSession

from app import texts
from app.db.repositories import channels as channels_repo
from app.handlers.admin.common import safe_edit
from app.keyboards.admin import cancel_kb, channels_kb
from app.states.admin import AddChannel
from app.utils import esc

router = Router(name="admin-channels")


async def _channels_view(session: AsyncSession):
    channels = await channels_repo.list_active(session)
    if not channels:
        text = texts.CHANNELS_TITLE + texts.CHANNELS_EMPTY
    else:
        parts = [texts.CHANNELS_TITLE]
        for index, channel in enumerate(channels, start=1):
            parts.append(
                texts.CHANNELS_ROW.format(
                    i=index,
                    title=esc(channel.title or channel.chat_id),
                    chat_id=channel.chat_id,
                )
            )
        text = "".join(parts)
    return text, channels_kb(channels)


@router.callback_query(F.data == "adm:channels")
async def cb_channels(callback: CallbackQuery, session: AsyncSession) -> None:
    text, markup = await _channels_view(session)
    await safe_edit(callback, text, markup)
    await callback.answer()


@router.callback_query(F.data == "chadd")
async def cb_add(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddChannel.waiting_channel)
    await safe_edit(callback, texts.ADD_CHANNEL_HELP, cancel_kb())
    await callback.answer()


@router.message(AddChannel.waiting_channel)
async def on_channel(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    target: str | int | None = None
    origin = message.forward_origin
    if isinstance(origin, MessageOriginChannel):
        target = origin.chat.id
    elif message.text:
        ident = message.text.strip()
        if ident.lstrip("-").isdigit():
            target = int(ident)
        elif ident.startswith("@"):
            target = ident
        else:
            target = "@" + ident.lstrip("@")

    if target is None:
        await message.answer(texts.CHANNEL_BAD)
        return

    try:
        chat = await bot.get_chat(target)
    except Exception:  # noqa: BLE001
        await message.answer(texts.CHANNEL_BAD)
        return

    if chat.type != ChatType.CHANNEL:
        await message.answer(texts.CHANNEL_BAD)
        return

    invite_link = getattr(chat, "invite_link", None)
    await channels_repo.add_channel(
        session, chat.id, chat.title, chat.username, invite_link
    )
    await state.clear()
    await message.answer(texts.CHANNEL_ADDED.format(title=esc(chat.title or chat.id)))
    text, markup = await _channels_view(session)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("chdel:"))
async def cb_del(callback: CallbackQuery, session: AsyncSession) -> None:
    channel_id = int(callback.data.split(":")[1])
    await channels_repo.remove_channel(session, channel_id)
    await callback.answer(texts.CHANNEL_REMOVED)
    text, markup = await _channels_view(session)
    await safe_edit(callback, text, markup)
