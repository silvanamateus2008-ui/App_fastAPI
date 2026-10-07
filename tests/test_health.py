from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_returns_exact_success_response(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_is_documented_in_openapi(client: TestClient) -> None:
    operacion = client.get("/openapi.json").json()["paths"]["/health"]["get"]

    assert operacion["summary"] == "Consultar el estado de salud"
    assert (
        operacion["description"]
        == "Indica si el proceso de la API esta disponible para atender solicitudes."
    )
    assert operacion["tags"] == ["infraestructura"]
    assert operacion["responses"]["200"]["description"] == "La API esta disponible."
