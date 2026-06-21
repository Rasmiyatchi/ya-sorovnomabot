from __future__ import annotations

import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Setting

_DEFAULT_ID = 1


async def get_settings(session: AsyncSession) -> Setting:
    """Return the singleton settings row, creating it if missing."""
    setting = await session.get(Setting, _DEFAULT_ID)
    if setting is None:
        setting = Setting(id=_DEFAULT_ID)
        session.add(setting)
        await session.commit()
        await session.refresh(setting)
    return setting


async def update_settings(session: AsyncSession, **fields) -> Setting:
    setting = await get_settings(session)
    for key, value in fields.items():
        setattr(setting, key, value)
    await session.commit()
    await session.refresh(setting)
    return setting


async def set_deadline(
    session: AsyncSession, deadline: dt.datetime | None
) -> Setting:
    return await update_settings(session, deadline=deadline)
