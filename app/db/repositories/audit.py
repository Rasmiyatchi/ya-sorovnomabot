from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditLog


async def log_action(
    session: AsyncSession, actor_id: int, action: str, target: str | None = None
) -> None:
    session.add(AuditLog(actor_id=actor_id, action=action, target=target))
    await session.commit()
