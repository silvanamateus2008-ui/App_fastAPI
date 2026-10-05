from __future__ import annotations

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import (
    ConflictoError,
    NoEncontradoError,
    ReglaNegocioError,
    StockInsuficienteError,
)
from app.core.pagination import Pagina, PaginacionParams, paginar
from app.models.cliente import Cliente
from app.models.producto import Producto
from app.models.venta import Venta
from app.models.venta_detalle import DetalleVenta
from app.schemas.venta import VentaCreate

DOS_DECIMALES = Decimal("0.01")


def _redondear(valor: Decimal) -> Decimal:
    return valor.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)


def listar_ventas(db: Session, paginacion: PaginacionParams) -> Pagina[Venta]:
    consulta = (
        select(Venta)
        .options(selectinload(Venta.detalles))
        .order_by(Venta.id_venta)
    )
    return paginar(db, consulta, paginacion)


def obtener_venta(db: Session, venta_id: int) -> Venta:
    venta = db.get(Venta, venta_id)
    if venta is None:
        raise NoEncontradoError("Venta no encontrada")
    return venta


def crear_venta(db: Session, venta_in: VentaCreate) -> Venta:
    cliente = db.get(Cliente, venta_in.id_cliente)
    if cliente is None:
        raise NoEncontradoError("Cliente no encontrado")
    if not venta_in.detalles:
        raise ReglaNegocioError("La venta debe incluir al menos un detalle")

    venta = Venta(
        id_cliente=venta_in.id_cliente,
        fecha=datetime.now(UTC),
        total=Decimal("0.00"),
    )
    total = Decimal("0.00")

    try:
        db.add(venta)
        db.flush()

        for detalle_in in venta_in.detalles:
            producto = db.get(Producto, detalle_in.id_producto)
            if producto is None:
                raise NoEncontradoError(f"Producto {detalle_in.id_producto} no encontrado")
            if producto.stock < detalle_in.cantidad:
                raise StockInsuficienteError(
                    f"No hay stock suficiente para {producto.nombre_producto}"
                )

            subtotal = _redondear(producto.precio * detalle_in.cantidad)
            total += subtotal

            db.add(
                DetalleVenta(
                    id_venta=venta.id_venta,
                    id_producto=detalle_in.id_producto,
                    cantidad=detalle_in.cantidad,
                    precio_unitario=producto.precio,
                    subtotal=subtotal,
                )
            )
            producto.stock -= detalle_in.cantidad

        venta.total = _redondear(total)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(venta)
    return venta


def eliminar_venta(db: Session, venta_id: int) -> None:
    venta = obtener_venta(db, venta_id)
    if venta.detalles:
        raise ConflictoError("No se puede eliminar una venta con detalles asociados")
    db.delete(venta)
    db.commit()