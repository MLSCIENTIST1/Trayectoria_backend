"""
BizFlow Studio - User Score Model
Scores del usuario (contratante, contratado, global)
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logger = logging.getLogger(__name__)

class UserScore(db.Model):
    __tablename__ = "user_scores"
    
    # Índices para mejorar performance
    __table_args__ = (
        Index('idx_user_score_user_date', 'usuario_id', 'fecha_calculo'),
    )
    
    # Identificador
    id = Column(Integer, primary_key=True)
    
    # Usuario
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    
    # === SCORES ===
    score_contratante = Column(Float, default=0.0)  # Score como contratante
    score_contratado = Column(Float, default=0.0)   # Score como contratado
    score_global = Column(Float, default=0.0)        # Score global promedio
    
    # === CAMBIOS RECIENTES ===
    cambio_contratante = Column(Float, default=0.0)  # +3, -2, etc
    cambio_contratado = Column(Float, default=0.0)
    cambio_global = Column(Float, default=0.0)
    
    # === PERCENTILES ===
    percentil = Column(Float, default=0.0)  # Percentil del usuario (0-100)
    
    # === METADATOS ===
    fecha_calculo = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # === RELACIONES ===
    usuario = relationship("Usuario", backref="scores", lazy="joined")
    
    def serialize(self):
        """Serializar para API"""
        return {
            "contratante": round(self.score_contratante, 1),
            "contratado": round(self.score_contratado, 1),
            "global": round(self.score_global, 1),
            "cambios": {
                "contratante": round(self.cambio_contratante, 1),
                "contratado": round(self.cambio_contratado, 1),
                "global": round(self.cambio_global, 1)
            },
            "percentil": round(self.percentil, 1),
            "fecha": self.fecha_calculo.isoformat() if self.fecha_calculo else None
        }
    
    @staticmethod
    def inicializar_score_usuario(usuario_id):
        """
        Crea el score inicial para un nuevo usuario
        
        Args:
            usuario_id: ID del usuario
        """
        try:
            # Verificar si ya existe
            existe = UserScore.query.filter_by(usuario_id=usuario_id).first()
            
            if not existe:
                score = UserScore(
                    usuario_id=usuario_id,
                    score_contratante=0.0,
                    score_contratado=0.0,
                    score_global=0.0,
                    percentil=0.0
                )
                db.session.add(score)
                db.session.commit()
                
                logger.info(f"Score inicializado para usuario {usuario_id}")
                return score
            
            return existe
            
        except Exception as e:
            logger.error(f"Error inicializando score para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def actualizar_scores(usuario_id, nuevo_contratante=None, nuevo_contratado=None):
        """
        Actualiza los scores del usuario
        
        Args:
            usuario_id: ID del usuario
            nuevo_contratante: Nuevo score como contratante (opcional)
            nuevo_contratado: Nuevo score como contratado (opcional)
        """
        try:
            score = UserScore.query.filter_by(usuario_id=usuario_id).first()
            
            if not score:
                logger.warning(f"Score no encontrado para usuario {usuario_id}")
                return None
            
            # Actualizar contratante
            if nuevo_contratante is not None:
                score.cambio_contratante = nuevo_contratante - score.score_contratante
                score.score_contratante = nuevo_contratante
            
            # Actualizar contratado
            if nuevo_contratado is not None:
                score.cambio_contratado = nuevo_contratado - score.score_contratado
                score.score_contratado = nuevo_contratado
            
            # Calcular global (promedio)
            score.score_global = (score.score_contratante + score.score_contratado) / 2
            score.cambio_global = (score.cambio_contratante + score.cambio_contratado) / 2
            
            # Actualizar fecha
            score.fecha_actualizacion = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Scores actualizados para usuario {usuario_id}: "
                       f"Contratante={score.score_contratante}, "
                       f"Contratado={score.score_contratado}, "
                       f"Global={score.score_global}")
            
            # Registrar en historial
            from src.models.trayectoria.user_score_history import UserScoreHistory
            UserScoreHistory.registrar_score(usuario_id, score.score_global, 'global')
            
            # Verificar badges
            from src.models.trayectoria.user_badge import UserBadge
            UserBadge.verificar_y_desbloquear_badges(usuario_id)
            
            return score
            
        except Exception as e:
            logger.error(f"Error actualizando scores para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def calcular_percentil(usuario_id):
        """
        Calcula el percentil del usuario respecto a todos los usuarios
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            float: Percentil del usuario (0-100)
        """
        from sqlalchemy import func
        
        try:
            score = UserScore.query.filter_by(usuario_id=usuario_id).first()
            
            if not score:
                return 0.0
            
            # Contar usuarios con score menor
            usuarios_menor = UserScore.query.filter(
                UserScore.score_global < score.score_global
            ).count()
            
            # Total de usuarios
            total_usuarios = UserScore.query.count()
            
            if total_usuarios == 0:
                return 0.0
            
            # Calcular percentil
            percentil = (usuarios_menor / total_usuarios) * 100
            
            # Actualizar en BD
            score.percentil = percentil
            db.session.commit()
            
            logger.info(f"Percentil calculado para usuario {usuario_id}: {percentil}%")
            
            return percentil
            
        except Exception as e:
            logger.error(f"Error calculando percentil para usuario {usuario_id}: {str(e)}")
            return 0.0
    
    def __repr__(self):
        return f"<UserScore usuario_id={self.usuario_id} global={self.score_global}>"


# Importación diferida para evitar circular imports
from src.models.usuarios import Usuario