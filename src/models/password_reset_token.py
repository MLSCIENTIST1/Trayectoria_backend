"""
BizFlow Studio - Modelo de Token de Restablecimiento de Contraseña
Para gestionar tokens seguros de recuperación de password
"""

import secrets
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import db


class PasswordResetToken(db.Model):
    """
    Modelo para almacenar tokens de restablecimiento de contraseña.
    Los tokens expiran después de 1 hora por seguridad.
    """
    __tablename__ = "password_reset_tokens"

    # ==========================================
    # COLUMNAS
    # ==========================================
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    token = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)

    # ==========================================
    # RELACIÓN
    # ==========================================
    usuario = relationship("Usuario", backref="reset_tokens")

    # ==========================================
    # CONSTRUCTOR
    # ==========================================
    def __init__(self, user_id, hours_valid=1):
        """
        Crea un nuevo token de reset.
        
        Args:
            user_id (int): ID del usuario
            hours_valid (int): Horas de validez del token (default: 1)
        """
        self.user_id = user_id
        self.token = self._generate_token()
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(hours=hours_valid)
        self.used = False

    # ==========================================
    # MÉTODOS ESTÁTICOS
    # ==========================================
    @staticmethod
    def _generate_token():
        """Genera un token seguro de 64 caracteres"""
        return secrets.token_urlsafe(48)

    # ==========================================
    # MÉTODOS DE INSTANCIA
    # ==========================================
    def is_valid(self):
        """
        Verifica si el token es válido (no expirado y no usado).
        
        Returns:
            bool: True si el token es válido
        """
        if self.used:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        return True

    def mark_as_used(self):
        """Marca el token como usado"""
        self.used = True
        self.used_at = datetime.utcnow()

    def to_dict(self):
        """Serializa el token (sin exponer el token real)"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "used": self.used,
            "is_valid": self.is_valid()
        }

    # ==========================================
    # MÉTODOS DE CLASE
    # ==========================================
    @classmethod
    def create_for_user(cls, user_id):
        """
        Crea un nuevo token para un usuario, invalidando tokens anteriores.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            PasswordResetToken: El nuevo token creado
        """
        # Invalidar tokens anteriores del usuario
        cls.query.filter_by(user_id=user_id, used=False).update({"used": True})
        
        # Crear nuevo token
        new_token = cls(user_id=user_id)
        db.session.add(new_token)
        db.session.commit()
        
        return new_token

    @classmethod
    def get_valid_token(cls, token_string):
        """
        Busca un token válido por su string.
        
        Args:
            token_string (str): El token a buscar
            
        Returns:
            PasswordResetToken or None: El token si es válido, None si no
        """
        token = cls.query.filter_by(token=token_string).first()
        if token and token.is_valid():
            return token
        return None

    @classmethod
    def cleanup_expired(cls):
        """Elimina tokens expirados (mantenimiento)"""
        expired = cls.query.filter(cls.expires_at < datetime.utcnow()).all()
        count = len(expired)
        for token in expired:
            db.session.delete(token)
        db.session.commit()
        return count

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __repr__(self):
        status = "válido" if self.is_valid() else "inválido"
        return f"<PasswordResetToken user={self.user_id} ({status})>"