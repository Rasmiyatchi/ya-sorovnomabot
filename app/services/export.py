from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Candidate, User
from app.utils import as_utc


async def build_results_xlsx(session: AsyncSession, include_voters: bool = False) -> bytes:
    """Aggregate results sheet. If include_voters (ROOT only), append a sheet
    with per-user vote details."""
    candidates = list(
        await session.scalars(
            select(Candidate)
            .where(Candidate.is_active == True)  # noqa: E712
            .order_by(Candidate.votes_count.desc(), Candidate.id.asc())
        )
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Natijalar"
    header = ["Reyting", "F.I.SH", "Ovozlar soni", "Qo'shilgan sana"]
    sheet.append(header)
    for cell in sheet[1]:
        cell.font = Font(bold=True)

    total = 0
    for rank, candidate in enumerate(candidates, start=1):
        created = as_utc(candidate.created_date)
        sheet.append(
            [
                rank,
                candidate.full_name,
                candidate.votes_count,
                created.strftime("%Y-%m-%d %H:%M") if created else "",
            ]
        )
        total += candidate.votes_count
    sheet.append([])
    sheet.append(["", "Jami ovozlar", total])

    for column, width in {"A": 10, "B": 40, "C": 16, "D": 20}.items():
        sheet.column_dimensions[column].width = width

    if include_voters:
        cand_names = {c.id: c.full_name for c in candidates}
        voters_sheet = workbook.create_sheet("Foydalanuvchilar")
        voters_sheet.append(
            ["telegram_id", "username", "first_name", "ovoz bergan nomzod", "sana"]
        )
        for cell in voters_sheet[1]:
            cell.font = Font(bold=True)
        users = await session.scalars(
            select(User).where(User.vote_status == 1).order_by(User.date.asc())
        )
        for user in users:
            voted = as_utc(user.date)
            voters_sheet.append(
                [
                    user.telegram_id,
                    user.username or "",
                    user.first_name or "",
                    cand_names.get(user.vote_candidate, user.vote_candidate or ""),
                    voted.strftime("%Y-%m-%d %H:%M") if voted else "",
                ]
            )

    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
