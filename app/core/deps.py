"""Dependencias de autenticacion y autorizacion."""

from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.errors import NoAutorizadoError, PermisoError
from app.models.usuario import RolUsuario, Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    """Valida el token y devuelve el usuario vigente en la base de datos."""
    if token is None:
        raise NoAutorizadoError
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        usuario_id = int(payload["sub"])
        rol = payload["role"]
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise NoAutorizadoError from None

    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.activo or usuario.rol.value != rol:
        raise NoAutorizadoError
    return usuario


def require_roles(*roles: RolUsuario) -> Callable[..., Usuario]:
    """Construye una dependencia que solo deja pasar a los roles indicados."""

    def role_dependency(
        current_user: Annotated[Usuario, Depends(get_current_user)],
    ) -> Usuario:
        if current_user.rol not in roles:
            raise PermisoError
        return current_user

    return role_dependency