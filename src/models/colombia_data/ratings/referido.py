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

    # ── NIVEL 1 — Activación: el referido PUBLICÓ SU TIENDA (premio chico) ──
    #    (columnas históricas 'convertido/recompensado' reusadas; antes era 1ª venta)
    convertido          = Column(Boolean, default=False, nullable=False)
    fecha_conversion    = Column(DateTime, nullable=True)
    recompensado        = Column(Boolean, default=False, nullable=False)

    # ── NIVEL 2 — Primer pago: el referido PAGÓ SU PRIMERA MENSUALIDAD (premio grande) ──
    pago_confirmado     = Column(Boolean, default=False, nullable=False)
    fecha_pago          = Column(DateTime, nullable=True)
    recompensado_pago   = Column(Boolean, default=False, nullable=False)

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

    @classmethod
    def vincular(cls, codigo, nuevo_usuario_id, db_session, referidor_existe=None):
        """
        Crea el vínculo de referido si el código es válido y no es propio.
        Pensada para el flujo de REGISTRO: a prueba de fallos, nunca lanza por un
        código inválido — simplemente no vincula. NO hace commit (lo hace quien llama).

        `referidor_existe` es un predicado opcional (uid -> bool) inyectable para
        tests; por defecto consulta la tabla usuarios.

        Retorna (Referido|None, motivo) donde motivo ∈
          'ok' | 'sin_codigo' | 'codigo_invalido' | 'auto_referido'
          | 'referidor_inexistente' | 'ya_referido'.
        """
        if not codigo:
            return None, 'sin_codigo'
        referidor_id = cls.usuario_de_codigo(codigo)
        if not referidor_id:
            return None, 'codigo_invalido'
        if referidor_id == nuevo_usuario_id:
            return None, 'auto_referido'

        # ¿el referidor existe?
        if referidor_existe is None:
            from src.models.usuarios import Usuario
            existe = db_session.query(Usuario.id_usuario).filter_by(
                id_usuario=referidor_id).first() is not None
        else:
            existe = bool(referidor_existe(referidor_id))
        if not existe:
            return None, 'referidor_inexistente'

        # el nuevo usuario no debe tener ya un referidor (constraint único)
        if cls.query.filter_by(referido_usuario_id=nuevo_usuario_id).first():
            return None, 'ya_referido'

        ref = cls(referidor_usuario_id=referidor_id, referido_usuario_id=nuevo_usuario_id)
        db_session.add(ref)
        return ref, 'ok'

    def serialize(self):
        return {
            'id': self.id,
            'referido_usuario_id': self.referido_usuario_id,
            'convertido': self.convertido,            # nivel 1: publicó tienda
            'recompensado': self.recompensado,
            'pago_confirmado': self.pago_confirmado,  # nivel 2: pagó 1ª mensualidad
            'recompensado_pago': self.recompensado_pago,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'fecha_conversion': self.fecha_conversion.isoformat() if self.fecha_conversion else None,
            'fecha_pago': self.fecha_pago.isoformat() if self.fecha_pago else None,
        }
