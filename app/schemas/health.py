"""Esquemas de respuesta para los endpoints de infraestructura."""

from typing import Literal

from app.schemas.base import CamelCaseSchema


class HealthResponse(CamelCaseSchema):
    """Estado de disponibilidad de la API."""

    status: Literal["ok"]
