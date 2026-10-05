from __future__ import annotations

from app.core.database import Base, engine


def create_schema() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_schema()
    print("Esquema de base de datos creado")
