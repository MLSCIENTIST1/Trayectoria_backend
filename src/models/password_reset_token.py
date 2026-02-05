# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗██╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗  ██████╗██╗ ██████╗ 
# ╚══██╔══╝██║   ██║██║ ██╔╝██╔═══██╗████╗ ████║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗
#    ██║   ██║   ██║█████╔╝ ██║   ██║██╔████╔██║█████╗  ██████╔╝██║     ██║██║   ██║
#    ██║   ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║   ██║
#    ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║╚██████╔╝
#    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝ 
# ═══════════════════════════════════════════════════════════════════════════════
#
# TUKOMERCIO - Plataforma de Comercio Electrónico, Gamificación y Gestión Empresarial
# Anteriormente conocido como: Trayectoria / BizFlow Studio
#
# ═══════════════════════════════════════════════════════════════════════════════
# AVISO DE PROPIEDAD INTELECTUAL Y DERECHOS DE AUTOR
# ═══════════════════════════════════════════════════════════════════════════════
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#
# TITULAR DE DERECHOS:
#   Nombre:     Carlos Eduardo Huérfano Bermúdez
#   C.C.:       1.064.986.917 (Cereté, Córdoba, Colombia)
#   Contacto:   carlos-5100@hotmail.com | +57 322 818 8375
#   Ubicación:  Bogotá D.C., Colombia
#
# INFORMACIÓN DEL PROYECTO:
#   Nombre:     TuKomercio
#   Inicio:     Julio 24, 2024
#   Repositorio: github.com/routeres (routeres@gmail.com)
#
# ═══════════════════════════════════════════════════════════════════════════════
# TÉRMINOS DE USO Y RESTRICCIONES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este código fuente es CONFIDENCIAL y constituye un SECRETO COMERCIAL.
#
# QUEDA ESTRICTAMENTE PROHIBIDO sin autorización ESCRITA del titular:
#
#   1. Copiar, reproducir o duplicar este código, total o parcialmente
#   2. Modificar, adaptar o crear obras derivadas
#   3. Distribuir, publicar, sublicenciar o transferir a terceros
#   4. Usar para desarrollo de productos competidores
#   5. Realizar ingeniería inversa, descompilar o desensamblar
#   6. Remover o alterar este aviso de propiedad intelectual
#
# El acceso a este código NO otorga ninguna licencia implícita o explícita.
#
# ═══════════════════════════════════════════════════════════════════════════════
# PROTECCIÓN LEGAL
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este software está protegido por:
#
#   • Ley 23 de 1982 - Derechos de Autor (Colombia)
#   • Ley 1915 de 2018 - Modernización Derechos de Autor (Colombia)
#   • Decisión Andina 351 de 1993 - Régimen Común sobre Derecho de Autor
#   • Convenio de Berna para la Protección de Obras Literarias y Artísticas
#   • Tratado OMPI sobre Derecho de Autor (WCT)
#   • Acuerdo ADPIC/TRIPS - Organización Mundial del Comercio
#
# SANCIONES POR INFRACCIÓN:
#   • Civiles: Indemnización por daños y perjuicios (Art. 57, Ley 23/1982)
#   • Penales: Prisión de 4 a 8 años y multa (Art. 271, Código Penal Colombiano)
#
# ═══════════════════════════════════════════════════════════════════════════════
# JURISDICCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
#
# Cualquier disputa será resuelta exclusivamente por los tribunales de
# Bogotá D.C., Colombia, bajo las leyes de la República de Colombia.
#
# ═══════════════════════════════════════════════════════════════════════════════
#
# Para solicitar autorización de uso: carlos-5100@hotmail.com
#
# ═══════════════════════════════════════════════════════════════════════════════



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