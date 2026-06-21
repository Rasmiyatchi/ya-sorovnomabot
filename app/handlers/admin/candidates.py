from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app import texts
from app.db.repositories import candidates as candidates_repo
from app.handlers.admin.common import safe_edit
from app.keyboards.admin import (
    admin_menu_kb,
    cancel_kb,
    delete_candidates_kb,
)
from app.db.repositories.admins import is_root
from app.states.admin import AddCandidate
from app.utils import esc

router = Router(name="admin-candidates")


@router.callback_query(F.data == "adm:add_cand")
async def cb_add(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddCandidate.waiting_name)
    await safe_edit(callback, texts.ASK_CANDIDATE_NAME, cancel_kb())
    await callback.answer()


@router.message(AddCandidate.waiting_name, F.text)
async def on_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    candidate = await candidates_repo.add(session, message.text)
    await state.clear()
    await message.answer(texts.CANDIDATE_ADDED.format(name=esc(candidate.full_name)))
    await message.answer(
        texts.ADMIN_MENU, reply_markup=admin_menu_kb(is_root(message.from_user.id))
    )


@router.callback_query(F.data == "adm:del_cand")
async def cb_del_list(callback: CallbackQuery, session: AsyncSession) -> None:
    candidates = await candidates_repo.list_active(session)
    if not candidates:
        await safe_edit(callback, texts.DEL_EMPTY, delete_candidates_kb([]))
    else:
        await safe_edit(callback, texts.DEL_PICK, delete_candidates_kb(candidates))
    await callback.answer()


@router.callback_query(F.data.startswith("acdel:"))
async def cb_del(callback: CallbackQuery, session: AsyncSession) -> None:
    candidate_id = int(callback.data.split(":")[1])
    candidate = await candidates_repo.soft_delete(session, candidate_id)
    if candidate is not None:
        await callback.answer(
            texts.CANDIDATE_DELETED.format(name=candidate.full_name), show_alert=True
        )
    else:
        await callback.answer(texts.CANDIDATE_NOT_FOUND, show_alert=True)
    candidates = await candidates_repo.list_active(session)
    text = texts.DEL_PICK if candidates else texts.DEL_EMPTY
    await safe_edit(callback, text, delete_candidates_kb(candidates))
