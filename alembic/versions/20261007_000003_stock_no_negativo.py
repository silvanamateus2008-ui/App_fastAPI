"""Restringe el inventario a cantidades no negativas.

Revision ID: 20261007000003
Revises: 20261002000002
Create Date: 2026-10-07 00:00:03.000000
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20261007000003"
down_revision = "20261002000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        op.f("ck_Producto_stock_no_negativo"),
        "Producto",
        "stock >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_Producto_stock_no_negativo"),
        "Producto",
        type_="check",
    )
