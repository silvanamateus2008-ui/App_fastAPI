from __future__ import annotations

from fastapi.testclient import TestClient

from tests import factories


def payload_cliente(nombre: str = "Cliente Nuevo", **cambios: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "nombreCliente": nombre,
        "telefono": "3001112222",
        "correo": "nuevo@fabrica.com",
        "direccion": "Calle 9",
    }
    payload.update(cambios)
    return payload


def test_crear_cliente_responde_201_y_persiste_el_nombre(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Regresion: el POST lanzaba TypeError y terminaba en 500."""
    response = client.post("/api/clientes", json=payload_cliente(), headers=admin_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["nombreCliente"] == "Cliente Nuevo"
    assert client.get(f"/api/clientes/{body['idCliente']}", headers=admin_headers).json()[
        "nombreCliente"
    ] == "Cliente Nuevo"


def test_actualizar_cliente_persiste_el_nombre(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Regresion: el PUT fijaba un atributo basura y no persistia el nombre."""
    creado = client.post(
        "/api/clientes",
        json=payload_cliente("Nombre Viejo"),
        headers=admin_headers,
    )
    cliente_id = creado.json()["idCliente"]

    response = client.put(
        f"/api/clientes/{cliente_id}",
        json=payload_cliente("Nombre Nuevo"),
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["nombreCliente"] == "Nombre Nuevo"
    assert client.get(f"/api/clientes/{cliente_id}", headers=admin_headers).json()[
        "nombreCliente"
    ] == "Nombre Nuevo"


def test_el_json_de_la_api_usa_camel_case(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    creado = client.post("/api/clientes", json=payload_cliente(), headers=admin_headers)

    assert "idCliente" in creado.json()
    assert "id_cliente" not in creado.json()
    assert "nombreCliente" in creado.json()
    assert "nombre_cliente" not in creado.json()


def test_listar_clientes_usa_camel_case(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    client.post("/api/clientes", json=payload_cliente(), headers=admin_headers)

    body = client.get("/api/clientes", headers=admin_headers).json()

    assert body["total"] == 1
    assert body["items"][0]["nombreCliente"] == "Cliente Nuevo"


def test_cliente_inexistente_responde_404(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.get("/api/clientes/9999", headers=admin_headers)

    assert response.status_code == 404
    assert response.json()["code"] == "no_encontrado"


def test_cliente_con_ventas_no_se_puede_eliminar(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session,
) -> None:
    cliente = factories.crear_cliente(db_session)
    producto = factories.crear_producto(db_session)
    client.post(
        "/api/ventas",
        json={
            "idCliente": cliente.id_cliente,
            "detalles": [{"idProducto": producto.id_producto, "cantidad": 1}],
        },
        headers=admin_headers,
    )

    response = client.delete(f"/api/clientes/{cliente.id_cliente}", headers=admin_headers)

    assert response.status_code == 409
    assert response.json()["code"] == "conflicto"


def test_los_tres_roles_pueden_gestionar_clientes(
    client: TestClient,
    almacen_headers: dict[str, str],
    ventas_headers: dict[str, str],
) -> None:
    creado_almacen = client.post(
        "/api/clientes",
        json=payload_cliente("De Almacen"),
        headers=almacen_headers,
    )
    creado_ventas = client.post(
        "/api/clientes",
        json=payload_cliente("De Ventas"),
        headers=ventas_headers,
    )

    assert creado_almacen.status_code == 201
    assert creado_ventas.status_code == 201


def test_solo_admin_puede_eliminar_clientes(
    client: TestClient,
    almacen_headers: dict[str, str],
    ventas_headers: dict[str, str],
) -> None:
    creado = client.post(
        "/api/clientes",
        json=payload_cliente(),
        headers=almacen_headers,
    )
    cliente_id = creado.json()["idCliente"]

    assert client.delete(f"/api/clientes/{cliente_id}", headers=almacen_headers).status_code == 403
    assert client.delete(f"/api/clientes/{cliente_id}", headers=ventas_headers).status_code == 403


def test_los_datos_de_cliente_exigen_token(client: TestClient) -> None:
    assert client.get("/api/clientes").status_code == 401
    assert client.post("/api/clientes", json=payload_cliente()).status_code == 401
    assert client.get("/api/clientes/1").status_code == 401