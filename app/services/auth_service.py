from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.errors import NoAutorizadoError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenOut


def login_user(db: Session, data: LoginRequest) -> TokenOut:
    """Valida las credenciales y devuelve un token de acceso."""
    usuario = db.scalar(select(Usuario).where(Usuario.email == data.email.lower()))
    if usuario is None or not usuario.activo:
        raise NoAutorizadoError("Credenciales invalidas")
    if not verify_password(data.password, usuario.password_hash):
        raise NoAutorizadoError("Credenciales invalidas")
    return TokenOut(access_token=create_access_token(usuario.id_usuario, usuario.rol.value))


def create_seed_user(
    db: Session,
    *,
    username: str,
    email: str,
    nombre: str,
    password: str,
    rol: str,
) -> Usuario:
    existing = db.scalar(
        select(Usuario).where(
            or_(Usuario.username == username, Usuario.email == email.lower())
        )
    )
    if existing is not None:
        return existing
    usuario = Usuario(
        username=username,
        email=email.lower(),
        nombre=nombre,
        password_hash=hash_password(password),
        rol=rol,
        activo=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
