from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Channel


async def list_active(session: AsyncSession) -> list[Channel]:
    return list(
        await session.scalars(
            select(Channel)
            .where(Channel.is_active == True)  # noqa: E712
            .order_by(Channel.position.asc(), Channel.id.asc())
        )
    )


async def list_all(session: AsyncSession) -> list[Channel]:
    return list(
        await session.scalars(
            select(Channel).order_by(Channel.position.asc(), Channel.id.asc())
        )
    )


async def get(session: AsyncSession, channel_id: int) -> Channel | None:
    return await session.get(Channel, channel_id)


async def add_channel(
    session: AsyncSession,
    chat_id: int,
    title: str | None,
    username: str | None,
    invite_link: str | None,
) -> Channel:
    existing = await session.scalar(select(Channel).where(Channel.chat_id == chat_id))
    if existing is not None:
        existing.title = title or existing.title
        existing.username = username or existing.username
        existing.invite_link = invite_link or existing.invite_link
        existing.is_active = True
        await session.commit()
        return existing

    max_pos = await session.scalar(select(func.coalesce(func.max(Channel.position), 0)))
    channel = Channel(
        chat_id=chat_id,
        title=title,
        username=username,
        invite_link=invite_link,
        position=(max_pos or 0) + 1,
    )
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return channel


async def remove_channel(session: AsyncSession, channel_id: int) -> bool:
    channel = await session.get(Channel, channel_id)
    if channel is None:
        return False
    await session.delete(channel)
    await session.commit()
    return True


async def count_active(session: AsyncSession) -> int:
    return (
        await session.scalar(
            select(func.count()).select_from(Channel).where(
                Channel.is_active == True  # noqa: E712
            )
        )
        or 0
    )
