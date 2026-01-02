from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Feedback(db.Model):
    __tablename__ = "feedback"

    id_feedback = Column(Integer, primary_key=True)
    # FK corregida a 'usuarios'
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=True)
    
    rol_usuario = Column(String(50), nullable=True)
    tipo_feedback = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=False)
    fecha_envio = Column(DateTime, default=datetime.utcnow, nullable=False)
    estado = Column(String(50), nullable=False, default="Pendiente")
    prioridad = Column(String(50), nullable=True)

    # El nombre en back_populates debe existir en la clase Usuario
    usuario = relationship("Usuario", back_populates="feedbacks", lazy="joined")

    def serialize(self):
        return {
            "id_feedback": self.id_feedback,
            "tipo": self.tipo_feedback,
            "descripcion": self.descripcion,
            "estado": self.estado,
            "fecha": self.fecha_envio.isoformat()
        }

from src.models.usuarios import Usuario