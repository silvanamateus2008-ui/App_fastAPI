from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.cliente import Cliente
    from app.models.venta_detalle import DetalleVenta


class Venta(Base):
    __tablename__ = "Venta"

    id_venta: Mapped[int] = mapped_column(
        "id_Venta",
        Integer,
        primary_key=True,
        index=True,
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    total: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    id_cliente: Mapped[int] = mapped_column(
        "id_Cliente",
        ForeignKey("Cliente.id_Cliente", ondelete="RESTRICT"),
        nullable=False,
    )

    cliente: Mapped[Cliente] = relationship(back_populates="ventas")
    detalles: Mapped[list[DetalleVenta]] = relationship(back_populates="venta")
