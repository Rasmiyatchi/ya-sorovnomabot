from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery


async def safe_edit(callback: CallbackQuery, text: str, reply_markup=None) -> None:
    """Edit the callback message; fall back to sending a new message when the
    original can't be edited (e.g. it's a photo, or content is unchanged)."""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=reply_markup)
