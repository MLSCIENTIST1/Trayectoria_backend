from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import db

class Foto(db.Model):
    __tablename__ = "fotos"

    id_foto = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False)  # Ruta de almacenamiento de la foto
    
    # Asegúrate de que el modelo Etapa use "__tablename__ = 'etapas'" y "id_etapa" como PK
    etapa_id = Column(Integer, ForeignKey('etapas.id_etapa'), nullable=False)

    # Relación con Etapa
    etapa = relationship("Etapa", back_populates="fotos")

    def __repr__(self):
        return f"<Foto {self.url}>"

    def serialize(self):
        return {
            "id_foto": self.id_foto,
            "url": self.url,
            "etapa_id": self.etapa_id
        }