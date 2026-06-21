from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


async def get_or_create_user(session: AsyncSession, tg_user) -> User:
    """Upsert: create the row on first /start, refresh name/username after."""
    user = await session.get(User, tg_user.id)
    if user is None:
        user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
        )
        session.add(user)
    else:
        user.username = tg_user.username
        user.first_name = tg_user.first_name
        if not user.is_active:
            user.is_active = True
    await session.commit()
    return user


async def get_user(session: AsyncSession, tg_id: int) -> User | None:
    return await session.get(User, tg_id)


async def find_user(session: AsyncSession, query: str) -> User | None:
    query = query.strip().lstrip("@")
    if query.isdigit():
        user = await session.get(User, int(query))
        if user:
            return user
    return await session.scalar(
        select(User).where(func.lower(User.username) == query.lower())
    )


async def list_users(session: AsyncSession, offset: int, limit: int) -> list[User]:
    return list(
        await session.scalars(
            select(User).order_by(User.date.desc()).offset(offset).limit(limit)
        )
    )


async def count_users(session: AsyncSession) -> int:
    return await session.scalar(select(func.count()).select_from(User)) or 0


async def count_voted(session: AsyncSession) -> int:
    return (
        await session.scalar(
            select(func.count()).select_from(User).where(User.vote_status == 1)
        )
        or 0
    )


async def count_blocked(session: AsyncSession) -> int:
    return (
        await session.scalar(
            select(func.count()).select_from(User).where(User.is_blocked == True)  # noqa: E712
        )
        or 0
    )


async def all_active_user_ids(session: AsyncSession) -> list[int]:
    return list(
        await session.scalars(
            select(User.telegram_id).where(
                User.is_active == True, User.is_blocked == False  # noqa: E712
            )
        )
    )


async def set_blocked(session: AsyncSession, tg_id: int, value: bool) -> None:
    await session.execute(
        update(User).where(User.telegram_id == tg_id).values(is_blocked=value)
    )
    await session.commit()


async def mark_inactive(session: AsyncSession, tg_id: int) -> None:
    await session.execute(
        update(User).where(User.telegram_id == tg_id).values(is_active=False)
    )
    await session.commit()
