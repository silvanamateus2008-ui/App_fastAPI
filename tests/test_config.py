from __future__ import annotations

import re

import pytest
from pydantic import ValidationError

from app.core.config import DEFAULT_CORS_ORIGINS, Settings


def test_development_generates_a_secure_secret_and_cors_origins() -> None:
    config = Settings(_env_file=None, environment="development")

    assert len(config.signing_secret) >= 32
    assert config.cors_origins == DEFAULT_CORS_ORIGINS


def test_standard_postgresql_url_uses_psycopg_three() -> None:
    config = Settings(
        _env_file=None,
        environment="development",
        database_url="postgresql://user:p%40ss@localhost/fabrica",
    )

    assert config.database_url == "postgresql+psycopg://user:p%40ss@localhost/fabrica"


def test_flutter_web_cors_allows_lan_host_only_on_development_port() -> None:
    config = Settings(_env_file=None, environment="development")
    cors_regex = re.compile(config.cors_origin_regex or "")

    assert cors_regex.fullmatch("http://192.168.1.20:5173")
    assert cors_regex.fullmatch("http://10.0.2.2:5173")
    assert not cors_regex.fullmatch("http://192.168.1.20:8000")


def test_non_development_requires_an_explicit_secret() -> None:
    with pytest.raises(ValidationError, match="requiere SECRET_KEY"):
        Settings(
            _env_file=None,
            environment="production",
            database_url="postgresql://db/fabrica",
            cors_origins=["https://fabrica.example"],
        )


def test_weak_secret_is_rejected() -> None:
    with pytest.raises(ValidationError, match="al menos 32 caracteres"):
        Settings(_env_file=None, environment="development", secret_key="short")
