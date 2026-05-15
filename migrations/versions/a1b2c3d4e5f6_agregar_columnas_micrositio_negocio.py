"""Agregar columnas de micrositio a la tabla negocio

Revision ID: a1b2c3d4e5f6
Revises: 7a444204d355
Create Date: 2026-05-14 20:00:00.000000

Agrega las columnas que fueron añadidas al modelo Negocio sin migración:
  - tipo_pagina   (VARCHAR 50, default 'landing')
  - whatsapp      (VARCHAR 20, nullable)
  - logo_url      (TEXT, nullable)
  - config_tienda (JSONB, default '{}')
  - qr_negocio_url  (TEXT, nullable)
  - qr_negocio_data (VARCHAR 300, nullable)
  - perfil_publico  (BOOLEAN, default true)

Usa ALTER TABLE ... ADD COLUMN IF NOT EXISTS para ser seguro
si alguna ya existe en la BD.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '7a444204d355'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Cada sentencia usa IF NOT EXISTS — idempotente aunque la columna ya exista
    columnas = [
        "ALTER TABLE negocio ADD COLUMN IF NOT EXISTS tipo_pagina    VARCHAR(50)  DEFAULT 'landing'",
        "ALTER TABLE negocio ADD COLUMN IF NOT EXISTS whatsapp       VARCHAR(20)",
        "ALTER TABLE negocio ADD COLUMN IF NOT EXISTS logo_url       TEXT",
        "ALTER TABLE negocio ADD COLUMN IF NOT EXISTS config_tienda  JSONB        DEFAULT '{}'",
        "ALTER TABLE negocio ADD COLUMN IF NOT EXISTS qr_negocio_url  TEXT",
        "ALTER TABLE negocio ADD COLUMN IF NOT EXISTS qr_negocio_data VARCHAR(300)",
        "ALTER TABLE negocio ADD COLUMN IF NOT EXISTS perfil_publico  BOOLEAN      DEFAULT TRUE NOT NULL",
    ]

    for sql in columnas:
        conn.execute(sa.text(sql))


def downgrade():
    # No eliminamos columnas en downgrade para evitar pérdida de datos
    pass
