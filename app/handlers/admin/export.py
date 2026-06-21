from __future__ import annotations

from datetime import date

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app import texts
from app.db.repositories.admins import is_root
from app.services.export import build_results_xlsx

router = Router(name="admin-export")


@router.callback_query(F.data == "adm:export")
async def cb_export(callback: CallbackQuery, session: AsyncSession) -> None:
    await callback.answer(texts.EXPORT_CAPTION)
    # ROOT additionally gets the per-voter detail sheet.
    include_voters = is_root(callback.from_user.id)
    data = await build_results_xlsx(session, include_voters=include_voters)
    filename = f"natijalar_{date.today().isoformat()}.xlsx"
    await callback.message.answer_document(
        BufferedInputFile(data, filename=filename), caption=texts.EXPORT_CAPTION
    )
