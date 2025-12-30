from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Modelo ServiceOverallScores cargado correctamente.")

class ServiceOverallScores(db.Model):
    __tablename__ = "service_overall_scores"

    # Identificador principal
    id_score = db.Column(db.Integer, primary_key=True)

    # Clave foránea relacionada con el servicio
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio.id_servicio', ondelete='CASCADE'), nullable=False)

    # Puntajes
    puntaje_global_servicio = db.Column(db.Float, nullable=False)
    puntaje_global_usuario = db.Column(db.Float, nullable=True)
    puntaje_global_contratante = db.Column(db.Float, nullable=True)
    puntaje_global_contratado = db.Column(db.Float, nullable=True)

    # Promedios de duración
    promedio_duracion_horas = db.Column(db.Float, nullable=True)
    promedio_duracion_dias = db.Column(db.Float, nullable=True)
    promedio_duracion_meses = db.Column(db.Float, nullable=True)
    promedio_duracion_total = db.Column(db.Float, nullable=True)

    # Calificaciones más comunes
    calificativo_mas_recibido_como_contratante = db.Column(db.String(50), nullable=True)
    calificativo_mas_recibido_como_contratado = db.Column(db.String(50), nullable=True)

    # Totales
    veces_volverian_a_ser_contratados = db.Column(db.Integer, nullable=True)
    veces_volverian_a_ser_contratantes = db.Column(db.Integer, nullable=True)
    total_calificaciones_recibidas = db.Column(db.Integer, nullable=True)
    total_calificaciones_hechas = db.Column(db.Integer, nullable=True)

    # Métodos de conexión
    cantidad_veces_qr = db.Column(db.Integer, nullable=True)
    cantidad_veces_manual = db.Column(db.Integer, nullable=True)

    # Coincidencias en calificaciones como contratante
    coincidencias_calificacion_1_contratante = db.Column(db.Integer, nullable=True)
    coincidencias_calificacion_2_contratante = db.Column(db.Integer, nullable=True)
    coincidencias_calificacion_3_contratante = db.Column(db.Integer, nullable=True)
    porcentaje_coincidencia_contratante = db.Column(db.Float, nullable=True)
    peso_calificacion_contratante = db.Column(db.Float, nullable=True)

    # Coincidencias en calificaciones como contratado
    coincidencias_calificacion_1_contratado = db.Column(db.Integer, nullable=True)
    coincidencias_calificacion_2_contratado = db.Column(db.Integer, nullable=True)
    coincidencias_calificacion_3_contratado = db.Column(db.Integer, nullable=True)
    porcentaje_coincidencia_contratado = db.Column(db.Float, nullable=True)
    peso_calificacion_contratado = db.Column(db.Float, nullable=True)

    # Calificaciones positivas y negativas
    suma_calificaciones_positivas = db.Column(db.Integer, nullable=True)
    suma_calificaciones_negativas = db.Column(db.Integer, nullable=True)

    # Peso de las calificaciones según usuarios verificados
    peso_calificacion_verificado = db.Column(db.Float, nullable=True)
    peso_calificacion_no_verificado = db.Column(db.Float, nullable=True)

    # Cantidad de calificaciones
    numero_calificaciones = db.Column(db.Integer, nullable=False)

    # Fecha de última actualización
    fecha_ultima_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow, nullable=True)

    # Relaciones
    ratings = db.relationship("ServiceRatings", back_populates="overall_score")
    servicio = db.relationship("Servicio", back_populates="overall_scores")