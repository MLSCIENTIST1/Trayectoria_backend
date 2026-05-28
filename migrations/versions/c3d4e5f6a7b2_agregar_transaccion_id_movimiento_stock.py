"""Agregar transaccion_id a movimientos_stock

Revision ID: c3d4e5f6a7b2
Revises: b2c3d4e5f6a1
Create Date: 2026-05-27 10:00:00.000000

Agrega la columna transaccion_id a movimientos_stock para vincular
cada movimiento de inventario con la TransaccionOperativa que lo originó.
Esto permite mostrar el conteo de productos por compra en el historial.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b2'
down_revision = 'b2c3d4e5f6a1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'movimientos_stock',
        sa.Column(
            'transaccion_id',
            sa.Integer(),
            sa.ForeignKey('transacciones_operativas.id_transaccion', ondelete='SET NULL'),
            nullable=True
        )
    )
    op.create_index(
        'ix_movimientos_stock_transaccion_id',
        'movimientos_stock',
        ['transaccion_id']
    )


def downgrade():
    op.drop_index('ix_movimientos_stock_transaccion_id', table_name='movimientos_stock')
    op.drop_column('movimientos_stock', 'transaccion_id')
