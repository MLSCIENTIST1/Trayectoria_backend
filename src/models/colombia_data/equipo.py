# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — Modelos de Equipo v2.0 (Links por Rol)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Diseño: un link compartido por rol (como Slack).
# El tendero genera el link → lo envía por WhatsApp → cualquiera que lo abra
# y ponga su nombre entra con ese rol. Sin emails, sin formularios largos.
#
# Tablas:
#   link_invitaciones  → un link activo por (negocio, rol). Regenerable.
#   empleados_negocio  → quién ha aceptado y con qué rol.
#
# Flujo:
#   1. Panel muestra 3 links (admin / vendedor / bodega) — se auto-crean.
#   2. Dueño copia el link del rol que quiere y lo envía por WhatsApp.
#   3. Empleado abre el link → pone su nombre → click "Unirme".
#   4. Aparece en la lista de miembros del panel.
#   5. Dueño puede regenerar cualquier link (invalida el anterior) o suspender
#      a cualquier miembro.
#
# ═══════════════════════════════════════════════════════════════════════════════

import secrets
from datetime import datetime, timezone
from src.models.database import db


# ─── Catálogo de roles ────────────────────────────────────────────────────────
ROLES = {
    'dueno':    {'label': 'Dueño',    'icon': '👑', 'color': '#7c3aed', 'desc': 'Control total del negocio'},
    'admin':    {'label': 'Admin',    'icon': '⚙️',  'color': '#2563eb', 'desc': 'Gestión completa — pedidos, productos, cupones'},
    'vendedor': {'label': 'Vendedor', 'icon': '🛍️', 'color': '#059669', 'desc': 'Procesar pedidos y ver productos'},
    'bodega':   {'label': 'Bodega',   'icon': '📦',  'color': '#d97706', 'desc': 'Actualizar stock y ver pedidos'},
}

# Roles que se pueden invitar (dueño no se invita)
ROLES_INVITABLES = ['admin', 'vendedor', 'bodega']

PERMISOS = {
    'dueno':    ['todo'],
    'admin':    ['pedidos', 'productos', 'cupones', 'resenas', 'analytics', 'equipo_ver'],
    'vendedor': ['pedidos', 'productos_ver', 'analytics_basico'],
    'bodega':   ['pedidos_ver', 'stock'],
}


# ══════════════════════════════════════════════════════════════════════════════
# LinkInvitacion — el link compartido por rol
# ══════════════════════════════════════════════════════════════════════════════
class LinkInvitacion(db.Model):
    """
    Link de invitación compartido para un rol en un negocio.
    Un solo link activo por (negocio_id, rol).
    Regenerar = nuevo token → el link anterior queda inválido.
    """

    __tablename__ = 'link_invitaciones'

    id         = db.Column(db.Integer, primary_key=True)
    negocio_id = db.Column(
        db.Integer,
        db.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False, index=True
    )
    rol    = db.Column(db.String(20), nullable=False)
    token  = db.Column(db.String(64), unique=True, nullable=False, index=True,
                       default=lambda: secrets.token_urlsafe(32))
    activo = db.Column(db.Boolean, default=True, nullable=False)

    # Usos: cuántas personas han entrado por este link
    usos   = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    negocio = db.relationship('Negocio', foreign_keys=[negocio_id])

    __table_args__ = (
        db.UniqueConstraint('negocio_id', 'rol', name='uq_link_negocio_rol'),
    )

    # ── Métodos ──────────────────────────────────────────────────────────────

    def regenerar(self):
        """Genera un nuevo token, invalidando el link anterior."""
        self.token     = secrets.token_urlsafe(32)
        self.usos      = 0
        self.activo    = True
        self.updated_at = datetime.now(timezone.utc)

    def rol_info(self) -> dict:
        return ROLES.get(self.rol, {'label': self.rol, 'icon': '👤', 'color': '#64748b', 'desc': ''})

    def to_dict(self) -> dict:
        info = self.rol_info()
        return {
            'id':        self.id,
            'negocio_id': self.negocio_id,
            'rol':       self.rol,
            'rol_label': info['label'],
            'rol_icon':  info['icon'],
            'rol_color': info['color'],
            'rol_desc':  info['desc'],
            'token':     self.token,
            'activo':    self.activo,
            'usos':      self.usos,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def get_or_create(cls, negocio_id: int, rol: str):
        """Devuelve el link existente o crea uno nuevo para ese rol."""
        link = cls.query.filter_by(negocio_id=negocio_id, rol=rol).first()
        if not link:
            link = cls(
                negocio_id=negocio_id,
                rol=rol,
                token=secrets.token_urlsafe(32),
            )
            db.session.add(link)
            db.session.flush()
        return link

    def __repr__(self):
        return f'<LinkInvitacion negocio={self.negocio_id} rol={self.rol} activo={self.activo}>'


# ══════════════════════════════════════════════════════════════════════════════
# EmpleadoNegocio — quien ya aceptó un link
# ══════════════════════════════════════════════════════════════════════════════
class EmpleadoNegocio(db.Model):
    """
    Miembro del equipo que ya aceptó una invitación.
    No requiere email — solo nombre (y opcionalmente usuario_id si tiene cuenta).
    """

    __tablename__ = 'empleados_negocio'

    id         = db.Column(db.Integer, primary_key=True)
    negocio_id = db.Column(
        db.Integer,
        db.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False, index=True
    )
    # Si tiene cuenta TuKomercio
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id_usuario', ondelete='SET NULL'),
        nullable=True, index=True
    )

    # Link por el que entró
    link_id = db.Column(
        db.Integer,
        db.ForeignKey('link_invitaciones.id', ondelete='SET NULL'),
        nullable=True
    )

    nombre = db.Column(db.String(100), nullable=False)  # nombre que puso al unirse
    email  = db.Column(db.String(150))                  # opcional

    rol    = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='activo', index=True)
    # activo | suspendido

    unido_en = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    negocio = db.relationship('Negocio', foreign_keys=[negocio_id])
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    link    = db.relationship('LinkInvitacion', foreign_keys=[link_id])

    # ── Métodos ──────────────────────────────────────────────────────────────

    def rol_info(self) -> dict:
        return ROLES.get(self.rol, {'label': self.rol, 'icon': '👤', 'color': '#64748b', 'desc': ''})

    def tiene_permiso(self, permiso: str) -> bool:
        perms = PERMISOS.get(self.rol, [])
        return 'todo' in perms or permiso in perms

    def to_dict(self) -> dict:
        info = self.rol_info()
        return {
            'id':          self.id,
            'negocio_id':  self.negocio_id,
            'usuario_id':  self.usuario_id,
            'nombre':      self.nombre,
            'email':       self.email or '',
            'rol':         self.rol,
            'rol_label':   info['label'],
            'rol_icon':    info['icon'],
            'rol_color':   info['color'],
            'estado':      self.estado,
            'unido_en':    self.unido_en.isoformat() if self.unido_en else None,
        }

    def __repr__(self):
        return f'<EmpleadoNegocio negocio={self.negocio_id} nombre={self.nombre} rol={self.rol}>'
