"""Alinea usuarios.rol con el Enum del modelo.

El modelo declara SAEnum(RolUsuario, native_enum=False), que en PostgreSQL
produce VARCHAR(7) (la longitud del valor mas largo, ALMACEN). La migracion
inicial lo creo como String(20), asi que el siguiente --autogenerate pedia un
ALTER que no correspondia a ningun cambio real del modelo.

Revision ID: 20261002000002
Revises: 20261002000001
Create Date: 2026-10-02 00:00:02.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20261002000002"
down_revision = "20261002000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "usuarios",
        "rol",
        existing_type=sa.String(length=20),
        type_=sa.String(length=7),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "usuarios",
        "rol",
        existing_type=sa.String(length=7),
        type_=sa.String(length=20),
        existing_nullable=False,
    )