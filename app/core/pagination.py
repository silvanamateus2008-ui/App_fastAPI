"""Paginacion estandar para las listas de la API."""

from pydantic import Field
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.schemas.base import CamelCaseSchema

TAMANO_MAXIMO = 100
TAMANO_POR_DEFECTO = 20


class PaginacionParams(CamelCaseSchema):
    """Parametros de pagina que llegan por query string."""

    pagina: int = Field(default=1, ge=1)
    tamano: int = Field(default=TAMANO_POR_DEFECTO, ge=1, le=TAMANO_MAXIMO)


class Pagina[T](CamelCaseSchema):
    """Envoltura de una lista paginada."""

    items: list[T]
    total: int
    pagina: int
    tamano: int
    paginas: int

    @property
    def tiene_siguiente(self) -> bool:
        return self.pagina < self.paginas


def paginar[T](db: Session, consulta: Select[tuple[T]], params: PaginacionParams) -> Pagina[T]:
    """Ejecuta la consulta y devuelve una pagina con el total real."""
    total = db.scalar(select(func.count()).select_from(consulta.order_by(None).subquery())) or 0
    offset = (params.pagina - 1) * params.tamano
    items = list(db.scalars(consulta.offset(offset).limit(params.tamano)).all())
    paginas = -(-total // params.tamano) if params.tamano else 0
    return Pagina(
        items=items,
        total=total,
        pagina=params.pagina,
        tamano=params.tamano,
        paginas=paginas,
    )
