from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app import texts
from app.db.repositories import candidates as candidates_repo
from app.utils import esc

router = Router(name="user-top")


async def _build_top(session: AsyncSession) -> str:
    candidates = await candidates_repo.list_active(session)
    if not candidates:
        return texts.TOP_TITLE + texts.TOP_EMPTY

    lines = [texts.TOP_TITLE]
    total = 0
    for rank, candidate in enumerate(candidates, start=1):
        lines.append(
            texts.TOP_ROW.format(
                rank=rank, name=esc(candidate.full_name), votes=candidate.votes_count
            )
        )
        total += candidate.votes_count
    lines.append(texts.TOP_TOTAL.format(total=total))
    return "".join(lines)


@router.message(Command("top"))
async def cmd_top(message: Message, session: AsyncSession) -> None:
    await message.answer(await _build_top(session))


@router.callback_query(F.data == "top")
async def cb_top(callback: CallbackQuery, session: AsyncSession) -> None:
    await callback.message.answer(await _build_top(session))
    await callback.answer()
