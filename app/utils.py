from __future__ import annotations

import datetime as dt
import html


def utcnow() -> dt.datetime:
    return dt.datetime.now(tz=dt.timezone.utc)


def as_utc(value: dt.datetime | None) -> dt.datetime | None:
    """SQLite returns naive datetimes; treat them as UTC."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.timezone.utc)
    return value.astimezone(dt.timezone.utc)


def esc(value) -> str:
    """HTML-escape for safe insertion into parse_mode=HTML messages."""
    if value is None:
        return ""
    return html.escape(str(value))
