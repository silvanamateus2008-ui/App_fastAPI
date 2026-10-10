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
    # SQLite no soporta ALTER TABLE ... ADD CONSTRAINT: batch recrea la tabla
    # una sola vez e incorpora la restriccion (PostgreSQL usa el ALTER normal).
    # El nombre coincide con el del modelo (CheckConstraint "stock_no_negativo"
    # + convencion "ck_%(table_name)s_%(constraint_name)s"), sin duplicarla.
    with op.batch_alter_table("Producto", schema=None) as batch_op:
        batch_op.create_check_constraint(
            op.f("ck_Producto_stock_no_negativo"),
            "stock >= 0",
        )


def downgrade() -> None:
    with op.batch_alter_table("Producto", schema=None) as batch_op:
        batch_op.drop_constraint(
            op.f("ck_Producto_stock_no_negativo"),
            type_="check",
        )
