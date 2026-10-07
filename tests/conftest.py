from __future__ import annotations

from collections.abc import Generator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.main import app
from app.models.usuario import RolUsuario, Usuario
from tests import factories

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine, "connect")
def activar_claves_foraneas(dbapi_connection, _record) -> None:
    """SQLite ignora las FK por defecto; PostgreSQL si las aplica."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def isolate_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def _crear_usuario_rol(db: Session, rol: RolUsuario) -> Usuario:
    return factories.crear_usuario(
        db,
        username=rol.value.lower(),
        email=f"{rol.value.lower()}@fabrica.com",
        nombre=f"Usuario {rol.value}",
        rol=rol,
    )


def _headers(usuario: Usuario) -> dict[str, str]:
    token = create_access_token(usuario.id_usuario, usuario.rol.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def usuario_admin(db_session: Session) -> Usuario:
    return _crear_usuario_rol(db_session, RolUsuario.ADMIN)


@pytest.fixture
def usuario_almacen(db_session: Session) -> Usuario:
    return _crear_usuario_rol(db_session, RolUsuario.ALMACEN)


@pytest.fixture
def usuario_ventas(db_session: Session) -> Usuario:
    return _crear_usuario_rol(db_session, RolUsuario.VENTAS)


@pytest.fixture
def admin_headers(usuario_admin: Usuario) -> dict[str, str]:
    return _headers(usuario_admin)


@pytest.fixture
def almacen_headers(usuario_almacen: Usuario) -> dict[str, str]:
    return _headers(usuario_almacen)


@pytest.fixture
def ventas_headers(usuario_ventas: Usuario) -> dict[str, str]:
    return _headers(usuario_ventas)