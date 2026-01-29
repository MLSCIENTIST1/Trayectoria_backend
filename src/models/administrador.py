"""
TuKomercio - Modelo de Administradores
Tabla: administradores
"""

from datetime import datetime
from src.models.database import db
from sqlalchemy.dialects.postgresql import JSONB


class Administrador(db.Model):
    """
    Modelo para gestionar administradores del sistema.
    
    Roles disponibles:
    - superadmin: Control total, puede gestionar otros admins
    - admin: Gestiona challenges, usuarios, negocios
    - moderator: Solo aprueba/rechaza contenido
    """
    
    __tablename__ = 'administradores'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(255))
    rol = db.Column(db.String(50), default='admin')  # superadmin, admin, moderator
    permisos = db.Column(JSONB, default=list)  # ['challenges', 'usuarios', 'negocios', 'reportes', 'configuracion', 'admins']
    activo = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('administradores.id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación auto-referencial para saber quién creó a quién
    creador = db.relationship('Administrador', remote_side=[id], backref='admins_creados')
    
    def __repr__(self):
        return f'<Administrador {self.email} ({self.rol})>'
    
    def to_dict(self):
        """Serializa el administrador a diccionario."""
        return {
            'id': self.id,
            'email': self.email,
            'nombre': self.nombre,
            'rol': self.rol,
            'permisos': self.permisos or [],
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def tiene_permiso(self, permiso):
        """Verifica si el admin tiene un permiso específico."""
        if self.rol == 'superadmin':
            return True
        return permiso in (self.permisos or [])
    
    def es_superadmin(self):
        """Verifica si es superadmin."""
        return self.rol == 'superadmin'
    
    @staticmethod
    def get_by_email(email):
        """Busca un administrador por email."""
        return Administrador.query.filter(
            db.func.lower(Administrador.email) == email.lower(),
            Administrador.activo == True
        ).first()
    
    @staticmethod
    def es_admin(email):
        """Verifica si un email es administrador activo."""
        admin = Administrador.get_by_email(email)
        return admin is not None