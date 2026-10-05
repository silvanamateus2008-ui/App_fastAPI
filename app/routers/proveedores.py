from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.pagination import Pagina, PaginacionParams
from app.models.usuario import RolUsuario, Usuario
from app.schemas.base import ErrorNegocioOut
from app.schemas.proveedor import ProveedorCreate, ProveedorOut, ProveedorUpdate
from app.services.proveedor_service import (
    actualizar_proveedor,
    crear_proveedor,
    eliminar_proveedor,
    listar_proveedores,
    obtener_proveedor,
)

router = APIRouter(prefix="/api/proveedores", tags=["proveedores"])

almacen_y_admin = require_roles(RolUsuario.ADMIN, RolUsuario.ALMACEN)
solo_administradores = require_roles(RolUsuario.ADMIN)

NO_ENCONTRADO = {404: {"description": "El proveedor no existe", "model": ErrorNegocioOut}}
CON_PRODUCTOS = {
    404: {"description": "El proveedor no existe", "model": ErrorNegocioOut},
    409: {"description": "El proveedor tiene productos asociados", "model": ErrorNegocioOut},
}


@router.get(
    "",
    response_model=Pagina[ProveedorOut],
    summary="Listar proveedores",
    description="Consulta la lista paginada de proveedores operativos.",
    responses=NO_ENCONTRADO,
)
def listar_proveedores_api(
    paginacion: Annotated[PaginacionParams, Depends()],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(almacen_y_admin)],
) -> Pagina[ProveedorOut]:
    return listar_proveedores(db, paginacion)


@router.get(
    "/{proveedor_id}",
    response_model=ProveedorOut,
    summary="Obtener proveedor",
    description="Busca un proveedor por su identificador unico.",
    responses=NO_ENCONTRADO,
)
def obtener_proveedor_api(
    proveedor_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(almacen_y_admin)],
) -> ProveedorOut:
    return obtener_proveedor(db, proveedor_id)


@router.post(
    "",
    response_model=ProveedorOut,
    summary="Crear proveedor",
    description="Registra un proveedor nuevo para la fabrica.",
    status_code=status.HTTP_201_CREATED,
    responses=NO_ENCONTRADO,
)
def crear_proveedor_api(
    proveedor_in: ProveedorCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(almacen_y_admin)],
) -> ProveedorOut:
    return crear_proveedor(db, proveedor_in)


@router.put(
    "/{proveedor_id}",
    response_model=ProveedorOut,
    summary="Actualizar proveedor",
    description="Modifica los datos de un proveedor existente.",
    responses=CON_PRODUCTOS,
)
def actualizar_proveedor_api(
    proveedor_id: Annotated[int, Path(gt=0)],
    proveedor_in: ProveedorUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(almacen_y_admin)],
) -> ProveedorOut:
    return actualizar_proveedor(db, proveedor_id, proveedor_in)


@router.delete(
    "/{proveedor_id}",
    summary="Eliminar proveedor",
    description="Elimina un proveedor que no tenga productos asociados.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=CON_PRODUCTOS,
)
def eliminar_proveedor_api(
    proveedor_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> None:
    eliminar_proveedor(db, proveedor_id)