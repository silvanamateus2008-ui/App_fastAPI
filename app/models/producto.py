from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.proveedor import Proveedor
    from app.models.venta_detalle import DetalleVenta


class Producto(Base):
    __tablename__ = "Producto"

    id_producto: Mapped[int] = mapped_column("id_Producto", primary_key=True, index=True)
    nombre_producto: Mapped[str] = mapped_column("nombreProducto", String(120), nullable=False)
    tipo: Mapped[str | None] = mapped_column(String(80), nullable=True)
    precio: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    id_proveedor: Mapped[int | None] = mapped_column(
        "id_Proveedor",
        ForeignKey("Proveedor.id_Proveedor", ondelete="RESTRICT"),
        nullable=True,
    )

    proveedor: Mapped[Proveedor | None] = relationship(back_populates="productos")
    detalles: Mapped[list[DetalleVenta]] = relationship(back_populates="producto")
