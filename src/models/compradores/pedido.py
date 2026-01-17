"""
TRAYECTORIA ECOSISTEMA
Modelo: Pedido
Descripción: Pedidos realizados en las tiendas del ecosistema
Versión: 2.0 - Actualizado para checkout con WhatsApp
"""

from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from src.models.database import db


class Pedido(db.Model):
    """
    Modelo de Pedido.
    
    Representa una orden de compra realizada por un comprador
    en una tienda del ecosistema Trayectoria.
    """
    __tablename__ = 'pedidos'
    
    # ==========================================
    # ESTADOS DEL PEDIDO
    # ==========================================
    ESTADOS = {
        'pendiente': {'label': 'Pendiente', 'color': '#f59e0b', 'icon': '⏳'},
        'confirmado': {'label': 'Confirmado', 'color': '#3b82f6', 'icon': '✓'},
        'preparando': {'label': 'Preparando', 'color': '#8b5cf6', 'icon': '📦'},
        'enviado': {'label': 'Enviado', 'color': '#6366f1', 'icon': '🚚'},
        'en_camino': {'label': 'En Camino', 'color': '#0ea5e9', 'icon': '🛵'},
        'entregado': {'label': 'Entregado', 'color': '#10b981', 'icon': '✅'},
        'cancelado': {'label': 'Cancelado', 'color': '#ef4444', 'icon': '❌'},
        'devuelto': {'label': 'Devuelto', 'color': '#64748b', 'icon': '↩️'}
    }
    
    ESTADOS_PAGO = {
        'pendiente': {'label': 'Pendiente', 'color': '#f59e0b'},
        'pagado': {'label': 'Pagado', 'color': '#10b981'},
        'reembolsado': {'label': 'Reembolsado', 'color': '#64748b'}
    }
    
    METODOS_PAGO = {
        'efectivo': {'label': 'Efectivo (Contra entrega)', 'icon': '💵'},
        'nequi': {'label': 'Nequi', 'icon': '📱'},
        'daviplata': {'label': 'Daviplata', 'icon': '📱'},
        'transferencia': {'label': 'Transferencia Bancaria', 'icon': '🏦'},
        'tarjeta': {'label': 'Tarjeta Débito/Crédito', 'icon': '💳'},
        'pse': {'label': 'PSE', 'icon': '🏦'}
    }
    
    # ==========================================
    # CAMPOS PRINCIPALES
    # ==========================================
    id_pedido = db.Column(db.Integer, primary_key=True)
    codigo_pedido = db.Column(db.String(30), unique=True, nullable=False, index=True)
    
    # ==========================================
    # RELACIONES
    # ==========================================
    comprador_id = db.Column(
        db.Integer,
        db.ForeignKey('compradores.id_comprador'),
        index=True
    )
    negocio_id = db.Column(db.Integer, nullable=False, index=True)
    sucursal_id = db.Column(db.Integer)
    direccion_id = db.Column(
        db.Integer,
        db.ForeignKey('direcciones_comprador.id_direccion')
    )
    
    # ==========================================
    # SNAPSHOTS (datos al momento del pedido)
    # ==========================================
    datos_comprador = db.Column(JSONB, nullable=False)
    # {nombre, correo, telefono, documento}
    
    datos_envio = db.Column(JSONB, nullable=False)
    # {tipo, ciudad, departamento, direccion, barrio, referencias, etc.}
    
    datos_negocio = db.Column(JSONB)
    # {nombre_negocio, whatsapp, slug, logo_url}
    
    # ==========================================
    # PRODUCTOS
    # ==========================================
    productos = db.Column(JSONB, nullable=False)
    # [{id, nombre, precio, cantidad, subtotal, imagen_url, categoria}]
    
    # ==========================================
    # TOTALES
    # ==========================================
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    descuento = db.Column(db.Numeric(12, 2), default=0)
    costo_envio = db.Column(db.Numeric(12, 2), default=0)
    impuestos = db.Column(db.Numeric(12, 2), default=0)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    
    # ==========================================
    # PAGO
    # ==========================================
    metodo_pago = db.Column(db.String(50))
    estado_pago = db.Column(db.String(30), default='pendiente')
    referencia_pago = db.Column(db.String(100))  # ID de transacción
    
    # ==========================================
    # ★ NUEVO: MÉTODO DE CONTACTO
    # ==========================================
    metodo_contacto = db.Column(db.String(20), default='whatsapp')
    # Valores: whatsapp, app, email
    # Indica cómo se contactó/confirmará con el cliente
    
    # ==========================================
    # ESTADO DEL PEDIDO
    # ==========================================
    estado = db.Column(db.String(50), default='pendiente', index=True)
    
    # ==========================================
    # NOTAS
    # ==========================================
    notas_cliente = db.Column(db.Text)  # Instrucciones especiales
    notas_vendedor = db.Column(db.Text)  # Notas internas
    
    # ==========================================
    # SEGUIMIENTO DE FECHAS
    # ==========================================
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    fecha_confirmacion = db.Column(db.DateTime)
    fecha_preparacion = db.Column(db.DateTime)
    fecha_envio = db.Column(db.DateTime)
    fecha_entrega = db.Column(db.DateTime)
    fecha_cancelacion = db.Column(db.DateTime)
    
    motivo_cancelacion = db.Column(db.Text)
    
    # ==========================================
    # METADATA
    # ==========================================
    ip_cliente = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    origen = db.Column(db.String(50), default='web')  # web, whatsapp, app
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ==========================================
    # RELACIÓN CON HISTORIAL
    # ==========================================
    historial = db.relationship(
        'PedidoHistorial',
        backref='pedido',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='PedidoHistorial.fecha.desc()'
    )
    
    # ==========================================
    # PROPIEDADES
    # ==========================================
    @property
    def estado_info(self):
        """Retorna información del estado actual."""
        return self.ESTADOS.get(self.estado, self.ESTADOS['pendiente'])
    
    @property
    def estado_pago_info(self):
        """Retorna información del estado de pago."""
        return self.ESTADOS_PAGO.get(self.estado_pago, self.ESTADOS_PAGO['pendiente'])
    
    @property
    def metodo_pago_info(self):
        """Retorna información del método de pago."""
        return self.METODOS_PAGO.get(self.metodo_pago, {'label': self.metodo_pago, 'icon': '💰'})
    
    @property
    def num_productos(self):
        """Cantidad total de productos."""
        if not self.productos:
            return 0
        return sum(p.get('cantidad', 1) for p in self.productos)
    
    @property
    def puede_cancelar(self):
        """Indica si el pedido puede ser cancelado."""
        return self.estado in ['pendiente', 'confirmado']
    
    @property
    def cliente_nombre(self):
        """Nombre del cliente desde el snapshot."""
        return self.datos_comprador.get('nombre', 'Cliente')
    
    @property
    def cliente_telefono(self):
        """Teléfono del cliente desde el snapshot."""
        return self.datos_comprador.get('telefono', '')
    
    @property
    def ciudad_envio(self):
        """Ciudad de envío desde el snapshot."""
        return self.datos_envio.get('ciudad', '')
    
    # ★ NUEVO: Propiedades para compatibilidad
    @property
    def numero_pedido(self):
        """Alias de codigo_pedido."""
        return self.codigo_pedido
    
    # ==========================================
    # MÉTODOS DE ESTADO
    # ==========================================
    def cambiar_estado(self, nuevo_estado, usuario_id=None, comentario=None):
        """Cambia el estado del pedido y registra en historial."""
        if nuevo_estado not in self.ESTADOS:
            raise ValueError(f"Estado inválido: {nuevo_estado}")
        
        estado_anterior = self.estado
        self.estado = nuevo_estado
        
        # Actualizar fecha según el estado
        ahora = datetime.utcnow()
        if nuevo_estado == 'confirmado':
            self.fecha_confirmacion = ahora
        elif nuevo_estado == 'preparando':
            self.fecha_preparacion = ahora
        elif nuevo_estado == 'enviado':
            self.fecha_envio = ahora
        elif nuevo_estado == 'entregado':
            self.fecha_entrega = ahora
        elif nuevo_estado == 'cancelado':
            self.fecha_cancelacion = ahora
        
        # Registrar en historial
        historial = PedidoHistorial(
            pedido_id=self.id_pedido,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            comentario=comentario,
            usuario_id=usuario_id
        )
        db.session.add(historial)
        
        return True
    
    def cancelar(self, motivo, usuario_id=None):
        """Cancela el pedido."""
        if not self.puede_cancelar:
            raise ValueError("Este pedido no puede ser cancelado")
        
        self.motivo_cancelacion = motivo
        self.cambiar_estado('cancelado', usuario_id, f"Cancelado: {motivo}")
    
    def marcar_pagado(self, referencia=None):
        """Marca el pedido como pagado."""
        self.estado_pago = 'pagado'
        if referencia:
            self.referencia_pago = referencia
    
    # ==========================================
    # SERIALIZACIÓN
    # ==========================================
    def to_dict(self, include_historial=False):
        """Serializa el pedido a diccionario."""
        data = {
            'id_pedido': self.id_pedido,
            'codigo_pedido': self.codigo_pedido,
            'numero_pedido': self.codigo_pedido,  # ★ NUEVO: Alias
            
            # Relaciones
            'comprador_id': self.comprador_id,
            'negocio_id': self.negocio_id,
            'sucursal_id': self.sucursal_id,
            
            # Datos snapshot
            'datos_comprador': self.datos_comprador,
            'datos_envio': self.datos_envio,
            'datos_negocio': self.datos_negocio,
            
            # Productos
            'productos': self.productos,
            'num_productos': self.num_productos,
            
            # Totales
            'subtotal': float(self.subtotal or 0),
            'descuento': float(self.descuento or 0),
            'costo_envio': float(self.costo_envio or 0),
            'impuestos': float(self.impuestos or 0),
            'total': float(self.total or 0),
            
            # Pago
            'metodo_pago': self.metodo_pago,
            'metodo_pago_label': self.metodo_pago_info['label'],
            'estado_pago': self.estado_pago,
            'estado_pago_info': self.estado_pago_info,
            'referencia_pago': self.referencia_pago,
            
            # ★ NUEVO: Método de contacto
            'metodo_contacto': self.metodo_contacto,
            
            # Estado
            'estado': self.estado,
            'estado_info': self.estado_info,
            'puede_cancelar': self.puede_cancelar,
            
            # Notas
            'notas_cliente': self.notas_cliente,
            'notas_vendedor': self.notas_vendedor,
            
            # Fechas
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None,
            'fecha_confirmacion': self.fecha_confirmacion.isoformat() if self.fecha_confirmacion else None,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else None,
            'fecha_entrega': self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            
            # Resumen
            'cliente_nombre': self.cliente_nombre,
            'cliente_telefono': self.cliente_telefono,
            'ciudad_envio': self.ciudad_envio,
            
            # Origen
            'origen': self.origen
        }
        
        if include_historial:
            data['historial'] = [h.to_dict() for h in self.historial.all()]
        
        return data
    
    def to_dict_lista(self):
        """Versión resumida para listas."""
        return {
            'id_pedido': self.id_pedido,
            'codigo_pedido': self.codigo_pedido,
            'numero_pedido': self.codigo_pedido,  # ★ NUEVO: Alias
            'cliente_nombre': self.cliente_nombre,
            'cliente_telefono': self.cliente_telefono,
            'ciudad_envio': self.ciudad_envio,
            'num_productos': self.num_productos,
            'total': float(self.total or 0),
            'estado': self.estado,
            'estado_info': self.estado_info,
            'metodo_pago': self.metodo_pago,
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None
        }
    
    # ==========================================
    # MÉTODOS DE CLASE
    # ==========================================
    @classmethod
    def generar_codigo(cls, negocio_id, prefijo='PED'):
        """Genera un código único para el pedido."""
        año = datetime.utcnow().strftime('%Y')
        
        # Contar pedidos del negocio en este año
        count = cls.query.filter(
            cls.negocio_id == negocio_id,
            cls.codigo_pedido.like(f'{prefijo}-{año}-%')
        ).count()
        
        secuencial = count + 1
        return f"{prefijo}-{año}-{secuencial:04d}"
    
    # ★ NUEVO: Alias para compatibilidad
    @classmethod
    def generar_numero_pedido(cls, negocio_id, prefijo='PED'):
        """Alias de generar_codigo() para compatibilidad."""
        return cls.generar_codigo(negocio_id, prefijo)
    
    @classmethod
    def crear_pedido(cls, comprador, direccion, negocio_data, productos, 
                     subtotal, costo_envio, total, metodo_pago, 
                     notas_cliente=None, metodo_contacto='whatsapp', origen='web'):  # ★ NUEVO parámetro
        """Crea un nuevo pedido."""
        
        # Generar código
        prefijo = negocio_data.get('slug', 'PED')[:3].upper()
        codigo = cls.generar_codigo(negocio_data['id'], prefijo)
        
        pedido = cls(
            codigo_pedido=codigo,
            comprador_id=comprador.id_comprador if comprador else None,
            negocio_id=negocio_data['id'],
            direccion_id=direccion.id_direccion if hasattr(direccion, 'id_direccion') else None,
            
            datos_comprador=comprador.to_dict_pedido() if hasattr(comprador, 'to_dict_pedido') else comprador,
            datos_envio=direccion.to_dict_pedido() if hasattr(direccion, 'to_dict_pedido') else direccion,
            datos_negocio=negocio_data,
            
            productos=productos,
            subtotal=subtotal,
            costo_envio=costo_envio,
            total=total,
            metodo_pago=metodo_pago,
            metodo_contacto=metodo_contacto,  # ★ NUEVO
            notas_cliente=notas_cliente,
            origen=origen
        )
        
        db.session.add(pedido)
        
        # Actualizar estadísticas del comprador
        if comprador and hasattr(comprador, 'registrar_compra'):
            comprador.registrar_compra(total)
        
        return pedido
    
    def __repr__(self):
        return f'<Pedido {self.codigo_pedido}: {self.estado}>'


class PedidoHistorial(db.Model):
    """
    Historial de cambios de estado del pedido.
    """
    __tablename__ = 'pedido_historial'
    
    id_historial = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey('pedidos.id_pedido', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    estado_anterior = db.Column(db.String(50))
    estado_nuevo = db.Column(db.String(50), nullable=False)
    comentario = db.Column(db.Text)
    usuario_id = db.Column(db.Integer)  # Quién hizo el cambio
    
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id_historial': self.id_historial,
            'estado_anterior': self.estado_anterior,
            'estado_nuevo': self.estado_nuevo,
            'comentario': self.comentario,
            'usuario_id': self.usuario_id,
            'fecha': self.fecha.isoformat() if self.fecha else None
        }
    
    def __repr__(self):
        return f'<PedidoHistorial {self.estado_anterior} -> {self.estado_nuevo}>'