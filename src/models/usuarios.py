import bcrypt
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import db
from flask_login import UserMixin
from src.models.servicio import Servicio
from src.models.usuario_servicio import usuario_servicio


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"

    # Definición de columnas
    id_usuario = Column(Integer, primary_key=True)
    ciudad_id = Column(Integer,nullable=False)
    nombre = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    correo = Column(String, nullable=False, unique=True)
    contrasenia = Column(String, nullable=False)
    confirmacion_contrasenia = Column(String, nullable=False)  # Almacena el hash de la contraseña
    profesion = Column(String, nullable=False)
    cedula = Column(BigInteger, nullable=False, unique=True)
    celular = Column(BigInteger, nullable=False)
    ciudad = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    pais_id = Column(Integer, nullable = True)
    validate= Column(Boolean, nullable = True, default = False)
    black_list = Column(Boolean, nullable = True, default = False)


    # Relaciones
    received_notifications = relationship("Notification", foreign_keys='Notification.user_id', back_populates='receiver')
    sent_notifications = relationship("Notification", foreign_keys='Notification.sender_id', back_populates='sender')
    servicios = relationship("Servicio", secondary=usuario_servicio, back_populates="usuarios", lazy='select')
   
    servicios_como_contratante = relationship("Servicio", foreign_keys="[Servicio.id_contratante]", back_populates="contratante")
    servicios_como_contratado = relationship("Servicio", foreign_keys="[Servicio.id_contratado]", back_populates="contratado")
    
    monetizaciones = relationship("MonetizationManagement", back_populates="usuario", cascade="all, delete-orphan")

    calificaciones = db.relationship('ServiceRatings', back_populates='usuario')

    received_feedbacks = relationship("Feedback", back_populates="usuario", cascade="all, delete-orphan",lazy='dynamic')
    # Relación con el modelo Colombia
    ciudad_id = Column(Integer, ForeignKey('colombia.ciudad_id'), nullable=True)
    ciudad = relationship("Colombia", backref="servicios")

    def __init__(self, nombre, apellidos, correo, profesion, cedula, celular, ciudad, validate=False, black_list=False):
        self.nombre = nombre
        self.apellidos = apellidos
        self.ciudad_id = ciudad
        self.correo = correo
        self.profesion = profesion
        self.cedula = cedula
        self.celular = celular
        self.validate = validate
        self.black_list = black_list

    # Métodos para manejar contraseñas
    def set_password(self, password):
        """
        Genera un hash seguro para la contraseña usando bcrypt.
        """
        salt = bcrypt.gensalt()  # Genera un salt único
        self.contrasenia = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')  # Genera el hash y lo guarda

    def check_password(self, password):
        """
        Verifica si la contraseña proporcionada coincide con el hash almacenado.
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.contrasenia.encode('utf-8'))  # Compara el hash

    def get_id(self):
        """
        Retorna el identificador del usuario para Flask-Login.
        """
        return str(self.id_usuario)

    def __repr__(self):
        """
        Representación del objeto Usuario como cadena de texto.
        """
        return f"<Usuario {self.correo}>"
    def set_validate(self, status):
        self.validate = status

    def set_black_list(self, status):
        self.black_list = status