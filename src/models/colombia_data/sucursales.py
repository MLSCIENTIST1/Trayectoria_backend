from src.models.database import db
from datetime import datetime
import sqlalchemy as sa

class Sucursal(db.Model):
    """
    Modelo para la gestión de sucursales de un negocio.
    Incluye almacenamiento flexible de personal mediante JSON.
    """
    __tablename__ = 'sucursales'
    
    # 1. Identificación y Ubicación
    id_sucursal = sa.Column(sa.Integer, primary_key=True)
    nombre_sucursal = sa.Column(sa.String(100), nullable=False)
    direccion = sa.Column(sa.String(200))
    telefono = sa.Column(sa.String(20))
    ciudad = sa.Column(sa.String(100))
    departamento = sa.Column(sa.String(100))
    codigo_postal = sa.Column(sa.String(20))
    
    # 2. Estado y Control
    activo = sa.Column(sa.Boolean, default=True)
    es_principal = sa.Column(sa.Boolean, default=False)
    fecha_registro = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    # 3. Personal (Uso de JSON para flexibilidad en PostgreSQL)
    # Almacena: [{"nombre": "Ana", "identificacion": "123"}, ...]
    cajeros = sa.Column(sa.JSON, default=list, server_default='[]')
    administradores = sa.Column(sa.JSON, default=list, server_default='[]')
    
    # 4. Relación con Negocio
    # IMPORTANTE: Apunta a 'negocios.id_negocio', que es la PK corregida en negocio.py
    negocio_id = sa.Column(sa.Integer, sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'), nullable=False)

    def to_dict(self):
        """Convierte el modelo a diccionario para respuestas JSON de la API"""
        return {
            "id": self.id_sucursal,
            "id_sucursal": self.id_sucursal,
            "nombre_sucursal": self.nombre_sucursal,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "ciudad": self.ciudad,
            "departamento": self.departamento,
            "codigo_postal": self.codigo_postal,
            "activo": self.activo,
            "es_principal": self.es_principal,
            "cajeros": self.cajeros if self.cajeros is not None else [],
            "administradores": self.administradores if self.administradores is not None else [],
            "negocio_id": self.negocio_id,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None
        }

    def __repr__(self):
        return f'<Sucursal {self.nombre_sucursal} - Negocio ID {self.negocio_id}>'