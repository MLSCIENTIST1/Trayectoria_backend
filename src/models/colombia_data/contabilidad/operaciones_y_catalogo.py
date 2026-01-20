"""
BizFlow Studio - Modelos de Contabilidad y Catálogo
Operaciones financieras y gestión de productos
ACTUALIZADO: Inventario PRO v2.1 - Soporte completo para galería, videos YouTube
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime
import json


# ==========================================
# MODELO: TRANSACCIÓN OPERATIVA
# ==========================================
class TransaccionOperativa(db.Model):
    """
    Modelo para registrar el historial financiero (Kardex).
    Almacena VENTAS, COMPRAS, GASTOS e INGRESOS.
    """
    __tablename__ = 'transacciones_operativas'

    id_transaccion = sa.Column(sa.Integer, primary_key=True)
    
    negocio_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    usuario_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    sucursal_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('sucursales.id_sucursal', ondelete='SET NULL'),
        nullable=True,
        default=1
    )

    tipo = sa.Column(sa.String(50), nullable=False, index=True)
    concepto = sa.Column(sa.String(255), nullable=False)
    monto = sa.Column(sa.Numeric(15, 2), nullable=False)
    categoria = sa.Column(sa.String(100), index=True)
    metodo_pago = sa.Column(sa.String(50))
    referencia_guia = sa.Column(sa.String(100))
    fecha = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    notas = sa.Column(sa.Text, nullable=True)

    negocio = relationship("Negocio", foreign_keys=[negocio_id])
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    sucursal = relationship("Sucursal", foreign_keys=[sucursal_id])

    def __init__(self, negocio_id, usuario_id, tipo, concepto, monto, **kwargs):
        self.negocio_id = negocio_id
        self.usuario_id = usuario_id
        self.tipo = tipo.upper()
        self.concepto = concepto
        self.monto = monto
        self.sucursal_id = kwargs.get('sucursal_id', 1)
        self.categoria = kwargs.get('categoria', 'General')
        self.metodo_pago = kwargs.get('metodo_pago', 'Efectivo')
        self.referencia_guia = kwargs.get('referencia_guia')
        self.notas = kwargs.get('notas')

    def to_dict(self):
        return {
            "id": self.id_transaccion,
            "id_transaccion": self.id_transaccion,
            "tipo": self.tipo,
            "concepto": self.concepto,
            "monto": float(self.monto),
            "categoria": self.categoria,
            "metodo": self.metodo_pago,
            "metodo_pago": self.metodo_pago,
            "guia": self.referencia_guia,
            "referencia_guia": self.referencia_guia,
            "notas": self.notas,
            "fecha": self.fecha.strftime('%Y-%m-%d %H:%M:%S') if self.fecha else None,
            "negocio_id": self.negocio_id,
            "usuario_id": self.usuario_id,
            "sucursal_id": self.sucursal_id
        }
    
    def serialize(self):
        return self.to_dict()

    def __repr__(self):
        return f'<Transaccion {self.tipo} - ${self.monto} - {self.concepto[:30]}>'


# ==========================================
# MODELO: ALERTA OPERATIVA
# ==========================================
class AlertaOperativa(db.Model):
    """Modelo para alertas de stock crítico y recordatorios."""
    __tablename__ = 'alertas_operativas'
    
    id_alerta = sa.Column(sa.Integer, primary_key=True)
    
    negocio_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    usuario_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'),
        nullable=False
    )
    
    tarea = sa.Column(sa.Text, nullable=False)
    prioridad = sa.Column(sa.String(20), default="MEDIA")
    tipo = sa.Column(sa.String(50), default="STOCK")
    completada = sa.Column(sa.Boolean, default=False, nullable=False)
    fecha_programada = sa.Column(sa.DateTime, nullable=False)
    fecha_completada = sa.Column(sa.DateTime, nullable=True)
    fecha_creacion = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    
    negocio = relationship("Negocio", foreign_keys=[negocio_id])
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    
    def marcar_completada(self):
        self.completada = True
        self.fecha_completada = datetime.utcnow()
    
    def to_dict(self):
        return {
            "id": self.id_alerta,
            "tarea": self.tarea,
            "prioridad": self.prioridad,
            "tipo": self.tipo,
            "completada": self.completada,
            "fecha_programada": self.fecha_programada.isoformat() if self.fecha_programada else None,
            "fecha_completada": self.fecha_completada.isoformat() if self.fecha_completada else None,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "negocio_id": self.negocio_id,
            "usuario_id": self.usuario_id
        }


# ==========================================
# MODELO: MOVIMIENTO DE STOCK
# ==========================================
class MovimientoStock(db.Model):
    """Historial de movimientos de inventario por producto."""
    __tablename__ = 'movimientos_stock'
    
    id_movimiento = sa.Column(sa.Integer, primary_key=True)
    
    producto_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('productos_catalogo.id_producto', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario'), nullable=False)
    negocio_id = sa.Column(sa.Integer, sa.ForeignKey('negocios.id_negocio'), nullable=False)
    sucursal_id = sa.Column(sa.Integer, sa.ForeignKey('sucursales.id_sucursal'), nullable=True)
    
    tipo = sa.Column(sa.String(20), nullable=False)
    cantidad = sa.Column(sa.Integer, nullable=False)
    stock_anterior = sa.Column(sa.Integer, nullable=False)
    stock_nuevo = sa.Column(sa.Integer, nullable=False)
    nota = sa.Column(sa.String(255), nullable=True)
    fecha = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    producto = relationship("ProductoCatalogo", backref="movimientos")
    
    def to_dict(self):
        return {
            "id": self.id_movimiento,
            "producto_id": self.producto_id,
            "tipo": self.tipo,
            "quantity": self.cantidad,
            "cantidad": self.cantidad,
            "previousStock": self.stock_anterior,
            "stock_anterior": self.stock_anterior,
            "newStock": self.stock_nuevo,
            "stock_nuevo": self.stock_nuevo,
            "note": self.nota,
            "nota": self.nota,
            "motivo": self.nota,
            "date": self.fecha.isoformat() if self.fecha else None,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "created_at": self.fecha.isoformat() if self.fecha else None
        }


# ==========================================
# MODELO: CATEGORÍA DE PRODUCTO
# ==========================================
class CategoriaProducto(db.Model):
    """Categorías personalizadas para productos."""
    __tablename__ = 'categorias_producto'
    
    id_categoria = sa.Column(sa.Integer, primary_key=True)
    
    usuario_id = sa.Column(sa.Integer, sa.ForeignKey('usuarios.id_usuario'), nullable=False)
    negocio_id = sa.Column(sa.Integer, sa.ForeignKey('negocios.id_negocio'), nullable=False)
    
    nombre = sa.Column(sa.String(100), nullable=False)
    icono = sa.Column(sa.String(10), default='📦')
    color = sa.Column(sa.String(20), default='#6366f1')
    fecha_creacion = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id_categoria,
            "name": self.nombre,
            "nombre": self.nombre,
            "icon": self.icono,
            "icono": self.icono,
            "color": self.color,
            "negocio_id": self.negocio_id
        }


# ==========================================
# MODELO: PRODUCTO CATÁLOGO (INVENTARIO PRO v2.1)
# ==========================================
class ProductoCatalogo(db.Model):
    """
    Modelo para gestión de productos en el catálogo/inventario.
    ACTUALIZADO v2.1: Soporte para galería de imágenes y videos YouTube.
    
    CAMPOS DE MULTIMEDIA:
    - imagen_url: URL de la imagen principal
    - imagenes: JSON array de URLs de galería (TEXT)
    - videos: JSON array de URLs de YouTube (TEXT)
    
    NOTA: El frontend puede enviar 'youtube_links', el backend lo guarda en 'videos'
    """
    __tablename__ = 'productos_catalogo'
    __table_args__ = {'extend_existing': True}

    # ==========================================
    # IDENTIFICACIÓN
    # ==========================================
    id_producto = sa.Column(sa.Integer, primary_key=True)

    # ==========================================
    # INFORMACIÓN DEL PRODUCTO
    # ==========================================
    nombre = sa.Column(sa.String(150), nullable=False, index=True)
    descripcion = sa.Column(sa.Text, nullable=True)
    
    # ==========================================
    # PRECIOS Y COSTOS
    # ==========================================
    precio = sa.Column(sa.Float, nullable=False)
    costo = sa.Column(sa.Float, default=0.0, nullable=False)
    
    # ==========================================
    # IDENTIFICACIÓN TÉCNICA
    # ==========================================
    referencia_sku = sa.Column(sa.String(100), nullable=True, default="SIN_SKU")
    codigo_barras = sa.Column(sa.String(100), nullable=True)
    
    # ==========================================
    # MULTIMEDIA (INVENTARIO PRO v2.1)
    # ==========================================
    # Imagen principal
    imagen_url = sa.Column(sa.String(500), nullable=True)
    
    # Galería de imágenes (JSON array de URLs)
    imagenes = sa.Column(sa.Text, nullable=True, default='[]')
    
    # Videos de YouTube (JSON array de URLs)
    # El frontend envía 'youtube_links', se almacena en 'videos'
    videos = sa.Column(sa.Text, nullable=True, default='[]')
    
    # ==========================================
    # CATEGORIZACIÓN Y ESTADO
    # ==========================================
    categoria = sa.Column(sa.String(100), default='General', index=True)
    plan = sa.Column(sa.String(20), default='basic', nullable=False)
    etiquetas = sa.Column(sa.Text, nullable=True, default='[]')
    
    # ==========================================
    # INVENTARIO Y ALERTAS
    # ==========================================
    stock = sa.Column(sa.Integer, default=0, nullable=False)
    stock_minimo = sa.Column(sa.Integer, default=5)
    stock_critico = sa.Column(sa.Integer, default=2)
    stock_bajo = sa.Column(sa.Integer, default=10)
    
    # ==========================================
    # ESTADO Y PUBLICACIÓN
    # ==========================================
    activo = sa.Column(sa.Boolean, default=True, nullable=False)
    estado_publicacion = sa.Column(sa.Boolean, default=True, nullable=False)
    
    # ==========================================
    # METADATA
    # ==========================================
    fecha_creacion = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ==========================================
    # RELACIONES (MULTI-TENENCIA)
    # ==========================================
    negocio_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    usuario_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'),
        nullable=False
    )
    sucursal_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('sucursales.id_sucursal', ondelete='SET NULL'),
        nullable=True,
        default=1,
        index=True
    )

    # ==========================================
    # RELACIONES ORM
    # ==========================================
    negocio = relationship("Negocio", foreign_keys=[negocio_id], back_populates="productos")
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    sucursal = relationship("Sucursal", foreign_keys=[sucursal_id], back_populates="productos")

    # ==========================================
    # CONSTRUCTOR
    # ==========================================
    def __init__(self, nombre, precio, negocio_id, usuario_id, **kwargs):
        self.nombre = nombre
        self.precio = precio
        self.negocio_id = negocio_id
        self.usuario_id = usuario_id
        self.descripcion = kwargs.get('descripcion')
        self.costo = kwargs.get('costo', 0.0)
        self.stock = kwargs.get('stock', 0)
        self.stock_minimo = kwargs.get('stock_minimo', 5)
        self.stock_critico = kwargs.get('stock_critico', 2)
        self.stock_bajo = kwargs.get('stock_bajo', 10)
        self.categoria = kwargs.get('categoria', 'General')
        self.referencia_sku = kwargs.get('referencia_sku', 'SIN_SKU')
        self.codigo_barras = kwargs.get('codigo_barras')
        self.imagen_url = kwargs.get('imagen_url')
        self.imagenes = kwargs.get('imagenes', '[]')
        self.videos = kwargs.get('videos', '[]')
        self.plan = kwargs.get('plan', 'basic')
        self.etiquetas = kwargs.get('etiquetas', '[]')
        self.sucursal_id = kwargs.get('sucursal_id', 1)
        self.activo = kwargs.get('activo', True)
        self.estado_publicacion = kwargs.get('estado_publicacion', True)
    
    # ==========================================
    # MÉTODOS DE STOCK
    # ==========================================
    def ajustar_stock(self, cantidad, tipo='SUMA'):
        """Ajusta el stock del producto"""
        if tipo == 'SUMA':
            self.stock += cantidad
        elif tipo == 'RESTA':
            self.stock = max(0, self.stock - cantidad)
    
    def necesita_reabastecimiento(self):
        """Verifica si el stock está bajo el mínimo"""
        return self.stock <= self.stock_minimo
    
    def nivel_stock(self):
        """Retorna el nivel de stock: 'critico', 'bajo', 'ok'"""
        if self.stock <= self.stock_critico:
            return 'critico'
        elif self.stock <= self.stock_bajo:
            return 'bajo'
        return 'ok'
    
    # ==========================================
    # MÉTODOS DE CÁLCULO FINANCIERO
    # ==========================================
    def get_margen_utilidad(self):
        """Calcula el margen de utilidad en porcentaje"""
        if self.costo == 0:
            return 0.0
        return round(((self.precio - self.costo) / self.costo) * 100, 2)
    
    def get_ganancia_unitaria(self):
        """Calcula la ganancia por unidad"""
        return round(self.precio - self.costo, 2)
    
    # ==========================================
    # HELPER PARA PARSEAR JSON
    # ==========================================
    def _parse_json_field(self, field_value):
        """
        Helper para parsear campos JSON almacenados como TEXT.
        Maneja correctamente el doble encoding que puede venir del frontend.
        """
        if field_value is None:
            return []
        if isinstance(field_value, list):
            return field_value
        if isinstance(field_value, str):
            try:
                parsed = json.loads(field_value)
                # Si el resultado es string, puede ser doble encoding
                if isinstance(parsed, str):
                    try:
                        return json.loads(parsed)
                    except:
                        return []
                if isinstance(parsed, list):
                    return parsed
                return []
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    # ==========================================
    # PROPIEDADES PARA ACCESO A MULTIMEDIA
    # ==========================================
    @property
    def imagenes_lista(self):
        """Obtiene la lista de imágenes como array"""
        return self._parse_json_field(self.imagenes)
    
    @property
    def videos_lista(self):
        """Obtiene la lista de videos como array"""
        return self._parse_json_field(self.videos)
    
    @property
    def youtube_links(self):
        """Alias para compatibilidad con frontend - retorna videos"""
        return self.videos_lista
    
    # ==========================================
    # SERIALIZACIÓN
    # ==========================================
    def to_dict(self):
        """Serializa el producto a diccionario (compatible con Inventario PRO v2.1)"""
        # Parsear campos JSON
        imagenes_lista = self._parse_json_field(self.imagenes)
        videos_lista = self._parse_json_field(self.videos)
        etiquetas_lista = self._parse_json_field(self.etiquetas)
        
        return {
            # ==========================================
            # IDENTIFICADORES
            # ==========================================
            "id": self.id_producto,
            "id_producto": self.id_producto,
            
            # ==========================================
            # INFORMACIÓN BÁSICA
            # ==========================================
            "nombre": self.nombre,
            "descripcion": self.descripcion or "",
            
            # ==========================================
            # PRECIOS Y COSTOS
            # ==========================================
            "precio": float(self.precio) if self.precio else 0,
            "costo": float(self.costo) if self.costo else 0,
            "margen_utilidad": self.get_margen_utilidad(),
            "ganancia_unitaria": self.get_ganancia_unitaria(),
            
            # ==========================================
            # IDENTIFICACIÓN TÉCNICA
            # ==========================================
            "sku": self.referencia_sku,
            "referencia_sku": self.referencia_sku,
            "codigo_barras": self.codigo_barras or "",
            "barcode": self.codigo_barras or "",
            
            # ==========================================
            # MULTIMEDIA (compatible con JS)
            # ==========================================
            "imagen_url": self.imagen_url,
            "imagen": self.imagen_url,
            "imagenes": imagenes_lista,
            "videos": videos_lista,
            "youtube_links": videos_lista,  # Alias para compatibilidad con JS
            
            # ==========================================
            # CATEGORIZACIÓN
            # ==========================================
            "categoria": self.categoria,
            "plan": self.plan,
            "etiquetas": etiquetas_lista,
            
            # ==========================================
            # INVENTARIO
            # ==========================================
            "stock": self.stock or 0,
            "stock_minimo": self.stock_minimo or 5,
            "stock_critico": self.stock_critico or 2,
            "stock_bajo": self.stock_bajo or 10,
            "necesita_reabastecimiento": self.necesita_reabastecimiento(),
            "nivel_stock": self.nivel_stock(),
            
            # ==========================================
            # ESTADO
            # ==========================================
            "activo": self.activo,
            "estado_publicacion": self.estado_publicacion,
            
            # ==========================================
            # RELACIONES
            # ==========================================
            "negocio_id": self.negocio_id,
            "sucursal_id": self.sucursal_id,
            "usuario_id": self.usuario_id,
            
            # ==========================================
            # FECHAS
            # ==========================================
            "fecha": self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None,
            "fecha_creacion": self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None,
            "created_at": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_actualizacion else None,
            "updated_at": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }

    def serialize(self):
        """Alias de to_dict() para compatibilidad"""
        return self.to_dict()

    def __repr__(self):
        return f'<Producto {self.nombre} - Stock: {self.stock} ({self.nivel_stock()})>'
    
    def __str__(self):
        return f"{self.nombre} (${self.precio})"