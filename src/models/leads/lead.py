"""
╔══════════════════════════════════════════════════════════════╗
║  LEADS CAMPAÑA — Modelo SQLAlchemy                          ║
║  Gestión interna de leads Meta Ads para superadmin Carlos   ║
╚══════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from src.models.database import db


class LeadCampana(db.Model):
    """Lead generado por campaña Meta Ads u otro canal."""
    __tablename__ = 'leads_campana'

    # ── Opciones de dominio ───────────────────────────────────
    ESTADOS = [
        'nuevo', 'en_seguimiento', 'caliente',
        'cierre_pendiente', 'cerrado_ganado', 'cerrado_perdido', 'frio'
    ]
    PRIORIDADES = ['baja', 'media', 'alta', 'estrella']
    ORIGENES    = [
        'meta_ads_tukomercio', 'meta_ads_rodar',
        'marketplace', 'organico', 'referido', 'otro'
    ]

    # ── Columnas ──────────────────────────────────────────────
    id                    = db.Column(db.Integer, primary_key=True)
    nombre                = db.Column(db.String(120), nullable=True)
    telefono              = db.Column(db.String(30),  nullable=False, index=True)
    nicho                 = db.Column(db.String(80),  nullable=True)
    info_adicional        = db.Column(db.Text,        nullable=True)

    estado                = db.Column(db.String(30),  nullable=False, default='nuevo',   index=True)
    prioridad             = db.Column(db.String(20),  nullable=False, default='media',   index=True)
    origen                = db.Column(db.String(40),  nullable=False, default='meta_ads_tukomercio')

    fecha_primer_contacto = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_ultimo_mensaje  = db.Column(db.DateTime, nullable=True)
    proximo_recordatorio  = db.Column(db.DateTime, nullable=True, index=True)
    mensajes_enviados     = db.Column(db.Integer,  nullable=False, default=0)

    created_at            = db.Column(db.DateTime, default=datetime.utcnow,  nullable=False)
    updated_at            = db.Column(db.DateTime, default=datetime.utcnow,
                                      onupdate=datetime.utcnow, nullable=False)

    # ── Helpers ───────────────────────────────────────────────
    def telefono_normalizado(self) -> str:
        """Devuelve el teléfono listo para wa.me (solo dígitos, incluye código país)."""
        digits = ''.join(c for c in self.telefono if c.isdigit())
        if not digits.startswith('57') and len(digits) == 10:
            digits = '57' + digits
        return digits

    def to_dict(self) -> dict:
        return {
            'id':                    self.id,
            'nombre':                self.nombre,
            'telefono':              self.telefono,
            'telefono_wa':           self.telefono_normalizado(),
            'nicho':                 self.nicho,
            'info_adicional':        self.info_adicional,
            'estado':                self.estado,
            'prioridad':             self.prioridad,
            'origen':                self.origen,
            'fecha_primer_contacto': self.fecha_primer_contacto.isoformat() if self.fecha_primer_contacto else None,
            'fecha_ultimo_mensaje':  self.fecha_ultimo_mensaje.isoformat()  if self.fecha_ultimo_mensaje  else None,
            'proximo_recordatorio':  self.proximo_recordatorio.isoformat()  if self.proximo_recordatorio  else None,
            'mensajes_enviados':     self.mensajes_enviados,
            'created_at':            self.created_at.isoformat(),
            'updated_at':            self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f'<LeadCampana {self.id} {self.nombre or self.telefono} [{self.estado}]>'


class PlantillaMensaje(db.Model):
    """Plantillas de mensaje predefinidas para envíos por WhatsApp."""
    __tablename__ = 'plantillas_mensajes'

    id         = db.Column(db.Integer, primary_key=True)
    nombre     = db.Column(db.String(120), nullable=False)
    cuerpo     = db.Column(db.Text,        nullable=False)   # Soporta {nombre}, {nicho}, {ciudad}
    orden      = db.Column(db.Integer,     nullable=False, default=0)
    activa     = db.Column(db.Boolean,     nullable=False, default=True)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime,    default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            'id':         self.id,
            'nombre':     self.nombre,
            'cuerpo':     self.cuerpo,
            'orden':      self.orden,
            'activa':     self.activa,
            'created_at': self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<PlantillaMensaje {self.id} "{self.nombre}">'
