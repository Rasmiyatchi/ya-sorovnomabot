from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app import texts
from app.config import settings
from app.db.models import User
from app.db.repositories import audit as audit_repo
from app.db.repositories import admins as admins_repo
from app.db.repositories import candidates as candidates_repo
from app.db.repositories import channels as channels_repo
from app.db.repositories import settings_repo
from app.db.repositories import users as users_repo
from app.db.repositories import votes as votes_repo
from app.filters import IsRoot
from app.handlers.admin.common import safe_edit
from app.keyboards.root import (
    admins_kb,
    back_to_root_kb,
    root_cancel_kb,
    root_menu_kb,
    user_card_kb,
)
from app.services.deadline import format_deadline, poll_closed
from app.states.admin import FindUser, ManageAdmin
from app.utils import as_utc, esc

# Double-gated: included under the IsAdmin admin router AND filtered by IsRoot here.
router = Router(name="root")
router.message.filter(IsRoot())
router.callback_query.filter(IsRoot())


def _fmt_date(value) -> str:
    aware = as_utc(value)
    if aware is None:
        return texts.SUM_NONE
    return aware.astimezone(settings.tz).strftime("%Y-%m-%d %H:%M")


# ── Root menu ────────────────────────────────────────────────────────────
@router.callback_query(F.data == "root:menu")
async def cb_root_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_edit(callback, texts.ROOT_TITLE, root_menu_kb())
    await callback.answer()


# ── Dashboard ────────────────────────────────────────────────────────────
@router.callback_query(F.data == "root:dashboard")
async def cb_dashboard(callback: CallbackQuery, session: AsyncSession) -> None:
    setting = await settings_repo.get_settings(session)
    text = texts.DASHBOARD.format(
        users=await users_repo.count_users(session),
        voted=await users_repo.count_voted(session),
        blocked=await users_repo.count_blocked(session),
        votes=await candidates_repo.total_votes(session),
        candidates=await candidates_repo.count_active(session),
        channels=await channels_repo.count_active(session),
        admins=await admins_repo.count_visible_admins(session),
        deadline=format_deadline(setting.deadline),
        status=texts.POLL_DONE if poll_closed(setting) else texts.POLL_OPEN,
    )
    await safe_edit(callback, text, back_to_root_kb())
    await callback.answer()


# ── Admin management ─────────────────────────────────────────────────────
async def _admins_view(session: AsyncSession):
    admins = await admins_repo.list_visible_admins(session)  # root excluded
    if not admins:
        text = texts.ROOT_ADMINS_TITLE + texts.ROOT_ADMINS_EMPTY
    else:
        parts = [texts.ROOT_ADMINS_TITLE]
        for index, admin in enumerate(admins, start=1):
            parts.append(
                texts.ROOT_ADMIN_ROW.format(i=index, tg_id=admin.telegram_id)
            )
        text = "".join(parts)
    return text, admins_kb(admins)


@router.callback_query(F.data == "root:admins")
async def cb_admins(callback: CallbackQuery, session: AsyncSession) -> None:
    text, markup = await _admins_view(session)
    await safe_edit(callback, text, markup)
    await callback.answer()


@router.callback_query(F.data == "root:addadmin")
async def cb_addadmin(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ManageAdmin.waiting_admin_id)
    await safe_edit(callback, texts.ROOT_ASK_ADMIN_ID, root_cancel_kb())
    await callback.answer()


