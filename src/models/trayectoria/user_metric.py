"""
BizFlow Studio - User Metric Model
Métricas del usuario (proyectos completados, tiempo promedio, etc.)
Sistema flexible de key-value para métricas
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logger = logging.getLogger(__name__)

class UserMetric(db.Model):
    __tablename__ = "user_metrics"
    
    # Índices para mejorar performance
    __table_args__ = (
        Index('idx_user_metric_key', 'usuario_id', 'metric_key'),
    )

    # Identificador
    id = Column(Integer, primary_key=True)
    
    # Usuario
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    
    # === MÉTRICA (SISTEMA KEY-VALUE FLEXIBLE) ===
    metric_key = Column(String(100), nullable=False)  # 'proyectos_completados', 'tiempo_promedio_dias', etc.
    metric_value = Column(Float, nullable=False, default=0.0)  # Valor numérico
    metric_display = Column(String(50), nullable=True)  # Cómo mostrarlo: "95", "12 días", "4.8 ⭐"
    
    # === INFORMACIÓN PARA UI ===
    metric_name = Column(String(100), nullable=False)  # "Proyectos Completados"
    metric_icon = Column(String(50), nullable=True)  # "briefcase-fill" (Bootstrap Icons)
    metric_color = Column(String(7), nullable=True)  # "#10b981"
    
    # === CAMBIO RECIENTE ===
    cambio_valor = Column(Float, nullable=True)  # +8, -2
    cambio_texto = Column(String(50), nullable=True)  # "+8 este mes"
    tipo_cambio = Column(String(20), nullable=True)  # 'positive', 'negative', 'neutral'
    
    # === VISIBILIDAD ===
    is_public = Column(Boolean, default=True)  # Si es visible públicamente
    is_system = Column(Boolean, default=False)  # Si es una métrica del sistema (no editable)
    
    # === ORDEN Y CATEGORÍA ===
    categoria = Column(String(50), nullable=True)  # 'rendimiento', 'calidad', 'velocidad'
    orden = Column(Integer, default=0)  # Orden de visualización
    
    # === METADATOS ===
    fecha_calculo = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # === RELACIONES ===
    usuario = relationship("Usuario", backref="metricas", lazy="joined")
    
    # Índice único por usuario y métrica
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'metric_key', name='unique_user_metric'),
    )
    
    def serialize(self):
        """Serializar para API"""
        return {
            "id": self.metric_key,
            "nombre": self.metric_name,
            "valor": self.metric_display or str(self.metric_value),
            "cambio": self.cambio_texto,
            "tipo_cambio": self.tipo_cambio,
            "icono": self.metric_icon,
            "color": self.metric_color,
            "visible": self.is_public,
            "sistema": self.is_system,
            "categoria": self.categoria
        }
    
    @staticmethod
    def inicializar_metricas_usuario(usuario_id):
        """
        Crea las métricas predeterminadas para un nuevo usuario
        
        Args:
            usuario_id: ID del usuario
        """
        metricas_config = [
            {
                'key': 'proyectos_completados',
                'name': 'Proyectos Completados',
                'value': 0,
                'display': '0',
                'icon': 'briefcase-fill',
                'color': '#10b981',
                'public': True,
                'system': False,
                'categoria': 'volumen'
            },
            {
                'key': 'tiempo_promedio_dias',
                'name': 'Tiempo Prom. Entrega',
                'value': 0,
                'display': '0 días',
                'icon': 'clock-fill',
                'color': '#3b82f6',
                'public': True,
                'system': False,
                'categoria': 'velocidad'
            },
            {
                'key': 'rating_promedio',
                'name': 'Rating Promedio',
                'value': 0,
                'display': '0 ⭐',
                'icon': 'star-fill',
                'color': '#ec4899',
                'public': True,
                'system': False,
                'categoria': 'calidad'
            },
            {
                'key': 'clientes_recurrentes',
                'name': 'Clientes Recurrentes',
                'value': 0,
                'display': '0',
                'icon': 'person-plus-fill',
                'color': '#6366f1',
                'public': True,
                'system': False,
                'categoria': 'fidelidad'
            },
            {
                'key': 'disputas',
                'name': 'Disputas',
                'value': 0,
                'display': '0',
                'icon': 'exclamation-triangle',
                'color': '#64748b',
                'public': False,
                'system': True,
                'categoria': 'riesgo'
            },
            {
                'key': 'cancelaciones',
                'name': 'Cancelaciones',
                'value': 0,
                'display': '0',
                'icon': 'x-octagon',
                'color': '#64748b',
                'public': False,
                'system': True,
                'categoria': 'riesgo'
            },
            {
                'key': 'tasa_exito',
                'name': 'Tasa de Éxito',
                'value': 0,
                'display': '0%',
                'icon': 'graph-up-arrow',
                'color': '#10b981',
                'public': True,
                'system': False,
                'categoria': 'rendimiento'
            },
            {
                'key': 'entregas_tiempo',
                'name': 'Entregas a Tiempo',
                'value': 0,
                'display': '0',
                'icon': 'calendar-check',
                'color': '#22d3ee',
                'public': True,
                'system': False,
                'categoria': 'cumplimiento'
            }
        ]
        
        try:
            metricas_creadas = 0
            
            for config in metricas_config:
                # Verificar si ya existe
                existe = UserMetric.query.filter_by(
                    usuario_id=usuario_id,
                    metric_key=config['key']
                ).first()
                
                if not existe:
                    metrica = UserMetric(
                        usuario_id=usuario_id,
                        metric_key=config['key'],
                        metric_name=config['name'],
                        metric_value=config['value'],
                        metric_display=config['display'],
                        metric_icon=config['icon'],
                        metric_color=config['color'],
                        is_public=config['public'],
                        is_system=config['system'],
                        categoria=config['categoria']
                    )
                    db.session.add(metrica)
                    metricas_creadas += 1
            
            if metricas_creadas > 0:
                db.session.commit()
                logger.info(f"Métricas inicializadas para usuario {usuario_id}: {metricas_creadas} métricas")
            
            return metricas_creadas
            
        except Exception as e:
            logger.error(f"Error inicializando métricas para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
            return 0
    
    @staticmethod
    def actualizar_metrica(usuario_id, metric_key, nuevo_valor, cambio_texto=None, tipo_cambio=None):
        """
        Actualiza una métrica del usuario
        
        Args:
            usuario_id: ID del usuario
            metric_key: Clave de la métrica
            nuevo_valor: Nuevo valor numérico
            cambio_texto: Texto del cambio (ej: "+8 este mes")
            tipo_cambio: 'positive', 'negative', 'neutral'
        
        Returns:
            UserMetric actualizada o None si hubo error
        """
        try:
            metrica = UserMetric.query.filter_by(
                usuario_id=usuario_id,
                metric_key=metric_key
            ).first()
            
            if not metrica:
                logger.warning(f"Métrica '{metric_key}' no encontrada para usuario {usuario_id}")
                return None
            
            # Calcular cambio
            valor_anterior = metrica.metric_value
            cambio_valor = nuevo_valor - valor_anterior
            
            # Actualizar valores
            metrica.metric_value = nuevo_valor
            metrica.cambio_valor = cambio_valor
            metrica.cambio_texto = cambio_texto or f"{'+' if cambio_valor > 0 else ''}{cambio_valor}"
            metrica.tipo_cambio = tipo_cambio or ('positive' if cambio_valor > 0 else 'negative' if cambio_valor < 0 else 'neutral')
            metrica.fecha_actualizacion = datetime.utcnow()
            
            # Actualizar display según el tipo de métrica
            if metric_key == 'tiempo_promedio_dias':
                metrica.metric_display = f"{int(nuevo_valor)} días"
            elif metric_key == 'rating_promedio':
                metrica.metric_display = f"{round(nuevo_valor, 1)} ⭐"
            elif metric_key == 'tasa_exito':
                metrica.metric_display = f"{int(nuevo_valor)}%"
            else:
                metrica.metric_display = str(int(nuevo_valor))
            
            db.session.commit()
            
            logger.info(f"Métrica '{metric_key}' actualizada para usuario {usuario_id}: {valor_anterior} → {nuevo_valor}")
            
            # Verificar si se desbloquearon badges con esta métrica
            from src.models.trayectoria.user_badge import UserBadge
            UserBadge.verificar_y_desbloquear_badges(usuario_id)
            
            return metrica
            
        except Exception as e:
            logger.error(f"Error actualizando métrica '{metric_key}' para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def calcular_metricas_desde_calificaciones(usuario_id):
        """
        Calcula todas las métricas del usuario desde sus calificaciones y servicios
        Esta función debería ejecutarse periódicamente o tras eventos importantes
        
        Args:
            usuario_id: ID del usuario
        """
        from src.models.colombia_data.ratings.service_ratings import ServiceRatings
        from src.models.servicio import Servicio
        from sqlalchemy import func
        
        try:
            # Obtener servicios del usuario
            servicios = Servicio.query.filter_by(usuario_id=usuario_id).all()
            servicios_ids = [s.id_servicio for s in servicios]
            
            if not servicios_ids:
                logger.info(f"Usuario {usuario_id} no tiene servicios aún")
                return
            
            # 1. Proyectos completados
            proyectos_completados = len(servicios_ids)
            UserMetric.actualizar_metrica(usuario_id, 'proyectos_completados', proyectos_completados)
            
            # 2. Rating promedio
            rating_avg = db.session.query(
                func.avg(ServiceRatings.calificacion_global)
            ).filter(
                ServiceRatings.servicio_id.in_(servicios_ids)
            ).scalar() or 0.0
            
            UserMetric.actualizar_metrica(usuario_id, 'rating_promedio', rating_avg)
            
            # 3. Tasa de éxito (ejemplo: calificaciones >= 4)
            total_calificaciones = ServiceRatings.query.filter(
                ServiceRatings.servicio_id.in_(servicios_ids)
            ).count()
            
            calificaciones_exitosas = ServiceRatings.query.filter(
                ServiceRatings.servicio_id.in_(servicios_ids),
                ServiceRatings.calificacion_global >= 4
            ).count()
            
            tasa_exito = (calificaciones_exitosas / total_calificaciones * 100) if total_calificaciones > 0 else 0
            UserMetric.actualizar_metrica(usuario_id, 'tasa_exito', tasa_exito)
            
            # 4. Otras métricas (tiempo promedio, clientes recurrentes, etc.)
            # Aquí agregarías la lógica específica para cada métrica
            
            logger.info(f"Métricas calculadas para usuario {usuario_id}")
            
        except Exception as e:
            logger.error(f"Error calculando métricas para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
    
    def __repr__(self):
        return f"<UserMetric usuario_id={self.usuario_id} key={self.metric_key} value={self.metric_value}>"


# Importación diferida para evitar circular imports
from src.models.usuarios import Usuario"""
BizFlow Studio - User Metric Model
Métricas del usuario (proyectos completados, tiempo promedio, etc.)
Sistema flexible de key-value para métricas
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logger = logging.getLogger(__name__)

