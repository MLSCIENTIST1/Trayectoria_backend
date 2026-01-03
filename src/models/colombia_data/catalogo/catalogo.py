from src.models.database import db
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship

class ProductoCatalogo(db.Model):
    """
    Modelo especializado para la gestión de inventarios y catálogos 
    dentro del ecosistema BizFlow Studio.
    Implementa la lógica de multi-tenencia vinculando cada producto a un negocio y sucursal.
    """
    __tablename__ = 'productos_catalogo'

    # 1. Identificación Única
    id_producto = sa.Column(sa.Integer, primary_key=True)
    
    # 2. Información del Producto (Visualización en Frontend)
    nombre = sa.Column(sa.String(150), nullable=False)
    descripcion = sa.Column(sa.Text, nullable=True)
    # Se usa String para el precio para soportar formatos regionales ($ 130.000)
    precio = sa.Column(sa.String(50), nullable=False) 
    imagen_url = sa.Column(sa.String(255), nullable=True, default='../../assets/css/electromechanics/imgs/Rodar.png')
    categoria = sa.Column(sa.String(100), nullable=True)
    
    # 3. Control de Inventario y Estado
    stock = sa.Column(sa.Integer, default=0)
    activo = sa.Column(sa.Boolean, default=True)
    fecha_creacion = sa.Column(sa.DateTime, default=datetime.utcnow)

    # 4. LLAVES FORÁNEAS (Multi-tenencia)
    # Vincula el producto a un negocio específico (Ej: Rodar Ledger)
    negocio_id = sa.Column(sa.Integer, sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'), nullable=False)
    
    # Vincula el producto a una sucursal específica (Sede Principal, etc.)
    sucursal_id = sa.Column(sa.Integer, sa.ForeignKey('sucursales.id_sucursal', ondelete='CASCADE'), nullable=False)

    # 5. Relaciones para facilitar consultas ORM
    negocio_rel = relationship("Negocio", backref="productos_catalogo")
    sucursal_rel = relationship("Sucursal", backref="productos_inventario")

    def __init__(self, **kwargs):
        """Constructor para inicialización flexible"""
        super(ProductoCatalogo, self).__init__(**kwargs)

    def to_dict(self):
        """
        Convierte el objeto a formato JSON para las APIs.
        Mapea 'imagen_url' a 'img' para compatibilidad directa con el 
        motor de renderizado de Rodar.html.
        """
        return {
            "id": self.id_producto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "img": self.imagen_url,
            "categoria": self.categoria,
            "stock": self.stock,
            "activo": self.activo,
            "negocio_id": self.negocio_id,
            "sucursal_id": self.sucursal_id,
            "fecha_creacion": self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<ProductoCatalogo {self.nombre} (Negocio ID: {self.negocio_id})>'