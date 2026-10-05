from __future__ import annotations

from enum import StrEnum

from sqlalchemy import Boolean, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RolUsuario(StrEnum):
    ADMIN = "ADMIN"
    ALMACEN = "ALMACEN"
    VENTAS = "VENTAS"


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(
        SAEnum(RolUsuario, native_enum=False, validate_strings=True),
        nullable=False,
        default=RolUsuario.VENTAS,
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
