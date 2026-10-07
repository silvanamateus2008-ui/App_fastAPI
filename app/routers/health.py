"""Endpoint de disponibilidad de la API."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["infraestructura"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Consultar el estado de salud",
    description="Indica si el proceso de la API esta disponible para atender solicitudes.",
    responses={200: {"description": "La API esta disponible."}},
)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
