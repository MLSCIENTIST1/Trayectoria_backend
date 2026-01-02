from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import db

class Audio(db.Model):
    __tablename__ = 'audios'

    id_audio = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False)
    etapa_id = Column(Integer, ForeignKey('etapas.id_etapa'), nullable=False)

    # Relación con Etapa
    etapa = relationship("Etapa", back_populates="audios")

    def __repr__(self):
        return f"<Audio {self.url}>"

    def serialize(self):
        return {
            "id_audio": self.id_audio,
            "url": self.url,
            "etapa_id": self.etapa_id
        }