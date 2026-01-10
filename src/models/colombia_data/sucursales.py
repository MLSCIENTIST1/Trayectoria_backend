"""
BizFlow Studio - Modelo de Sucursales
Gestión de sucursales de negocios con personal en JSON
"""

from src.models.database import db
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship


class Sucursal(db.Model):
    """
    Modelo para gestión de sucursales de un negocio.
    Soporta almacenamiento flexible de personal mediante JSON.
    """
    __tablename__ = 'sucursales'
    
    # ==========================================
    # IDENTIFICACIÓN
    # ==========================================
    id_sucursal = sa.Column(sa.Integer, primary_key=True)
    nombre_sucursal = sa.Column(sa.String(100), nullable=False)
    
    # ==========================================
    # UBICACIÓN
    # ==========================================
    direccion = sa.Column(sa.String(200), nullable=True)
    ciudad = sa.Column(sa.String(100), nullable=True)
    departamento = sa.Column(sa.String(100), nullable=True)
    codigo_postal = sa.Column(sa.String(20), nullable=True)
    
    # Coordenadas geográficas (opcional, para futuro)
    latitud = sa.Column(sa.Float, nullable=True)
    longitud = sa.Column(sa.Float, nullable=True)
    
    # ==========================================
    # CONTACTO
    # ==========================================
    telefono = sa.Column(sa.String(20), nullable=True)
    email = sa.Column(sa.String(100), nullable=True)
    
    # ==========================================
    # ESTADO Y CONTROL
    # ==========================================
    activo = sa.Column(sa.Boolean, default=True, nullable=False)
    es_principal = sa.Column(sa.Boolean, default=False, nullable=False)
    
    # ==========================================
    # PERSONAL (JSON)
    # ==========================================
    # Almacena arrays de objetos: [{"nombre": "Ana", "identificacion": "123", "rol": "cajero"}]
    cajeros = sa.Column(
        sa.JSON,
        nullable=False,
        default=list,
        server_default='[]'
    )
    administradores = sa.Column(
        sa.JSON,
        nullable=False,
        default=list,
        server_default='[]'
    )
    
    # ==========================================
    # METADATA
    # ==========================================
    fecha_registro = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ==========================================
    # CLAVE FORÁNEA
    # ==========================================
    negocio_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # ==========================================
    # RELACIÓN
    # ==========================================
    negocio = relationship("Negocio", back_populates="sucursales")
    
    # Productos de esta sucursal
    productos = relationship(
        "ProductoCatalogo",
        foreign_keys="[ProductoCatalogo.sucursal_id]",
        lazy='dynamic'
    )

    # ==========================================
    # MÉTODOS
    # ==========================================
    
    def __init__(self, nombre_sucursal, negocio_id, **kwargs):
        """
        Constructor de sucursal.
        
        Args:
            nombre_sucursal (str): Nombre de la sucursal
            negocio_id (int): ID del negocio al que pertenece
            **kwargs: Campos adicionales
        """
        self.nombre_sucursal = nombre_sucursal
        self.negocio_id = negocio_id
        
        # Campos opcionales
        self.direccion = kwargs.get('direccion')
        self.ciudad = kwargs.get('ciudad')
        self.departamento = kwargs.get('departamento')
        self.codigo_postal = kwargs.get('codigo_postal')
        self.telefono = kwargs.get('telefono')
        self.email = kwargs.get('email')
        self.activo = kwargs.get('activo', True)
        self.es_principal = kwargs.get('es_principal', False)
        
        # Personal
        self.cajeros = kwargs.get('cajeros', [])
        self.administradores = kwargs.get('administradores', [])
    
    def agregar_cajero(self, nombre, identificacion, **extra):
        """
        Agrega un cajero a la sucursal.
        
        Args:
            nombre (str): Nombre del cajero
            identificacion (str): Documento de identidad
            **extra: Datos adicionales (teléfono, email, etc.)
        """
        if self.cajeros is None:
            self.cajeros = []
        
        cajero = {
            "nombre": nombre,
            "identificacion": identificacion,
            **extra
        }
        
        # Evitar duplicados por identificación
        if not any(c.get('identificacion') == identificacion for c in self.cajeros):
            self.cajeros.append(cajero)
            # IMPORTANTE: Marcar como modificado para que SQLAlchemy detecte el cambio en JSON
            sa.orm.attributes.flag_modified(self, 'cajeros')
    
    def remover_cajero(self, identificacion):
        """
        Remueve un cajero de la sucursal.
        
        Args:
            identificacion (str): Documento del cajero a remover
        """
        if self.cajeros:
            self.cajeros = [c for c in self.cajeros if c.get('identificacion') != identificacion]
            sa.orm.attributes.flag_modified(self, 'cajeros')
    
    def agregar_administrador(self, nombre, identificacion, **extra):
        """
        Agrega un administrador a la sucursal.
        
        Args:
            nombre (str): Nombre del administrador
            identificacion (str): Documento de identidad
            **extra: Datos adicionales
        """
        if self.administradores is None:
            self.administradores = []
        
        admin = {
            "nombre": nombre,
            "identificacion": identificacion,
            **extra
        }
        
        if not any(a.get('identificacion') == identificacion for a in self.administradores):
            self.administradores.append(admin)
            sa.orm.attributes.flag_modified(self, 'administradores')
    
    def remover_administrador(self, identificacion):
        """
        Remueve un administrador de la sucursal.
        
        Args:
            identificacion (str): Documento del administrador a remover
        """
        if self.administradores:
            self.administradores = [a for a in self.administradores if a.get('identificacion') != identificacion]
            sa.orm.attributes.flag_modified(self, 'administradores')
    
    def get_total_personal(self):
        """
        Obtiene el total de personal de la sucursal.
        
        Returns:
            int: Total de cajeros + administradores
        """
        cajeros_count = len(self.cajeros) if self.cajeros else 0
        admins_count = len(self.administradores) if self.administradores else 0
        return cajeros_count + admins_count
    
    def to_dict(self, include_products=False):
        """
        Convierte la sucursal a diccionario.
        
        Args:
            include_products (bool): Si incluir conteo de productos
            
        Returns:
            dict: Datos de la sucursal
        """
        data = {
            "id": self.id_sucursal,
            "id_sucursal": self.id_sucursal,
            "nombre_sucursal": self.nombre_sucursal,
            "direccion": self.direccion,
            "ciudad": self.ciudad,
            "departamento": self.departamento,
            "codigo_postal": self.codigo_postal,
            "telefono": self.telefono,
            "email": self.email,
            "activo": self.activo,
            "es_principal": self.es_principal,
            
            # Personal
            "cajeros": self.cajeros if self.cajeros is not None else [],
            "administradores": self.administradores if self.administradores is not None else [],
            "total_personal": self.get_total_personal(),
            
            # Relaciones
            "negocio_id": self.negocio_id,
            
            # Metadata
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
        
        if include_products:
            data["productos_count"] = self.productos.count()
        
        return data
    
    def serialize(self):
        """Alias de to_dict() para compatibilidad."""
        return self.to_dict()
    
    def __repr__(self):
        return f'<Sucursal {self.nombre_sucursal} - Negocio ID {self.negocio_id}>'
    
    def __str__(self):
        return f"{self.nombre_sucursal} ({self.ciudad or 'Sin ciudad'})"