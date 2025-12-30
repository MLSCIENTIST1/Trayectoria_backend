from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import db

class Etapa(db.Model):
    __tablename__ = 'etapas'

    id_etapa = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio.id_servicio'), nullable=False)

    
    
    # Relación con Servicio
    servicio = relationship("Servicio", back_populates="etapas")

    # Relación con recursos multimedia
    fotos = relationship("Foto", back_populates="etapa", cascade="all, delete-orphan")
    audios = relationship("Audio", back_populates="etapa", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="etapa", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Etapa {self.nombre}>"