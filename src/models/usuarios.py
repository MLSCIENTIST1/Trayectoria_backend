import bcrypt
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import db
from flask_login import UserMixin
from src.models.usuario_servicio import usuario_servicio

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"

    # 1. Columnas Principales
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    correo = Column(String, nullable=False, unique=True)
    contrasenia = Column(String, nullable=False)
    # Nota: confirmacion_contrasenia suele ser temporal, pero si la DB la exige, la mantenemos
    confirmacion_contrasenia = Column(String, nullable=False) 
    profesion = Column(String, nullable=False)
    cedula = Column(BigInteger, nullable=False, unique=True)
    celular = Column(BigInteger, nullable=False)
    
    # 2. Estado y Validación
    active = Column(Boolean, default=True)
    validate = Column(Boolean, default=False)
    black_list = Column(Boolean, default=False)
    pais_id = Column(Integer, nullable=True)

    # 3. Relación con Ciudad (Tabla Colombia)
    # Corregido: Una sola definición para la FK y la relación
    ciudad_id = Column(Integer, ForeignKey('colombia.ciudad_id'), nullable=True)
    ciudad_rel = relationship("Colombia", backref="usuarios_en_ciudad")

    # 4. Otras Relaciones
    received_notifications = relationship("Notification", foreign_keys='Notification.user_id', back_populates='receiver')
    sent_notifications = relationship("Notification", foreign_keys='Notification.sender_id', back_populates='sender')
    
    # Relación muchos a muchos con Servicios
    servicios = relationship("Servicio", secondary=usuario_servicio, back_populates="usuarios", lazy='select')
    
    # Relaciones específicas de contratos
    servicios_como_contratante = relationship("Servicio", foreign_keys="[Servicio.id_contratante]", back_populates="contratante")
    servicios_como_contratado = relationship("Servicio", foreign_keys="[Servicio.id_contratado]", back_populates="contratado")
    
    monetizaciones = relationship("MonetizationManagement", back_populates="usuario", cascade="all, delete-orphan")
    calificaciones = relationship('ServiceRatings', back_populates='usuario')
    received_feedbacks = relationship("Feedback", back_populates="usuario", cascade="all, delete-orphan", lazy='dynamic')

    def __init__(self, nombre, apellidos, correo, profesion, cedula, celular, ciudad, validate=False, black_list=False):
        self.nombre = nombre
        self.apellidos = apellidos
        self.correo = correo
        self.profesion = profesion
        self.cedula = cedula
        self.celular = celular
        self.ciudad_id = ciudad # Aquí pasamos el ID obtenido de la tabla Colombia
        self.validate = validate
        self.black_list = black_list

    # --- MÉTODOS DE SEGURIDAD (CRUCIALES) ---

    def set_password(self, password):
        """Genera un hash bcrypt y lo asigna a la contraseña y su confirmación."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        self.contrasenia = hashed
        self.confirmacion_contrasenia = hashed # Para evitar error de Not Null en la DB

    def check_password(self, password):
        """Compara texto plano contra el hash almacenado."""
        if not self.contrasenia:
            return False
        # bcrypt.checkpw(password_en_bytes, hash_en_bytes)
        return bcrypt.checkpw(password.encode('utf-8'), self.contrasenia.encode('utf-8'))

    def get_id(self):
        return str(self.id_usuario)

    def __repr__(self):
        return f"<Usuario {self.correo}>"