"""
TuKomercio — Modelo de Pagos de Suscripción
============================================
Registra cada pago que un negocio realiza a TuKomercio.
Permite llevar historial completo, generar reportes de MRR real
y mostrar al tendero sus "facturas" de servicio.

Estados del pago:
  pendiente   — registrado pero aún no confirmado
  completado  — pago confirmado/recibido
  fallido     — intentado pero fallido (cargo rechazado, etc.)
  reembolsado — devuelto al cliente

Métodos de pago:
  nequi, daviplata, transferencia, efectivo, tarjeta, otro
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

METODOS_PAGO = {
    'nequi':         '📱 Nequi',
    'daviplata':     '📱 Daviplata',
    'transferencia': '🏦 Transferencia bancaria',
    'efectivo':      '💵 Efectivo',
    'tarjeta':       '💳 Tarjeta',
    'otro':          '📋 Otro',
}

ESTADOS_PAGO = ('pendiente', 'completado', 'fallido', 'reembolsado')


class PagoSuscripcion(db.Model):
    """
    Registro de un pago de suscripción de un negocio.
    Cada vez que el admin confirma un pago mensual se crea un registro aquí.
    """
    __tablename__ = 'pagos_suscripcion'

    id = sa.Column(sa.Integer, primary_key=True)

    # ── Relaciones ────────────────────────────────────────────────────
    suscripcion_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('suscripciones_negocio.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    negocio_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # ── Datos del pago ────────────────────────────────────────────────
    monto   = sa.Column(sa.Numeric(12, 2), nullable=False)
    moneda  = sa.Column(sa.String(3), nullable=False, default='COP')

    metodo_pago = sa.Column(sa.String(30), nullable=False, default='transferencia')
    # nequi | daviplata | transferencia | efectivo | tarjeta | otro

    estado = sa.Column(sa.String(20), nullable=False, default='completado', index=True)
    # pendiente | completado | fallido | reembolsado

    # ── Trazabilidad ──────────────────────────────────────────────────
    referencia      = sa.Column(sa.String(200), nullable=True)
    # Número de comprobante, ID de transacción, etc.
    comprobante_url = sa.Column(sa.String(500), nullable=True)
    # URL a imagen/PDF del comprobante (Cloudinary u otro)

    # ── Período cubierto ──────────────────────────────────────────────
    periodo_inicio = sa.Column(sa.DateTime, nullable=True)
    periodo_fin    = sa.Column(sa.DateTime, nullable=True)

    # ── Auditoría ─────────────────────────────────────────────────────
    notas          = sa.Column(sa.Text, nullable=True)
    registrado_por = sa.Column(sa.String(80), nullable=False, default='admin')
    # 'admin:<email>' | 'sistema' | 'usuario'

    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # ── Relaciones ORM ────────────────────────────────────────────────
    suscripcion = relationship(
        'SuscripcionNegocio',
        backref=db.backref('pagos', lazy='dynamic', order_by='PagoSuscripcion.created_at.desc()')
    )
    negocio = relationship('Negocio', lazy='select')

    # ── Serialización ─────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            'id':             self.id,
            'suscripcion_id': self.suscripcion_id,
            'negocio_id':     self.negocio_id,
            'negocio_nombre': self.negocio.nombre_negocio if self.negocio else None,

            'monto':          float(self.monto) if self.monto is not None else None,
            'moneda':         self.moneda,
            'metodo_pago':    self.metodo_pago,
            'metodo_label':   METODOS_PAGO.get(self.metodo_pago, self.metodo_pago),
            'estado':         self.estado,

            'referencia':      self.referencia,
            'comprobante_url': self.comprobante_url,

            'periodo_inicio': self.periodo_inicio.isoformat() if self.periodo_inicio else None,
            'periodo_fin':    self.periodo_fin.isoformat()    if self.periodo_fin    else None,

            'notas':          self.notas,
            'registrado_por': self.registrado_por,

            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return (f'<PagoSuscripcion negocio={self.negocio_id} '
                f'monto={self.monto} {self.moneda} estado={self.estado}>')
