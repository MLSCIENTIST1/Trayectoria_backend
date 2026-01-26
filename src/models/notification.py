"""
TUKOMERCIO - Sistema de Notificaciones Unificado
Versión: 2.1 (Corregido)
Soporta:
  - Notificaciones Usuario ↔ Usuario (red social)
  - Notificaciones Sistema → Negocio (operativas)
"""

import logging
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from src.models.database import db

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    file_handler = logging.FileHandler('notifications.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


class Notification(db.Model):
    """
    Modelo unificado de notificaciones.
    
    Tipos de uso:
    1. Social (usuario a usuario): sender_id + user_id
    2. Negocio (sistema a negocio): negocio_id + user_id (del dueño)
    """
    __tablename__ = "notification"

    # ==========================================
    # TIPOS DE NOTIFICACIÓN
    # ==========================================
    TIPOS = {
        # Operativas (Sistema → Negocio)
        'nuevo_pedido': {'label': 'Nuevo Pedido', 'icon': '🛒', 'color': '#10b981', 'categoria': 'pedidos'},
        'pedido_pagado': {'label': 'Pago Recibido', 'icon': '💰', 'color': '#3b82f6', 'categoria': 'pedidos'},
        'pedido_cancelado': {'label': 'Pedido Cancelado', 'icon': '❌', 'color': '#ef4444', 'categoria': 'pedidos'},
        'pedido_enviado': {'label': 'Pedido Enviado', 'icon': '🚚', 'color': '#6366f1', 'categoria': 'pedidos'},
        'pedido_entregado': {'label': 'Pedido Entregado', 'icon': '✅', 'color': '#10b981', 'categoria': 'pedidos'},
        'stock_bajo': {'label': 'Stock Bajo', 'icon': '⚠️', 'color': '#f59e0b', 'categoria': 'inventario'},
        'stock_agotado': {'label': 'Sin Stock', 'icon': '🚫', 'color': '#ef4444', 'categoria': 'inventario'},
        'nuevo_cliente': {'label': 'Nuevo Cliente', 'icon': '👤', 'color': '#8b5cf6', 'categoria': 'clientes'},
        'meta_alcanzada': {'label': 'Meta Alcanzada', 'icon': '🎯', 'color': '#10b981', 'categoria': 'ventas'},
        
        # Sociales (Usuario ↔ Usuario)
        'solicitud_amistad': {'label': 'Solicitud', 'icon': '👋', 'color': '#3b82f6', 'categoria': 'social'},
        'mensaje': {'label': 'Mensaje', 'icon': '💬', 'color': '#6366f1', 'categoria': 'social'},
        'mencion': {'label': 'Mención', 'icon': '@', 'color': '#8b5cf6', 'categoria': 'social'},
        'seguidor_nuevo': {'label': 'Nuevo Seguidor', 'icon': '➕', 'color': '#10b981', 'categoria': 'social'},
        
        # Sistema
        'sistema': {'label': 'Sistema', 'icon': '⚙️', 'color': '#64748b', 'categoria': 'sistema'},
        'recordatorio': {'label': 'Recordatorio', 'icon': '🔔', 'color': '#f59e0b', 'categoria': 'sistema'},
        'actualizacion': {'label': 'Actualización', 'icon': '🆕', 'color': '#3b82f6', 'categoria': 'sistema'},
        'default_type': {'label': 'Notificación', 'icon': '🔔', 'color': '#64748b', 'categoria': 'sistema'}
    }
    
    PRIORIDADES = {
        'alta': {'label': 'Alta', 'color': '#ef4444'},
        'media': {'label': 'Media', 'color': '#f59e0b'},
        'baja': {'label': 'Baja', 'color': '#6b7280'}
    }

    # ==========================================
    # CAMPOS PRINCIPALES
    # ==========================================
    id = Column(Integer, primary_key=True)
    
    # ★ CORREGIDO: user_id ahora es nullable (para notificaciones de negocio sin usuario específico)
    user_id = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=True, index=True)
    
    # Remitente (opcional - NULL para notificaciones del sistema)
    sender_id = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=True)
    
    # Contexto de negocio
    negocio_id = Column(Integer, ForeignKey('negocios.id_negocio'), nullable=True, index=True)
    
    # ==========================================
    # CONTENIDO
    # ==========================================
    type = Column(String(50), default='default_type', index=True)
    titulo = Column(String(255), nullable=True)
    message = Column(Text, nullable=True)
    
    # ==========================================
    # REFERENCIA A OBJETO RELACIONADO
    # ==========================================
    referencia_tipo = Column(String(50), nullable=True)  # 'pedido', 'producto', 'cliente'
    referencia_id = Column(Integer, nullable=True)
    action_url = Column(String(500), nullable=True)
    
    # ==========================================
    # ESTADO Y PRIORIDAD
    # ==========================================
    is_read = Column(Boolean, default=False, index=True)
    is_accepted = Column(Boolean, default=False)
    prioridad = Column(String(20), default='media')
    
    # ==========================================
    # CAMPOS LEGACY (compatibilidad red social)
    # ==========================================
    request_id = Column(Integer, nullable=True)
    response = Column(String(255), nullable=True)
    request_message_details = Column(String(255), nullable=True)
    questions = Column(String(255), nullable=True)
    
    # ==========================================
    # DATOS EXTRA Y TIMESTAMPS
    # ==========================================
    extra_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    fecha_lectura = Column(DateTime, nullable=True)
    
    # ==========================================
    # RELACIONES (lazy loading para evitar circular imports)
    # ==========================================
    sender = relationship('Usuario', foreign_keys=[sender_id], 
                          back_populates='sent_notifications', lazy='select')
    receiver = relationship('Usuario', foreign_keys=[user_id], 
                            back_populates='received_notifications', lazy='select')
    negocio = relationship('Negocio', foreign_keys=[negocio_id], 
                           backref='notificaciones', lazy='select')
    messages = relationship('Message', back_populates='notification', lazy='select')

    # ==========================================
    # PROPIEDADES
    # ==========================================
    @property
    def tipo_info(self):
        """Retorna información del tipo de notificación."""
        return self.TIPOS.get(self.type, self.TIPOS['default_type'])
    
    @property
    def prioridad_info(self):
        """Retorna información de prioridad."""
        return self.PRIORIDADES.get(self.prioridad, self.PRIORIDADES['media'])
    
    @property
    def es_de_negocio(self):
        """Indica si es una notificación de negocio."""
        return self.negocio_id is not None
    
    @property
    def es_social(self):
        """Indica si es una notificación social."""
        return self.sender_id is not None and self.negocio_id is None
    
    @property
    def tiempo_transcurrido(self):
        """Retorna tiempo desde creación en formato legible."""
        if not self.timestamp:
            return "ahora"
        
        delta = datetime.utcnow() - self.timestamp
        
        if delta.days > 30:
            return f"hace {delta.days // 30}mes"
        elif delta.days > 0:
            return f"hace {delta.days}d"
        elif delta.seconds >= 3600:
            return f"hace {delta.seconds // 3600}h"
        elif delta.seconds >= 60:
            return f"hace {delta.seconds // 60}m"
        else:
            return "ahora"

    # ==========================================
    # MÉTODOS DE INSTANCIA
    # ==========================================
    def marcar_leida(self):
        """Marca la notificación como leída."""
        if not self.is_read:
            self.is_read = True
            self.fecha_lectura = datetime.utcnow()
    
    def to_dict(self):
        """Serializa la notificación completa."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sender_id': self.sender_id,
            'negocio_id': self.negocio_id,
            
            # Contenido
            'type': self.type,
            'tipo_info': self.tipo_info,
            'titulo': self.titulo,
            'message': self.message,
            
            # Referencia
            'referencia_tipo': self.referencia_tipo,
            'referencia_id': self.referencia_id,
            'action_url': self.action_url,
            
            # Estado
            'is_read': self.is_read,
            'is_accepted': self.is_accepted,
            'prioridad': self.prioridad,
            'prioridad_info': self.prioridad_info,
            
            # Tiempo
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'fecha_creacion': self.timestamp.isoformat() if self.timestamp else None,
            'tiempo_transcurrido': self.tiempo_transcurrido,
            'fecha_lectura': self.fecha_lectura.isoformat() if self.fecha_lectura else None,
            
            # Extra
            'extra_data': self.extra_data,
            
            # Categoría
            'es_de_negocio': self.es_de_negocio,
            'es_social': self.es_social
        }
    
    def to_dict_mini(self):
        """Versión compacta para listas/campanita."""
        return {
            'id': self.id,
            'type': self.type,
            'icon': self.tipo_info['icon'],
            'color': self.tipo_info['color'],
            'titulo': self.titulo or self.tipo_info['label'],
            'mensaje': self.message[:100] if self.message else None,
            'is_read': self.is_read,
            'leida': self.is_read,
            'tiempo': self.tiempo_transcurrido,
            'fecha_creacion': self.timestamp.isoformat() if self.timestamp else None,
            'action_url': self.action_url,
            'prioridad': self.prioridad
        }

    # ==========================================
    # HELPER: Obtener user_id del dueño del negocio
    # ==========================================
    @staticmethod
    def _obtener_user_id_de_negocio(negocio_id):
        """Obtiene el user_id del dueño de un negocio."""
        try:
            from src.models.negocio import Negocio
            negocio = Negocio.query.get(negocio_id)
            if negocio:
                return negocio.usuario_id
        except Exception as e:
            logger.warning(f"No se pudo obtener user_id del negocio {negocio_id}: {e}")
        return None

    # ==========================================
    # MÉTODOS DE CLASE - CREAR NOTIFICACIONES SOCIALES
    # ==========================================
    @classmethod
    def create_notification(cls, user_id, sender_id, request_id, message, params=None, extra_data=None):
        """Método legacy para notificaciones sociales."""
        try:
            notification_type = params.get('type', 'default_type') if params else 'default_type'
            titulo = params.get('titulo') if params else None
            
            notification = cls(
                user_id=user_id,
                sender_id=sender_id,
                request_id=request_id,
                message=message,
                titulo=titulo,
                type=notification_type,
                extra_data=extra_data
            )
            db.session.add(notification)
            db.session.commit()
            logger.info(f"Notificación social creada: {notification}")
            return notification
        except Exception as e:
            logger.error(f"Error al crear notificación social: {e}", exc_info=True)
            db.session.rollback()
            raise

    @classmethod
    def accept_notification(cls, notification_id):
        """Acepta una notificación (solicitudes)."""
        try:
            notification = cls.query.get(notification_id)
            if not notification:
                logger.error(f"No se encontró la notificación con ID {notification_id}.")
                return False
            if notification.is_accepted:
                logger.info(f"La notificación con ID {notification_id} ya estaba aceptada.")
                return True
            notification.is_accepted = True
            db.session.commit()
            db.session.refresh(notification)
            logger.info(f"Notificación con ID {notification_id} aceptada.")
            return True
        except Exception as e:
            logger.error(f"Error al aceptar la notificación: {e}", exc_info=True)
            db.session.rollback()
            return False

    # ==========================================
    # ★ MÉTODOS DE CLASE - NOTIFICACIONES DE NEGOCIO
    # ==========================================
    @classmethod
    def crear_notificacion_pedido(cls, pedido, user_id=None):
        """
        Crea notificación cuando llega un pedido nuevo.
        
        Args:
            pedido: Objeto Pedido
            user_id: ID del usuario a notificar (opcional, se obtiene del negocio)
        """
        try:
            # ★ CORREGIDO: Obtener user_id del dueño si no se proporciona
            if user_id is None:
                user_id = cls._obtener_user_id_de_negocio(pedido.negocio_id)
            
            notif = cls(
                user_id=user_id,
                negocio_id=pedido.negocio_id,
                type='nuevo_pedido',
                titulo=f'Nuevo pedido #{pedido.codigo_pedido}',
                message=f'{pedido.cliente_nombre} - ${pedido.total:,.0f} COP',
                referencia_tipo='pedido',
                referencia_id=pedido.id_pedido,
                prioridad='alta',
                extra_data={
                    'codigo_pedido': pedido.codigo_pedido,
                    'cliente': pedido.cliente_nombre,
                    'telefono': getattr(pedido, 'cliente_telefono', None),
                    'total': float(pedido.total) if pedido.total else 0,
                    'num_productos': getattr(pedido, 'num_productos', None),
                    'metodo_pago': getattr(pedido, 'metodo_pago', None)
                },
                action_url=f'modulos_crear_tienda/pedidos.html?id={pedido.id_pedido}'
            )
            db.session.add(notif)
            logger.info(f"Notificación de pedido creada: {pedido.codigo_pedido}")
            return notif
        except Exception as e:
            logger.error(f"Error al crear notificación de pedido: {e}", exc_info=True)
            raise
    
    @classmethod
    def crear_notificacion_stock_bajo(cls, producto, negocio_id, user_id=None):
        """Crea notificación de stock bajo."""
        try:
            if user_id is None:
                user_id = cls._obtener_user_id_de_negocio(negocio_id)
            
            notif = cls(
                user_id=user_id,
                negocio_id=negocio_id,
                type='stock_bajo',
                titulo=f'Stock bajo: {producto.nombre[:50]}',
                message=f'Solo quedan {producto.stock} unidades',
                referencia_tipo='producto',
                referencia_id=producto.id_producto,
                prioridad='media',
                extra_data={
                    'producto': producto.nombre,
                    'stock_actual': producto.stock,
                    'sku': getattr(producto, 'sku', None)
                },
                action_url=f'modulos_crear_tienda/inventario.html?id={producto.id_producto}'
            )
            db.session.add(notif)
            logger.info(f"Notificación de stock bajo: {producto.nombre}")
            return notif
        except Exception as e:
            logger.error(f"Error al crear notificación de stock: {e}", exc_info=True)
            raise
    
    @classmethod
    def crear_notificacion_cambio_estado_pedido(cls, pedido, estado_anterior, user_id=None):
        """Crea notificación cuando cambia el estado de un pedido."""
        tipo_map = {
            'confirmado': 'pedido_pagado',
            'enviado': 'pedido_enviado',
            'entregado': 'pedido_entregado',
            'cancelado': 'pedido_cancelado'
        }
        
        tipo = tipo_map.get(pedido.estado, 'sistema')
        
        try:
            if user_id is None:
                user_id = cls._obtener_user_id_de_negocio(pedido.negocio_id)
            
            estado_label = pedido.estado.capitalize()
            if hasattr(pedido, 'estado_info'):
                estado_label = pedido.estado_info.get('label', estado_label)
            
            notif = cls(
                user_id=user_id,
                negocio_id=pedido.negocio_id,
                type=tipo,
                titulo=f'Pedido #{pedido.codigo_pedido} - {estado_label}',
                message=f'Estado: {estado_anterior} → {pedido.estado}',
                referencia_tipo='pedido',
                referencia_id=pedido.id_pedido,
                prioridad='media' if pedido.estado != 'cancelado' else 'alta',
                extra_data={
                    'codigo_pedido': pedido.codigo_pedido,
                    'estado_anterior': estado_anterior,
                    'estado_nuevo': pedido.estado
                },
                action_url=f'modulos_crear_tienda/pedidos.html?id={pedido.id_pedido}'
            )
            db.session.add(notif)
            logger.info(f"Notificación de cambio de estado: {pedido.codigo_pedido}")
            return notif
        except Exception as e:
            logger.error(f"Error al crear notificación de estado: {e}", exc_info=True)
            raise

    @classmethod
    def crear_notificacion_generica(cls, negocio_id, titulo, mensaje, 
                                     tipo='sistema', user_id=None,
                                     referencia_tipo=None, referencia_id=None, 
                                     action_url=None, prioridad='media', extra_data=None):
        """Crea una notificación genérica."""
        try:
            if user_id is None:
                user_id = cls._obtener_user_id_de_negocio(negocio_id)
            
            notif = cls(
                user_id=user_id,
                negocio_id=negocio_id,
                type=tipo,
                titulo=titulo,
                message=mensaje,
                referencia_tipo=referencia_tipo,
                referencia_id=referencia_id,
                action_url=action_url,
                prioridad=prioridad,
                extra_data=extra_data
            )
            db.session.add(notif)
            logger.info(f"Notificación genérica creada: {titulo}")
            return notif
        except Exception as e:
            logger.error(f"Error al crear notificación genérica: {e}", exc_info=True)
            raise

    # ==========================================
    # ★ MÉTODOS DE CONSULTA
    # ==========================================
    @classmethod
    def contar_no_leidas(cls, user_id=None, negocio_id=None):
        """Cuenta notificaciones no leídas."""
        query = cls.query.filter_by(is_read=False)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        if negocio_id:
            query = query.filter_by(negocio_id=negocio_id)
        
        return query.count()
    
    @classmethod
    def obtener_recientes(cls, user_id=None, negocio_id=None, limite=20, solo_no_leidas=False):
        """Obtiene notificaciones recientes."""
        query = cls.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        if negocio_id:
            query = query.filter_by(negocio_id=negocio_id)
        if solo_no_leidas:
            query = query.filter_by(is_read=False)
        
        return query.order_by(
            cls.is_read.asc(),  # No leídas primero
            cls.timestamp.desc()
        ).limit(limite).all()
    
    @classmethod
    def marcar_todas_leidas(cls, user_id=None, negocio_id=None):
        """Marca todas las notificaciones como leídas."""
        query = cls.query.filter_by(is_read=False)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        if negocio_id:
            query = query.filter_by(negocio_id=negocio_id)
        
        ahora = datetime.utcnow()
        count = query.update({
            'is_read': True,
            'fecha_lectura': ahora
        })
        
        return count
    
    @classmethod
    def obtener_por_categoria(cls, user_id=None, negocio_id=None, categoria=None, limite=20):
        """Obtiene notificaciones filtradas por categoría."""
        tipos_por_categoria = {}
        for tipo, info in cls.TIPOS.items():
            cat = info['categoria']
            if cat not in tipos_por_categoria:
                tipos_por_categoria[cat] = []
            tipos_por_categoria[cat].append(tipo)
        
        query = cls.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        if negocio_id:
            query = query.filter_by(negocio_id=negocio_id)
        if categoria and categoria in tipos_por_categoria:
            query = query.filter(cls.type.in_(tipos_por_categoria[categoria]))
        
        return query.order_by(cls.timestamp.desc()).limit(limite).all()

    def __repr__(self):
        return f"<Notification id={self.id} type={self.type} negocio={self.negocio_id} is_read={self.is_read}>"