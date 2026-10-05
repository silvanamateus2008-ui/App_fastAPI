from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.pagination import Pagina, PaginacionParams
from app.models.usuario import RolUsuario, Usuario
from app.schemas.base import ErrorNegocioOut
from app.schemas.producto import ProductoCreate, ProductoOut, ProductoUpdate
from app.services.producto_service import (
    actualizar_producto,
    crear_producto,
    eliminar_producto,
    listar_productos,
    obtener_producto,
)

router = APIRouter(prefix="/api/productos", tags=["productos"])

cualquiera_autorizado = require_roles(
    RolUsuario.ADMIN,
    RolUsuario.ALMACEN,
    RolUsuario.VENTAS,
)
almacen_y_admin = require_roles(RolUsuario.ADMIN, RolUsuario.ALMACEN)
solo_administradores = require_roles(RolUsuario.ADMIN)

NO_ENCONTRADO = {404: {"description": "El producto no existe", "model": ErrorNegocioOut}}
CON_VENTAS = {
    404: {"description": "El producto no existe", "model": ErrorNegocioOut},
    409: {"description": "El producto tiene ventas asociadas", "model": ErrorNegocioOut},
}


@router.get(
    "",
    response_model=Pagina[ProductoOut],
    summary="Listar productos",
    description="Consulta la lista paginada de productos de la fabrica.",
    responses=NO_ENCONTRADO,
)
def listar_productos_api(
    paginacion: Annotated[PaginacionParams, Depends()],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(cualquiera_autorizado)],
) -> Pagina[ProductoOut]:
    return listar_productos(db, paginacion)


@router.get(
    "/{producto_id}",
    response_model=ProductoOut,
    summary="Obtener producto",
    description="Busca un producto por su identificador unico.",
    responses=NO_ENCONTRADO,
)
def obtener_producto_api(
    producto_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(cualquiera_autorizado)],
) -> ProductoOut:
    return obtener_producto(db, producto_id)


@router.post(
    "",
    response_model=ProductoOut,
    summary="Crear producto",
    description="Registra un producto nuevo en la fabrica.",
    status_code=status.HTTP_201_CREATED,
    responses=NO_ENCONTRADO,
)
def crear_producto_api(
    producto_in: ProductoCreate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(almacen_y_admin)],
) -> ProductoOut:
    return crear_producto(db, producto_in)


@router.put(
    "/{producto_id}",
    response_model=ProductoOut,
    summary="Actualizar producto",
    description="Actualiza los datos y el stock asociado a un producto.",
    responses=CON_VENTAS,
)
def actualizar_producto_api(
    producto_id: Annotated[int, Path(gt=0)],
    producto_in: ProductoUpdate,
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(almacen_y_admin)],
) -> ProductoOut:
    return actualizar_producto(db, producto_id, producto_in)


@router.delete(
    "/{producto_id}",
    summary="Eliminar producto",
    description="Elimina un producto del inventario cuando no tiene ventas asociadas.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=CON_VENTAS,
)
def eliminar_producto_api(
    producto_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db)],
    usuario: Annotated[Usuario, Depends(solo_administradores)],
) -> None:
    eliminar_producto(db, producto_id)