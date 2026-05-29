"""Agregar imagen_guia_url a pedidos

Revision ID: g7b8c9d0e1f6
Revises: f6a7b8c9d0e5
Create Date: 2026-05-29 10:00:00.000000

Agrega la columna imagen_guia_url a la tabla pedidos para almacenar
la URL de Cloudinary de la imagen o PDF de la guía de envío.
El cliente puede verla en heyden.html.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'g7b8c9d0e1f6'
down_revision = 'f6a7b8c9d0e5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'pedidos',
        sa.Column(
            'imagen_guia_url',
            sa.String(500),
            nullable=True
        )
    )


def downgrade():
    op.drop_column('pedidos', 'imagen_guia_url')
