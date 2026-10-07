from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.producto import Producto
    from app.models.venta import Venta


class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id_detalle: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_venta: Mapped[int] = mapped_column(
        "id_venta",
        ForeignKey("Venta.id_Venta", ondelete="RESTRICT"),
        nullable=False,
    )
    id_producto: Mapped[int] = mapped_column(
        "id_producto",
        ForeignKey("Producto.id_Producto", ondelete="RESTRICT"),
        nullable=False,
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)

    venta: Mapped[Venta] = relationship(back_populates="detalles")
    producto: Mapped[Producto] = relationship(back_populates="detalles")
