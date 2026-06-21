from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import texts
from app.db.models import Candidate, Channel


def admin_menu_kb(is_root: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.ADM_ADD_CANDIDATE, callback_data="adm:add_cand")
    builder.button(text=texts.ADM_DEL_CANDIDATE, callback_data="adm:del_cand")
    builder.button(text=texts.ADM_RESULTS, callback_data="adm:results")
    builder.button(text=texts.ADM_EXPORT, callback_data="adm:export")
    builder.button(text=texts.ADM_STATS, callback_data="adm:stats")
    builder.button(text=texts.ADM_CHANNELS, callback_data="adm:channels")
    builder.button(text=texts.ADM_BROADCAST, callback_data="adm:broadcast")
    builder.button(text=texts.ADM_SETTINGS, callback_data="adm:settings")
    builder.button(text="📢 Kanalga e'lon", callback_data="adm:post_poll")
    builder.button(text="🔄 Ovozlarni nolga tushirish", callback_data="adm:reset_votes")
    if is_root:
        builder.button(text=texts.ROOT_PANEL_BTN, callback_data="root:menu")
    builder.adjust(2)
    return builder.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BACK, callback_data="adm:menu")
    return builder.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.CANCEL, callback_data="adm:menu")
    return builder.as_markup()


def delete_candidates_kb(candidates: list[Candidate]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for candidate in candidates:
        builder.button(
            text=f"🗑 {candidate.full_name} ({candidate.votes_count})",
            callback_data=f"acdel:{candidate.id}",
        )
    builder.button(text=texts.BACK, callback_data="adm:menu")
    builder.adjust(1)
    return builder.as_markup()


def channels_kb(channels: list[Channel]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for channel in channels:
        builder.button(
            text=texts.CH_BTN_DEL.format(title=channel.title or channel.chat_id),
            callback_data=f"chdel:{channel.id}",
        )
    builder.button(text="➕ Kanal qo'shish", callback_data="chadd")
    builder.button(text=texts.BACK, callback_data="adm:menu")
    builder.adjust(1)
    return builder.as_markup()


def settings_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.SET_NAME, callback_data="set:name")
    builder.button(text=texts.SET_DESC, callback_data="set:desc")
    builder.button(text=texts.SET_BANNER, callback_data="set:banner")
    builder.button(text=texts.SET_DEADLINE, callback_data="set:deadline")
    builder.button(text=texts.BACK, callback_data="adm:menu")
    builder.adjust(2)
    return builder.as_markup()


def broadcast_confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BROADCAST_YES, callback_data="bcast:go")
    builder.button(text=texts.CANCEL, callback_data="adm:menu")
    builder.adjust(1)
    return builder.as_markup()
