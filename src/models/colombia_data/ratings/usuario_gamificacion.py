"""
TuKomercio — Gamificación de Usuario (Persona) v1.0  ·  Sprint 8
═══════════════════════════════════════════════════════════════════════════════

Gamificación a nivel de PERSONA (no de negocio). Mientras NegocioGamificacion
mide el desempeño de cada tienda, esto mide la trayectoria del emprendedor a
través de todos sus negocios: su XP personal, su nivel de creador y su racha
de actividad (login diario).

La tabla se crea automáticamente vía db.create_all() al arranque.

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date
from datetime import datetime, date
from src.models.database import db


class UsuarioGamificacion(db.Model):
    """Estado de gamificación personal del usuario (creador/emprendedor)."""
    __tablename__ = 'usuario_gamificacion'

    id          = Column(Integer, primary_key=True)
    usuario_id  = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'),
                         unique=True, nullable=False, index=True)

    # XP y nivel de CREADOR (distinto del nivel de cada negocio)
    xp_personal = Column(Integer, default=0, nullable=False)
    nivel       = Column(Integer, default=1, nullable=False)

    # Racha de actividad personal (login diario)
    racha_login_dias  = Column(Integer, default=0, nullable=False)
    racha_login_max   = Column(Integer, default=0, nullable=False)
    racha_login_fecha = Column(Date, nullable=True)

    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Escalera de niveles de CREADOR ────────────────────────────────
    # (XP requerido, nivel, nombre) — temática de emprendedor, sobria.
    NIVELES = [
        (0,     1,  '🌱 Aprendiz'),
        (150,   2,  '🛠️ Emprendedor'),
        (400,   3,  '📈 Comerciante'),
        (900,   4,  '🚀 Empresario'),
        (1800,  5,  '🧭 Mentor'),
        (3600,  6,  '💼 Maestro'),
        (7000,  8,  '🏛️ Magnate'),
        (15000, 10, '👑 Visionario'),
    ]

    def calcular_nivel(self):
        nivel_actual, nombre_actual = 1, self.NIVELES[0][2]
        for xp_req, nivel, nombre in self.NIVELES:
            if self.xp_personal >= xp_req:
                nivel_actual, nombre_actual = nivel, nombre
        self.nivel = nivel_actual
        return nivel_actual, nombre_actual

    def xp_para_siguiente_nivel(self):
        for i, (xp_req, nivel, nombre) in enumerate(self.NIVELES):
            if self.xp_personal < xp_req:
                prev = self.NIVELES[i - 1][0] if i > 0 else 0
                return (self.xp_personal - prev, xp_req - prev, nombre)
        return (self.xp_personal, self.xp_personal, self.NIVELES[-1][2])

    def agregar_xp(self, cantidad, motivo=''):
        """Suma XP y recalcula nivel. Retorna True si subió de nivel."""
        nivel_antes = self.nivel
        self.xp_personal = max(0, self.xp_personal + cantidad)
        self.calcular_nivel()
        return self.nivel > nivel_antes

    def actualizar_racha_login(self):
        """Actualiza la racha de login diario. Retorna True si la racha avanzó hoy."""
        hoy = date.today()
        if self.racha_login_fecha == hoy:
            return False  # ya contado hoy
        if self.racha_login_fecha is None:
            self.racha_login_dias = 1
        elif (hoy - self.racha_login_fecha).days == 1:
            self.racha_login_dias += 1
        else:
            self.racha_login_dias = 1  # racha rota
        self.racha_login_fecha = hoy
        self.racha_login_max = max(self.racha_login_max, self.racha_login_dias)
        return True

    @staticmethod
    def obtener_o_crear(usuario_id, db_session):
        reg = db_session.query(UsuarioGamificacion).filter_by(usuario_id=usuario_id).first()
        if not reg:
            reg = UsuarioGamificacion(usuario_id=usuario_id)
            db_session.add(reg)
            db_session.flush()
        return reg

    def serialize(self):
        nivel_actual, nombre_nivel = self.calcular_nivel()
        xp_rango, xp_sig, nombre_sig = self.xp_para_siguiente_nivel()
        progreso = round((xp_rango / xp_sig * 100) if xp_sig else 100, 1)
        return {
            'usuario_id':        self.usuario_id,
            'xp_personal':       self.xp_personal,
            'nivel':             nivel_actual,
            'nombre_nivel':      nombre_nivel,
            'nivel_siguiente':   nombre_sig,
            'xp_en_rango':       xp_rango,
            'xp_para_siguiente': xp_sig,
            'progreso_pct':      progreso,
            'racha_login': {
                'dias': self.racha_login_dias,
                'max':  self.racha_login_max,
                'fecha': self.racha_login_fecha.isoformat() if self.racha_login_fecha else None,
            },
        }
