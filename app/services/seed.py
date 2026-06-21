from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.constants import Role
from app.db.repositories import admins as admins_repo
from app.db.repositories import settings_repo

log = logging.getLogger(__name__)


async def seed(session: AsyncSession) -> None:
    """Seed root + regular admins from config and ensure the settings row.

    The root id is seeded with role=ROOT and is intentionally NOT part of
    ADMIN_IDS, so it stays invisible in every admin-facing listing.
    """
    await admins_repo.ensure_admin(session, settings.root_id, Role.ROOT)

    for admin_id in settings.admin_ids:
        if admin_id == settings.root_id:
            continue
        await admins_repo.ensure_admin(session, admin_id, Role.ADMIN)

    await settings_repo.get_settings(session)
    log.info(
        "Seed complete: root=%s, admins=%s",
        settings.root_id,
        settings.admin_ids,
    )
