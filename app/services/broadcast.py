from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import users as users_repo

log = logging.getLogger(__name__)

ProgressCb = Callable[[int, int], Awaitable[None]]  # (sent, processed)


async def broadcast(
    bot: Bot,
    session: AsyncSession,
    from_chat_id: int,
    message_id: int,
    user_ids: list[int],
    progress_cb: ProgressCb | None = None,
    progress_every: int = 25,
) -> tuple[int, int, int]:
    """Copy a message to every user id. Returns (sent, blocked, failed)."""
    sent = blocked = failed = 0
    total = len(user_ids)

    for index, user_id in enumerate(user_ids, start=1):
        try:
            await bot.copy_message(
                chat_id=user_id, from_chat_id=from_chat_id, message_id=message_id
            )
            sent += 1
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after + 1)
            try:
                await bot.copy_message(
                    chat_id=user_id, from_chat_id=from_chat_id, message_id=message_id
                )
                sent += 1
            except Exception:  # noqa: BLE001
                failed += 1
        except TelegramForbiddenError:
            await users_repo.mark_inactive(session, user_id)
            blocked += 1
        except TelegramBadRequest:
            await users_repo.mark_inactive(session, user_id)
            failed += 1
        except Exception as exc:  # noqa: BLE001
            log.warning("Broadcast to %s failed: %s", user_id, exc)
            failed += 1

        await asyncio.sleep(0.05)  # ~20 msg/s, under Telegram's ~30/s ceiling

        if progress_cb and (index % progress_every == 0 or index == total):
            await progress_cb(sent, index)

    return sent, blocked, failed
