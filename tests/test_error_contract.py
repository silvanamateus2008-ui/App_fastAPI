from __future__ import annotations

from fastapi.testclient import TestClient


def test_validation_errors_use_the_api_error_contract(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "La solicitud contiene datos invalidos"
    assert body["code"] == "datos_invalidos"
    assert body["errors"]
    assert "input" not in body["errors"][0]

    documented_schema = client.get("/openapi.json").json()["paths"]["/api/auth/login"]["post"][
        "responses"
    ]["422"]["content"]["application/json"]["schema"]["$ref"]
    assert documented_schema.endswith("/ErrorNegocioOut")


def test_unknown_routes_use_the_api_error_contract(client: TestClient) -> None:
    response = client.get("/ruta-inexistente")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "El recurso solicitado no existe",
        "code": "no_encontrado",
        "errors": [],
    }


def test_cors_accepts_flutter_web_and_lan_development_origins(client: TestClient) -> None:
    for origin in ("http://localhost:5173", "http://192.168.1.20:5173"):
        response = client.options(
            "/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
