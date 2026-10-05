from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ConflictoError, NoEncontradoError
from app.core.pagination import Pagina, PaginacionParams, paginar
from app.models.proveedor import Proveedor
from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate


def listar_proveedores(db: Session, paginacion: PaginacionParams) -> Pagina[Proveedor]:
    return paginar(db, select(Proveedor).order_by(Proveedor.id_proveedor), paginacion)


def obtener_proveedor(db: Session, proveedor_id: int) -> Proveedor:
    proveedor = db.get(Proveedor, proveedor_id)
    if proveedor is None:
        raise NoEncontradoError("Proveedor no encontrado")
    return proveedor


def crear_proveedor(db: Session, proveedor_in: ProveedorCreate) -> Proveedor:
    proveedor = Proveedor(**proveedor_in.model_dump())
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


def actualizar_proveedor(
    db: Session,
    proveedor_id: int,
    proveedor_in: ProveedorUpdate,
) -> Proveedor:
    proveedor = obtener_proveedor(db, proveedor_id)
    for campo, valor in proveedor_in.model_dump(exclude_unset=True).items():
        setattr(proveedor, campo, valor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


def eliminar_proveedor(db: Session, proveedor_id: int) -> None:
    proveedor = obtener_proveedor(db, proveedor_id)
    if proveedor.productos:
        raise ConflictoError("No se puede eliminar un proveedor con productos asociados")
    db.delete(proveedor)
    db.commit()