from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import texts
from app.db.models import Admin, User


def root_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.ROOT_DASHBOARD, callback_data="root:dashboard")
    builder.button(text=texts.ROOT_ADMINS, callback_data="root:admins")
    builder.button(text=texts.ROOT_USERS, callback_data="root:users")
    builder.button(text=texts.BACK, callback_data="adm:menu")
    builder.adjust(2)
    return builder.as_markup()


def back_to_root_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BACK, callback_data="root:menu")
    return builder.as_markup()


def root_cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.CANCEL, callback_data="root:menu")
    return builder.as_markup()


def admins_kb(admins: list[Admin]) -> InlineKeyboardMarkup:
    """Caller MUST pass only visible (non-root) admins."""
    builder = InlineKeyboardBuilder()
    for admin in admins:
        builder.button(
            text=texts.ADM_BTN_DEL.format(tg_id=admin.telegram_id),
            callback_data=f"radel:{admin.telegram_id}",
        )
    builder.button(text=texts.ROOT_ADD_ADMIN, callback_data="root:addadmin")
    builder.button(text=texts.BACK, callback_data="root:menu")
    builder.adjust(1)
    return builder.as_markup()


def user_card_kb(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if user.vote_status:
        builder.button(
            text=texts.ROOT_USER_RESET, callback_data=f"ruser:reset:{user.telegram_id}"
        )
    if user.is_blocked:
        builder.button(
            text=texts.ROOT_USER_UNBLOCK,
            callback_data=f"ruser:unblock:{user.telegram_id}",
        )
    else:
        builder.button(
            text=texts.ROOT_USER_BLOCK,
            callback_data=f"ruser:block:{user.telegram_id}",
        )
    builder.button(text=texts.BACK, callback_data="root:menu")
    builder.adjust(1)
    return builder.as_markup()
