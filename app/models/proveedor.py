from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.producto import Producto


class Proveedor(Base):
    __tablename__ = "Proveedor"

    id_proveedor: Mapped[int] = mapped_column(
        "id_Proveedor",
        primary_key=True,
        index=True,
    )
    nombre_proveedor: Mapped[str] = mapped_column(
        "nombreProveedor",
        String(100),
        nullable=False,
    )
    telefono_proveedor: Mapped[str | None] = mapped_column(
        "telefonoProveedor",
        String(30),
        nullable=True,
    )
    correo_proveedor: Mapped[str | None] = mapped_column(
        "correoProveedor",
        String(150),
        nullable=True,
    )
    direccion_proveedor: Mapped[str | None] = mapped_column(
        "direccionProveedor",
        String(200),
        nullable=True,
    )

    productos: Mapped[list[Producto]] = relationship(back_populates="proveedor")
