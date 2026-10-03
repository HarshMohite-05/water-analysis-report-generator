from __future__ import annotations

import hashlib
import hmac
import os
from typing import Optional
from sqlalchemy import func

from database.database import session_scope
from database.models import User
from services import audit_service

_ITER = 200_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITER)
    return f"pbkdf2${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_hex, dk_hex = stored.split("$")
        if scheme != "pbkdf2":
            return False
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), _ITER)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except (ValueError, AttributeError, TypeError):
        return False


def authenticate(identifier: str, password: str) -> Optional[dict]:
    from services.dataset_service import sync_directory
    sync_directory()
    identifier = (identifier or "").strip()
    with session_scope() as s:
        u = (
            s.query(User)
            .filter((func.lower(User.employee_id) == identifier.lower()) | (User.email == identifier.lower()))
            .first()
        )
        if not u or not u.active or not verify_password(password, u.password_hash):
            audit_service.log(None, "login_failed", identifier)
            return None
        audit_service.log(u.id, "login", "")
        return dict(
            id=u.id, employee_id=u.employee_id, email=u.email, full_name=u.full_name,
            role=u.role, default_office=u.default_office,
        )



def refresh_user(user_id):
    from services.dataset_service import sync_directory
    sync_directory()
    with session_scope() as session:
        user = session.get(User, user_id)
        if not user or not user.active:
            return None
        return dict(id=user.id, employee_id=user.employee_id, full_name=user.full_name,
                    role=user.role, email=user.email, default_office=user.default_office,
                    contact_number=user.contact_number)
