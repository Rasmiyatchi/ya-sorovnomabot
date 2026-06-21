from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Candidate


async def list_active(session: AsyncSession) -> list[Candidate]:
    return list(
        await session.scalars(
            select(Candidate)
            .where(Candidate.is_active == True)  # noqa: E712
            .order_by(Candidate.votes_count.desc(), Candidate.id.asc())
        )
    )


async def get(session: AsyncSession, candidate_id: int) -> Candidate | None:
    return await session.get(Candidate, candidate_id)


async def add(session: AsyncSession, full_name: str) -> Candidate:
    candidate = Candidate(full_name=full_name.strip())
    session.add(candidate)
    await session.commit()
    await session.refresh(candidate)
    return candidate


async def soft_delete(session: AsyncSession, candidate_id: int) -> Candidate | None:
    candidate = await session.get(Candidate, candidate_id)
    if candidate is None or not candidate.is_active:
        return None
    candidate.is_active = False
    await session.commit()
    return candidate


async def adjust_votes(session: AsyncSession, candidate_id: int, delta: int) -> None:
    await session.execute(
        update(Candidate)
        .where(Candidate.id == candidate_id)
        .values(votes_count=func.max(0, Candidate.votes_count + delta))
    )
    await session.commit()


async def total_votes(session: AsyncSession) -> int:
    return (
        await session.scalar(
            select(func.coalesce(func.sum(Candidate.votes_count), 0)).where(
                Candidate.is_active == True  # noqa: E712
            )
        )
        or 0
    )


async def count_active(session: AsyncSession) -> int:
    return (
        await session.scalar(
            select(func.count()).select_from(Candidate).where(
                Candidate.is_active == True  # noqa: E712
            )
        )
        or 0
    )
