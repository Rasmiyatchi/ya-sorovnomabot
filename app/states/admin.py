from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class AddCandidate(StatesGroup):
    waiting_name = State()


class Broadcast(StatesGroup):
    waiting_content = State()
    waiting_confirm = State()


class AddChannel(StatesGroup):
    waiting_channel = State()


class SettingsFSM(StatesGroup):
    waiting_name = State()
    waiting_description = State()
    waiting_banner = State()
    waiting_deadline = State()


class ManageAdmin(StatesGroup):
    waiting_admin_id = State()


class FindUser(StatesGroup):
    waiting_query = State()
