"""
TuKomercio — Modelo de Log de Auditoría de Administradores (Admin Panel A2)
Tabla: admin_audit_log

Registra QUIÉN (admin), QUÉ (acción), SOBRE QUÉ (entidad), CUÁNDO y con qué
detalle (antes/después). Es la base de seguridad/trazabilidad de todo el panel:
a partir de la Fase 1 toda acción mutante del admin debe quedar registrada aquí.
"""

from datetime import datetime
from src.models.database import db
from sqlalchemy.dialects.postgresql import JSONB


# Acciones reconocidas (whitelist para normalizar lo que se registra).
ACCIONES_VALIDAS = {
    'crear', 'editar', 'eliminar', 'restaurar', 'activar', 'desactivar',
    'toggle', 'otorgar', 'revocar', 'ajustar', 'asignar', 'aprobar',
    'rechazar', 'login', 'export', 'recalcular', 'enviar',
}


def normalizar_accion(accion):
    """Función PURA: normaliza una acción a minúsculas/whitelist. 'otro' si no se reconoce."""
    if not accion:
        return 'otro'
    a = str(accion).strip().lower()
    return a if a in ACCIONES_VALIDAS else 'otro'


class AdminAuditLog(db.Model):
    __tablename__ = 'admin_audit_log'

    id           = db.Column(db.Integer, primary_key=True)
    admin_id     = db.Column(db.Integer, index=True)          # id en tabla administradores (nullable por robustez)
    admin_email  = db.Column(db.String(255), index=True)
    accion       = db.Column(db.String(50), nullable=False, index=True)   # crear/editar/eliminar/...
    entidad      = db.Column(db.String(100), index=True)      # 'administrador','usuario','feature','badge',...
    entidad_id   = db.Column(db.String(100))                  # id afectado (string = flexible)
    detalle      = db.Column(JSONB, default=dict)             # {antes, despues, extra}
    ip           = db.Column(db.String(64))
    user_agent   = db.Column(db.String(300))
    created_at   = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<AdminAuditLog {self.admin_email} {self.accion} {self.entidad}:{self.entidad_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'admin_email': self.admin_email,
            'accion': self.accion,
            'entidad': self.entidad,
            'entidad_id': self.entidad_id,
            'detalle': self.detalle or {},
            'ip': self.ip,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
