"""Initial factory schema.

Revision ID: 20261002000001
Revises:
Create Date: 2026-10-02 00:00:01.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20261002000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id_usuario", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=60), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("rol", sa.String(length=20), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id_usuario", name=op.f("pk_usuarios")),
        sa.UniqueConstraint("email", name=op.f("uq_usuarios_email")),
        sa.UniqueConstraint("username", name=op.f("uq_usuarios_username")),
    )
    with op.batch_alter_table("usuarios", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_usuarios_id_usuario"), ["id_usuario"], unique=False)
        batch_op.create_index(batch_op.f("ix_usuarios_username"), ["username"], unique=False)
        batch_op.create_index(batch_op.f("ix_usuarios_email"), ["email"], unique=False)

    op.create_table(
        '"Cliente"',
        sa.Column("id_Cliente", sa.Integer(), nullable=False),
        sa.Column("nombreCliente", sa.String(length=100), nullable=False),
        sa.Column("telefono", sa.String(length=30), nullable=True),
        sa.Column("correo", sa.String(length=150), nullable=True),
        sa.Column("direccion", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("id_Cliente", name=op.f("pk_Cliente")),
    )
    with op.batch_alter_table('"Cliente"', schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_Cliente_id_Cliente"), ["id_Cliente"], unique=False)

    op.create_table(
        '"Proveedor"',
        sa.Column("id_Proveedor", sa.Integer(), nullable=False),
        sa.Column("nombreProveedor", sa.String(length=100), nullable=False),
        sa.Column("telefonoProveedor", sa.String(length=30), nullable=True),
        sa.Column("correoProveedor", sa.String(length=150), nullable=True),
        sa.Column("direccionProveedor", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("id_Proveedor", name=op.f("pk_Proveedor")),
    )
    with op.batch_alter_table('"Proveedor"', schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_Proveedor_id_Proveedor"), ["id_Proveedor"], unique=False)

    op.create_table(
        '"Producto"',
        sa.Column("id_Producto", sa.Integer(), nullable=False),
        sa.Column("nombreProducto", sa.String(length=120), nullable=False),
        sa.Column("tipo", sa.String(length=80), nullable=True),
        sa.Column("precio", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("id_Proveedor", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_Proveedor"],
            ['"Proveedor"."id_Proveedor"'],
            name=op.f("fk_Producto_id_Proveedor_Proveedor"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id_Producto", name=op.f("pk_Producto")),
    )
    with op.batch_alter_table('"Producto"', schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_Producto_id_Producto"), ["id_Producto"], unique=False)

    op.create_table(
        '"Venta"',
        sa.Column("id_Venta", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column("id_Cliente", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_Cliente"],
            ['"Cliente"."id_Cliente"'],
            name=op.f("fk_Venta_id_Cliente_Cliente"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id_Venta", name=op.f("pk_Venta")),
    )
    with op.batch_alter_table('"Venta"', schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_Venta_id_Venta"), ["id_Venta"], unique=False)

    op.create_table(
        "detalle_venta",
        sa.Column("id_detalle", sa.Integer(), nullable=False),
        sa.Column("id_venta", sa.Integer(), nullable=False),
        sa.Column("id_producto", sa.Integer(), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("precio_unitario", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column("subtotal", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_venta"],
            ['"Venta"."id_Venta"'],
            name=op.f("fk_detalle_venta_id_venta_Venta"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["id_producto"],
            ['"Producto"."id_Producto"'],
            name=op.f("fk_detalle_venta_id_producto_Producto"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id_detalle", name=op.f("pk_detalle_venta")),
    )
    with op.batch_alter_table("detalle_venta", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_detalle_venta_id_detalle"), ["id_detalle"], unique=False)


def downgrade() -> None:
    op.drop_table("detalle_venta")
    op.drop_table('"Venta"')
    op.drop_table('"Producto"')
    op.drop_table('"Proveedor"')
    op.drop_table('"Cliente"')
    op.drop_table("usuarios")
