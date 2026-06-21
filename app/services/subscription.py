from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from app.db.models import Channel

log = logging.getLogger(__name__)

_SUBSCRIBED = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


async def _is_subscribed(bot: Bot, user_id: int, channel: Channel) -> bool:
    """True if subscribed. On configuration errors we 'fail open' for that
    channel (don't block the user) but log it, so a misconfigured channel
    doesn't lock everyone out."""
    try:
        member = await bot.get_chat_member(channel.chat_id, user_id)
    except TelegramForbiddenError:
        log.warning("Bot is not admin in channel %s; skipping check", channel.chat_id)
        return True
    except TelegramBadRequest as exc:
        text = str(exc).lower()
        if "user not found" in text or "participant_id_invalid" in text:
            return False
        log.warning("get_chat_member failed for %s: %s", channel.chat_id, exc)
        return True

    if member.status == ChatMemberStatus.RESTRICTED:
        return bool(getattr(member, "is_member", False))
    return member.status in _SUBSCRIBED


async def not_subscribed(
    bot: Bot, user_id: int, channels: list[Channel]
) -> list[Channel]:
    """Return the channels the user still needs to join (empty => all good)."""
    if not channels:
        return []
    results = await asyncio.gather(
        *(_is_subscribed(bot, user_id, ch) for ch in channels)
    )
    return [ch for ch, ok in zip(channels, results) if not ok]
