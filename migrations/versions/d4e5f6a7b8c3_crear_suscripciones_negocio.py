"""Crear tabla suscripciones_negocio

Revision ID: d4e5f6a7b8c3
Revises: c3d4e5f6a7b2
Create Date: 2026-05-28 10:00:00.000000

Crea la tabla suscripciones_negocio para gestionar el ciclo de vida
de las suscripciones: trial (primer mes gratis) → activa → gracia → vencida.
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta


revision = 'd4e5f6a7b8c3'
down_revision = 'c3d4e5f6a7b2'
branch_labels = None
depends_on = None


def upgrade():
    # ── Crear tabla ──────────────────────────────────────────────────────────
    op.create_table(
        'suscripciones_negocio',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('negocio_id', sa.Integer(),
                  sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('plan_id', sa.Integer(),
                  sa.ForeignKey('planes.id', ondelete='SET NULL'),
                  nullable=True),

        # Estado
        sa.Column('estado', sa.String(20), nullable=False, server_default='trial'),

        # Trial
        sa.Column('es_trial',           sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fecha_inicio_trial', sa.DateTime(), nullable=True),
        sa.Column('fecha_fin_trial',    sa.DateTime(), nullable=True),

        # Suscripción paga
        sa.Column('fecha_inicio',     sa.DateTime(), nullable=True),
        sa.Column('fecha_fin',        sa.DateTime(), nullable=True),
        sa.Column('fecha_renovacion', sa.DateTime(), nullable=True),

        # Control
        sa.Column('dias_gracia',           sa.Integer(), nullable=False, server_default='3'),
        sa.Column('renovacion_automatica', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('trial_usado',           sa.Boolean(), nullable=False, server_default='false'),

        # Auditoría
        sa.Column('creado_por',    sa.String(50),  nullable=True, server_default='sistema'),
        sa.Column('modificado_por',sa.String(50),  nullable=True),
        sa.Column('notas',         sa.Text(),       nullable=True),
        sa.Column('created_at',    sa.DateTime(),   nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at',    sa.DateTime(),   nullable=False,
                  server_default=sa.text('NOW()')),
    )

    # ── Índices ──────────────────────────────────────────────────────────────
    op.create_index('ix_suscripciones_negocio_negocio_id',
                    'suscripciones_negocio', ['negocio_id'])
    op.create_index('ix_suscripciones_negocio_estado',
                    'suscripciones_negocio', ['estado'])
    op.create_index('ix_suscripciones_negocio_fecha_fin_trial',
                    'suscripciones_negocio', ['fecha_fin_trial'])

    # ── Backfill: crear trial para todos los negocios existentes ─────────────
    # Los negocios ya existentes obtienen un trial retroactivo calculado
    # desde su fecha_registro (primer mes gratis desde que se registraron)
    op.execute(sa.text("""
        INSERT INTO suscripciones_negocio
            (negocio_id, estado, es_trial, trial_usado,
             fecha_inicio_trial, fecha_fin_trial,
             dias_gracia, renovacion_automatica,
             creado_por, notas, created_at, updated_at)
        SELECT
            n.id_negocio,
            CASE
                WHEN NOW() <= n.fecha_registro + INTERVAL '30 days' THEN 'trial'
                WHEN NOW() <= n.fecha_registro + INTERVAL '33 days' THEN 'gracia'
                ELSE 'vencida'
            END                                     AS estado,
            true                                    AS es_trial,
            true                                    AS trial_usado,
            n.fecha_registro                        AS fecha_inicio_trial,
            n.fecha_registro + INTERVAL '30 days'  AS fecha_fin_trial,
            3                                       AS dias_gracia,
            false                                   AS renovacion_automatica,
            'migracion'                             AS creado_por,
            'Suscripción creada por migración automática desde fecha_registro' AS notas,
            NOW()                                   AS created_at,
            NOW()                                   AS updated_at
        FROM negocios n
        WHERE NOT EXISTS (
            SELECT 1 FROM suscripciones_negocio s WHERE s.negocio_id = n.id_negocio
        )
    """))


def downgrade():
    op.drop_index('ix_suscripciones_negocio_fecha_fin_trial',
                  table_name='suscripciones_negocio')
    op.drop_index('ix_suscripciones_negocio_estado',
                  table_name='suscripciones_negocio')
    op.drop_index('ix_suscripciones_negocio_negocio_id',
                  table_name='suscripciones_negocio')
    op.drop_table('suscripciones_negocio')
