from __future__ import annotations

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import NoAutorizadoError
from app.core.security import create_access_token
from app.models.usuario import RolUsuario
from app.schemas.auth import LoginRequest
from app.services.auth_service import login_user
from tests import factories
from tests.factories import CONTRASENA_DE_PRUEBA


def test_login_returns_token(db_session: Session) -> None:
    factories.crear_usuario(db_session, email="admin@fabrica.com", rol=RolUsuario.ADMIN)

    token = login_user(
        db_session,
        LoginRequest(email="admin@fabrica.com", password=CONTRASENA_DE_PRUEBA),
    )

    assert token.access_token
    assert token.token_type == "bearer"


def test_login_rejects_invalid_credentials(db_session: Session) -> None:
    """La asercion ya no acepta Exception: cualquier fallo hacia pasar el test."""
    factories.crear_usuario(db_session, email="admin@fabrica.com")

    with pytest.raises(NoAutorizadoError):
        login_user(db_session, LoginRequest(email="admin@fabrica.com", password="incorrecta"))


def test_login_responde_401_y_json_en_camel_case(client: TestClient, db_session: Session) -> None:
    factories.crear_usuario(db_session, email="admin@fabrica.com")

    response = client.post(
        "/api/auth/login",
        json={"email": "admin@fabrica.com", "password": "incorrecta"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "no_autorizado"
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_exitoso_devuelve_token(client: TestClient, db_session: Session) -> None:
    factories.crear_usuario(
        db_session,
        email="ventas@fabrica.com",
        rol=RolUsuario.VENTAS,
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "ventas@fabrica.com", "password": CONTRASENA_DE_PRUEBA},
    )

    assert response.status_code == 200
    assert response.json()["accessToken"]
    assert response.json()["tokenType"] == "bearer"


def test_perfil_devuelve_el_usuario_autenticado(
    client: TestClient,
    ventas_headers: dict[str, str],
    usuario_ventas,
) -> None:
    response = client.get("/api/auth/me", headers=ventas_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["idUsuario"] == usuario_ventas.id_usuario
    assert body["rol"] == "VENTAS"


def test_perfil_exige_token(client: TestClient) -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json()["code"] == "no_autorizado"


def test_token_invalido_responde_401(client: TestClient) -> None:
    response = client.get("/api/clientes", headers={"Authorization": "Bearer no-es-un-jwt"})

    assert response.status_code == 401


def test_token_firmado_con_otra_clave_responde_401(
    client: TestClient,
    usuario_ventas,
) -> None:
    token = jwt.encode(
        {"sub": str(usuario_ventas.id_usuario), "role": "VENTAS", "exp": 9999999999},
        "clave-falsa-para-la-prueba-de-32-caracteres",
        algorithm=settings.jwt_algorithm,
    )

    response = client.get("/api/clientes", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_usuario_inactivo_responde_401(client: TestClient, db_session: Session) -> None:
    usuario = factories.crear_usuario(db_session, activo=False)
    token = create_access_token(usuario.id_usuario, usuario.rol.value)

    response = client.get("/api/clientes", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_rol_del_token_desactualizado_responde_401(client: TestClient, db_session: Session) -> None:
    usuario = factories.crear_usuario(db_session, rol=RolUsuario.VENTAS)
    token = create_access_token(usuario.id_usuario, RolUsuario.ADMIN.value)

    response = client.get("/api/clientes", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401