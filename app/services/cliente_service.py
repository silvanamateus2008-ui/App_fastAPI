from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ConflictoError, NoEncontradoError
from app.core.pagination import Pagina, PaginacionParams, paginar
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.services._integridad import eliminar_con_restriccion


def listar_clientes(db: Session, paginacion: PaginacionParams) -> Pagina[Cliente]:
    return paginar(db, select(Cliente).order_by(Cliente.id_cliente), paginacion)


def obtener_cliente(db: Session, cliente_id: int) -> Cliente:
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise NoEncontradoError("Cliente no encontrado")
    return cliente


def crear_cliente(db: Session, cliente_in: ClienteCreate) -> Cliente:
    cliente = Cliente(**cliente_in.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def actualizar_cliente(db: Session, cliente_id: int, cliente_in: ClienteUpdate) -> Cliente:
    cliente = obtener_cliente(db, cliente_id)
    for campo, valor in cliente_in.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return cliente


def eliminar_cliente(db: Session, cliente_id: int) -> None:
    cliente = obtener_cliente(db, cliente_id)
    if cliente.ventas:
        raise ConflictoError("No se puede eliminar un cliente con ventas asociadas")
    eliminar_con_restriccion(db, cliente, "No se puede eliminar un cliente con ventas asociadas")
