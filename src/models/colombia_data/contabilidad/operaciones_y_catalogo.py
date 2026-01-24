"""
BizFlow Studio - Modelos de Contabilidad y Catálogo
Operaciones financieras y gestión de productos
ACTUALIZADO: Inventario PRO v2.3 - Sistema de Badges con badges_data JSON
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from src.models.database import db
from datetime import datetime, timedelta
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
# MODELO: ESTADÍSTICAS DE PRODUCTO
# ==========================================
class ProductoEstadisticas(db.Model):
    """Estadísticas diarias de productos para badges automáticos."""
    __tablename__ = 'producto_estadisticas'
    __table_args__ = (
        sa.UniqueConstraint('producto_id', 'fecha', name='uq_producto_fecha'),
        {'extend_existing': True}
    )
    
    id = sa.Column(sa.Integer, primary_key=True)
    producto_id = sa.Column(
        sa.Integer, 
        sa.ForeignKey('productos_catalogo.id_producto', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    negocio_id = sa.Column(
        sa.Integer, 
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    fecha = sa.Column(sa.Date, nullable=False, index=True)
    visitas = sa.Column(sa.Integer, default=0)
    agregados_carrito = sa.Column(sa.Integer, default=0)
    compras = sa.Column(sa.Integer, default=0)
    ingresos = sa.Column(sa.Numeric(12, 2), default=0)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "visitas": self.visitas,
            "agregados_carrito": self.agregados_carrito,
            "compras": self.compras,
            "ingresos": float(self.ingresos) if self.ingresos else 0
        }


# ==========================================
# MODELO: HISTORIAL DE PRECIOS
# ==========================================
class ProductoPreciosHistorico(db.Model):
    """Historial de precios para badge de 'precio más bajo'."""
    __tablename__ = 'producto_precios_historico'
    __table_args__ = {'extend_existing': True}
    
    id = sa.Column(sa.Integer, primary_key=True)
    producto_id = sa.Column(
        sa.Integer, 
        sa.ForeignKey('productos_catalogo.id_producto', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    negocio_id = sa.Column(
        sa.Integer, 
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'), 
        nullable=False
    )
    precio = sa.Column(sa.Numeric(12, 2), nullable=False)
    precio_original = sa.Column(sa.Numeric(12, 2))
    fecha = sa.Column(sa.Date, nullable=False, index=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "precio": float(self.precio),
            "precio_original": float(self.precio_original) if self.precio_original else None,
            "fecha": self.fecha.isoformat() if self.fecha else None
        }


# ==========================================
# MODELO: REVIEWS DE PRODUCTO
# ==========================================
class ProductoReview(db.Model):
    """Reviews de productos para badge de 'mejor valorado'."""
    __tablename__ = 'producto_reviews'
    __table_args__ = {'extend_existing': True}
    
    id = sa.Column(sa.Integer, primary_key=True)
    producto_id = sa.Column(
        sa.Integer, 
        sa.ForeignKey('productos_catalogo.id_producto', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    negocio_id = sa.Column(
        sa.Integer, 
        sa.ForeignKey('negocios.id_negocio', ondelete='CASCADE'), 
        nullable=False
    )
    cliente_nombre = sa.Column(sa.String(100))
    cliente_email = sa.Column(sa.String(150))
    rating = sa.Column(sa.Integer, nullable=False)
    titulo = sa.Column(sa.String(150))
    comentario = sa.Column(sa.Text)
    verificado = sa.Column(sa.Boolean, default=False)
    aprobado = sa.Column(sa.Boolean, default=False)
    fecha = sa.Column(sa.DateTime, default=datetime.utcnow)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "cliente_nombre": self.cliente_nombre,
            "rating": self.rating,
            "titulo": self.titulo,
            "comentario": self.comentario,
            "verificado": self.verificado,
            "aprobado": self.aprobado,
            "fecha": self.fecha.isoformat() if self.fecha else None
        }
# ==========================================
# MODELO: PRODUCTO CATÁLOGO (INVENTARIO PRO v2.3)
# ==========================================
class ProductoCatalogo(db.Model):
    """
    Modelo para gestión de productos en el catálogo/inventario.
    ACTUALIZADO v2.3: Sistema de Badges con columna badges_data (JSON)
    
    BADGES AUTOMÁTICOS (calculados en calcular_badges):
    - nuevo: fecha_creacion < 30 días
    - descuento: precio_original > precio
    - agotado: stock = 0
    - ultima_unidad: stock = 1
    - ultimas_unidades: stock <= 5 y > 0
    - mejor_valorado: rating >= 4.5 con 5+ reviews
    - popular: visitas_7_dias >= 50
    
    BADGES MANUALES (columnas legacy BD):
    - badge_destacado, badge_mas_vendido, badge_envio_gratis
    
    BADGES FLEXIBLES (en badges_data JSON - v2.3):
    - destacado, envio_gratis, pre_orden, edicion_limitada
    - oferta_flash, combo, garantia_extendida, eco_friendly
    - badge_personalizado (texto libre max 20 chars)
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
    precio_original = sa.Column(sa.Numeric(12, 2), nullable=True)
    costo = sa.Column(sa.Float, default=0.0, nullable=False)
    precio_historico_min = sa.Column(sa.Numeric(12, 2), nullable=True)
    
    # ==========================================
    # IDENTIFICACIÓN TÉCNICA
    # ==========================================
    referencia_sku = sa.Column(sa.String(100), nullable=True, default="SIN_SKU")
    codigo_barras = sa.Column(sa.String(100), nullable=True)
    
    # ==========================================
    # MULTIMEDIA
    # ==========================================
    imagen_url = sa.Column(sa.String(500), nullable=True)
    imagenes = sa.Column(sa.Text, nullable=True, default='[]')
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
    # MÉTRICAS PARA BADGES AUTOMÁTICOS
    # ==========================================
    total_ventas = sa.Column(sa.Integer, default=0)
    ventas_30_dias = sa.Column(sa.Integer, default=0)
    visitas_7_dias = sa.Column(sa.Integer, default=0)
    rating_promedio = sa.Column(sa.Numeric(2, 1), default=0)
    total_reviews = sa.Column(sa.Integer, default=0)
    velocidad_venta = sa.Column(sa.Numeric(5, 2), default=0)
    
    # ==========================================
    # BADGES MANUALES (columnas legacy)
    # ==========================================
    badge_destacado = sa.Column(sa.Boolean, default=False)
    badge_mas_vendido = sa.Column(sa.Boolean, default=False)
    badge_envio_gratis = sa.Column(sa.Boolean, default=False)
    
    # ==========================================
    # ★ BADGES FLEXIBLES (v2.3 - JSON Storage)
    # ==========================================
    # Almacena: destacado, envio_gratis, pre_orden, edicion_limitada,
    # oferta_flash, combo, garantia_extendida, eco_friendly, badge_personalizado
    badges_data = sa.Column(sa.Text, nullable=True, default='{}')
    
    # ==========================================
    # PROMOCIONES PROGRAMADAS
    # ==========================================
    promo_inicio = sa.Column(sa.DateTime, nullable=True)
    promo_fin = sa.Column(sa.DateTime, nullable=True)
    promo_badge_texto = sa.Column(sa.String(50), nullable=True)
    
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
        self.precio_original = kwargs.get('precio_original')
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
        
        # Badges columnas legacy
        self.badge_destacado = kwargs.get('badge_destacado', False)
        self.badge_mas_vendido = kwargs.get('badge_mas_vendido', False)
        self.badge_envio_gratis = kwargs.get('badge_envio_gratis', False)
        
        # ★ Badges flexibles (JSON) v2.3
        badges_data = kwargs.get('badges_data')
        if badges_data:
            if isinstance(badges_data, dict):
                self.badges_data = json.dumps(badges_data)
            elif isinstance(badges_data, str):
                self.badges_data = badges_data
            else:
                self.badges_data = '{}'
        else:
            self.badges_data = '{}'
    
    # ==========================================
    # HELPER PARA PARSEAR JSON
    # ==========================================
    def _parse_json_field(self, field_value, default=None):
        """
        Helper para parsear campos JSON almacenados como TEXT.
        Maneja correctamente el doble encoding.
        """
        if default is None:
            default = []
        if field_value is None:
            return default
        if isinstance(field_value, (list, dict)):
            return field_value
        if isinstance(field_value, str):
            try:
                parsed = json.loads(field_value)
                if isinstance(parsed, str):
                    try:
                        return json.loads(parsed)
                    except:
                        return default
                return parsed
            except (json.JSONDecodeError, TypeError):
                return default
        return default
    
    def _parse_badges_data(self):
        """Parsea el campo badges_data (JSON) de forma segura."""
        return self._parse_json_field(self.badges_data, {})
    
    # ==========================================
    # MÉTODOS DE BADGES v2.3
    # ==========================================
    def get_badges_manuales(self):
        """
        Obtiene todos los badges manuales (columnas legacy + JSON).
        Prioriza badges_data JSON sobre columnas legacy.
        """
        badges_flex = self._parse_badges_data()
        
        return {
            # Desde badges_data JSON (prioridad) o columnas legacy
            "destacado": badges_flex.get('destacado', bool(self.badge_destacado)),
            "mas_vendido": badges_flex.get('mas_vendido', bool(self.badge_mas_vendido)),
            "envio_gratis": badges_flex.get('envio_gratis', bool(self.badge_envio_gratis)),
            # Solo desde badges_data JSON
            "pre_orden": badges_flex.get('pre_orden', False),
            "edicion_limitada": badges_flex.get('edicion_limitada', False),
            "oferta_flash": badges_flex.get('oferta_flash', False),
            "combo": badges_flex.get('combo', False),
            "garantia_extendida": badges_flex.get('garantia_extendida', False),
            "eco_friendly": badges_flex.get('eco_friendly', False),
            "badge_personalizado": badges_flex.get('badge_personalizado')
        }
    
    def set_badges_manuales(self, badges_dict):
        """
        Guarda los badges manuales desde el frontend.
        Actualiza tanto badges_data JSON como columnas legacy.
        """
        if not badges_dict:
            return
        
        # Si viene como string JSON, parsearlo
        if isinstance(badges_dict, str):
            try:
                badges_dict = json.loads(badges_dict)
            except:
                return
        
        if not isinstance(badges_dict, dict):
            return
        
        # Actualizar columnas legacy para compatibilidad
        if 'destacado' in badges_dict:
            self.badge_destacado = bool(badges_dict['destacado'])
        if 'mas_vendido' in badges_dict:
            self.badge_mas_vendido = bool(badges_dict['mas_vendido'])
        if 'envio_gratis' in badges_dict:
            self.badge_envio_gratis = bool(badges_dict['envio_gratis'])
        
        # Guardar todos los badges en badges_data JSON
        badges_flex = {
            'destacado': bool(badges_dict.get('destacado', False)),
            'envio_gratis': bool(badges_dict.get('envio_gratis', False)),
            'pre_orden': bool(badges_dict.get('pre_orden', False)),
            'edicion_limitada': bool(badges_dict.get('edicion_limitada', False)),
            'oferta_flash': bool(badges_dict.get('oferta_flash', False)),
            'combo': bool(badges_dict.get('combo', False)),
            'garantia_extendida': bool(badges_dict.get('garantia_extendida', False)),
            'eco_friendly': bool(badges_dict.get('eco_friendly', False)),
            'badge_personalizado': badges_dict.get('badge_personalizado') or None
        }
        self.badges_data = json.dumps(badges_flex)
    
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
    # PROPIEDADES PARA MULTIMEDIA
    # ==========================================
    @property
    def imagenes_lista(self):
        """Obtiene la lista de imágenes como array"""
        return self._parse_json_field(self.imagenes, [])
    
    @property
    def videos_lista(self):
        """Obtiene la lista de videos como array"""
        return self._parse_json_field(self.videos, [])
    
    @property
    def youtube_links(self):
        """Alias para compatibilidad con frontend"""
        return self.videos_lista
    
    # ==========================================
    # ★ MÉTODO PARA CALCULAR BADGES (v2.3)
    # ==========================================
    def calcular_badges(self):
        """
        Calcula todos los badges (automáticos + manuales).
        Retorna diccionario completo para la API.
        """
        now = datetime.utcnow()
        
        # Convertir precios a float
        precio_actual = float(self.precio) if self.precio else 0
        precio_orig = float(self.precio_original) if self.precio_original else None
        precio_min = float(self.precio_historico_min) if self.precio_historico_min else None
        
        # ═══════════════════════════════════════
        # BADGE: DESCUENTO
        # ═══════════════════════════════════════
        tiene_descuento = precio_orig is not None and precio_orig > precio_actual
        descuento_porcentaje = 0
        descuento_ahorro = 0
        if tiene_descuento and precio_orig > 0:
            descuento_porcentaje = round((1 - precio_actual / precio_orig) * 100)
            descuento_ahorro = round(precio_orig - precio_actual, 2)
        
        # ═══════════════════════════════════════
        # BADGE: NUEVO (menos de 30 días)
        # ═══════════════════════════════════════
        es_nuevo = False
        if self.fecha_creacion:
            dias_desde_creacion = (now - self.fecha_creacion).days
            es_nuevo = dias_desde_creacion < 30
        
        # ═══════════════════════════════════════
        # BADGES DE STOCK
        # ═══════════════════════════════════════
        stock = self.stock or 0
        es_agotado = stock == 0
        es_ultima_unidad = stock == 1
        es_ultimas_unidades = 0 < stock <= 5
        
        # ═══════════════════════════════════════
        # PROMOCIÓN ACTIVA
        # ═══════════════════════════════════════
        promo_activa = False
        promo_segundos = None
        if self.promo_inicio and self.promo_fin:
            promo_activa = self.promo_inicio <= now <= self.promo_fin
            if promo_activa and self.promo_fin > now:
                promo_segundos = int((self.promo_fin - now).total_seconds())
        
        # ═══════════════════════════════════════
        # MÉTRICAS
        # ═══════════════════════════════════════
        rating = float(self.rating_promedio) if self.rating_promedio else 0
        reviews = self.total_reviews or 0
        visitas = self.visitas_7_dias or 0
        velocidad = float(self.velocidad_venta or 0)
        
        # ═══════════════════════════════════════
        # BADGES MANUALES (desde JSON + legacy)
        # ═══════════════════════════════════════
        badges_manuales = self.get_badges_manuales()
        
        return {
            # ═══════════════════════════════════════
            # BADGES AUTOMÁTICOS
            # ═══════════════════════════════════════
            "nuevo": es_nuevo,
            "descuento": tiene_descuento,
            "descuento_porcentaje": descuento_porcentaje,
            "descuento_ahorro": descuento_ahorro,
            "agotado": es_agotado,
            "ultima_unidad": es_ultima_unidad,
            "ultimas_unidades": es_ultimas_unidades,
            "stock_bajo": 0 < stock <= (self.stock_minimo or 5),
            "mejor_valorado": rating >= 4.5 and reviews >= 5,
            "popular": visitas >= 50,
            "vende_rapido": velocidad >= 1.0,
            "precio_minimo": precio_min is not None and precio_actual <= precio_min,
            
            # ═══════════════════════════════════════
            # BADGES MANUALES (desde badges_data JSON)
            # ═══════════════════════════════════════
            "destacado": badges_manuales.get("destacado", False),
            "mas_vendido": badges_manuales.get("mas_vendido", False),
            "envio_gratis": badges_manuales.get("envio_gratis", False),
            "pre_orden": badges_manuales.get("pre_orden", False),
            "edicion_limitada": badges_manuales.get("edicion_limitada", False),
            "oferta_flash": badges_manuales.get("oferta_flash", False),
            "combo": badges_manuales.get("combo", False),
            "garantia_extendida": badges_manuales.get("garantia_extendida", False),
            "eco_friendly": badges_manuales.get("eco_friendly", False),
            "badge_personalizado": badges_manuales.get("badge_personalizado"),
            
            # ═══════════════════════════════════════
            # PROMOCIÓN
            # ═══════════════════════════════════════
            "promo_activa": promo_activa,
            "promo_texto": self.promo_badge_texto if promo_activa else None,
            "promo_segundos_restantes": promo_segundos,
            
            # ═══════════════════════════════════════
            # MÉTRICAS (social proof)
            # ═══════════════════════════════════════
            "rating": rating,
            "total_reviews": reviews,
            "total_ventas": self.total_ventas or 0,
            "ventas_30_dias": self.ventas_30_dias or 0,
            "visitas_7_dias": visitas
        }
    
    # ==========================================
    # SERIALIZACIÓN
    # ==========================================
    def to_dict(self):
        """
        Serializa el producto a diccionario.
        Compatible con Inventario PRO v2.3 y Tienda Pública.
        """
        imagenes_lista = self._parse_json_field(self.imagenes, [])
        videos_lista = self._parse_json_field(self.videos, [])
        etiquetas_lista = self._parse_json_field(self.etiquetas, [])
        
        # ★ Calcular todos los badges
        badges = self.calcular_badges()
        
        return {
            # IDENTIFICADORES
            "id": self.id_producto,
            "id_producto": self.id_producto,
            
            # INFORMACIÓN BÁSICA
            "nombre": self.nombre,
            "descripcion": self.descripcion or "",
            
            # PRECIOS Y COSTOS
            "precio": float(self.precio) if self.precio else 0,
            "precio_original": float(self.precio_original) if self.precio_original else None,
            "costo": float(self.costo) if self.costo else 0,
            "margen_utilidad": self.get_margen_utilidad(),
            "ganancia_unitaria": self.get_ganancia_unitaria(),
            
            # IDENTIFICACIÓN TÉCNICA
            "sku": self.referencia_sku,
            "referencia_sku": self.referencia_sku,
            "codigo_barras": self.codigo_barras or "",
            "barcode": self.codigo_barras or "",
            
            # MULTIMEDIA
            "imagen_url": self.imagen_url,
            "imagen": self.imagen_url,
            "imagenes": imagenes_lista,
            "videos": videos_lista,
            "youtube_links": videos_lista,
            
            # CATEGORIZACIÓN
            "categoria": self.categoria,
            "plan": self.plan,
            "etiquetas": etiquetas_lista,
            
            # INVENTARIO
            "stock": self.stock or 0,
            "stock_minimo": self.stock_minimo or 5,
            "stock_critico": self.stock_critico or 2,
            "stock_bajo": self.stock_bajo or 10,
            "necesita_reabastecimiento": self.necesita_reabastecimiento(),
            "nivel_stock": self.nivel_stock(),
            
            # ★ BADGES COMPLETOS (v2.3)
            "badges": badges,
            
            # Atajos para compatibilidad frontend
            "nuevo": badges["nuevo"],
            "destacado": badges["destacado"],
            "mas_vendido": badges["mas_vendido"],
            "envio_gratis": badges["envio_gratis"],
            "tiene_descuento": badges["descuento"],
            "descuento_porcentaje": badges["descuento_porcentaje"],
            
            # MÉTRICAS
            "rating": badges["rating"],
            "total_reviews": badges["total_reviews"],
            "total_ventas": badges["total_ventas"],
            "ventas_30_dias": badges["ventas_30_dias"],
            "visitas_7_dias": badges["visitas_7_dias"],
            
            # ESTADO
            "activo": self.activo,
            "estado_publicacion": self.estado_publicacion,
            
            # RELACIONES
            "negocio_id": self.negocio_id,
            "sucursal_id": self.sucursal_id,
            "usuario_id": self.usuario_id,
            
            # FECHAS
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