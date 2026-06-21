from __future__ import annotations

from io import BytesIO

import matplotlib

matplotlib.use("Agg")  # headless backend, must be set before pyplot import

import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.db.models import Candidate, Vote  # noqa: E402
from app.utils import as_utc  # noqa: E402


def _fig_to_png(fig) -> bytes:
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return buffer.getvalue()


async def candidates_bar(session: AsyncSession) -> bytes | None:
    candidates = list(
        await session.scalars(
            select(Candidate)
            .where(Candidate.is_active == True)  # noqa: E712
            .order_by(Candidate.votes_count.asc(), Candidate.id.desc())
        )
    )
    if not candidates or sum(c.votes_count for c in candidates) == 0:
        return None

    names = [
        (c.full_name if len(c.full_name) <= 28 else c.full_name[:25] + "…")
        for c in candidates
    ]
    values = [c.votes_count for c in candidates]

    fig, ax = plt.subplots(figsize=(9, max(3, 0.5 * len(candidates) + 1)))
    bars = ax.barh(names, values, color="#2a6fdb")
    ax.bar_label(bars, padding=3)
    ax.set_title("Nomzodlar bo'yicha ovozlar")
    ax.set_xlabel("Ovozlar soni")
    ax.margins(x=0.12)
    return _fig_to_png(fig)


async def votes_over_time(session: AsyncSession) -> bytes | None:
    rows = list(
        await session.scalars(select(Vote.created_at).order_by(Vote.created_at.asc()))
    )
    if len(rows) < 2:
        return None

    times = [as_utc(r) for r in rows]
    cumulative = list(range(1, len(times) + 1))

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(times, cumulative, color="#2a6fdb", linewidth=2)
    ax.fill_between(times, cumulative, color="#2a6fdb", alpha=0.12)
    ax.set_title("Vaqt bo'yicha ovozlar dinamikasi")
    ax.set_ylabel("Jami ovozlar")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
    fig.autofmt_xdate()
    return _fig_to_png(fig)
