from __future__ import annotations

from pydantic import EmailStr

from app.models.usuario import RolUsuario
from app.schemas.base import CamelCaseSchema


class UsuarioCreate(CamelCaseSchema):
    username: str
    email: EmailStr
    nombre: str
    password: str
    rol: RolUsuario = RolUsuario.VENTAS


class UsuarioOut(CamelCaseSchema):
    id_usuario: int
    username: str
    email: EmailStr
    nombre: str
    rol: RolUsuario
    activo: bool = True
