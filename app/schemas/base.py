from typing import Any

from pydantic import BaseModel, ConfigDict
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
    errors: list[dict[str, Any]] = []