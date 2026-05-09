# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Modelo WompiConfig v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
# Tabla: wompi_configs
#   - Configuración de pagos en línea Wompi por negocio (1:1)
#   - Guarda public_key, integrity_key y events_key
#   - La integrity_key nunca sale por la API pública
#
# Flujo Wompi Widget:
#   1. Tendero guarda sus claves en el panel
#   2. Checkout llama /api/negocio/<id>/wompi/config-pub → {activo, public_key}
#   3. Si activo, checkout llama /api/negocio/<id>/wompi/session → signature
#   4. Frontend lanza el widget de Wompi con esos params
#
# ═══════════════════════════════════════════════════════════════════════════════

from datetime import datetime, timezone
from src.models.database import db


class WompiConfig(db.Model):
    """Configuración de pasarela de pago Wompi para una tienda TuKomercio."""

    __tablename__ = 'wompi_configs'

    # ─── PK ───────────────────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)

    # ─── Pertenencia (1:1 por negocio) ───────────────────────────────────────
    negocio_id = db.Column(
        db.Integer,
        db.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )

    # ─── Claves Wompi ─────────────────────────────────────────────────────────
    # public_key: pk_test_xxx o pk_prod_xxx (se puede mostrar al frontend)
    public_key   = db.Column(db.String(120))
    # integrity_key: para generar firmas HMAC-SHA256 (NUNCA se expone al comprador)
    integrity_key = db.Column(db.String(120))
    # events_key: para verificar webhooks (opcional en MVP)
    events_key   = db.Column(db.String(120))

    # ─── Ambiente ─────────────────────────────────────────────────────────────
    # 'test' → sandbox Wompi (transacciones ficticias)
    # 'prod' → producción real
    ambiente = db.Column(db.String(10), default='test', nullable=False)

    # ─── Estado ───────────────────────────────────────────────────────────────
    activo = db.Column(db.Boolean, default=False, nullable=False)

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # ─────────────────────────────────────────────────────────────────────────
    # MÉTODOS
    # ─────────────────────────────────────────────────────────────────────────

    def tiene_claves(self) -> bool:
        """True si ya se han configurado public_key e integrity_key."""
        return bool(self.public_key and self.integrity_key)

    def to_dict_public(self) -> dict:
        """Solo datos seguros para exponer al frontend (SIN integrity/events keys)."""
        return {
            'activo': self.activo and self.tiene_claves(),
            'public_key': self.public_key if self.activo else None,
            'ambiente': self.ambiente,
        }

    def to_dict_admin(self) -> dict:
        """Datos completos para el panel del tendero."""
        return {
            'id': self.id,
            'negocio_id': self.negocio_id,
            'public_key': self.public_key or '',
            'integrity_key': self.integrity_key or '',
            'events_key': self.events_key or '',
            'ambiente': self.ambiente,
            'activo': self.activo,
            'tiene_claves': self.tiene_claves(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return (
            f'<WompiConfig negocio={self.negocio_id} '
            f'ambiente={self.ambiente} activo={self.activo}>'
        )
