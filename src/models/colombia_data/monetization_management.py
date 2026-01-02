from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Modelo Monetización colombia cargado correctamente.")

class MonetizationManagement(db.Model):
    __tablename__ = "monetization_management"

    id_monetizacion = Column(Integer, primary_key=True)
    
    # ✅ CORRECCIÓN: Se cambia 'usuario.id_usuario' por 'usuarios.id_usuario'
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    
    rol_usuario = Column(String(50), nullable=True)  # Freelancer, Dueño de negocio, etc.

    # Detalles del pago
    plan = Column(String(50), nullable=False)  # Básico, Premium, Corporativo
    monto_pago = Column(Float, nullable=False)
    moneda = Column(String(10), nullable=False)  # COP, USD, etc.
    metodo_pago = Column(String(50), nullable=True)  # Tarjeta, PayPal, etc.
    fecha_pago = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Manejo del QR
    codigo_qr = Column(String(255), nullable=True)  # Código QR único
    estado_qr = Column(String(50), nullable=True, default="Pendiente")  # Estado del pago QR
    fecha_transaccion_qr = Column(DateTime, nullable=True)  # Fecha de transacción

    # Control de funciones
    funcionalidades_habilitadas = Column(Text, nullable=True)  # Ejemplo: "Chat, Contratación"
    duracion_plan = Column(Integer, nullable=True)  # Duración del plan en días
    fecha_expiracion = Column(DateTime, nullable=True)  # Fecha en que expira el plan

    # Estado del pago
    estado_pago = Column(String(50), nullable=False, default="Pendiente")  # Exitoso, Fallido, etc.
    notificacion_pago = Column(Boolean, default=False, nullable=True)  # True si el usuario fue notificado

    # ✅ Relación con usuario corregida
    usuario = relationship("Usuario", back_populates="monetizaciones")

    def serialize(self):
        return {
            "id_monetizacion": self.id_monetizacion,
            "plan": self.plan,
            "monto": self.monto_pago,
            "moneda": self.moneda,
            "estado": self.estado_pago,
            "fecha_expiracion": self.fecha_expiracion.isoformat() if self.fecha_expiracion else None
        }

# Importación diferida para evitar ciclos
from src.models.usuarios import Usuario