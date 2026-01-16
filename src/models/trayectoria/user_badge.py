"""
BizFlow Studio - User Badge Model
Relación entre usuarios y badges desbloqueados
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logger = logging.getLogger(__name__)

class UserBadge(db.Model):
    __tablename__ = "user_badges"

    # Identificador
    id = Column(Integer, primary_key=True)
    
    # === RELACIONES ===
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    badge_id = Column(Integer, ForeignKey('badges.id', ondelete='CASCADE'), nullable=False)
    
    # === ESTADO ===
    desbloqueado = Column(Boolean, default=False, nullable=False)
    fecha_desbloqueo = Column(DateTime, nullable=True)
    
    # === CONTEXTO DEL DESBLOQUEO ===
    motivo_desbloqueo = Column(Text, nullable=True)  # Por qué se desbloqueó
    valor_alcanzado = Column(Integer, nullable=True)  # Valor que alcanzó para desbloquearlo
    
    # === VISIBILIDAD ===
    mostrar_en_perfil = Column(Boolean, default=True)  # Si el usuario quiere mostrarlo
    
    # === METADATOS ===
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # === RELACIONES ===
    usuario = relationship("Usuario", backref="badges", lazy="joined")
    badge = relationship("Badge", backref="usuarios_con_badge", lazy="joined")
    
    # Índice único: un usuario solo puede tener un badge una vez
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'badge_id', name='unique_user_badge'),
    )
    
    def serialize(self):
        """Serializar para API"""
        return {
            "id": self.badge.badge_id if self.badge else None,
            "nombre": self.badge.nombre if self.badge else None,
            "descripcion": self.badge.descripcion if self.badge else None,
            "emoji": self.badge.emoji if self.badge else None,
            "color": self.badge.color if self.badge else None,
            "rgb": self.badge.color_rgb if self.badge else None,
            "desbloqueado": self.desbloqueado,
            "fecha_desbloqueo": self.fecha_desbloqueo.isoformat() if self.fecha_desbloqueo else None,
            "mostrar_en_perfil": self.mostrar_en_perfil
        }
    
    @staticmethod
    def inicializar_badges_usuario(usuario_id):
        """
        Crea la relación usuario-badge para todos los badges del sistema
        Todos empiezan como bloqueados
        
        Args:
            usuario_id: ID del usuario
        """
        from src.models.trayectoria.badge import Badge
        
        try:
            # Obtener todos los badges activos
            badges = Badge.query.filter_by(activo=True).all()
            
            badges_creados = 0
            
            for badge in badges:
                # Verificar si ya existe la relación
                existe = UserBadge.query.filter_by(
                    usuario_id=usuario_id,
                    badge_id=badge.id
                ).first()
                
                if not existe:
                    user_badge = UserBadge(
                        usuario_id=usuario_id,
                        badge_id=badge.id,
                        desbloqueado=False
                    )
                    db.session.add(user_badge)
                    badges_creados += 1
            
            if badges_creados > 0:
                db.session.commit()
                logger.info(f"Badges inicializados para usuario {usuario_id}: {badges_creados} badges")
            
            return badges_creados
            
        except Exception as e:
            logger.error(f"Error inicializando badges para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
            return 0
    
    @staticmethod
    def desbloquear_badge(usuario_id, badge_id_str, motivo=None, valor_alcanzado=None):
        """
        Desbloquea un badge para un usuario
        
        Args:
            usuario_id: ID del usuario
            badge_id_str: String ID del badge (ej: 'primera-estrella')
            motivo: Razón del desbloqueo
            valor_alcanzado: Valor que alcanzó (opcional)
        
        Returns:
            UserBadge desbloqueado o None si hubo error
        """
        from src.models.trayectoria.badge import Badge
        
        try:
            # Buscar el badge
            badge = Badge.query.filter_by(badge_id=badge_id_str).first()
            
            if not badge:
                logger.warning(f"Badge '{badge_id_str}' no encontrado")
                return None
            
            # Buscar la relación usuario-badge
            user_badge = UserBadge.query.filter_by(
                usuario_id=usuario_id,
                badge_id=badge.id
            ).first()
            
            if not user_badge:
                # Crear si no existe
                user_badge = UserBadge(
                    usuario_id=usuario_id,
                    badge_id=badge.id
                )
                db.session.add(user_badge)
            
            # Si ya estaba desbloqueado, no hacer nada
            if user_badge.desbloqueado:
                logger.info(f"Badge '{badge_id_str}' ya estaba desbloqueado para usuario {usuario_id}")
                return user_badge
            
            # Desbloquear
            user_badge.desbloqueado = True
            user_badge.fecha_desbloqueo = datetime.utcnow()
            user_badge.motivo_desbloqueo = motivo
            user_badge.valor_alcanzado = valor_alcanzado
            
            db.session.commit()
            
            logger.info(f"✨ Badge '{badge_id_str}' desbloqueado para usuario {usuario_id}")
            
            # TODO: Aquí podrías crear una notificación al usuario
            # from src.models.notificaciones import crear_notificacion
            # crear_notificacion(usuario_id, f"¡Badge desbloqueado: {badge.nombre}!")
            
            return user_badge
            
        except Exception as e:
            logger.error(f"Error desbloqueando badge para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def verificar_y_desbloquear_badges(usuario_id):
        """
        Verifica qué badges puede desbloquear el usuario basándose en sus métricas
        Esta función debería llamarse cada vez que se actualicen métricas del usuario
        
        Args:
            usuario_id: ID del usuario
        """
        from src.models.trayectoria.badge import Badge
        from src.models.trayectoria.user_metric import UserMetric
        
        try:
            # Obtener métricas del usuario
            metricas = UserMetric.query.filter_by(usuario_id=usuario_id).all()
            metricas_dict = {m.metric_key: m.metric_value for m in metricas}
            
            # Obtener badges no desbloqueados
            badges_pendientes = db.session.query(Badge).join(
                UserBadge, 
                (UserBadge.badge_id == Badge.id) & (UserBadge.usuario_id == usuario_id)
            ).filter(
                UserBadge.desbloqueado == False,
                Badge.activo == True
            ).all()
            
            badges_desbloqueados = 0
            
            for badge in badges_pendientes:
                # Verificar si cumple el criterio
                criterio_cumplido = False
                valor_actual = 0
                
                if badge.criterio_tipo in metricas_dict:
                    valor_actual = metricas_dict[badge.criterio_tipo]
                    if valor_actual >= badge.criterio_valor:
                        criterio_cumplido = True
                
                if criterio_cumplido:
                    UserBadge.desbloquear_badge(
                        usuario_id,
                        badge.badge_id,
                        motivo=f"Alcanzó {valor_actual} en {badge.criterio_tipo}",
                        valor_alcanzado=valor_actual
                    )
                    badges_desbloqueados += 1
            
            if badges_desbloqueados > 0:
                logger.info(f"✨ {badges_desbloqueados} badge(s) desbloqueado(s) para usuario {usuario_id}")
            
            return badges_desbloqueados
            
        except Exception as e:
            logger.error(f"Error verificando badges para usuario {usuario_id}: {str(e)}")
            return 0
    
    @staticmethod
    def obtener_progreso_badges(usuario_id):
        """
        Obtiene el progreso de badges del usuario
        
        Returns:
            dict con desbloqueados, total y porcentaje
        """
        try:
            total = UserBadge.query.filter_by(usuario_id=usuario_id).count()
            desbloqueados = UserBadge.query.filter_by(
                usuario_id=usuario_id,
                desbloqueado=True
            ).count()
            
            porcentaje = (desbloqueados / total * 100) if total > 0 else 0
            
            return {
                "desbloqueados": desbloqueados,
                "total": total,
                "porcentaje": round(porcentaje, 1)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo progreso de badges: {str(e)}")
            return {"desbloqueados": 0, "total": 0, "porcentaje": 0}
    
    def __repr__(self):
        return f"<UserBadge usuario_id={self.usuario_id} badge={self.badge.badge_id if self.badge else None} desbloqueado={self.desbloqueado}>"


# Importación diferida para evitar circular imports
from src.models.usuarios import Usuario