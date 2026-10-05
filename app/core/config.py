"""Configuracion de la aplicacion leida desde variables de entorno."""

from urllib.parse import quote, unquote

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET_KEY = "dev-only-insecure-secret-key-please-change"
DEVELOPMENT_ENVIRONMENTS = {"development", "dev", "test", "testing"}
UNSAFE_SECRET_KEY_MARKERS = ("REPLACE_WITH", "CHANGE_ME", "TODO")
DEFAULT_DATABASE_URL = "sqlite:///./fabrica.db"


class Settings(BaseSettings):
    """Valores de configuracion de la API de la fabrica."""

    app_name: str = "API Fabrica"
    environment: str = "development"
    database_url: str | None = None
    secret_key: str = DEFAULT_SECRET_KEY
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def encode_database_password(cls, value: object) -> object:
        """Codifica la contrasena del DSN para que sobreviva a ConfigParser."""
        if not isinstance(value, str):
            return value
        separador = "://"
        if separador not in value:
            return value
        esquema, _, resto = value.partition(separador)
        usuario, arroba, servidor = resto.rpartition("@")
        if not arroba or ":" not in usuario:
            return value
        nombre_usuario, _, contrasena = usuario.partition(":")
        if not contrasena:
            return value
        contrasena_segura = quote(unquote(contrasena), safe="")
        return f"{esquema}{separador}{nombre_usuario}:{contrasena_segura}@{servidor}"

    @model_validator(mode="after")
    def validate_environment(self) -> "Settings":
        """Impide arrancar en produccion con una configuracion insegura o ambigua."""
        self.environment = self.environment.strip().lower()
        if not self.environment:
            raise ValueError("ENVIRONMENT no puede estar vacio")
        if not self.is_development:
            if not self.database_url:
                raise ValueError("Fuera de desarrollo se requiere DATABASE_URL explicito")
            self._validate_secret_key_for_deployment()
        return self

    def _validate_secret_key_for_deployment(self) -> None:
        if self.secret_key == DEFAULT_SECRET_KEY:
            raise ValueError(
                "SECRET_KEY por defecto no permitido fuera de desarrollo; "
                'genere una con python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        if any(marker in self.secret_key.upper() for marker in UNSAFE_SECRET_KEY_MARKERS):
            raise ValueError("SECRET_KEY contiene un marcador sin reemplazar")
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")

    @property
    def is_development(self) -> bool:
        return self.environment in DEVELOPMENT_ENVIRONMENTS

    @property
    def is_production(self) -> bool:
        return not self.is_development

    @property
    def resolved_database_url(self) -> str:
        return self.database_url or DEFAULT_DATABASE_URL


settings = Settings()
