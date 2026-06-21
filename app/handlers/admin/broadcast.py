from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app import texts
from app.db.repositories import users as users_repo
from app.db.repositories.admins import is_root
from app.handlers.admin.common import safe_edit
from app.keyboards.admin import admin_menu_kb, broadcast_confirm_kb, cancel_kb
from app.services.broadcast import broadcast as do_broadcast
from app.states.admin import Broadcast

router = Router(name="admin-broadcast")


@router.callback_query(F.data == "adm:broadcast")
async def cb_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Broadcast.waiting_content)
    await safe_edit(callback, texts.BROADCAST_ASK, cancel_kb())
    await callback.answer()


@router.message(Broadcast.waiting_content)
async def on_content(message: Message, state: FSMContext, session: AsyncSession) -> None:
    count = len(await users_repo.all_active_user_ids(session))
    await state.update_data(
        from_chat_id=message.chat.id, message_id=message.message_id
    )
    await state.set_state(Broadcast.waiting_confirm)
    await message.answer(
        texts.BROADCAST_CONFIRM.format(n=count), reply_markup=broadcast_confirm_kb()
    )


@router.callback_query(Broadcast.waiting_confirm, F.data == "bcast:go")
async def cb_go(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    data = await state.get_data()
    await state.clear()
    from_chat_id = data.get("from_chat_id")
    message_id = data.get("message_id")
    if from_chat_id is None or message_id is None:
        await callback.answer()
        return

    user_ids = await users_repo.all_active_user_ids(session)
    total = len(user_ids)
    status = await callback.message.answer(texts.BROADCAST_START)
    await callback.answer()

    async def progress(sent: int, _processed: int) -> None:
        try:
            await status.edit_text(
                texts.BROADCAST_PROGRESS.format(sent=sent, total=total)
            )
        except Exception:  # noqa: BLE001
            pass

    sent, blocked, failed = await do_broadcast(
        bot, session, from_chat_id, message_id, user_ids, progress_cb=progress
    )
    try:
        await status.edit_text(
            texts.BROADCAST_DONE.format(sent=sent, blocked=blocked, failed=failed)
        )
    except Exception:  # noqa: BLE001
        await callback.message.answer(
            texts.BROADCAST_DONE.format(sent=sent, blocked=blocked, failed=failed)
        )
    await callback.message.answer(
        texts.ADMIN_MENU, reply_markup=admin_menu_kb(is_root(callback.from_user.id))
    )
