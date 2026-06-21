from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import admins as admins_repo


class IsAdmin(BaseFilter):
    """Passes for regular admins AND root (root is also an admin)."""

    async def __call__(self, event: TelegramObject, session: AsyncSession) -> bool:
        user = getattr(event, "from_user", None)
        if user is None:
            return False
        return await admins_repo.is_admin(session, user.id)


class IsRoot(BaseFilter):
    """Passes only for the hidden root id."""

    async def __call__(self, event: TelegramObject) -> bool:
        user = getattr(event, "from_user", None)
        if user is None:
            return False
        return admins_repo.is_root(user.id)
