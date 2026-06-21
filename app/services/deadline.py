from __future__ import annotations

import datetime as dt

from app.config import settings
from app.db.models import Setting
from app.utils import as_utc, utcnow

_FMT = "%Y-%m-%d %H:%M"


def poll_closed(setting: Setting | None) -> bool:
    if setting is None or setting.deadline is None:
        return False
    return utcnow() >= as_utc(setting.deadline)


def parse_deadline(text: str) -> dt.datetime | None:
    """Parse 'YYYY-MM-DD HH:MM' in local tz, return UTC. None if invalid."""
    try:
        local = dt.datetime.strptime(text.strip(), _FMT).replace(tzinfo=settings.tz)
    except ValueError:
        return None
    return local.astimezone(dt.timezone.utc)


def format_deadline(deadline: dt.datetime | None) -> str:
    if deadline is None:
        return "—"
    local = as_utc(deadline).astimezone(settings.tz)
    return local.strftime(_FMT)
