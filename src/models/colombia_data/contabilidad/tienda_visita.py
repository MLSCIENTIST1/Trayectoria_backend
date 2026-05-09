# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Modelo TiendaVisita v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
# Conteo de visitas diarias por negocio.
# Estrategia: un registro por (negocio_id, fecha) con contador incremental.
# → Muy eficiente: máximo 365 filas/año por negocio.
# → Sin PII: no almacenamos IP ni user-agent.
#
# ═══════════════════════════════════════════════════════════════════════════════

from datetime import date as _date
from src.models.database import db


class TiendaVisita(db.Model):
    """Contador de visitas diarias a la tienda pública de un negocio."""

    __tablename__ = 'tienda_visitas'

    # ─── PK ───────────────────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)

    # ─── Pertenencia ──────────────────────────────────────────────────────────
    negocio_id = db.Column(
        db.Integer,
        db.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # ─── Fecha del bucket diario ──────────────────────────────────────────────
    fecha = db.Column(db.Date, nullable=False, default=_date.today, index=True)

    # ─── Contador (se incrementa en cada visita del día) ──────────────────────
    contador = db.Column(db.Integer, default=1, nullable=False)

    # ─── Unicidad: un registro por negocio por día ────────────────────────────
    __table_args__ = (
        db.UniqueConstraint('negocio_id', 'fecha', name='uq_visita_negocio_fecha'),
    )

    # ─────────────────────────────────────────────────────────────────────────
    # MÉTODO DE NEGOCIO
    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def registrar(cls, negocio_id: int) -> bool:
        """
        Registra una visita del día actual.
        - Si ya existe el bucket → incrementa el contador.
        - Si no existe → crea el registro con contador=1.
        Retorna True si tuvo éxito.
        """
        hoy = _date.today()
        try:
            fila = cls.query.filter_by(negocio_id=negocio_id, fecha=hoy).with_for_update().first()
            if fila:
                fila.contador += 1
            else:
                fila = cls(negocio_id=negocio_id, fecha=hoy, contador=1)
                db.session.add(fila)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            # Segundo intento (race condition al crear simultáneamente)
            try:
                fila = cls.query.filter_by(negocio_id=negocio_id, fecha=hoy).first()
                if fila:
                    fila.contador += 1
                    db.session.commit()
                    return True
            except Exception:
                db.session.rollback()
            return False

    def __repr__(self):
        return f'<TiendaVisita negocio={self.negocio_id} fecha={self.fecha} n={self.contador}>'
