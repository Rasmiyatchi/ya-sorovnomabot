from __future__ import annotations

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app import texts
from app.services import charts

router = Router(name="admin-stats")


@router.callback_query(F.data == "adm:stats")
async def cb_stats(callback: CallbackQuery, session: AsyncSession) -> None:
    await callback.answer(texts.STATS_CAPTION)

    bar = await charts.candidates_bar(session)
    line = await charts.votes_over_time(session)

    if bar is None and line is None:
        await callback.message.answer(texts.STATS_EMPTY)
        return

    if bar is not None:
        await callback.message.answer_photo(
            BufferedInputFile(bar, "candidates.png"), caption=texts.ADM_STATS
        )
    if line is not None:
        await callback.message.answer_photo(
            BufferedInputFile(line, "timeline.png")
        )
