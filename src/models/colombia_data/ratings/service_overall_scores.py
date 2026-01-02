from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Modelo ServiceOverallScores cargado correctamente.")

class ServiceOverallScores(db.Model):
    __tablename__ = "service_overall_scores"

    # Identificador principal
    id_score = Column(Integer, primary_key=True)

    # Clave foránea relacionada con el servicio - Tabla 'servicio' (singular)
    servicio_id = Column(Integer, ForeignKey('servicio.id_servicio', ondelete='CASCADE'), nullable=False)

    # Puntajes
    puntaje_global_servicio = Column(Float, nullable=False)
    puntaje_global_usuario = Column(Float, nullable=True)
    puntaje_global_contratante = Column(Float, nullable=True)
    puntaje_global_contratado = Column(Float, nullable=True)

    # Promedios de duración
    promedio_duracion_horas = Column(Float, nullable=True)
    promedio_duracion_dias = Column(Float, nullable=True)
    promedio_duracion_meses = Column(Float, nullable=True)
    promedio_duracion_total = Column(Float, nullable=True)

    # Calificaciones más comunes
    calificativo_mas_recibido_como_contratante = Column(String(50), nullable=True)
    calificativo_mas_recibido_como_contratado = Column(String(50), nullable=True)

    # Totales
    veces_volverian_a_ser_contratados = Column(Integer, nullable=True)
    veces_volverian_a_ser_contratantes = Column(Integer, nullable=True)
    total_calificaciones_recibidas = Column(Integer, nullable=True)
    total_calificaciones_hechas = Column(Integer, nullable=True)

    # Métodos de conexión
    cantidad_veces_qr = Column(Integer, nullable=True)
    cantidad_veces_manual = Column(Integer, nullable=True)

    # Coincidencias en calificaciones como contratante
    coincidencias_calificacion_1_contratante = Column(Integer, nullable=True)
    coincidencias_calificacion_2_contratante = Column(Integer, nullable=True)
    coincidencias_calificacion_3_contratante = Column(Integer, nullable=True)
    porcentaje_coincidencia_contratante = Column(Float, nullable=True)
    peso_calificacion_contratante = Column(Float, nullable=True)

    # Coincidencias en calificaciones como contratado
    coincidencias_calificacion_1_contratado = Column(Integer, nullable=True)
    coincidencias_calificacion_2_contratado = Column(Integer, nullable=True)
    coincidencias_calificacion_3_contratado = Column(Integer, nullable=True)
    porcentaje_coincidencia_contratado = Column(Float, nullable=True)
    peso_calificacion_contratado = Column(Float, nullable=True)

    # Calificaciones positivas y negativas
    suma_calificaciones_positivas = Column(Integer, nullable=True)
    suma_calificaciones_negativas = Column(Integer, nullable=True)

    # Peso de las calificaciones según usuarios verificados
    peso_calificacion_verificado = Column(Float, nullable=True)
    peso_calificacion_no_verificado = Column(Float, nullable=True)

    # Cantidad de calificaciones
    numero_calificaciones = Column(Integer, nullable=False)

    # Fecha de última actualización
    fecha_ultima_actualizacion = Column(DateTime, onupdate=datetime.utcnow, nullable=True)

    # Relaciones
    ratings = relationship("ServiceRatings", back_populates="overall_score")
    servicio = relationship("Servicio", back_populates="overall_scores")

    def serialize(self):
        return {
            "id_score": self.id_score,
            "servicio_id": self.servicio_id,
            "puntaje_global_servicio": self.puntaje_global_servicio,
            "numero_calificaciones": self.numero_calificaciones,
            "ultima_actualizacion": self.fecha_ultima_actualizacion.isoformat() if self.fecha_ultima_actualizacion else None
        }

# Importación diferida para evitar ciclos
from src.models.servicio import Servicio
from src.models.colombia_data.ratings.service_ratings import ServiceRatings