from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelCaseSchema(BaseModel):
    """Base de los schemas de la API: el JSON viaja en camelCase."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class ErrorNegocioOut(CamelCaseSchema):
    """Respuesta de error de negocio: {"detail", "code", "errors"}."""

    detail: str
    code: str
    errors: list[dict[str, Any]] = Field(default_factory=list)


RESPUESTAS_COMUNES = {
    401: {
        "description": "Se requiere autenticacion.",
        "model": ErrorNegocioOut,
    },
    403: {
        "description": "El usuario no tiene permisos para esta operacion.",
        "model": ErrorNegocioOut,
    },
    422: {
        "description": "La solicitud contiene datos invalidos.",
        "model": ErrorNegocioOut,
    }
}
