from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenOut
from app.schemas.base import ErrorNegocioOut
from app.schemas.usuario import UsuarioOut
from app.services.auth_service import login_user

router = APIRouter(prefix="/api/auth", tags=["autenticacion"])

NO_AUTORIZADO = {
    401: {"description": "Credenciales invalidas", "model": ErrorNegocioOut},
}


@router.post(
    "/login",
    response_model=TokenOut,
    summary="Iniciar sesion",
    description="Valida un usuario y devuelve un token JWT para acceder a la API.",
    status_code=status.HTTP_200_OK,
    responses=NO_AUTORIZADO,
)
def login_usuario(
    data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenOut:
    return login_user(db, data)


@router.get(
    "/me",
    response_model=UsuarioOut,
    summary="Consultar perfil del usuario",
    description="Devuelve la informacion del usuario autenticado.",
    responses=NO_AUTORIZADO,
)
def obtener_mi_perfil(
    usuario: Annotated[Usuario, Depends(get_current_user)],
) -> UsuarioOut:
    return usuario