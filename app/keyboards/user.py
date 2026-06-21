from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import texts
from app.db.models import Candidate, Channel


def channel_url(channel: Channel) -> str | None:
    if channel.invite_link:
        return channel.invite_link
    if channel.username:
        return f"https://t.me/{channel.username.lstrip('@')}"
    return None


def candidates_kb(candidates: list[Candidate]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for candidate in candidates:
        builder.button(
            text=f"{candidate.votes_count} {candidate.full_name}",
            callback_data=f"vote:{candidate.id}",
        )
    builder.button(text=texts.TOP_BUTTON, callback_data="top")
    builder.adjust(1)
    return builder.as_markup()


def confirm_kb(candidate_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BTN_CONFIRM, callback_data=f"confirm:{candidate_id}")
    builder.button(text=texts.CANCEL, callback_data="cancel")
    builder.adjust(1)
    return builder.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.CANCEL, callback_data="cancel")
    return builder.as_markup()


def subscribe_kb(channels: list[Channel]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    index = 0
    for channel in channels:
        url = channel_url(channel)
        if url is None:
            continue
        index += 1
        builder.button(text=texts.SUB_BTN_CHANNEL.format(i=index), url=url)
    builder.button(text=texts.SUB_BTN_JOINED, callback_data="recheck")
    builder.adjust(1)
    return builder.as_markup()
