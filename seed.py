from __future__ import annotations

from app.core.database import SessionLocal
from app.models.usuario import RolUsuario
from app.services.auth_service import create_seed_user


def seed_users() -> None:
    db = SessionLocal()
    try:
        create_seed_user(
            db,
            username="admin",
            email="admin@fabrica.local",
            nombre="Administrador",
            password="admin123",
            rol=RolUsuario.ADMIN.value,
        )
        create_seed_user(
            db,
            username="almacen",
            email="almacen@fabrica.local",
            nombre="Almacen",
            password="almacen123",
            rol=RolUsuario.ALMACEN.value,
        )
        create_seed_user(
            db,
            username="ventas",
            email="ventas@fabrica.local",
            nombre="Ventas",
            password="ventas123",
            rol=RolUsuario.VENTAS.value,
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
    print("Usuarios semilla creados")
