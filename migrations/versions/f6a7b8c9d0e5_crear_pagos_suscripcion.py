"""Crear tabla pagos_suscripcion

Revision ID: f6a7b8c9d0e5
Revises: e5f6a7b8c9d4
Create Date: 2026-05-28 12:00:00.000000

Crea la tabla pagos_suscripcion para registrar el historial de pagos
de cada negocio: monto, método, período cubierto, comprobante, estado.
"""
from alembic import op
import sqlalchemy as sa


revision = 'f6a7b8c9d0e5'
down_revision = 'e5f6a7b8c9d4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pagos_suscripcion',

        sa.Column('id', sa.Integer(), primary_key=True),

        # Relaciones
        sa.Column('suscripcion_id', sa.Integer(),
                  sa.ForeignKey('suscripciones_negocio.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('negocio_id', sa.Integer(),
                  sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
                  nullable=False),

        # Pago
        sa.Column('monto',       sa.Numeric(12, 2), nullable=False),
        sa.Column('moneda',      sa.String(3),  nullable=False, server_default='COP'),
        sa.Column('metodo_pago', sa.String(30), nullable=False, server_default='transferencia'),
        sa.Column('estado',      sa.String(20), nullable=False, server_default='completado'),

        # Trazabilidad
        sa.Column('referencia',      sa.String(200), nullable=True),
        sa.Column('comprobante_url', sa.String(500), nullable=True),

        # Período cubierto
        sa.Column('periodo_inicio', sa.DateTime(), nullable=True),
        sa.Column('periodo_fin',    sa.DateTime(), nullable=True),

        # Auditoría
        sa.Column('notas',          sa.Text(),      nullable=True),
        sa.Column('registrado_por', sa.String(80),  nullable=False, server_default='admin'),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('NOW()')),
    )

    op.create_index('ix_pagos_sus_suscripcion_id', 'pagos_suscripcion', ['suscripcion_id'])
    op.create_index('ix_pagos_sus_negocio_id',     'pagos_suscripcion', ['negocio_id'])
    op.create_index('ix_pagos_sus_estado',          'pagos_suscripcion', ['estado'])
    op.create_index('ix_pagos_sus_created_at',      'pagos_suscripcion', ['created_at'])


def downgrade():
    op.drop_index('ix_pagos_sus_created_at',      table_name='pagos_suscripcion')
    op.drop_index('ix_pagos_sus_estado',           table_name='pagos_suscripcion')
    op.drop_index('ix_pagos_sus_negocio_id',       table_name='pagos_suscripcion')
    op.drop_index('ix_pagos_sus_suscripcion_id',   table_name='pagos_suscripcion')
    op.drop_table('pagos_suscripcion')
