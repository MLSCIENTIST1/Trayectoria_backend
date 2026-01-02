from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship
from src.models.usuario_servicio import usuario_servicio  # Se importa la tabla intermedia
from src.models.database import db
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Modelo Servicio cargado correctamente.")

class Servicio(db.Model):
    __tablename__ = "servicio"

    # Definición de columnas
    id_servicio = Column(Integer, primary_key=True)
    nombre_servicio = Column(String, nullable=True)
    descripcion = Column(Text, nullable=True) 
    categoria = Column(Text, nullable=True)      
    fecha_solicitud = Column(Date, nullable=True)
    fecha_aceptacion = Column(Date, nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    nombre_contratante = Column(String, nullable=True)
    aditional_service = Column(String(234), nullable=True)
    service_active = Column(Boolean, default=True)
    precio = Column(Float, nullable=True)
    etapas_calificacion = Column(Integer, nullable=True)
    viajar_dentro_pais = Column(Boolean, default=False)
    viajar_fuera_pais = Column(Boolean, default=False)
    domicilios = Column(Boolean, default=False)
    incluye_asesoria = Column(Boolean, default=False)
    requiere_presencia_cliente = Column(Boolean, default=False)
    experiencia_previa = Column(Boolean, default=False)
    facturacion_formal = Column(Boolean, default=False)
    modelos_negocio = Column(String(200), nullable=True)

    # ✅ CORRECCIÓN: Apuntar a 'usuarios.id_usuario' (plural)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    id_contratante = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=True)
    id_contratado = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=True)

    # ✅ CORRECCIÓN DE TYPO: de 'id_contrado' a 'id_contratado'
    contratante = relationship("Usuario", foreign_keys=[id_contratante], back_populates="servicios_como_contratante")
    contratado = relationship("Usuario", foreign_keys=[id_contratado], back_populates="servicios_como_contratado")

    # Relación con usuarios (Muchos a Muchos)
    usuarios = relationship("Usuario", secondary=usuario_servicio, back_populates="servicios")
    
    # Relación con Etapa
    etapas = relationship("Etapa", back_populates="servicio", cascade="all, delete-orphan")

    # Relación con el modelo Colombia
    ciudad_id = Column(Integer, ForeignKey('colombia.ciudad_id'), nullable=True)
    ciudad_rel = relationship("Colombia", backref="ciudad_servicios")

    # Relación con Ratings
    calificaciones = relationship("ServiceRatings", back_populates="servicio")
    overall_scores = relationship("ServiceOverallScores", back_populates="servicio")

    # Métodos CRUD
    @classmethod
    def leer(cls, session, id_servicio):
        return session.query(cls).filter_by(id_servicio=id_servicio).first()

    def actualizar(self, session, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()

    @classmethod
    def eliminar(cls, session, id_servicio):
        servicio = cls.leer(session, id_servicio)
        if servicio:
            session.delete(servicio)
            session.commit()

    def serialize(self):
        return {
            "id_servicio": self.id_servicio,
            "nombre_servicio": self.nombre_servicio,
            "categoria": self.categoria,
            "precio": self.precio,
            "service_active": self.service_active
        }

# Importaciones diferidas para evitar ciclos
from src.models.usuarios import Usuario
from src.models.colombia_data.colombia import Colombia
from src.models.colombia_data.ratings.service_ratings import ServiceRatings