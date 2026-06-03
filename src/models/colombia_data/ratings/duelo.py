"""
TuKomercio — Duelos entre negocios v1.0 (Sprint 31)
═══════════════════════════════════════════════════════════════════════════════

Un negocio reta a otro a competir durante 7 días por el mayor número de pedidos
entregados. Al finalizar, gana quien más vendió. La tabla se crea sola.

Estados: pendiente → activo → finalizado | rechazado | expirado

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime, timedelta
from src.models.database import db

DURACION_DUELO_DIAS = 7


class Duelo(db.Model):
    __tablename__ = 'duelos'

    id                 = Column(Integer, primary_key=True)
    retador_negocio_id = Column(Integer, index=True, nullable=False)
    retado_negocio_id  = Column(Integer, index=True, nullable=False)

    estado             = Column(String(20), default='pendiente', nullable=False)
    # pendiente | activo | finalizado | rechazado | expirado

    fecha_inicio       = Column(DateTime, nullable=True)   # al aceptar
    fecha_fin          = Column(DateTime, nullable=True)   # inicio + 7d
    creado_en          = Column(DateTime, default=datetime.utcnow)

    ganador_negocio_id = Column(Integer, nullable=True)    # None = empate
    ventas_retador     = Column(Integer, default=0)
    ventas_retado      = Column(Integer, default=0)

    def aceptar(self):
        self.estado = 'activo'
        self.fecha_inicio = datetime.utcnow()
        self.fecha_fin = self.fecha_inicio + timedelta(days=DURACION_DUELO_DIAS)

    def serialize(self):
        return {
            'id': self.id,
            'retador_negocio_id': self.retador_negocio_id,
            'retado_negocio_id': self.retado_negocio_id,
            'estado': self.estado,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'ganador_negocio_id': self.ganador_negocio_id,
            'ventas_retador': self.ventas_retador or 0,
            'ventas_retado': self.ventas_retado or 0,
        }


def determinar_ganador(id_retador, ventas_retador, id_retado, ventas_retado):
    """Devuelve el negocio_id ganador, o None si hay empate. Función PURA."""
    if (ventas_retador or 0) > (ventas_retado or 0):
        return id_retador
    if (ventas_retado or 0) > (ventas_retador or 0):
        return id_retado
    return None  # empate
