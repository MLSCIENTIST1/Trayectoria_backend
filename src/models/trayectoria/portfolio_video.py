"""
BizFlow Studio - Portfolio Video Model
Videos del portfolio personal del usuario (diferentes a los videos de servicios)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logger = logging.getLogger(__name__)

class PortfolioVideo(db.Model):
    __tablename__ = "portfolio_videos"

    # Identificador
    id = Column(Integer, primary_key=True)
    
    # Usuario
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    
    # === INFORMACIÓN DEL VIDEO ===
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # === URLs ===
    url = Column(String(500), nullable=False)  # URL del video
    thumbnail_url = Column(String(500), nullable=True)  # URL de la miniatura
    
    # === DURACIÓN ===
    duracion = Column(String(20), nullable=True)  # "2:00:58" formato
    duracion_segundos = Column(Integer, nullable=True)  # Duración en segundos
    
    # === ESTADÍSTICAS ===
    vistas = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    
    # === MÉTRICAS Y BADGES ASOCIADOS ===
    metricas_asociadas = Column(JSON, nullable=True)  # ['proyectos_completados', 'rating_promedio']
    badges_asociados = Column(JSON, nullable=True)  # ['perfeccionista', 'rayo-veloz']
    
    # === ESTADO ===
    activo = Column(Boolean, default=True)
    destacado = Column(Boolean, default=False)  # Si está destacado en el perfil
    
    # === PROMOCIÓN ===
    promovido = Column(Boolean, default=False)  # Si el usuario pagó para promocionarlo
    fecha_promocion = Column(DateTime, nullable=True)
    
    # === METADATOS ===
    fecha_subida = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # === ORDEN ===
    orden = Column(Integer, default=0)  # Orden de visualización en el portfolio
    
    # === RELACIONES ===
    usuario = relationship("Usuario", backref="portfolio_videos", lazy="joined")
    
    def serialize(self):
        """Serializar para API"""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "url": self.url,
            "thumbnail": self.thumbnail_url,
            "duracion": self.duracion,
            "vistas": self.vistas,
            "likes": self.likes,
            "metricas": self.metricas_asociadas or [],
            "badges": self.badges_asociados or [],
            "destacado": self.destacado,
            "promovido": self.promovido,
            "fecha": self.fecha_subida.isoformat() if self.fecha_subida else None
        }
    
    @staticmethod
    def crear_video(usuario_id, titulo, url, descripcion=None, duracion=None, thumbnail_url=None):
        """
        Crea un nuevo video en el portfolio
        
        Args:
            usuario_id: ID del usuario
            titulo: Título del video
            url: URL del video
            descripcion: Descripción opcional
            duracion: Duración en formato "HH:MM:SS"
            thumbnail_url: URL de la miniatura
        
        Returns:
            PortfolioVideo creado o None si hubo error
        """
        try:
            # Calcular orden (último video + 1)
            ultimo_orden = db.session.query(
                db.func.max(PortfolioVideo.orden)
            ).filter_by(usuario_id=usuario_id).scalar() or 0
            
            # Calcular duración en segundos si se proporciona
            duracion_segundos = None
            if duracion:
                try:
                    partes = duracion.split(':')
                    if len(partes) == 3:  # HH:MM:SS
                        h, m, s = map(int, partes)
                        duracion_segundos = h * 3600 + m * 60 + s
                    elif len(partes) == 2:  # MM:SS
                        m, s = map(int, partes)
                        duracion_segundos = m * 60 + s
                except:
                    pass
            
            video = PortfolioVideo(
                usuario_id=usuario_id,
                titulo=titulo,
                descripcion=descripcion,
                url=url,
                thumbnail_url=thumbnail_url,
                duracion=duracion,
                duracion_segundos=duracion_segundos,
                orden=ultimo_orden + 1,
                vistas=0,
                likes=0
            )
            
            db.session.add(video)
            db.session.commit()
            
            logger.info(f"Video creado en portfolio de usuario {usuario_id}: {titulo}")
            
            return video
            
        except Exception as e:
            logger.error(f"Error creando video para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def asociar_metricas(video_id, metric_keys):
        """
        Asocia métricas a un video
        
        Args:
            video_id: ID del video
            metric_keys: Lista de claves de métricas ['proyectos_completados', 'rating_promedio']
        
        Returns:
            Video actualizado o None
        """
        try:
            video = PortfolioVideo.query.get(video_id)
            
            if not video:
                logger.warning(f"Video {video_id} no encontrado")
                return None
            
            video.metricas_asociadas = metric_keys
            video.fecha_actualizacion = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Métricas asociadas al video {video_id}: {metric_keys}")
            
            return video
            
        except Exception as e:
            logger.error(f"Error asociando métricas al video {video_id}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def asociar_badges(video_id, badge_ids):
        """
        Asocia badges a un video
        
        Args:
            video_id: ID del video
            badge_ids: Lista de badge_ids ['perfeccionista', 'rayo-veloz']
        
        Returns:
            Video actualizado o None
        """
        try:
            video = PortfolioVideo.query.get(video_id)
            
            if not video:
                logger.warning(f"Video {video_id} no encontrado")
                return None
            
            video.badges_asociados = badge_ids
            video.fecha_actualizacion = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Badges asociados al video {video_id}: {badge_ids}")
            
            return video
            
        except Exception as e:
            logger.error(f"Error asociando badges al video {video_id}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def incrementar_vista(video_id):
        """
        Incrementa el contador de vistas de un video
        
        Args:
            video_id: ID del video
        """
        try:
            video = PortfolioVideo.query.get(video_id)
            
            if video:
                video.vistas += 1
                db.session.commit()
                
        except Exception as e:
            logger.error(f"Error incrementando vista del video {video_id}: {str(e)}")
            db.session.rollback()
    
    @staticmethod
    def toggle_like(video_id):
        """
        Incrementa el contador de likes de un video
        (En una implementación real, deberías verificar que el usuario no haya dado like antes)
        
        Args:
            video_id: ID del video
        """
        try:
            video = PortfolioVideo.query.get(video_id)
            
            if video:
                video.likes += 1
                db.session.commit()
                return video.likes
                
        except Exception as e:
            logger.error(f"Error incrementando like del video {video_id}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def promover_video(video_id):
        """
        Marca un video como promovido (función premium)
        
        Args:
            video_id: ID del video
        """
        try:
            video = PortfolioVideo.query.get(video_id)
            
            if video:
                video.promovido = True
                video.fecha_promocion = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"Video {video_id} promovido")
                return video
                
        except Exception as e:
            logger.error(f"Error promoviendo video {video_id}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def reordenar_videos(usuario_id, orden_ids):
        """
        Reordena los videos del portfolio
        
        Args:
            usuario_id: ID del usuario
            orden_ids: Lista de IDs en el orden deseado [3, 1, 2, 4]
        """
        try:
            for idx, video_id in enumerate(orden_ids):
                video = PortfolioVideo.query.filter_by(
                    id=video_id,
                    usuario_id=usuario_id
                ).first()
                
                if video:
                    video.orden = idx
            
            db.session.commit()
            logger.info(f"Videos reordenados para usuario {usuario_id}")
            
        except Exception as e:
            logger.error(f"Error reordenando videos para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
    
    def __repr__(self):
        return f"<PortfolioVideo id={self.id} usuario_id={self.usuario_id} titulo='{self.titulo}'>"


# Importación diferida para evitar circular imports
from src.models.usuarios import Usuario