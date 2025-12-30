from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import db

class Audio(db.Model):
    __tablename__ = 'audios'

    id_audio = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    etapa_id = db.Column(db.Integer, db.ForeignKey('etapas.id_etapa'), nullable=False)

    def __repr__(self):
        return f"<Audio {self.url}>"
    # Relación con Etapa
    etapa = relationship("Etapa", back_populates="audios")