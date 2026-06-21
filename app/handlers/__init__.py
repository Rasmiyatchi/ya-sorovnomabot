from __future__ import annotations

from aiogram import Dispatcher

from app.handlers.admin import build_admin_router
from app.handlers.user import start as user_start
from app.handlers.user import top as user_top
from app.handlers.user import vote as user_vote


def setup_routers(dp: Dispatcher) -> None:
    # User routers first (state-gated captcha won't shadow admin flows).
    dp.include_router(user_start.router)
    dp.include_router(user_top.router)
    dp.include_router(user_vote.router)
    # Admin (with nested, double-gated root) last.
    dp.include_router(build_admin_router())
