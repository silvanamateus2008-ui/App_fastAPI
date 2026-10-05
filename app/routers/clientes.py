from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.pagination import Pagina, PaginacionParams
from app.models.usuario import RolUsuario, Usuario
from app.schemas.base import ErrorNegocioOut
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from app.services.cliente_service import (
    actualizar_cliente,
    crear_cliente,
    eliminar_cliente,
    listar_clientes,
    obtener_cliente,
)

router = APIRouter(prefix="/api/clientes", tags=["clientes"])

cualquiera_autorizado = require_roles(
    RolUsuario.ADMIN,
    RolUsuario.ALMACEN,
    RolUsuario.VENTAS,
)
solo_administradores = require_roles(RolUsuario.ADMIN)

NO_ENCONTRADO = {404: {"description": "El cliente no existe", "model": ErrorNegocioOut}}
CON_VENTAS = {
    404: {"description": "El cliente no existe", "model": ErrorNegocioOut},
    409: {"description": "El cliente tiene ventas asociadas", "model": ErrorNegocioOut},
}


@router.get(
    "",
    response_model=Pagina[ClienteOut],
    summary="Listar clientes",
    description="Consulta la lista paginada de clientes registrados en la fabrica.",
    responses=NO_ENCONTRADO,
)
def listar_clientes_api(
    paginacion: Annotated[PaginacionParams, Depends()],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(cualquiera_autorizado)],
) -> Pagina[ClienteOut]:
    return listar_clientes(db, paginacion)


@router.get(
    "/{cliente_id}",
    response_model=ClienteOut,
    summary="Obtener cliente",
    description="Busca un cliente por su identificador unico.",
    responses=NO_ENCONTRADO,
)
def obtener_cliente_api(
    cliente_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(cualquiera_autorizado)],
) -> ClienteOut:
    return obtener_cliente(db, cliente_id)


@router.post(
    "",
    response_model=ClienteOut,
    summary="Crear cliente",
    description="Registra un nuevo cliente para la fabrica.",
    status_code=status.HTTP_201_CREATED,
    responses=NO_ENCONTRADO,
)
def crear_cliente_api(
    cliente_in: ClienteCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(cualquiera_autorizado)],
) -> ClienteOut:
    return crear_cliente(db, cliente_in)


@router.put(
    "/{cliente_id}",
    response_model=ClienteOut,
    summary="Actualizar cliente",
    description="Actualiza los datos de un cliente existente.",
    responses=CON_VENTAS,
)
def actualizar_cliente_api(
    cliente_id: Annotated[int, Path(gt=0)],
    cliente_in: ClienteUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(cualquiera_autorizado)],
) -> ClienteOut:
    return actualizar_cliente(db, cliente_id, cliente_in)


@router.delete(
    "/{cliente_id}",
    summary="Eliminar cliente",
    description="Elimina un cliente que no tenga ventas asociadas.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=CON_VENTAS,
)
def eliminar_cliente_api(
    cliente_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> None:
    eliminar_cliente(db, cliente_id)