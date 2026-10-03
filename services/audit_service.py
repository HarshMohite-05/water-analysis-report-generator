from __future__ import annotations

from database.database import session_scope
from database.models import AuditLog


def log(user_id, action: str, detail: str = "") -> None:
    with session_scope() as s:
        s.add(AuditLog(user_id=user_id, action=action, detail=detail))


def recent(limit: int = 200):
    with session_scope() as s:
        rows = s.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
        return [dict(at=r.at, user_id=r.user_id, action=r.action, detail=r.detail) for r in rows]