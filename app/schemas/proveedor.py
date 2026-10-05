from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.base import CamelCaseSchema


class ProveedorBase(CamelCaseSchema):
    nombre_proveedor: str = Field(..., min_length=1, max_length=100)
    telefono_proveedor: str | None = None
    correo_proveedor: EmailStr | None = None
    direccion_proveedor: str | None = None


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(ProveedorBase):
    pass


class ProveedorOut(ProveedorBase):
    id_proveedor: int
