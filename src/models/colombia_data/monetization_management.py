# Importamos Boolean y String que faltaban o daban error
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
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
    
    # ✅ Clave foránea sincronizada con 'usuarios'
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    
    rol_usuario = Column(String(50), nullable=True) 

    # Detalles del pago
    plan = Column(String(50), nullable=False) 
    monto_pago = Column(Float, nullable=False)
    moneda = Column(String(10), nullable=False) 
    metodo_pago = Column(String(50), nullable=True) 
    fecha_pago = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Manejo del QR
    codigo_qr = Column(String(255), nullable=True) 
    estado_qr = Column(String(50), nullable=True, default="Pendiente") 
    fecha_transaccion_qr = Column(DateTime, nullable=True) 

    # Control de funciones
    funcionalidades_habilitadas = Column(Text, nullable=True) 
    duracion_plan = Column(Integer, nullable=True) 
    fecha_expiracion = Column(DateTime, nullable=True) 

    # Estado del pago
    estado_pago = Column(String(50), nullable=False, default="Pendiente") 
    # ✅ Ahora Boolean funcionará porque ya está en el import
    notificacion_pago = Column(Boolean, default=False, nullable=True) 

    # Relación con usuario
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

# Importación diferida
from src.models.usuarios import Usuario