

from sqlalchemy import Column, Integer, String, Date, ForeignKey,String, Boolean
from sqlalchemy.orm import relationship
from src.models.database import db

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Modelo ServiceQualifiers cargado correctamente.")









class ServiceQualifiers(db.Model):
    __tablename__ = "service_qualifiers"

    id_qualifier = db.Column(db.Integer, primary_key=True)
    nombre_calificativo = db.Column(db.String(50), nullable=False, unique=True)  # Ejemplo: "Excelente", "Bueno", "Regular", etc.
    descripcion = db.Column(db.String(255), nullable=True)
    calificativo_mas_usado = db.Column(db.Boolean, nullable=True)
    calificativo_menos_usado = db.Column(db.Boolean, nullable=True)
    peso_calificativo = db.Column(db.Float, nullable=True)

    # Relación bidireccional
    ratings = db.relationship('ServiceRatings', back_populates='calificativo')