# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO - Plataforma de Comercio Electrónico, Gamificación y Gestión Empresarial
# ═══════════════════════════════════════════════════════════════════════════════
# AVISO DE PROPIEDAD INTELECTUAL Y DERECHOS DE AUTOR
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#   C.C.: 1.064.986.917 (Cereté, Córdoba, Colombia) — Bogotá D.C., Colombia
#   Contacto: carlos-5100@hotmail.com | +57 322 818 8375
#
# Este código fuente es CONFIDENCIAL y constituye un SECRETO COMERCIAL.
# Prohibida su copia, modificación o distribución sin autorización escrita.
# ═══════════════════════════════════════════════════════════════════════════════

"""
Modelo NegocioInteraccion — Interacciones sociales del comprador con el negocio.

Una fila = un usuario que SIGUE o le da LIKE a un negocio.
- tipo='seguir' → seguidor del negocio (alimenta el conteo de seguidores).
- tipo='like'   → me gusta al negocio.

La unicidad (negocio_id, usuario_id, tipo) hace que la acción sea un TOGGLE:
si ya existe, se quita; si no, se crea. Sirve a la trust strip de la tienda.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, Index
from src.models.database import db


class NegocioInteraccion(db.Model):
    __tablename__ = "negocio_interacciones"

    id         = Column(Integer, primary_key=True)
    negocio_id = Column(Integer, nullable=False)   # negocio destino (a quién se sigue/like)
    usuario_id = Column(Integer, nullable=False)   # usuario que interactúa
    tipo       = Column(String(16), nullable=False)  # 'seguir' | 'like'
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('negocio_id', 'usuario_id', 'tipo', name='uq_negocio_interaccion'),
        Index('ix_neg_inter_conteo', 'negocio_id', 'tipo'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'negocio_id': self.negocio_id,
            'usuario_id': self.usuario_id,
            'tipo': self.tipo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<NegocioInteraccion negocio={self.negocio_id} usuario={self.usuario_id} tipo={self.tipo}>"
