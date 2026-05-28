"""Agregar columna alertas_enviadas a suscripciones_negocio

Revision ID: e5f6a7b8c9d4
Revises: d4e5f6a7b8c3
Create Date: 2026-05-28 11:00:00.000000

Agrega la columna JSON alertas_enviadas para trackear qué emails
de alerta ya se enviaron en cada ciclo de suscripción y evitar
envíos duplicados.
"""
from alembic import op
import sqlalchemy as sa


revision = 'e5f6a7b8c9d4'
down_revision = 'd4e5f6a7b8c3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'suscripciones_negocio',
        sa.Column(
            'alertas_enviadas',
            sa.JSON(),
            nullable=True,
            server_default=sa.text("'{}'::jsonb"),
            comment=(
                'Fechas ISO en que se enviaron los emails de alerta. '
                'Claves: trial_7d, trial_3d, trial_gracia, trial_vencida, '
                'sus_7d, sus_3d, sus_gracia, sus_vencida'
            )
        )
    )


def downgrade():
    op.drop_column('suscripciones_negocio', 'alertas_enviadas')
