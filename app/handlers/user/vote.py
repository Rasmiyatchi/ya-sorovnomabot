from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app import texts
from app.config import settings
from app.db.repositories import candidates as candidates_repo
from app.db.repositories import channels as channels_repo
from app.db.repositories import pending as pending_repo
from app.db.repositories import settings_repo
from app.db.repositories import votes as votes_repo
from app.handlers.user.render import show_poll
from app.keyboards.user import cancel_kb, confirm_kb, subscribe_kb
from app.services import captcha as captcha_service
from app.services import subscription as sub_service
from app.services.deadline import poll_closed
from app.states.user import VoteFlow
from app.utils import esc

router = Router(name="user-vote")


async def _issue_captcha(
    message: Message, session: AsyncSession, state: FSMContext, user_id: int, candidate_id: int
) -> None:
    code = captcha_service.new_code()
    await pending_repo.upsert_pending(
        session, user_id, candidate_id, code, settings.captcha_ttl
    )
    image = captcha_service.render(code)
    sent = await message.answer_photo(
        BufferedInputFile(image, "captcha.png"),
        caption=texts.ENTER_CAPTCHA,
        reply_markup=cancel_kb(),
    )
    await state.set_state(VoteFlow.captcha)
    await state.update_data(candidate_id=candidate_id, captcha_msg_id=sent.message_id)


@router.callback_query(F.data.startswith("vote:"))
async def on_candidate(callback: CallbackQuery, session: AsyncSession) -> None:
    candidate_id = int(callback.data.split(":")[1])
    setting = await settings_repo.get_settings(session)
    if poll_closed(setting):
        await callback.answer(texts.POLL_CLOSED, show_alert=True)
        return
    if await votes_repo.has_voted(session, callback.from_user.id):
        await callback.answer(texts.ALREADY_VOTED, show_alert=True)
        return
    candidate = await candidates_repo.get(session, candidate_id)
    if candidate is None or not candidate.is_active:
        await callback.answer(texts.CANDIDATE_NOT_FOUND, show_alert=True)
        return
    await callback.message.answer(
        texts.CONFIRM_VOTE.format(name=esc(candidate.full_name)),
        reply_markup=confirm_kb(candidate_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm:"))
async def on_confirm(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext, bot: Bot
) -> None:
    candidate_id = int(callback.data.split(":")[1])
    setting = await settings_repo.get_settings(session)
    if poll_closed(setting):
        await state.clear()
        await callback.answer(texts.POLL_CLOSED, show_alert=True)
        return
    if await votes_repo.has_voted(session, callback.from_user.id):
        await state.clear()
        await callback.answer(texts.ALREADY_VOTED, show_alert=True)
        return
    candidate = await candidates_repo.get(session, candidate_id)
    if candidate is None or not candidate.is_active:
        await callback.answer(texts.CANDIDATE_NOT_FOUND, show_alert=True)
        return

    channels = await channels_repo.list_active(session)
    pending_channels = await sub_service.not_subscribed(
        bot, callback.from_user.id, channels
    )
    if pending_channels:
        await state.update_data(candidate_id=candidate_id)
        await callback.message.answer(
            texts.MUST_SUBSCRIBE, reply_markup=subscribe_kb(pending_channels)
        )
        await callback.answer()
        return

    await _issue_captcha(
        callback.message, session, state, callback.from_user.id, candidate_id
    )
    await callback.answer()


@router.callback_query(F.data == "recheck")
async def on_recheck(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext, bot: Bot
) -> None:
    channels = await channels_repo.list_active(session)
    pending_channels = await sub_service.not_subscribed(
        bot, callback.from_user.id, channels
    )
    if pending_channels:
        await callback.answer(texts.MUST_SUBSCRIBE, show_alert=True)
        return

    data = await state.get_data()
    candidate_id = data.get("candidate_id")
    if candidate_id is None:
        await callback.answer(texts.SUB_OK)
        await show_poll(callback.message, session)
        return

    setting = await settings_repo.get_settings(session)
    if poll_closed(setting):
        await state.clear()
        await callback.answer(texts.POLL_CLOSED, show_alert=True)
        return
    if await votes_repo.has_voted(session, callback.from_user.id):
        await state.clear()
        await callback.answer(texts.ALREADY_VOTED, show_alert=True)
        return

    await _issue_captcha(
        callback.message, session, state, callback.from_user.id, candidate_id
    )
    await callback.answer(texts.SUB_OK)


@router.callback_query(F.data == "cancel")
async def on_cancel(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
) -> None:
    await pending_repo.clear_pending(session, callback.from_user.id)
    await state.clear()
    await callback.answer(texts.CANCELLED)
    await show_poll(callback.message, session)


@router.message(StateFilter(VoteFlow.captcha), F.text)
async def on_captcha_text(
    message: Message, session: AsyncSession, state: FSMContext
) -> None:
    user_id = message.from_user.id
    pending = await pending_repo.get_pending(session, user_id)
    if pending is None or pending_repo.is_expired(pending):
        await pending_repo.clear_pending(session, user_id)
        await state.clear()
        await message.answer(texts.CAPTCHA_EXPIRED)
        await show_poll(message, session)
        return

    if captcha_service.matches(pending.code, message.text):
        candidate_id = pending.candidate_id
        recorded = await votes_repo.commit_vote(session, user_id, candidate_id)
        await pending_repo.clear_pending(session, user_id)
        await state.clear()
        await message.answer(texts.VOTE_ACCEPTED if recorded else texts.ALREADY_VOTED)
        await show_poll(message, session)
        return

    if pending.attempts + 1 >= settings.captcha_max_attempts:
        await pending_repo.clear_pending(session, user_id)
        await state.clear()
        await message.answer(texts.TOO_MANY_ATTEMPTS)
        await show_poll(message, session)
        return

    new_code = captcha_service.new_code()
    await pending_repo.regenerate(session, pending, new_code, settings.captcha_ttl)
    image = captcha_service.render(new_code)
    left = settings.captcha_max_attempts - pending.attempts
    await message.answer_photo(
        BufferedInputFile(image, "captcha.png"),
        caption=texts.WRONG_CAPTCHA.format(left=left),
        reply_markup=cancel_kb(),
    )


@router.message(StateFilter(VoteFlow.captcha))
async def on_captcha_nontext(message: Message) -> None:
    await message.answer(texts.SEND_TEXT_ONLY)
