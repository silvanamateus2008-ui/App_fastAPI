"""Operaciones de borrado protegidas por las restricciones de la base."""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictoError


def eliminar_con_restriccion(db: Session, objeto: object, mensaje: str) -> None:
    """Borra un objeto y traduce la violacion de ON DELETE RESTRICT en un 409.

    Cubre la carrera entre la verificacion previa y el borrado real: si otra
    peticion creo un registro hijo en ese intervalo, la base rechaza el borrado
    y el cliente recibe el conflicto en lugar de un 500.
    """
    db.delete(objeto)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictoError(mensaje) from None
