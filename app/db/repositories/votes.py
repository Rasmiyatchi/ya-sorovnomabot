from __future__ import annotations

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Candidate, User, Vote


async def has_voted(session: AsyncSession, user_id: int) -> bool:
    status = await session.scalar(
        select(User.vote_status).where(User.telegram_id == user_id)
    )
    return bool(status)


async def commit_vote(session: AsyncSession, user_id: int, candidate_id: int) -> bool:
    """Atomically record exactly one vote. Returns False if already voted.

    Guard 1: conditional UPDATE on vote_status==0 (rowcount check).
    Guard 2: UNIQUE(votes.user_id) constraint (IntegrityError backstop).
    Counter increment is done in SQL (no read-modify-write race).
    """
    result = await session.execute(
        update(User)
        .where(User.telegram_id == user_id, User.vote_status == 0)
        .values(vote_status=1, vote_candidate=candidate_id)
    )
    if result.rowcount == 0:
        await session.rollback()
        return False

    session.add(Vote(user_id=user_id, candidate_id=candidate_id))
    await session.execute(
        update(Candidate)
        .where(Candidate.id == candidate_id)
        .values(votes_count=Candidate.votes_count + 1)
    )
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return False
    return True


async def reset_user_vote(session: AsyncSession, user_id: int) -> bool:
    """ROOT-only: undo a user's vote so they can vote again. Returns True if a
    vote was actually removed."""
    user = await session.get(User, user_id)
    if user is None or not user.vote_status:
        return False

    voted_for = user.vote_candidate
    await session.execute(delete(Vote).where(Vote.user_id == user_id))
    if voted_for is not None:
        await session.execute(
            update(Candidate)
            .where(Candidate.id == voted_for, Candidate.votes_count > 0)
            .values(votes_count=Candidate.votes_count - 1)
        )
    user.vote_status = 0
    user.vote_candidate = None
    await session.commit()
    return True
