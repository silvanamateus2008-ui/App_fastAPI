from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.base import CamelCaseSchema


class DetalleVentaCreate(CamelCaseSchema):
    id_producto: int
    cantidad: int = Field(..., gt=0)


class DetalleVentaOut(CamelCaseSchema):
    id_detalle: int
    id_venta: int
    id_producto: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class VentaCreate(CamelCaseSchema):
    id_cliente: int
    detalles: list[DetalleVentaCreate]


class VentaOut(CamelCaseSchema):
    id_venta: int
    fecha: datetime
    total: Decimal
    id_cliente: int
    detalles: list[DetalleVentaOut] = []