@router.message(ManageAdmin.waiting_admin_id, F.text)
async def on_admin_id(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    raw = message.text.strip()
    if not raw.lstrip("-").isdigit():
        await message.answer(texts.ROOT_BAD_ID)
        return
    tg_id = int(raw)
    added = await admins_repo.add_admin(session, tg_id, message.from_user.id)
    await state.clear()
    if added:
        await audit_repo.log_action(
            session, message.from_user.id, "add_admin", str(tg_id)
        )
        await message.answer(texts.ROOT_ADMIN_ADDED.format(tg_id=tg_id))
    else:
        await message.answer(texts.ROOT_ADMIN_EXISTS)
    text, markup = await _admins_view(session)
    await message.answer(text, reply_markup=markup)


@router.callback_query(F.data.startswith("radel:"))
async def cb_radel(callback: CallbackQuery, session: AsyncSession) -> None:
    tg_id = int(callback.data.split(":")[1])
    removed = await admins_repo.remove_admin(session, tg_id)
    if removed:
        await audit_repo.log_action(
            session, callback.from_user.id, "remove_admin", str(tg_id)
        )
        await callback.answer(f"🗑 {tg_id}", show_alert=True)
    else:
        await callback.answer(texts.NO_ACCESS, show_alert=True)
    text, markup = await _admins_view(session)
    await safe_edit(callback, text, markup)


# ── User inspection & limited edits ──────────────────────────────────────
async def _user_card_text(session: AsyncSession, user: User) -> str:
    voted_for = texts.SUM_NONE
    if user.vote_candidate:
        candidate = await candidates_repo.get(session, user.vote_candidate)
        voted_for = esc(candidate.full_name) if candidate else str(user.vote_candidate)
    return texts.ROOT_USER_CARD.format(
        tg_id=user.telegram_id,
        username=("@" + user.username) if user.username else texts.SUM_NONE,
        first_name=esc(user.first_name) or texts.SUM_NONE,
        vote_status=texts.YES if user.vote_status else texts.NO,
        voted_for=voted_for,
        blocked=texts.YES if user.is_blocked else texts.NO,
        active=texts.YES if user.is_active else texts.NO,
        date=_fmt_date(user.date),
    )


async def _refresh_card(
    callback: CallbackQuery, session: AsyncSession, tg_id: int
) -> None:
    user = await users_repo.get_user(session, tg_id)
    if user is None:
        return
    text = await _user_card_text(session, user)
    await safe_edit(callback, text, user_card_kb(user))


@router.callback_query(F.data == "root:users")
async def cb_users(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FindUser.waiting_query)
    await safe_edit(callback, texts.ROOT_ASK_USER, root_cancel_kb())
    await callback.answer()


@router.message(FindUser.waiting_query, F.text)
async def on_find_user(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    user = await users_repo.find_user(session, message.text)
    await state.clear()
    if user is None:
        await message.answer(texts.ROOT_USER_NOT_FOUND)
        await message.answer(texts.ROOT_TITLE, reply_markup=root_menu_kb())
        return
    text = await _user_card_text(session, user)
    await message.answer(text, reply_markup=user_card_kb(user))


@router.callback_query(F.data.startswith("ruser:reset:"))
async def cb_reset_vote(callback: CallbackQuery, session: AsyncSession) -> None:
    tg_id = int(callback.data.split(":")[2])
    done = await votes_repo.reset_user_vote(session, tg_id)
    if done:
        await audit_repo.log_action(
            session, callback.from_user.id, "reset_vote", str(tg_id)
        )
        await callback.answer(texts.ROOT_VOTE_RESET_OK, show_alert=True)
    else:
        await callback.answer(texts.ROOT_VOTE_RESET_NONE, show_alert=True)
    await _refresh_card(callback, session, tg_id)


@router.callback_query(F.data.startswith("ruser:block:"))
async def cb_block(callback: CallbackQuery, session: AsyncSession) -> None:
    tg_id = int(callback.data.split(":")[2])
    await users_repo.set_blocked(session, tg_id, True)
    await audit_repo.log_action(session, callback.from_user.id, "block_user", str(tg_id))
    await callback.answer(texts.ROOT_USER_BLOCKED, show_alert=True)
    await _refresh_card(callback, session, tg_id)


@router.callback_query(F.data.startswith("ruser:unblock:"))
async def cb_unblock(callback: CallbackQuery, session: AsyncSession) -> None:
    tg_id = int(callback.data.split(":")[2])
    await users_repo.set_blocked(session, tg_id, False)
    await audit_repo.log_action(
        session, callback.from_user.id, "unblock_user", str(tg_id)
    )
    await callback.answer(texts.ROOT_USER_UNBLOCKED, show_alert=True)
    await _refresh_card(callback, session, tg_id)
