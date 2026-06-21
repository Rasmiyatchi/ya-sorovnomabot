from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import candidates as candidates_repo
from app.db.repositories import settings_repo
from app.db.repositories import users as users_repo
from app.handlers.user.render import show_poll
from app.keyboards.user import confirm_kb
from app import texts
from app.services.deadline import poll_closed
from app.db.repositories import votes as votes_repo
from app.utils import esc

router = Router(name="user-start")


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    command: CommandObject,
) -> None:
    await state.clear()
    await users_repo.get_or_create_user(session, message.from_user)

    arg = command.args or ""

    # Deep-link: ?start=vote_N — to'g'ridan-to'g'ri nomzodga ovoz berish
    if arg.startswith("vote_"):
        try:
            candidate_id = int(arg.split("_")[1])
        except (IndexError, ValueError):
            await show_poll(message, session)
            return

        setting = await settings_repo.get_settings(session)
        if poll_closed(setting):
            await message.answer(texts.POLL_CLOSED)
            await show_poll(message, session)
            return

        if await votes_repo.has_voted(session, message.from_user.id):
            await message.answer(texts.ALREADY_VOTED)
            await show_poll(message, session)
            return

        candidate = await candidates_repo.get(session, candidate_id)
        if candidate is None or not candidate.is_active:
            await message.answer(texts.CANDIDATE_NOT_FOUND)
            await show_poll(message, session)
            return

        await message.answer(
            texts.CONFIRM_VOTE.format(name=esc(candidate.full_name)),
            reply_markup=confirm_kb(candidate_id),
        )
        return

    # Default: so'rovnomani ko'rsat
    await show_poll(message, session)

