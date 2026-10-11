from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.pagination import Pagina, PaginacionParams
from app.models.usuario import RolUsuario, Usuario
from app.schemas.base import ErrorNegocioOut
from app.schemas.venta import VentaCreate, VentaOut
from app.services.venta_service import crear_venta, eliminar_venta, listar_ventas, obtener_venta

router = APIRouter(prefix="/api/ventas", tags=["ventas"])
from app.schemas.base import RESPUESTAS_COMUNES, ErrorNegocioOut
from app.schemas.venta import VentaCreate, VentaOut
from app.services.venta_service import crear_venta, eliminar_venta, listar_ventas, obtener_venta

router = APIRouter(
    prefix="/api/ventas",
    tags=["ventas"],
    responses=RESPUESTAS_COMUNES,
)

ventas_y_admin = require_roles(RolUsuario.ADMIN, RolUsuario.VENTAS)
solo_administradores = require_roles(RolUsuario.ADMIN)

NO_ENCONTRADA = {404: {"description": "La venta no existe", "model": ErrorNegocioOut}}
CON_DETALLES = {
    404: {"description": "La venta no existe", "model": ErrorNegocioOut},
    409: {"description": "La venta tiene detalles asociados", "model": ErrorNegocioOut},
}
REGLAS_VENTA = {
    404: {"description": "El cliente o el producto no existe", "model": ErrorNegocioOut},
    409: {"description": "No hay stock suficiente", "model": ErrorNegocioOut},
    422: {"description": "La venta no cumple las reglas de negocio", "model": ErrorNegocioOut},
}


@router.get(
    "",
    response_model=Pagina[VentaOut],
    summary="Listar ventas",
    description="Consulta la lista paginada de ventas registradas en la fabrica.",
    responses=NO_ENCONTRADA,
)
def listar_ventas_api(
    paginacion: Annotated[PaginacionParams, Depends()],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(ventas_y_admin)],
) -> Pagina[VentaOut]:
    return listar_ventas(db, paginacion)


@router.get(
    "/{venta_id}",
    response_model=VentaOut,
    summary="Obtener venta",
    description="Consulta una venta con sus detalles por identificador.",
    responses=NO_ENCONTRADA,
)
def obtener_venta_api(
    venta_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(ventas_y_admin)],
) -> VentaOut:
    return obtener_venta(db, venta_id)


@router.post(
    "",
    response_model=VentaOut,
    summary="Registrar venta",
    description="Registra una nueva venta junto con sus detalles y descuenta el stock asociado.",
    status_code=status.HTTP_201_CREATED,
    responses=REGLAS_VENTA,
)
def crear_venta_api(
    venta_in: VentaCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(ventas_y_admin)],
) -> VentaOut:
    return crear_venta(db, venta_in)


@router.delete(
    "/{venta_id}",
    summary="Eliminar venta",
    description="Elimina una venta sin detalles asociados. Se bloquea para preservar el historico.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=CON_DETALLES,
)
def eliminar_venta_api(
    venta_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> None:
    eliminar_venta(db, venta_id)