class UserMetric(db.Model):
    __tablename__ = "user_metrics"
    
    # Índices para mejorar performance
    __table_args__ = (
        Index('idx_user_metric_key', 'usuario_id', 'metric_key'),
    )

    # Identificador
    id = Column(Integer, primary_key=True)
    
    # Usuario
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    
    # === MÉTRICA (SISTEMA KEY-VALUE FLEXIBLE) ===
    metric_key = Column(String(100), nullable=False)  # 'proyectos_completados', 'tiempo_promedio_dias', etc.
    metric_value = Column(Float, nullable=False, default=0.0)  # Valor numérico
    metric_display = Column(String(50), nullable=True)  # Cómo mostrarlo: "95", "12 días", "4.8 ⭐"
    
    # === INFORMACIÓN PARA UI ===
    metric_name = Column(String(100), nullable=False)  # "Proyectos Completados"
    metric_icon = Column(String(50), nullable=True)  # "briefcase-fill" (Bootstrap Icons)
    metric_color = Column(String(7), nullable=True)  # "#10b981"
    
    # === CAMBIO RECIENTE ===
    cambio_valor = Column(Float, nullable=True)  # +8, -2
    cambio_texto = Column(String(50), nullable=True)  # "+8 este mes"
    tipo_cambio = Column(String(20), nullable=True)  # 'positive', 'negative', 'neutral'
    
    # === VISIBILIDAD ===
    is_public = Column(Boolean, default=True)  # Si es visible públicamente
    is_system = Column(Boolean, default=False)  # Si es una métrica del sistema (no editable)
    
    # === ORDEN Y CATEGORÍA ===
    categoria = Column(String(50), nullable=True)  # 'rendimiento', 'calidad', 'velocidad'
    orden = Column(Integer, default=0)  # Orden de visualización
    
    # === METADATOS ===
    fecha_calculo = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # === RELACIONES ===
    usuario = relationship("Usuario", backref="metricas", lazy="joined")
    
    # Índice único por usuario y métrica
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'metric_key', name='unique_user_metric'),
    )
    
    def serialize(self):
        """Serializar para API"""
        return {
            "id": self.metric_key,
            "nombre": self.metric_name,
            "valor": self.metric_display or str(self.metric_value),
            "cambio": self.cambio_texto,
            "tipo_cambio": self.tipo_cambio,
            "icono": self.metric_icon,
            "color": self.metric_color,
            "visible": self.is_public,
            "sistema": self.is_system,
            "categoria": self.categoria
        }
    
    @staticmethod
    def inicializar_metricas_usuario(usuario_id):
        """
        Crea las métricas predeterminadas para un nuevo usuario
        
        Args:
            usuario_id: ID del usuario
        """
        metricas_config = [
            {
                'key': 'proyectos_completados',
                'name': 'Proyectos Completados',
                'value': 0,
                'display': '0',
                'icon': 'briefcase-fill',
                'color': '#10b981',
                'public': True,
                'system': False,
                'categoria': 'volumen'
            },
            {
                'key': 'tiempo_promedio_dias',
                'name': 'Tiempo Prom. Entrega',
                'value': 0,
                'display': '0 días',
                'icon': 'clock-fill',
                'color': '#3b82f6',
                'public': True,
                'system': False,
                'categoria': 'velocidad'
            },
            {
                'key': 'rating_promedio',
                'name': 'Rating Promedio',
                'value': 0,
                'display': '0 ⭐',
                'icon': 'star-fill',
                'color': '#ec4899',
                'public': True,
                'system': False,
                'categoria': 'calidad'
            },
            {
                'key': 'clientes_recurrentes',
                'name': 'Clientes Recurrentes',
                'value': 0,
                'display': '0',
                'icon': 'person-plus-fill',
                'color': '#6366f1',
                'public': True,
                'system': False,
                'categoria': 'fidelidad'
            },
            {
                'key': 'disputas',
                'name': 'Disputas',
                'value': 0,
                'display': '0',
                'icon': 'exclamation-triangle',
                'color': '#64748b',
                'public': False,
                'system': True,
                'categoria': 'riesgo'
            },
            {
                'key': 'cancelaciones',
                'name': 'Cancelaciones',
                'value': 0,
                'display': '0',
                'icon': 'x-octagon',
                'color': '#64748b',
                'public': False,
                'system': True,
                'categoria': 'riesgo'
            },
            {
                'key': 'tasa_exito',
                'name': 'Tasa de Éxito',
                'value': 0,
                'display': '0%',
                'icon': 'graph-up-arrow',
                'color': '#10b981',
                'public': True,
                'system': False,
                'categoria': 'rendimiento'
            },
            {
                'key': 'entregas_tiempo',
                'name': 'Entregas a Tiempo',
                'value': 0,
                'display': '0',
                'icon': 'calendar-check',
                'color': '#22d3ee',
                'public': True,
                'system': False,
                'categoria': 'cumplimiento'
            }
        ]
        
        try:
            metricas_creadas = 0
            
            for config in metricas_config:
                # Verificar si ya existe
                existe = UserMetric.query.filter_by(
                    usuario_id=usuario_id,
                    metric_key=config['key']
                ).first()
                
                if not existe:
                    metrica = UserMetric(
                        usuario_id=usuario_id,
                        metric_key=config['key'],
                        metric_name=config['name'],
                        metric_value=config['value'],
                        metric_display=config['display'],
                        metric_icon=config['icon'],
                        metric_color=config['color'],
                        is_public=config['public'],
                        is_system=config['system'],
                        categoria=config['categoria']
                    )
                    db.session.add(metrica)
                    metricas_creadas += 1
            
            if metricas_creadas > 0:
                db.session.commit()
                logger.info(f"Métricas inicializadas para usuario {usuario_id}: {metricas_creadas} métricas")
            
            return metricas_creadas
            
        except Exception as e:
            logger.error(f"Error inicializando métricas para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
            return 0
    
    @staticmethod
    def actualizar_metrica(usuario_id, metric_key, nuevo_valor, cambio_texto=None, tipo_cambio=None):
        """
        Actualiza una métrica del usuario
        
        Args:
            usuario_id: ID del usuario
            metric_key: Clave de la métrica
            nuevo_valor: Nuevo valor numérico
            cambio_texto: Texto del cambio (ej: "+8 este mes")
            tipo_cambio: 'positive', 'negative', 'neutral'
        
        Returns:
            UserMetric actualizada o None si hubo error
        """
        try:
            metrica = UserMetric.query.filter_by(
                usuario_id=usuario_id,
                metric_key=metric_key
            ).first()
            
            if not metrica:
                logger.warning(f"Métrica '{metric_key}' no encontrada para usuario {usuario_id}")
                return None
            
            # Calcular cambio
            valor_anterior = metrica.metric_value
            cambio_valor = nuevo_valor - valor_anterior
            
            # Actualizar valores
            metrica.metric_value = nuevo_valor
            metrica.cambio_valor = cambio_valor
            metrica.cambio_texto = cambio_texto or f"{'+' if cambio_valor > 0 else ''}{cambio_valor}"
            metrica.tipo_cambio = tipo_cambio or ('positive' if cambio_valor > 0 else 'negative' if cambio_valor < 0 else 'neutral')
            metrica.fecha_actualizacion = datetime.utcnow()
            
            # Actualizar display según el tipo de métrica
            if metric_key == 'tiempo_promedio_dias':
                metrica.metric_display = f"{int(nuevo_valor)} días"
            elif metric_key == 'rating_promedio':
                metrica.metric_display = f"{round(nuevo_valor, 1)} ⭐"
            elif metric_key == 'tasa_exito':
                metrica.metric_display = f"{int(nuevo_valor)}%"
            else:
                metrica.metric_display = str(int(nuevo_valor))
            
            db.session.commit()
            
            logger.info(f"Métrica '{metric_key}' actualizada para usuario {usuario_id}: {valor_anterior} → {nuevo_valor}")
            
            # Verificar si se desbloquearon badges con esta métrica
            from src.models.trayectoria.user_badge import UserBadge
            UserBadge.verificar_y_desbloquear_badges(usuario_id)
            
            return metrica
            
        except Exception as e:
            logger.error(f"Error actualizando métrica '{metric_key}' para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def calcular_metricas_desde_calificaciones(usuario_id):
        """
        Calcula todas las métricas del usuario desde sus calificaciones y servicios
        Esta función debería ejecutarse periódicamente o tras eventos importantes
        
        Args:
            usuario_id: ID del usuario
        """
        from src.models.colombia_data.ratings.service_ratings import ServiceRatings
        from src.models.servicio import Servicio
        from sqlalchemy import func
        
        try:
            # Obtener servicios del usuario
            servicios = Servicio.query.filter_by(usuario_id=usuario_id).all()
            servicios_ids = [s.id_servicio for s in servicios]
            
            if not servicios_ids:
                logger.info(f"Usuario {usuario_id} no tiene servicios aún")
                return
            
            # 1. Proyectos completados
            proyectos_completados = len(servicios_ids)
            UserMetric.actualizar_metrica(usuario_id, 'proyectos_completados', proyectos_completados)
            
            # 2. Rating promedio
            rating_avg = db.session.query(
                func.avg(ServiceRatings.calificacion_global)
            ).filter(
                ServiceRatings.servicio_id.in_(servicios_ids)
            ).scalar() or 0.0
            
            UserMetric.actualizar_metrica(usuario_id, 'rating_promedio', rating_avg)
            
            # 3. Tasa de éxito (ejemplo: calificaciones >= 4)
            total_calificaciones = ServiceRatings.query.filter(
                ServiceRatings.servicio_id.in_(servicios_ids)
            ).count()
            
            calificaciones_exitosas = ServiceRatings.query.filter(
                ServiceRatings.servicio_id.in_(servicios_ids),
                ServiceRatings.calificacion_global >= 4
            ).count()
            
            tasa_exito = (calificaciones_exitosas / total_calificaciones * 100) if total_calificaciones > 0 else 0
            UserMetric.actualizar_metrica(usuario_id, 'tasa_exito', tasa_exito)
            
            # 4. Otras métricas (tiempo promedio, clientes recurrentes, etc.)
            # Aquí agregarías la lógica específica para cada métrica
            
            logger.info(f"Métricas calculadas para usuario {usuario_id}")
            
        except Exception as e:
            logger.error(f"Error calculando métricas para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
    
    def __repr__(self):
        return f"<UserMetric usuario_id={self.usuario_id} key={self.metric_key} value={self.metric_value}>"


# Importación diferida para evitar circular imports
from src.models.usuarios import Usuario