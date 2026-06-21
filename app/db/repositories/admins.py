from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.constants import Role
from app.db.models import Admin

ROOT_ID = settings.root_id


async def get_role(session: AsyncSession, tg_id: int) -> Role | None:
    return await session.scalar(select(Admin.role).where(Admin.telegram_id == tg_id))


async def is_admin(session: AsyncSession, tg_id: int) -> bool:
    """Root counts as an admin too."""
    if tg_id == ROOT_ID:
        return True
    return (await get_role(session, tg_id)) is not None


def is_root(tg_id: int) -> bool:
    # Hardcoded check is the source of truth for root identity.
    return tg_id == ROOT_ID


# ── THE INVISIBILITY SEAM ────────────────────────────────────────────────
# Every admin-facing listing/count of admins MUST go through these helpers so
# the root admin never appears anywhere.
async def list_visible_admins(session: AsyncSession) -> list[Admin]:
    return list(
        await session.scalars(
            select(Admin)
            .where(Admin.role != Role.ROOT)
            .order_by(Admin.created_at.asc())
        )
    )


async def count_visible_admins(session: AsyncSession) -> int:
    return (
        await session.scalar(
            select(func.count()).select_from(Admin).where(Admin.role != Role.ROOT)
        )
        or 0
    )


async def ensure_admin(
    session: AsyncSession, tg_id: int, role: Role, added_by: int | None = None
) -> None:
    """Idempotent upsert used by the seeder."""
    existing = await session.get(Admin, tg_id)
    if existing is None:
        session.add(Admin(telegram_id=tg_id, role=role, added_by=added_by))
    else:
        existing.role = role
    await session.commit()


async def add_admin(session: AsyncSession, tg_id: int, added_by: int) -> bool:
    """Returns True if a new admin was added, False if root/already exists."""
    if tg_id == ROOT_ID:
        return False
    existing = await session.get(Admin, tg_id)
    if existing is not None:
        return False
    session.add(Admin(telegram_id=tg_id, role=Role.ADMIN, added_by=added_by))
    await session.commit()
    return True


async def remove_admin(session: AsyncSession, tg_id: int) -> bool:
    """Root is undeletable and unaddressable."""
    if tg_id == ROOT_ID:
        return False
    existing = await session.get(Admin, tg_id)
    if existing is None or existing.role == Role.ROOT:
        return False
    await session.delete(existing)
    await session.commit()
    return True
