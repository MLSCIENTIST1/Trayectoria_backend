"""
TuKomercio — Referidos gamificados v1.0 (Sprint 29)
═══════════════════════════════════════════════════════════════════════════════

Registra quién refirió a quién. Cuando el referido completa su PRIMERA venta,
el referido se marca como "convertido" y el referidor recibe recompensa.

La tabla se crea automáticamente vía db.create_all() al arranque.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, UniqueConstraint
from datetime import datetime
from src.models.database import db


class Referido(db.Model):
    """Un referido: un usuario (referidor) invitó a otro (referido)."""
    __tablename__ = 'referidos'
    __table_args__ = (
        UniqueConstraint('referido_usuario_id', name='uq_referido_unico'),
    )

    id                  = Column(Integer, primary_key=True)
    referidor_usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'),
                                  nullable=False, index=True)
    referido_usuario_id  = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'),
                                  nullable=False, index=True)
    fecha_registro      = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Conversión: el referido completó su primera venta
    convertido          = Column(Boolean, default=False, nullable=False)
    fecha_conversion    = Column(DateTime, nullable=True)
    recompensado        = Column(Boolean, default=False, nullable=False)

    @staticmethod
    def codigo_de_usuario(usuario_id):
        """Código de referido = el id del usuario (simple y único)."""
        return f"TK{usuario_id}"

    @staticmethod
    def usuario_de_codigo(codigo):
        """Extrae el usuario_id de un código 'TK123'. None si inválido."""
        if not codigo:
            return None
        c = str(codigo).strip().upper()
        if c.startswith('TK') and c[2:].isdigit():
            return int(c[2:])
        if c.isdigit():
            return int(c)
        return None

    def serialize(self):
        return {
            'id': self.id,
            'referido_usuario_id': self.referido_usuario_id,
            'convertido': self.convertido,
            'recompensado': self.recompensado,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'fecha_conversion': self.fecha_conversion.isoformat() if self.fecha_conversion else None,
        }
