from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from app.schemas.base import CamelCaseSchema


class ProductoBase(CamelCaseSchema):
    nombre_producto: str = Field(..., min_length=1, max_length=120)
    tipo: str | None = None
    precio: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    id_proveedor: int | None = None


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(ProductoBase):
    pass


class ProductoOut(ProductoBase):
    id_producto: int
