from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship
from src.models.database import db

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Modelo ServiceQualifiers cargado correctamente.")

class ServiceQualifiers(db.Model):
    __tablename__ = "service_qualifiers"

    id_qualifier = Column(Integer, primary_key=True)
    nombre_calificativo = Column(String(50), nullable=False, unique=True)  # Ejemplo: "Excelente", "Bueno"
    descripcion = Column(String(255), nullable=True)
    calificativo_mas_usado = Column(Boolean, nullable=True)
    calificativo_menos_usado = Column(Boolean, nullable=True)
    peso_calificativo = Column(Float, nullable=True)

    # Relación bidireccional con ServiceRatings
    ratings = relationship('ServiceRatings', back_populates='calificativo')

    def __repr__(self):
        return f"<ServiceQualifier {self.nombre_calificativo}>"

    def serialize(self):
        return {
            "id_qualifier": self.id_qualifier,
            "nombre": self.nombre_calificativo,
            "descripcion": self.descripcion,
            "peso": self.peso_calificativo
        }