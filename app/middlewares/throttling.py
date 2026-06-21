from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject, User
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    """Per-user rate limit to curb captcha brute-force and button spam."""

    def __init__(self, rate: float) -> None:
        self.cache: TTLCache = TTLCache(maxsize=10_000, ttl=rate)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user is not None:
            if user.id in self.cache:
                if isinstance(event, CallbackQuery):
                    await event.answer()
                return None
            self.cache[user.id] = True
        return await handler(event, data)
