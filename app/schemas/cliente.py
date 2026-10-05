from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.base import CamelCaseSchema


class ClienteBase(CamelCaseSchema):
    nombre_cliente: str = Field(..., min_length=1, max_length=100)
    telefono: str | None = None
    correo: EmailStr | None = None
    direccion: str | None = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(ClienteBase):
    pass


class ClienteOut(ClienteBase):
    id_cliente: int
