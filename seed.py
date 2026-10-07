from __future__ import annotations

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.database import SessionLocal
from app.models.usuario import RolUsuario
from app.services.auth_service import create_seed_user


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


def seed_users() -> None:
    config = SeedSettings()
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
