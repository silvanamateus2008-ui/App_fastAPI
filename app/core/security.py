"""Hash de contrasenas y emision de tokens de acceso."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(user_id: int, role: str) -> str:
    """Emite un JWT con el id del usuario y su rol dentro del payload."""
    expira_en = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": str(user_id), "role": role, "exp": expira_en}
    return jwt.encode(payload, settings.signing_secret, algorithm=settings.jwt_algorithm)
