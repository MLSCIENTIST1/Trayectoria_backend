from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import db

class Etapa(db.Model):
    __tablename__ = 'etapas'

    id_etapa = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    
    # Esta FK está bien porque la tabla de servicios se llama 'servicio'
    servicio_id = Column(Integer, ForeignKey('servicio.id_servicio'), nullable=False)

    # Relación con Servicio
    servicio = relationship("Servicio", back_populates="etapas")

    # Relaciones con recursos multimedia
    # cascade="all, delete-orphan" asegura que si borras una etapa, se borren sus archivos
    fotos = relationship("Foto", back_populates="etapa", cascade="all, delete-orphan")
    audios = relationship("Audio", back_populates="etapa", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="etapa", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Etapa {self.nombre}>"

    def serialize(self):
        return {
            "id_etapa": self.id_etapa,
            "nombre": self.nombre,
            "servicio_id": self.servicio_id,
            "fotos": [f.serialize() for f in self.fotos],
            "audios": [a.serialize() for a in self.audios],
            "videos": [v.serialize() for v in self.videos]
        }