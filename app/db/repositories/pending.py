from __future__ import annotations

import datetime as dt

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PendingVote
from app.utils import as_utc, utcnow


async def upsert_pending(
    session: AsyncSession,
    telegram_id: int,
    candidate_id: int,
    code: str,
    ttl_seconds: int,
) -> PendingVote:
    """One pending vote per user; re-tapping overwrites the previous one."""
    expires_at = utcnow() + dt.timedelta(seconds=ttl_seconds)
    pending = await session.get(PendingVote, telegram_id)
    if pending is None:
        pending = PendingVote(
            telegram_id=telegram_id,
            candidate_id=candidate_id,
            code=code,
            attempts=0,
            expires_at=expires_at,
        )
        session.add(pending)
    else:
        pending.candidate_id = candidate_id
        pending.code = code
        pending.attempts = 0
        pending.expires_at = expires_at
    await session.commit()
    return pending


async def get_pending(session: AsyncSession, telegram_id: int) -> PendingVote | None:
    return await session.get(PendingVote, telegram_id)


def is_expired(pending: PendingVote) -> bool:
    return as_utc(pending.expires_at) < utcnow()


async def regenerate(
    session: AsyncSession, pending: PendingVote, code: str, ttl_seconds: int
) -> None:
    pending.code = code
    pending.attempts += 1
    pending.expires_at = utcnow() + dt.timedelta(seconds=ttl_seconds)
    await session.commit()


async def clear_pending(session: AsyncSession, telegram_id: int) -> None:
    await session.execute(
        delete(PendingVote).where(PendingVote.telegram_id == telegram_id)
    )
    await session.commit()
