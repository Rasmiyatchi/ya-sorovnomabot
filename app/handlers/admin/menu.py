from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app import texts
from app.db.repositories.admins import is_root
from app.handlers.admin.common import safe_edit
from app.keyboards.admin import admin_menu_kb

router = Router(name="admin-menu")


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        texts.ADMIN_MENU, reply_markup=admin_menu_kb(is_root(message.from_user.id))
    )


@router.callback_query(F.data == "adm:menu")
async def cb_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_edit(
        callback, texts.ADMIN_MENU, admin_menu_kb(is_root(callback.from_user.id))
    )
    await callback.answer()
