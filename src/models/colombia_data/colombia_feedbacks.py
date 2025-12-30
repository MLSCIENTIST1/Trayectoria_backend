from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Modelo Feedback cargado correctamente.")

class Feedback(db.Model):
    __tablename__ = "feedback"

    id_feedback = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario', ondelete='CASCADE'), nullable=True)  # Usuario que envió el feedback
    rol_usuario = db.Column(db.String(50), nullable=True)  # Rol del usuario: Contratante/Contratado

    tipo_feedback = db.Column(db.String(50), nullable=False)  # Tipo de feedback: Sugerencia, Error, Queja
    descripcion = db.Column(db.Text, nullable=False)  # Contenido del feedback

    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Fecha y hora de envío
    estado = db.Column(db.String(50), nullable=False, default="Pendiente")  # Estado actual del feedback
    prioridad = db.Column(db.String(50), nullable=True)  # Opcional: Nivel de prioridad

    usuario = relationship("Usuario", back_populates="received_feedbacks", lazy="joined")
    