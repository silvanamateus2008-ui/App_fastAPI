from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.cliente import Cliente
from app.models.producto import Producto
from app.models.proveedor import Proveedor
from app.models.usuario import RolUsuario, Usuario

CONTRASENA_DE_PRUEBA = "test-password-123"


def crear_usuario(
    db: Session,
    *,
    username: str = "testuser",
    email: str = "test@fabrica.com",
    nombre: str = "Usuario Test",
    password: str = CONTRASENA_DE_PRUEBA,
    rol: RolUsuario = RolUsuario.VENTAS,
    activo: bool = True,
) -> Usuario:
    usuario = Usuario(
        username=username,
        email=email,
        nombre=nombre,
        password_hash=hash_password(password),
        rol=rol,
        activo=activo,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def crear_cliente(
    db: Session,
    *,
    nombre_cliente: str = "Cliente Uno",
    telefono: str | None = "3000000000",
    correo: str | None = "cliente@fabrica.com",
    direccion: str | None = "Calle 1",
) -> Cliente:
    cliente = Cliente(
        nombre_cliente=nombre_cliente,
        telefono=telefono,
        correo=correo,
        direccion=direccion,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def crear_proveedor(
    db: Session,
    *,
    nombre_proveedor: str = "Proveedor Uno",
    telefono_proveedor: str | None = "3100000000",
    correo_proveedor: str | None = "proveedor@fabrica.com",
    direccion_proveedor: str | None = "Calle 2",
) -> Proveedor:
    proveedor = Proveedor(
        nombre_proveedor=nombre_proveedor,
        telefono_proveedor=telefono_proveedor,
        correo_proveedor=correo_proveedor,
        direccion_proveedor=direccion_proveedor,
    )
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


def crear_producto(
    db: Session,
    *,
    nombre_producto: str = "Tela",
    tipo: str | None = "Material",
    precio: Decimal = Decimal("100.00"),
    stock: int = 10,
    proveedor: Proveedor | None = None,
) -> Producto:
    producto = Producto(
        nombre_producto=nombre_producto,
        tipo=tipo,
        precio=precio,
        stock=stock,
        id_proveedor=proveedor.id_proveedor if proveedor else None,
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto