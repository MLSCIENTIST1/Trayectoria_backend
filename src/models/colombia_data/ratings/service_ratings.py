from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime  # Corrección aquí: importar datetime para usar utcnow
from src.models.database import db

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Modelo ServiceRatings cargado correctamente.")

class ServiceRatings(db.Model):
    __tablename__ = "service_ratings"

    # Columnas principales
    id_rating = db.Column(db.Integer, primary_key=True)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio.id_servicio', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario', ondelete='CASCADE'), nullable=False)

    # Calificaciones (Contratante -> Contratado y viceversa)
    calificacion_recived_contratante1 = db.Column(db.Integer, nullable=True)
    razon_contratante1 = db.Column(db.String(255), nullable=True)

    calificacion_recived_contratante2 = db.Column(db.Integer, nullable=True)
    razon_contratante2 = db.Column(db.String(255), nullable=True)

    calificacion_recived_contratante3 = db.Column(db.Integer, nullable=True)
    razon_contratante3 = db.Column(db.String(255), nullable=True)

    id_calificativo_como_contratante = db.Column(db.Integer, nullable=True)  # ID del calificativo como contratante
    id_calificativo_como_contratado = db.Column(db.Integer, nullable=True)  # ID del calificativo como contratado
    volveria_a_contratar = db.Column(db.Boolean, nullable=True)  # True/False para volver a contratar
    volveria_a_ser_contratado = db.Column(db.Boolean, nullable=True)  # True/False para volver a ser contratado

    calificacion_recived_contratado1 = db.Column(db.Integer, nullable=True)
    razon_contratado1 = db.Column(db.String(255), nullable=True)

    calificacion_recived_contratado2 = db.Column(db.Integer, nullable=True)
    razon_contratado2 = db.Column(db.String(255), nullable=True)

    calificacion_recived_contratado3 = db.Column(db.Integer, nullable=True)
    razon_contratado3 = db.Column(db.String(255), nullable=True)

    # QR o Manual
    qr_o_manual = db.Column(db.String(10), nullable=True)  # Si fue QR o Manual
    id_qr_usado = db.Column(db.String(50), nullable=True)  # ID del QR usado (si aplica)

    # Duración del contrato
    horas = db.Column(db.Integer, nullable=True)
    dias = db.Column(db.Integer, nullable=True)
    meses = db.Column(db.Integer, nullable=True)
    duracion_total = db.Column(db.String(50), nullable=True)
    
    puntaje_por_labor = db.Column(db.Integer, nullable=True)  # Cálculo individual de calificaciones
    resultado_contratante = db.Column(db.Float, nullable=True)  # Resultado final como contratante
    resultado_contratado = db.Column(db.Float, nullable=True)  # Resultado final como contratado

    comentary_hired_employer = db.Column(db.String, nullable=True)  # Comentario del contratado
    comentary_employer_hired = db.Column(db.String, nullable=True)  # Comentario del contratante

    # Fecha de creación y modificación
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_modificacion = db.Column(db.DateTime, onupdate=datetime.utcnow, nullable=True)

    # Relación con el puntaje global (ServiceOverallScores)
    overall_score_id = db.Column(db.Integer, db.ForeignKey('service_overall_scores.id_score', ondelete='CASCADE'), nullable=True)
    overall_score = db.relationship("ServiceOverallScores", back_populates="ratings")

    # Relación con calificativos
    calificativo_id = db.Column(db.Integer, db.ForeignKey('service_qualifiers.id_qualifier'))
    calificativo = db.relationship('ServiceQualifiers', back_populates='ratings', lazy='joined')

    # Relaciones existentes
    usuario = db.relationship("Usuario", back_populates="calificaciones")
    servicio = db.relationship("Servicio", back_populates="calificaciones")