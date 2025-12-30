from sqlalchemy import Column, Integer, String, Date, ForeignKey,String, Boolean
from sqlalchemy.orm import relationship
from src.models.usuario_servicio import usuario_servicio  # Se importa la tabla intermedia
from src.models.database import db
from src.models.colombia_data.ratings.service_ratings import ServiceRatings
 
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Modelo Servicio cargado correctamente.")

class Servicio(db.Model):
    __tablename__ = "servicio"

    # Definición de columnas
    id_servicio = Column(Integer, primary_key=True)
    nombre_servicio = Column(String, nullable=True)
    descripcion = db.Column(db.Text, nullable=True) 
    categoria = db.Column(db.Text, nullable=True)      
    fecha_solicitud = Column(Date, nullable=True)
    fecha_aceptacion = Column(Date, nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    nombre_contratante = Column(String, nullable=True)
    aditional_service = Column(String(234), nullable=True)
    service_active = Column(Boolean, default=True)
    precio = db.Column(db.Float, nullable=True)
    etapas_calificacion = db.Column(db.Integer, nullable=True)
    viajar_dentro_pais = db.Column(db.Boolean, default=False)
    viajar_fuera_pais = db.Column(db.Boolean, default=False)
    domicilios = db.Column(db.Boolean, default=False)
    incluye_asesoria = db.Column(db.Boolean, default=False)
    requiere_presencia_cliente = db.Column(db.Boolean, default=False)
    experiencia_previa = db.Column(db.Boolean, default=False)
    facturacion_formal = db.Column(db.Boolean, default=False)
    modelos_negocio = db.Column(db.String(200), nullable=True)

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_contratante = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=True)
    id_contratado = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=True)  # Nuevo campo

    contratante = relationship("Usuario", foreign_keys=[id_contratante], back_populates="servicios_como_contratante")
    contratado = relationship("Usuario", foreign_keys=[id_contratado], back_populates="servicios_como_contratado")

    # Relación con usuarios
    usuarios = relationship("Usuario", secondary=usuario_servicio, back_populates="servicios")
   
    #Relaciones con media_storage
    etapas = relationship("Etapa", back_populates="servicio", cascade="all, delete-orphan")

    # Relación con el modelo Colombia
    ciudad_id = Column(Integer, ForeignKey('colombia.ciudad_id'), nullable=True)
    ciudad = relationship("Colombia", backref="ciudad_servicios")

     # Relación con el modelo Ratings
    calificaciones = db.relationship("ServiceRatings", back_populates="servicio")
    overall_scores = db.relationship("ServiceOverallScores", back_populates="servicio")
    

    # CRUD
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