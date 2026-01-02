from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Modelo Feedback cargado correctamente.")

class Feedback(db.Model):
    __tablename__ = "feedback"

    id_feedback = Column(Integer, primary_key=True)
    
    # ✅ CORRECCIÓN: Apuntar a 'usuarios.id_usuario' (plural)
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=True)
    
    rol_usuario = Column(String(50), nullable=True)  # Rol del usuario: Contratante/Contratado
    tipo_feedback = Column(String(50), nullable=False)  # Tipo: Sugerencia, Error, Queja
    descripcion = Column(Text, nullable=False)  # Contenido del feedback

    fecha_envio = Column(DateTime, default=datetime.utcnow, nullable=False)
    estado = Column(String(50), nullable=False, default="Pendiente")
    prioridad = Column(String(50), nullable=True)

    # ✅ CORRECCIÓN: Asegurar que back_populates coincida con la relación en Usuario
    usuario = relationship("Usuario", back_populates="feedbacks", lazy="joined")

    def serialize(self):
        return {
            "id_feedback": self.id_feedback,
            "tipo": self.tipo_feedback,
            "descripcion": self.descripcion,
            "estado": self.estado,
            "fecha": self.fecha_envio.isoformat()
        }

# Importación al final para evitar ciclos
from src.models.usuarios import Usuario