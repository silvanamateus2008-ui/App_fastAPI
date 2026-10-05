from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ConflictoError, NoEncontradoError
from app.core.pagination import Pagina, PaginacionParams, paginar
from app.models.producto import Producto
from app.models.proveedor import Proveedor
from app.schemas.producto import ProductoCreate, ProductoUpdate


def _verificar_proveedor(db: Session, proveedor_id: int | None) -> None:
    """Evita un 500 por FK: el proveedor referenciado debe existir."""
    if proveedor_id is None:
        return
    if db.get(Proveedor, proveedor_id) is None:
        raise NoEncontradoError(f"Proveedor {proveedor_id} no encontrado")


def listar_productos(db: Session, paginacion: PaginacionParams) -> Pagina[Producto]:
    return paginar(db, select(Producto).order_by(Producto.id_producto), paginacion)


def obtener_producto(db: Session, producto_id: int) -> Producto:
    producto = db.get(Producto, producto_id)
    if producto is None:
        raise NoEncontradoError("Producto no encontrado")
    return producto


def crear_producto(db: Session, producto_in: ProductoCreate) -> Producto:
    _verificar_proveedor(db, producto_in.id_proveedor)
    producto = Producto(**producto_in.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


def actualizar_producto(db: Session, producto_id: int, producto_in: ProductoUpdate) -> Producto:
    producto = obtener_producto(db, producto_id)
    _verificar_proveedor(db, producto_in.id_proveedor)
    for campo, valor in producto_in.model_dump(exclude_unset=True).items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto


def eliminar_producto(db: Session, producto_id: int) -> None:
    producto = obtener_producto(db, producto_id)
    if producto.detalles:
        raise ConflictoError("No se puede eliminar un producto con ventas asociadas")
    db.delete(producto)
    db.commit()