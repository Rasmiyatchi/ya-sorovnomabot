from __future__ import annotations

from aiogram.types import Message

from app import texts
from app.db.repositories import candidates as candidates_repo
from app.db.repositories import settings_repo
from app.keyboards.user import candidates_kb
from app.utils import esc


async def show_poll(message: Message, session) -> None:
    """Render the main poll screen (banner + name + description + candidates)."""
    setting = await settings_repo.get_settings(session)
    candidates = await candidates_repo.list_active(session)

    name = setting.poll_name or texts.DEFAULT_POLL_NAME
    description = setting.description or texts.DEFAULT_DESCRIPTION
    caption = f"<b>{esc(name)}</b>\n\n{esc(description)}"

    if not candidates:
        await message.answer(f"{caption}\n\n{texts.NO_CANDIDATES}")
        return

    markup = candidates_kb(candidates)
    
    if setting.banner_file_id:
        if len(caption) > 1024:
            caption = caption[:1021] + "..."
        await message.answer_photo(
            setting.banner_file_id, caption=caption, reply_markup=markup
        )
    else:
        if len(caption) > 4096:
            caption = caption[:4093] + "..."
        await message.answer(caption, reply_markup=markup)
