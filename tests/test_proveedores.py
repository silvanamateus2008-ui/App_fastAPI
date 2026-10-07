from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests import factories


def payload_proveedor(nombre: str = "Proveedor Nuevo", **cambios: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "nombreProveedor": nombre,
        "telefonoProveedor": "3101112222",
        "correoProveedor": "nuevo@fabrica.com",
        "direccionProveedor": "Avenida 1",
    }
    payload.update(cambios)
    return payload


def test_crear_proveedor_responde_201_y_persiste_el_nombre(
    client: TestClient,
    almacen_headers: dict[str, str],
) -> None:
    """Regresion: el POST lanzaba TypeError y terminaba en 500."""
    response = client.post("/api/proveedores", json=payload_proveedor(), headers=almacen_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["nombreProveedor"] == "Proveedor Nuevo"
    assert client.get(f"/api/proveedores/{body['idProveedor']}", headers=almacen_headers).json()[
        "nombreProveedor"
    ] == "Proveedor Nuevo"


def test_actualizar_proveedor_persiste_el_nombre(
    client: TestClient,
    almacen_headers: dict[str, str],
) -> None:
    """Regresion: el PUT fijaba un atributo basura y no persistia el nombre."""
    creado = client.post(
        "/api/proveedores",
        json=payload_proveedor("Nombre Viejo"),
        headers=almacen_headers,
    )
    proveedor_id = creado.json()["idProveedor"]

    response = client.put(
        f"/api/proveedores/{proveedor_id}",
        json=payload_proveedor("Nombre Nuevo"),
        headers=almacen_headers,
    )

    assert response.status_code == 200
    assert client.get(f"/api/proveedores/{proveedor_id}", headers=almacen_headers).json()[
        "nombreProveedor"
    ] == "Nombre Nuevo"


def test_proveedor_inexistente_responde_404(
    client: TestClient,
    almacen_headers: dict[str, str],
) -> None:
    response = client.get("/api/proveedores/9999", headers=almacen_headers)

    assert response.status_code == 404
    assert response.json()["code"] == "no_encontrado"


def test_proveedor_con_productos_no_se_puede_eliminar(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    proveedor = factories.crear_proveedor(db_session)
    factories.crear_producto(db_session, proveedor=proveedor)

    response = client.delete(f"/api/proveedores/{proveedor.id_proveedor}", headers=admin_headers)

    assert response.status_code == 409
    assert response.json()["code"] == "conflicto"


def test_ventas_no_puede_gestionar_proveedores(
    client: TestClient,
    almacen_headers: dict[str, str],
    ventas_headers: dict[str, str],
) -> None:
    creado = client.post("/api/proveedores", json=payload_proveedor(), headers=almacen_headers)

    assert creado.status_code == 201
    assert client.get("/api/proveedores", headers=ventas_headers).status_code == 403
    assert client.post(
        "/api/proveedores",
        json=payload_proveedor("Otro"),
        headers=ventas_headers,
    ).status_code == 403


def test_los_datos_de_proveedor_exigen_token(client: TestClient) -> None:
    assert client.get("/api/proveedores").status_code == 401
    assert client.post("/api/proveedores", json=payload_proveedor()).status_code == 401
    assert client.get("/api/proveedores/1").status_code == 401