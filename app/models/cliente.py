from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.venta import Venta


class Cliente(Base):
    __tablename__ = "Cliente"

    id_cliente: Mapped[int] = mapped_column("id_Cliente", primary_key=True, index=True)
    nombre_cliente: Mapped[str] = mapped_column("nombreCliente", String(100), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    correo: Mapped[str | None] = mapped_column(String(150), nullable=True)
    direccion: Mapped[str | None] = mapped_column(String(200), nullable=True)

    ventas: Mapped[list[Venta]] = relationship(back_populates="cliente")
