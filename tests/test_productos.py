from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from tests import factories


def payload_producto(nombre: str = "Tela Nueva", **cambios: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "nombreProducto": nombre,
        "tipo": "Material",
        "precio": "100.00",
        "stock": 10,
    }
    payload.update(cambios)
    return payload


def test_crear_producto_responde_201_y_persiste_el_nombre(
    client: TestClient,
    almacen_headers: dict[str, str],
    db_session: Session,
) -> None:
    """Regresion: el POST lanzaba TypeError y terminaba en 500."""
    proveedor = factories.crear_proveedor(db_session)

    response = client.post(
        "/api/productos",
        json=payload_producto(idProveedor=proveedor.id_proveedor),
        headers=almacen_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["nombreProducto"] == "Tela Nueva"
    assert body["idProveedor"] == proveedor.id_proveedor
    assert body["precio"] == "100.00"


def test_actualizar_producto_persiste_el_nombre_y_el_stock(
    client: TestClient,
    almacen_headers: dict[str, str],
) -> None:
    """Regresion: el PUT fijaba un atributo basura y no persistia los cambios."""
    creado = client.post("/api/productos", json=payload_producto(), headers=almacen_headers)
    producto_id = creado.json()["idProducto"]

    response = client.put(
        f"/api/productos/{producto_id}",
        json=payload_producto("Tela Renombrada", stock=42),
        headers=almacen_headers,
    )

    assert response.status_code == 200
    body = client.get(f"/api/productos/{producto_id}", headers=almacen_headers).json()
    assert body["nombreProducto"] == "Tela Renombrada"
    assert body["stock"] == 42


def test_producto_inexistente_responde_404(
    client: TestClient,
    almacen_headers: dict[str, str],
) -> None:
    response = client.get("/api/productos/9999", headers=almacen_headers)

    assert response.status_code == 404
    assert response.json()["code"] == "no_encontrado"


def test_producto_con_ventas_no_se_puede_eliminar(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    cliente = factories.crear_cliente(db_session)
    producto = factories.crear_producto(db_session, precio=Decimal("100.00"), stock=10)
    client.post(
        "/api/ventas",
        json={
            "idCliente": cliente.id_cliente,
            "detalles": [{"idProducto": producto.id_producto, "cantidad": 1}],
        },
        headers=admin_headers,
    )

    response = client.delete(f"/api/productos/{producto.id_producto}", headers=admin_headers)

    assert response.status_code == 409
    assert response.json()["code"] == "conflicto"


def test_ventas_no_puede_crear_ni_actualizar_productos(
    client: TestClient,
    almacen_headers: dict[str, str],
    ventas_headers: dict[str, str],
) -> None:
    creado = client.post("/api/productos", json=payload_producto(), headers=almacen_headers)
    producto_id = creado.json()["idProducto"]

    crear = client.post("/api/productos", json=payload_producto("Otra"), headers=ventas_headers)
    actualizar = client.put(
        f"/api/productos/{producto_id}",
        json=payload_producto("Cambiada"),
        headers=ventas_headers,
    )

    assert crear.status_code == 403
    assert actualizar.status_code == 403
    assert crear.json()["code"] == "permiso"


def test_proveedor_inexistente_responde_404_y_no_500(
    client: TestClient,
    almacen_headers: dict[str, str],
) -> None:
    """La FK se viola en PostgreSQL si el service no valida el proveedor."""
    crear = client.post(
        "/api/productos",
        json=payload_producto(idProveedor=999),
        headers=almacen_headers,
    )

    assert crear.status_code == 404
    assert crear.json()["code"] == "no_encontrado"


def test_actualizar_producto_con_proveedor_inexistente_responde_404(
    client: TestClient,
    almacen_headers: dict[str, str],
) -> None:
    creado = client.post("/api/productos", json=payload_producto(), headers=almacen_headers)
    producto_id = creado.json()["idProducto"]

    response = client.put(
        f"/api/productos/{producto_id}",
        json=payload_producto(idProveedor=999),
        headers=almacen_headers,
    )

    assert response.status_code == 404


def test_precio_con_mas_de_dos_decimales_responde_422(
    client: TestClient,
    almacen_headers: dict[str, str],
) -> None:
    """Numeric(12,2) no admite 3 decimales: debe rechazarse, no redondearse."""
    response = client.post(
        "/api/productos",
        json=payload_producto(precio="10.555"),
        headers=almacen_headers,
    )

    assert response.status_code == 422


def test_precio_y_stock_se_validan_con_422(
    client: TestClient,
    almacen_headers: dict[str, str],
) -> None:
    precio_cero = client.post(
        "/api/productos", json=payload_producto(precio="0"), headers=almacen_headers
    )
    stock_negativo = client.post(
        "/api/productos", json=payload_producto(stock=-1), headers=almacen_headers
    )
    nombre_vacio = client.post(
        "/api/productos", json=payload_producto(nombre=""), headers=almacen_headers
    )

    assert precio_cero.status_code == 422
    assert stock_negativo.status_code == 422
    assert nombre_vacio.status_code == 422


def test_la_base_rechaza_stock_negativo(db_session: Session) -> None:
    producto = factories.crear_producto(db_session)
    producto.stock = -1

    try:
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
    else:
        raise AssertionError("La base de datos acepto stock negativo")


def test_los_datos_de_producto_exigen_token(client: TestClient) -> None:
    assert client.get("/api/productos").status_code == 401
    assert client.post("/api/productos", json=payload_producto()).status_code == 401
    assert client.get("/api/productos/1").status_code == 401