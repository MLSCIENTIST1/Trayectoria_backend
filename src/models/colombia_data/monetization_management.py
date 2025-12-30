from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db


import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Modelo Monetización colombia cargado correctamente.")







class MonetizationManagement(db.Model):
    __tablename__ = "monetization_management"

    id_monetizacion = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario', ondelete='CASCADE'), nullable=False)
    rol_usuario = db.Column(db.String(50), nullable=True)  # Freelancer, Dueño de negocio, etc.

    # Detalles del pago
    plan = db.Column(db.String(50), nullable=False)  # Básico, Premium, Corporativo
    monto_pago = db.Column(db.Float, nullable=False)
    moneda = db.Column(db.String(10), nullable=False)  # COP, USD, etc.
    metodo_pago = db.Column(db.String(50), nullable=True)  # Tarjeta, PayPal, etc.
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

     # Manejo del QR
    codigo_qr = db.Column(db.String(255), nullable=True)  # Código QR único
    estado_qr = db.Column(db.String(50), nullable=True, default="Pendiente")  # Estado del pago QR
    fecha_transaccion_qr = db.Column(db.DateTime, nullable=True)  # Fecha de transacción

    # Control de funciones
    funcionalidades_habilitadas = db.Column(db.Text, nullable=True)  # Ejemplo: "Chat, Contratación"
    duracion_plan = db.Column(db.Integer, nullable=True)  # Duración del plan en días
    fecha_expiracion = db.Column(db.DateTime, nullable=True)  # Fecha en que expira el plan

    # Estado del pago
    estado_pago = db.Column(db.String(50), nullable=False, default="Pendiente")  # Exitoso, Fallido, etc.
    notificacion_pago = db.Column(db.Boolean, default=False, nullable=True)  # True si el usuario fue notificado

    # Relación con usuario
    usuario = relationship("Usuario", back_populates="monetizaciones")