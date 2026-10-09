"""Crea el esquema local directamente desde los modelos (atajo de desarrollo).

El metodo reproducible y canonico es Alembic:

    alembic upgrade head

Este script se conserva solo para recrear rapido una base SQLite vacia a
partir de `Base.metadata`. Importa explicitamente `app.models` para que todas
las tablas queden registradas antes de `create_all`; sin ese import,
`Base.metadata` estaria vacio y no se crearia ninguna tabla.
"""

from __future__ import annotations

import app.models  # noqa: F401  registra todas las tablas en Base.metadata
from app.core.database import Base, engine


def create_schema() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_schema()
    print("Esquema de base de datos creado")
