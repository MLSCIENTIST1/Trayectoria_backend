from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Modelo ServiceRatings cargado correctamente.")

class ServiceRatings(db.Model):
    __tablename__ = "service_ratings"

    # Columnas principales
    id_rating = Column(Integer, primary_key=True)
    servicio_id = Column(Integer, ForeignKey('servicio.id_servicio', ondelete='CASCADE'), nullable=False)
    
    # ✅ CORRECCIÓN: Apuntar a 'usuarios.id_usuario' (plural)
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)

    # Calificaciones (Contratante -> Contratado y viceversa)
    calificacion_recived_contratante1 = Column(Integer, nullable=True)
    razon_contratante1 = Column(String(255), nullable=True)

    calificacion_recived_contratante2 = Column(Integer, nullable=True)
    razon_contratante2 = Column(String(255), nullable=True)

    calificacion_recived_contratante3 = Column(Integer, nullable=True)
    razon_contratante3 = Column(String(255), nullable=True)

    id_calificativo_como_contratante = Column(Integer, nullable=True)
    id_calificativo_como_contratado = Column(Integer, nullable=True)
    volveria_a_contratar = Column(Boolean, nullable=True)
    volveria_a_ser_contratado = Column(Boolean, nullable=True)

    calificacion_recived_contratado1 = Column(Integer, nullable=True)
    razon_contratado1 = Column(String(255), nullable=True)

    calificacion_recived_contratado2 = Column(Integer, nullable=True)
    razon_contratado2 = Column(String(255), nullable=True)

    calificacion_recived_contratado3 = Column(Integer, nullable=True)
    razon_contratado3 = Column(String(255), nullable=True)

    # QR o Manual
    qr_o_manual = Column(String(10), nullable=True)
    id_qr_usado = Column(String(50), nullable=True)

    # Duración del contrato
    horas = Column(Integer, nullable=True)
    dias = Column(Integer, nullable=True)
    meses = Column(Integer, nullable=True)
    duracion_total = Column(String(50), nullable=True)
    
    puntaje_por_labor = Column(Integer, nullable=True)
    resultado_contratante = Column(Float, nullable=True)
    resultado_contratado = Column(Float, nullable=True)

    comentary_hired_employer = Column(Text, nullable=True)
    comentary_employer_hired = Column(Text, nullable=True)

    # Fecha de creación y modificación
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_modificacion = Column(DateTime, onupdate=datetime.utcnow, nullable=True)

    # Relación con el puntaje global (ServiceOverallScores)
    overall_score_id = Column(Integer, ForeignKey('service_overall_scores.id_score', ondelete='CASCADE'), nullable=True)
    overall_score = relationship("ServiceOverallScores", back_populates="ratings")

    # Relación con calificativos
    calificativo_id = Column(Integer, ForeignKey('service_qualifiers.id_qualifier'))
    calificativo = relationship('ServiceQualifiers', back_populates='ratings', lazy='joined')

    # ✅ Relaciones existentes sincronizadas
    usuario = relationship("Usuario", back_populates="calificaciones")
    servicio = relationship("Servicio", back_populates="calificaciones")

    def serialize(self):
        return {
            "id_rating": self.id_rating,
            "servicio_id": self.servicio_id,
            "usuario_id": self.usuario_id,
            "resultado_contratante": self.resultado_contratante,
            "resultado_contratado": self.resultado_contratado,
            "fecha": self.fecha_creacion.isoformat()
        }

# Importaciones diferidas
from src.models.usuarios import Usuario
from src.models.servicio import Servicio