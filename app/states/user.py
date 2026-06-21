from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class VoteFlow(StatesGroup):
    captcha = State()  # data: candidate_id, captcha_msg_id
