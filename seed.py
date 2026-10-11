from __future__ import annotations

from app.core.database import SessionLocal
from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import inspect

from app.core.database import SessionLocal, engine
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
class SeedSettings(BaseSettings):
    admin_username: str = Field(validation_alias="SEED_ADMIN_USERNAME", min_length=1)
    admin_email: str = Field(validation_alias="SEED_ADMIN_EMAIL", min_length=1)
    admin_nombre: str = Field(validation_alias="SEED_ADMIN_NOMBRE", min_length=1)
    admin_password: SecretStr = Field(validation_alias="SEED_ADMIN_PASSWORD")
    almacen_username: str = Field(validation_alias="SEED_ALMACEN_USERNAME", min_length=1)
    almacen_email: str = Field(validation_alias="SEED_ALMACEN_EMAIL", min_length=1)
    almacen_nombre: str = Field(validation_alias="SEED_ALMACEN_NOMBRE", min_length=1)
    almacen_password: SecretStr = Field(validation_alias="SEED_ALMACEN_PASSWORD")
    ventas_username: str = Field(validation_alias="SEED_VENTAS_USERNAME", min_length=1)
    ventas_email: str = Field(validation_alias="SEED_VENTAS_EMAIL", min_length=1)
    ventas_nombre: str = Field(validation_alias="SEED_VENTAS_NOMBRE", min_length=1)
    ventas_password: SecretStr = Field(validation_alias="SEED_VENTAS_PASSWORD")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("admin_password", "almacen_password", "ventas_password")
    @classmethod
    def validate_password_length(cls, password: SecretStr) -> SecretStr:
        if len(password.get_secret_value()) < 12:
            raise ValueError("Las contrasenas de semilla deben tener al menos 12 caracteres")
        return password


def _esquema_listo() -> bool:
    """Indica si la tabla de usuarios ya existe en la base configurada."""
    return inspect(engine).has_table("usuarios")


def _cargar_configuracion() -> SeedSettings:
    """Lee SEED_* del entorno con un mensaje claro si falta configuracion."""
    try:
        return SeedSettings()
    except ValidationError as error:
        campos = sorted(
            str(item["loc"][0])
            for item in error.errors()
            if item.get("loc")
        )
        raise RuntimeError(
            "Falta configuracion de semilla en el entorno (.env): "
            f"{', '.join(campos)}. Paso pendiente: crea el archivo .env a "
            "partir de .env.example y define todos los SEED_* (usuario, "
            "email, nombre y contrasena de al menos 12 caracteres)."
        ) from error


def seed_users() -> None:
    if not _esquema_listo():
        raise RuntimeError(
            "La base de datos no tiene el esquema inicializado (falta la "
            "tabla 'usuarios'). Paso pendiente: inicializa el esquema antes "
            "de crear usuarios con:\n"
            "  alembic upgrade head\n"
            "y despues vuelve a ejecutar:\n"
            "  python seed.py"
        )

    config = _cargar_configuracion()
    usuarios = (
        (
            config.admin_username,
            config.admin_email,
            config.admin_nombre,
            config.admin_password,
            RolUsuario.ADMIN,
        ),
        (
            config.almacen_username,
            config.almacen_email,
            config.almacen_nombre,
            config.almacen_password,
            RolUsuario.ALMACEN,
        ),
        (
            config.ventas_username,
            config.ventas_email,
            config.ventas_nombre,
            config.ventas_password,
            RolUsuario.VENTAS,
        ),
    )

    db = SessionLocal()
    try:
        for username, email, nombre, password, rol in usuarios:
            create_seed_user(
                db,
                username=username,
                email=email,
                nombre=nombre,
                password=password.get_secret_value(),
                rol=rol.value,
            )
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
    print("Usuarios semilla creados")
