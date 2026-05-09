# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Modelo EmpleadoNegocio v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
# Tabla: empleados_negocio
#   Multi-usuario: un negocio puede tener varios usuarios con roles distintos.
#
# Roles:
#   dueno    → dueño (auto-asignado al crear el negocio, no se puede remover)
#   admin    → acceso completo excepto facturación
#   vendedor → procesar pedidos, ver productos (no puede editar config)
#   bodega   → actualizar stock, ver pedidos (solo inventario)
#
# Flujo de invitación:
#   1. Dueño ingresa email + rol → se crea registro con estado='pendiente' + token
#   2. Sistema genera link con el token
#   3. Empleado abre el link → acepta → su usuario_id queda vinculado
#   4. Estado cambia a 'activo'
#
# ═══════════════════════════════════════════════════════════════════════════════

import secrets
from datetime import datetime, timezone
from src.models.database import db


ROLES = {
    'dueno':    {'label': 'Dueño',    'icon': '👑', 'color': '#7c3aed'},
    'admin':    {'label': 'Admin',    'icon': '⚙️',  'color': '#2563eb'},
    'vendedor': {'label': 'Vendedor', 'icon': '🛍️', 'color': '#059669'},
    'bodega':   {'label': 'Bodega',   'icon': '📦',  'color': '#d97706'},
}

PERMISOS = {
    'dueno':    ['todo'],
    'admin':    ['pedidos', 'productos', 'cupones', 'resenas', 'analytics', 'equipo_ver'],
    'vendedor': ['pedidos', 'productos_ver', 'analytics_basico'],
    'bodega':   ['pedidos_ver', 'stock'],
}


class EmpleadoNegocio(db.Model):
    """Miembro del equipo de un negocio TuKomercio."""

    __tablename__ = 'empleados_negocio'

    # ─── PK ───────────────────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)

    # ─── Negocio ──────────────────────────────────────────────────────────────
    negocio_id = db.Column(
        db.Integer,
        db.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # ─── Usuario (None = invitación pendiente sin cuenta aún) ─────────────────
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id_usuario', ondelete='SET NULL'),
        nullable=True,
        index=True
    )

    # ─── Email de invitación ──────────────────────────────────────────────────
    email = db.Column(db.String(150), nullable=False)
    nombre_display = db.Column(db.String(100))     # nombre que puso el dueño al invitar

    # ─── Rol ──────────────────────────────────────────────────────────────────
    rol = db.Column(db.String(20), nullable=False, default='vendedor')

    # ─── Estado ───────────────────────────────────────────────────────────────
    # pendiente → activo → suspendido
    estado = db.Column(db.String(20), nullable=False, default='pendiente', index=True)

    # ─── Token de invitación ──────────────────────────────────────────────────
    token_invitacion = db.Column(db.String(64), unique=True, index=True)
    token_expira     = db.Column(db.DateTime(timezone=True))

    # ─── Fechas ───────────────────────────────────────────────────────────────
    invitado_en = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    aceptado_en = db.Column(db.DateTime(timezone=True))

    # ─── Relaciones ───────────────────────────────────────────────────────────
    negocio = db.relationship('Negocio', foreign_keys=[negocio_id])
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])

    # ─── Unicidad: un usuario no puede estar dos veces en el mismo negocio ─────
    __table_args__ = (
        db.UniqueConstraint('negocio_id', 'email', name='uq_empleado_negocio_email'),
    )

    # ─────────────────────────────────────────────────────────────────────────
    # MÉTODOS
    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def generar_token(cls) -> str:
        return secrets.token_urlsafe(32)

    def rol_info(self) -> dict:
        return ROLES.get(self.rol, {'label': self.rol, 'icon': '👤', 'color': '#64748b'})

    def tiene_permiso(self, permiso: str) -> bool:
        perms = PERMISOS.get(self.rol, [])
        return 'todo' in perms or permiso in perms

    def to_dict(self) -> dict:
        info = self.rol_info()
        nombre = (
            self.nombre_display
            or (f'{self.usuario.nombre} {self.usuario.apellidos}'.strip() if self.usuario else None)
            or self.email.split('@')[0]
        )
        return {
            'id':            self.id,
            'negocio_id':    self.negocio_id,
            'usuario_id':    self.usuario_id,
            'email':         self.email,
            'nombre':        nombre,
            'rol':           self.rol,
            'rol_label':     info['label'],
            'rol_icon':      info['icon'],
            'rol_color':     info['color'],
            'estado':        self.estado,
            'invitado_en':   self.invitado_en.isoformat() if self.invitado_en else None,
            'aceptado_en':   self.aceptado_en.isoformat() if self.aceptado_en else None,
            'tiene_token':   bool(self.token_invitacion),
        }

    def __repr__(self):
        return (
            f'<EmpleadoNegocio negocio={self.negocio_id} '
            f'email={self.email} rol={self.rol} estado={self.estado}>'
        )
