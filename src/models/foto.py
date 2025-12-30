from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.database import db



class Foto(db.Model):
    __tablename__ = "fotos"

    id_foto = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)  # Ruta de almacenamiento de la foto
    etapa_id = db.Column(Integer, ForeignKey('etapas.id_etapa'), nullable=False)


    def __repr__(self):
       return f"<Foto {self.url}>"
    # Relación con Etapa
    etapa = relationship("Etapa", back_populates="fotos")