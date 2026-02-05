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
BizFlow Studio - Modelo de Usuario
Optimizado para Flask-Login y autenticación segura
"""

import bcrypt
from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.models.database import db
from flask_login import UserMixin

# Importar tabla de asociación (debe existir en usuario_servicio.py)
from src.models.usuario_servicio import usuario_servicio


class Usuario(db.Model, UserMixin):
    """
    Modelo de Usuario con soporte completo para Flask-Login
    y gestión de sesiones seguras.
    """
    __tablename__ = "usuarios"

    # ==========================================
    # COLUMNAS PRINCIPALES
    # ==========================================
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    correo = Column(String(100), nullable=False, unique=True, index=True)
    contrasenia = Column(String(255), nullable=False)  # Hash bcrypt
    confirmacion_contrasenia = Column(String(255), nullable=False)
    profesion = Column(String(100), nullable=False)
    cedula = Column(BigInteger, nullable=False, unique=True, index=True)
    celular = Column(BigInteger, nullable=False)
    foto_url = Column(String(500), nullable=True)  # ← NUEVO: URL de foto de perfil (Cloudinary)
    
    # ==========================================
    # ESTADO Y VALIDACIÓN
    # ==========================================
    active = Column(Boolean, default=True, nullable=False)
    validate = Column(Boolean, default=False, nullable=False)
    black_list = Column(Boolean, default=False, nullable=False)
    
    # ==========================================
    # UBICACIÓN
    # ==========================================
    pais_id = Column(Integer, nullable=True)
    ciudad_id = Column(Integer, ForeignKey('colombia.ciudad_id'), nullable=True)
    
    # ==========================================
    # METADATA (IMPORTANTE PARA SESIONES)
    # ==========================================
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)  # CRÍTICO para tracking de sesiones
    
    # ==========================================
    # RELACIONES
    # ==========================================
    
    # Ciudad
    ciudad_rel = relationship("Colombia", backref="usuarios_en_ciudad")
    
    # Notificaciones
    received_notifications = relationship(
        "Notification", 
        foreign_keys='Notification.user_id', 
        back_populates='receiver',
        cascade="all, delete-orphan"
    )
    sent_notifications = relationship(
        "Notification", 
        foreign_keys='Notification.sender_id', 
        back_populates='sender',
        cascade="all, delete-orphan"
    )
    
    # Servicios (muchos a muchos)
    servicios = relationship(
        "Servicio", 
        secondary=usuario_servicio, 
        back_populates="usuarios", 
        lazy='select'
    )
    
    # Servicios como contratante/contratado
    servicios_como_contratante = relationship(
        "Servicio", 
        foreign_keys="[Servicio.id_contratante]", 
        back_populates="contratante"
    )
    servicios_como_contratado = relationship(
        "Servicio", 
        foreign_keys="[Servicio.id_contratado]", 
        back_populates="contratado"
    )
    
    # Monetización
    monetizaciones = relationship(
        "MonetizationManagement", 
        back_populates="usuario", 
        cascade="all, delete-orphan"
    )
    
    # Calificaciones
    calificaciones = relationship(
        'ServiceRatings', 
        back_populates='usuario',
        cascade="all, delete-orphan"
    )
    
    # Feedbacks
    feedbacks = relationship(
        "Feedback", 
        back_populates="usuario", 
        cascade="all, delete-orphan"
    )

    # ==========================================
    # CONSTRUCTOR
    # ==========================================
    def __init__(self, nombre, apellidos, correo, profesion, cedula, celular, 
                 ciudad=None, validate=False, black_list=False):
        self.nombre = nombre
        self.apellidos = apellidos
        self.correo = correo.lower().strip()  # Normalizar correo
        self.profesion = profesion
        self.cedula = cedula
        self.celular = celular
        self.ciudad_id = ciudad
        self.validate = validate
        self.black_list = black_list
        self.active = True
        self.created_at = datetime.utcnow()

    # ==========================================
    # MÉTODOS DE AUTENTICACIÓN (CRÍTICOS)
    # ==========================================
    
    def set_password(self, password):
        """
        Genera un hash bcrypt y lo asigna a las columnas de contraseña.
        
        Args:
            password (str): Contraseña en texto plano
        """
        if not password or len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds es un buen balance
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        self.contrasenia = hashed
        self.confirmacion_contrasenia = hashed

    def check_password(self, password):
        """
        Compara una contraseña en texto plano contra el hash almacenado.
        CRÍTICO para el login.
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            bool: True si coincide, False si no
        """
        if not password or not self.contrasenia:
            return False
        
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                self.contrasenia.encode('utf-8')
            )
        except Exception as e:
            # Log del error pero no revelar detalles al usuario
            import logging
            logging.error(f"Error verificando password para {self.correo}: {e}")
            return False

    # ==========================================
    # MÉTODOS DE FLASK-LOGIN (REQUERIDOS)
    # ==========================================
    
    def get_id(self):
        """
        CRÍTICO: Flask-Login usa este método para obtener el ID del usuario.
        DEBE retornar un string.
        
        Returns:
            str: ID del usuario como string
        """
        return str(self.id_usuario)
    
    @property
    def is_active(self):
        """
        CRÍTICO: Flask-Login verifica este método para saber si el usuario
        puede autenticarse.
        
        Returns:
            bool: True si el usuario está activo
        """
        return self.active and not self.black_list
    
    @property
    def is_authenticated(self):
        """
        CRÍTICO: Flask-Login verifica si el usuario está autenticado.
        
        Returns:
            bool: Siempre True para usuarios reales
        """
        return True
    
    @property
    def is_anonymous(self):
        """
        CRÍTICO: Flask-Login verifica si es un usuario anónimo.
        
        Returns:
            bool: Siempre False para usuarios reales
        """
        return False

    # ==========================================
    # MÉTODOS DE UTILIDAD
    # ==========================================
    
    def update_last_login(self):
        """
        Actualiza el timestamp de último login.
        Llamar después de un login exitoso.
        """
        self.last_login = datetime.utcnow()
    
    def to_dict(self, include_sensitive=False):
        """
        Serializa el usuario a un diccionario.
        
        Args:
            include_sensitive (bool): Si True, incluye información sensible
            
        Returns:
            dict: Datos del usuario
        """
        data = {
            "id": self.id_usuario,
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "apellidos": self.apellidos,
            "correo": self.correo,
            "telefono": self.celular,
            "profesion": self.profesion,
            "activo": self.active,
            "validado": self.validate,
            "ciudad_id": self.ciudad_id,
            "foto_url": self.foto_url,  # ← NUEVO: incluir foto_url en serialización
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data["cedula"] = self.cedula
            data["last_login"] = self.last_login.isoformat() if self.last_login else None
            data["updated_at"] = self.updated_at.isoformat() if self.updated_at else None
        
        return data
    
    def serialize(self):
        """Alias de to_dict() para compatibilidad"""
        return self.to_dict()

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    
    def __repr__(self):
        return f"<Usuario {self.correo} (ID: {self.id_usuario})>"
    
    def __str__(self):
        return f"{self.nombre} {self.apellidos}"