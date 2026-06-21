from __future__ import annotations

from aiogram import Router

from app.filters import IsAdmin
from app.handlers.admin import (
    broadcast,
    candidates,
    channels,
    export,
    menu,
    results,
    root,
    settings,
    stats,
)


def build_admin_router() -> Router:
    """Admin router gated by IsAdmin. Root sub-router is additionally IsRoot
    gated, so root-only features stay invisible to regular admins."""
    admin_router = Router(name="admin")
    admin_router.message.filter(IsAdmin())
    admin_router.callback_query.filter(IsAdmin())

    admin_router.include_router(menu.router)
    admin_router.include_router(candidates.router)
    admin_router.include_router(results.router)
    admin_router.include_router(export.router)
    admin_router.include_router(stats.router)
    admin_router.include_router(channels.router)
    admin_router.include_router(broadcast.router)
    admin_router.include_router(settings.router)
    admin_router.include_router(root.router)
    return admin_router
