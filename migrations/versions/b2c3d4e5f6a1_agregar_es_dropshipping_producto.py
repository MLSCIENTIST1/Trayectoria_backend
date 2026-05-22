"""Agregar columna es_dropshipping a productos_catalogo

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-05-22 10:00:00.000000

Agrega la columna es_dropshipping al modelo ProductoCatalogo
para marcar productos que se venden por dropshipping.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a1'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'productos_catalogo',
        sa.Column('es_dropshipping', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade():
    op.drop_column('productos_catalogo', 'es_dropshipping')
