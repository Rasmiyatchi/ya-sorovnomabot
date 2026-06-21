from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app import texts
from app.db.models import Candidate, User, Vote
from app.db.repositories import candidates as candidates_repo
from app.handlers.admin.common import safe_edit
from app.keyboards.admin import back_to_menu_kb
from app.utils import esc

router = Router(name="admin-results")


@router.callback_query(F.data == "adm:results")
async def cb_results(callback: CallbackQuery, session: AsyncSession) -> None:
    candidates = await candidates_repo.list_active(session)
    if not candidates:
        await safe_edit(callback, texts.RESULTS_EMPTY, back_to_menu_kb())
        await callback.answer()
        return

    lines = [texts.RESULTS_TITLE]
    total = 0
    for rank, candidate in enumerate(candidates, start=1):
        lines.append(
            texts.RESULTS_ROW.format(
                rank=rank, name=esc(candidate.full_name), votes=candidate.votes_count
            )
        )
        total += candidate.votes_count
    lines.append(texts.RESULTS_TOTAL.format(total=total))
    await safe_edit(callback, "".join(lines), back_to_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "adm:reset_votes")
async def cb_reset_votes(callback: CallbackQuery, session: AsyncSession) -> None:
    await session.execute(update(Candidate).values(votes_count=0))
    await session.execute(update(User).values(vote_status=0, vote_candidate=None))
    await session.execute(delete(Vote))
    await session.commit()
    await callback.answer("Barcha ovozlar muvaffaqiyatli 0 ga tushirildi!", show_alert=True)
