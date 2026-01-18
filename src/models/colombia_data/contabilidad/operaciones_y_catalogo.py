"""
BizFlow Studio - Modelos de Contabilidad y Catálogo
Operaciones financieras y gestión de productos
ACTUALIZADO: Inventario PRO v2.0 - Soporte para galería, videos y planes
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime


# ==========================================
# MODELO: TRANSACCIÓN OPERATIVA
# ==========================================
class TransaccionOperativa(db.Model):
    """
    Modelo para registrar el historial financiero (Kardex).
    Almacena VENTAS, COMPRAS, GASTOS e INGRESOS.
    """
    __tablename__ = 'transacciones_operativas'

    # Identificación
    id_transaccion = sa.Column(sa.Integer, primary_key=True)
    
    # Relaciones de jerarquía (Multi-tenancy)
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

    # Detalles de la operación
    tipo = sa.Column(
        sa.String(50),
        nullable=False,
        index=True
    )  # 'VENTA', 'COMPRA', 'GASTO', 'INGRESO'
    
    concepto = sa.Column(sa.String(255), nullable=False)
    monto = sa.Column(sa.Numeric(15, 2), nullable=False)
    categoria = sa.Column(sa.String(100), index=True)
    metodo_pago = sa.Column(sa.String(50))  # 'Efectivo', 'Nequi', 'Transferencia', etc.
    referencia_guia = sa.Column(sa.String(100))  # Número de guía, factura, etc.
    
    # Metadata
    fecha = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False, index=True)
    notas = sa.Column(sa.Text, nullable=True)

    # Relaciones
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
    """
    Modelo para alertas de stock crítico y recordatorios de tareas.
    """
    __tablename__ = 'alertas_operativas'
    
    id_alerta = sa.Column(sa.Integer, primary_key=True)
    
    # Relaciones
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
    
    # Contenido de la alerta
    tarea = sa.Column(sa.Text, nullable=False)
    prioridad = sa.Column(sa.String(20), default="MEDIA")  # ALTA, MEDIA, BAJA
    tipo = sa.Column(sa.String(50), default="STOCK")  # STOCK, TAREA, VENCIMIENTO
    
    # Control
    completada = sa.Column(sa.Boolean, default=False, nullable=False)
    fecha_programada = sa.Column(sa.DateTime, nullable=False)
    fecha_completada = sa.Column(sa.DateTime, nullable=True)
    
    # Metadata
    fecha_creacion = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
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
# MODELO: PRODUCTO CATÁLOGO (INVENTARIO PRO v2.0)
# ==========================================
class ProductoCatalogo(db.Model):
    """
    Modelo para gestión de productos en el catálogo/inventario.
    ACTUALIZADO: Soporte para galería de imágenes, videos y sistema de planes.
    """
    __tablename__ = 'productos_catalogo'
    __table_args__ = {'extend_existing': True}

    # Identificación
    id_producto = sa.Column(sa.Integer, primary_key=True)

    # Información del producto
    nombre = sa.Column(sa.String(150), nullable=False, index=True)
    descripcion = sa.Column(sa.Text, nullable=True)
    
    # Precios y costos
    precio = sa.Column(sa.Float, nullable=False)
    costo = sa.Column(sa.Float, default=0.0, nullable=False)
    
    # Identificación técnica
    referencia_sku = sa.Column(sa.String(100), nullable=True, default="SIN_SKU")
    codigo_barras = sa.Column(sa.String(100), nullable=True)
    
    # Multimedia (INVENTARIO PRO v2.0)
    imagen_url = sa.Column(sa.String(500), nullable=True)  # Imagen principal
    imagenes = sa.Column(sa.JSON, nullable=True)  # Array de URLs de galería
    videos = sa.Column(sa.JSON, nullable=True)  # Array de URLs de videos (YouTube/Vimeo)
    
    # Categorización y estado
    categoria = sa.Column(sa.String(100), default='General', index=True)
    plan = sa.Column(sa.String(20), default='basic', nullable=False)  # basic, pro, premium, deluxe
    etiquetas = sa.Column(sa.JSON, nullable=True)  # Array de tags personalizados
    
    # Inventario
    stock = sa.Column(sa.Integer, default=0, nullable=False)
    stock_minimo = sa.Column(sa.Integer, default=5)
    stock_critico = sa.Column(sa.Integer, default=5)  # Nivel crítico personalizable
    stock_bajo = sa.Column(sa.Integer, default=20)  # Nivel bajo personalizable
    
    # Estado y publicación
    activo = sa.Column(sa.Boolean, default=True, nullable=False)
    estado_publicacion = sa.Column(sa.Boolean, default=True, nullable=False)
    
    # Metadata
    fecha_creacion = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones (Multi-tenencia)
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

    # Relaciones ORM
    negocio = relationship("Negocio", foreign_keys=[negocio_id], back_populates="productos")
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    sucursal = relationship("Sucursal", foreign_keys=[sucursal_id], back_populates="productos")

    def __init__(self, nombre, precio, negocio_id, usuario_id, **kwargs):
        self.nombre = nombre
        self.precio = precio
        self.negocio_id = negocio_id
        self.usuario_id = usuario_id
        self.descripcion = kwargs.get('descripcion')
        self.costo = kwargs.get('costo', 0.0)
        self.stock = kwargs.get('stock', 0)
        self.stock_minimo = kwargs.get('stock_minimo', 5)
        self.stock_critico = kwargs.get('stock_critico', 5)
        self.stock_bajo = kwargs.get('stock_bajo', 20)
        self.categoria = kwargs.get('categoria', 'General')
        self.referencia_sku = kwargs.get('referencia_sku', 'SIN_SKU')
        self.codigo_barras = kwargs.get('codigo_barras')
        self.imagen_url = kwargs.get('imagen_url')
        self.imagenes = kwargs.get('imagenes')  # NUEVO
        self.videos = kwargs.get('videos')  # NUEVO
        self.plan = kwargs.get('plan', 'basic')  # NUEVO
        self.etiquetas = kwargs.get('etiquetas')  # NUEVO
        self.sucursal_id = kwargs.get('sucursal_id', 1)
        self.activo = kwargs.get('activo', True)
        self.estado_publicacion = kwargs.get('estado_publicacion', True)
    
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
        if self.stock < self.stock_critico:
            return 'critico'
        elif self.stock < self.stock_bajo:
            return 'bajo'
        return 'ok'
    
    def get_margen_utilidad(self):
        """Calcula el margen de utilidad en porcentaje"""
        if self.costo == 0:
            return 0.0
        return round(((self.precio - self.costo) / self.costo) * 100, 2)
    
    def get_ganancia_unitaria(self):
        """Calcula la ganancia por unidad"""
        return round(self.precio - self.costo, 2)
    
    def to_dict(self):
        """Serializa el producto a diccionario (compatible con inventario PRO)"""
        return {
            # Identificadores
            "id": self.id_producto,
            "id_producto": self.id_producto,
            
            # Información básica
            "nombre": self.nombre,
            "descripcion": self.descripcion or "",
            
            # Precios y costos
            "precio": self.precio,
            "costo": self.costo,
            "margen_utilidad": self.get_margen_utilidad(),
            "ganancia_unitaria": self.get_ganancia_unitaria(),
            
            # Identificación técnica
            "sku": self.referencia_sku,
            "referencia_sku": self.referencia_sku,
            "codigo_barras": self.codigo_barras,
            
            # Multimedia
            "imagen_url": self.imagen_url,
            "imagenes": self.imagenes if self.imagenes else [],  # NUEVO
            "videos": self.videos if self.videos else [],  # NUEVO
            
            # Categorización
            "categoria": self.categoria,
            "plan": self.plan,  # NUEVO
            "etiquetas": self.etiquetas if self.etiquetas else [],  # NUEVO
            
            # Inventario
            "stock": self.stock,
            "stock_minimo": self.stock_minimo,
            "stock_critico": self.stock_critico,  # NUEVO
            "stock_bajo": self.stock_bajo,  # NUEVO
            "necesita_reabastecimiento": self.necesita_reabastecimiento(),
            "nivel_stock": self.nivel_stock(),  # NUEVO
            
            # Estado
            "activo": self.activo,
            "estado_publicacion": self.estado_publicacion,
            
            # Relaciones
            "negocio_id": self.negocio_id,
            "sucursal_id": self.sucursal_id,
            "usuario_id": self.usuario_id,
            
            # Fechas
            "fecha": self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None,
            "fecha_creacion": self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_actualizacion else None
        }

    def serialize(self):
        """Alias de to_dict() para compatibilidad"""
        return self.to_dict()

    def __repr__(self):
        return f'<Producto {self.nombre} - Stock: {self.stock} ({self.nivel_stock()})>'
    
    def __str__(self):
        return f"{self.nombre} (${self.precio})"