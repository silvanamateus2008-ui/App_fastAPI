from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.errors import ConflictoError, ReglaNegocioError, StockInsuficienteError
from app.schemas.venta import VentaCreate
from app.services.producto_service import eliminar_producto
from app.services.venta_service import crear_venta
from tests import factories


def test_venta_descuenta_stock(db_session: Session) -> None:
    cliente = factories.crear_cliente(db_session)
    producto = factories.crear_producto(db_session, precio=Decimal("100.00"), stock=10)
    venta = VentaCreate(
        id_cliente=cliente.id_cliente,
        detalles=[{"id_producto": producto.id_producto, "cantidad": 3}],
    )

    creada = crear_venta(db_session, venta)
    db_session.refresh(producto)

    assert creada.total == Decimal("300.00")
    assert producto.stock == 7


def test_venta_falla_si_no_hay_stock(db_session: Session) -> None:
    cliente = factories.crear_cliente(db_session)
    producto = factories.crear_producto(db_session, stock=10)
    venta = VentaCreate(
        id_cliente=cliente.id_cliente,
        detalles=[{"id_producto": producto.id_producto, "cantidad": 99}],
    )

    with pytest.raises(StockInsuficienteError):
        crear_venta(db_session, venta)


def test_venta_rechaza_productos_repetidos(db_session: Session) -> None:
    cliente = factories.crear_cliente(db_session)
    producto = factories.crear_producto(db_session, stock=10)
    venta = VentaCreate(
        id_cliente=cliente.id_cliente,
        detalles=[
            {"id_producto": producto.id_producto, "cantidad": 2},
            {"id_producto": producto.id_producto, "cantidad": 3},
        ],
    )

    with pytest.raises(ReglaNegocioError, match="repite el mismo producto"):
        crear_venta(db_session, venta)

    db_session.refresh(producto)
    assert producto.stock == 10
def test_producto_con_ventas_no_puede_eliminarse(db_session: Session) -> None:
    cliente = factories.crear_cliente(db_session)
    producto = factories.crear_producto(db_session, stock=10)
    crear_venta(
        db_session,
        VentaCreate(
            id_cliente=cliente.id_cliente,
            detalles=[{"id_producto": producto.id_producto, "cantidad": 1}],
        ),
    )

    with pytest.raises(ConflictoError):
        eliminar_producto(db_session, producto.id_producto)


def test_venta_sin_detalles_responde_422(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    cliente = factories.crear_cliente(db_session)

    response = client.post(
        "/api/ventas",
        json={"idCliente": cliente.id_cliente, "detalles": []},
        headers=admin_headers,
    )

    assert response.status_code == 422
    assert response.json()["code"] == "regla_negocio"


def test_venta_sin_stock_responde_409_y_no_deja_ventas(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    cliente = factories.crear_cliente(db_session)
    producto = factories.crear_producto(db_session, stock=2)

    response = client.post(
        "/api/ventas",
        json={
            "idCliente": cliente.id_cliente,
            "detalles": [{"idProducto": producto.id_producto, "cantidad": 5}],
        },
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "stock_insuficiente"
    assert client.get("/api/ventas", headers=admin_headers).json()["total"] == 0


def test_el_servidor_calcula_subtotal_y_total(
    client: TestClient,
    ventas_headers: dict[str, str],
    db_session: Session,
) -> None:
    cliente = factories.crear_cliente(db_session)
    producto = factories.crear_producto(db_session, precio=Decimal("12.50"), stock=10)

    response = client.post(
        "/api/ventas",
        json={
            "idCliente": cliente.id_cliente,
            "detalles": [{"idProducto": producto.id_producto, "cantidad": 4}],
        },
        headers=ventas_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total"] == "50.00"
    assert body["detalles"][0]["precioUnitario"] == "12.50"
    assert body["detalles"][0]["subtotal"] == "50.00"
    assert body["idCliente"] == cliente.id_cliente


def test_cliente_inexistente_responde_404(
    client: TestClient,
    ventas_headers: dict[str, str],
    db_session: Session,
) -> None:
    factories.crear_producto(db_session)

    response = client.post(
        "/api/ventas",
        json={"idCliente": 999, "detalles": [{"idProducto": 1, "cantidad": 1}]},
        headers=ventas_headers,
    )

    assert response.status_code == 404
    assert response.json()["code"] == "no_encontrado"


def test_venta_inexistente_responde_404(
    client: TestClient,
    ventas_headers: dict[str, str],
) -> None:
    response = client.get("/api/ventas/999", headers=ventas_headers)

    assert response.status_code == 404
    assert response.json()["code"] == "no_encontrado"


def test_venta_con_detalles_no_se_puede_eliminar(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    cliente = factories.crear_cliente(db_session)
    producto = factories.crear_producto(db_session, stock=10)
    creada = client.post(
        "/api/ventas",
        json={
            "idCliente": cliente.id_cliente,
            "detalles": [{"idProducto": producto.id_producto, "cantidad": 1}],
        },
        headers=admin_headers,
    )
    venta_id = creada.json()["idVenta"]

    response = client.delete(f"/api/ventas/{venta_id}", headers=admin_headers)

    assert response.status_code == 409
    assert response.json()["code"] == "conflicto"


def test_almacen_no_puede_registrar_ventas(
    client: TestClient,
    almacen_headers: dict[str, str],
    db_session: Session,
) -> None:
    cliente = factories.crear_cliente(db_session)
    producto = factories.crear_producto(db_session)

    response = client.post(
        "/api/ventas",
        json={
            "idCliente": cliente.id_cliente,
            "detalles": [{"idProducto": producto.id_producto, "cantidad": 1}],
        },
        headers=almacen_headers,
    )

    assert response.status_code == 403
    assert response.json()["code"] == "permiso"


def test_las_ventas_exigen_token(client: TestClient) -> None:
    assert client.get("/api/ventas").status_code == 401
    assert client.get("/api/ventas/1").status_code == 401
    assert client.delete("/api/ventas/1").status_code == 401