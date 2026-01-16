"""
BizFlow Studio - User Stage Score Model
Scores del usuario en las 4 etapas de la trayectoria:
E1: Primer Contacto
E2: Ejecución
E3: Entrega
E4: Post-Servicio
"""

from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logger = logging.getLogger(__name__)

class UserStageScore(db.Model):
    __tablename__ = "user_stage_scores"

    # Identificador
    id = Column(Integer, primary_key=True)
    
    # Usuario
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    
    # === ETAPA ===
    stage_id = Column(String(5), nullable=False)  # 'e1', 'e2', 'e3', 'e4'
    stage_number = Column(Integer, nullable=False)  # 1, 2, 3, 4
    stage_name = Column(String(50), nullable=False)  # 'Primer Contacto', 'Ejecución', etc.
    
    # === SCORE DE LA ETAPA ===
    score = Column(Float, nullable=False, default=0.0)  # Score de 0 a 5
    
    # === VISIBILIDAD ===
    is_public = Column(Boolean, default=True)  # Si es visible públicamente
    
    # === MÉTRICAS ESPECÍFICAS DE LA ETAPA (JSON flexible) ===
    metrics = Column(JSON, nullable=True)  # Almacena métricas específicas de cada etapa
    
    # === METADATOS ===
    fecha_calculo = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # === COLOR PARA UI ===
    color = Column(String(7), nullable=True)  # Hex color para la UI
    
    # === RELACIONES ===
    usuario = relationship("Usuario", backref="stage_scores", lazy="joined")
    
    # Índice único por usuario y etapa
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'stage_id', name='unique_user_stage'),
    )
    
    def serialize(self):
        """Serializar para API"""
        return {
            "id": self.stage_id,
            "numero": self.stage_number,
            "nombre": self.stage_name,
            "color": self.color or self._get_default_color(),
            "score": round(self.score, 1),
            "visible": self.is_public,
            "metricas": self.metrics or self._get_default_metrics()
        }
    
    def _get_default_color(self):
        """Colores predeterminados por etapa"""
        colors = {
            'e1': '#3b82f6',  # Azul
            'e2': '#8b5cf6',  # Púrpura
            'e3': '#10b981',  # Verde
            'e4': '#f59e0b'   # Ámbar
        }
        return colors.get(self.stage_id, '#6366f1')
    
    def _get_default_metrics(self):
        """Métricas predeterminadas por etapa"""
        defaults = {
            'e1': [
                {'label': 'Velocidad', 'icono': 'lightning-charge', 'valor': '-'},
                {'label': 'Profesionalismo', 'icono': 'chat-heart', 'valor': '-'},
                {'label': 'Propuestas claras', 'icono': 'file-check', 'valor': '-'}
            ],
            'e2': [
                {'label': 'Cumplimiento', 'icono': 'kanban', 'valor': '-'},
                {'label': 'Actualizaciones', 'icono': 'arrow-repeat', 'valor': '-'},
                {'label': 'Calidad', 'icono': 'tools', 'valor': '-'}
            ],
            'e3': [
                {'label': 'A tiempo', 'icono': 'calendar-check', 'valor': '-'},
                {'label': 'Sin revisiones', 'icono': 'patch-check', 'valor': '-'},
                {'label': 'Satisfacción', 'icono': 'emoji-laughing', 'valor': '-'}
            ],
            'e4': [
                {'label': 'Soporte', 'icono': 'headset', 'valor': '-'},
                {'label': 'Garantía', 'icono': 'shield-check', 'valor': '-'},
                {'label': 'Recomendarían', 'icono': 'hand-thumbs-up', 'valor': '-'}
            ]
        }
        return defaults.get(self.stage_id, [])
    
    @staticmethod
    def inicializar_etapas_usuario(usuario_id):
        """
        Crea las 4 etapas para un nuevo usuario
        
        Args:
            usuario_id: ID del usuario
        
        Returns:
            Lista de UserStageScore creados
        """
        try:
            etapas_config = [
                {'id': 'e1', 'number': 1, 'name': 'Primer Contacto', 'color': '#3b82f6'},
                {'id': 'e2', 'number': 2, 'name': 'Ejecución', 'color': '#8b5cf6'},
                {'id': 'e3', 'number': 3, 'name': 'Entrega', 'color': '#10b981'},
                {'id': 'e4', 'number': 4, 'name': 'Post-Servicio', 'color': '#f59e0b'}
            ]
            
            etapas_creadas = []
            
            for config in etapas_config:
                # Verificar si ya existe
                existe = UserStageScore.query.filter_by(
                    usuario_id=usuario_id,
                    stage_id=config['id']
                ).first()
                
                if not existe:
                    etapa = UserStageScore(
                        usuario_id=usuario_id,
                        stage_id=config['id'],
                        stage_number=config['number'],
                        stage_name=config['name'],
                        color=config['color'],
                        score=0.0,
                        is_public=True,
                        metrics=None  # Se usarán los defaults
                    )
                    db.session.add(etapa)
                    etapas_creadas.append(etapa)
            
            if etapas_creadas:
                db.session.commit()
                logger.info(f"Etapas inicializadas para usuario {usuario_id}: {len(etapas_creadas)} etapas")
            
            return etapas_creadas
            
        except Exception as e:
            logger.error(f"Error inicializando etapas para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
            return []
    
    @staticmethod
    def calcular_scores_etapas(usuario_id):
        """
        Calcula los scores de las 4 etapas basándose en calificaciones
        Esta es una versión simplificada - deberás adaptarla a tu lógica de calificaciones
        
        Args:
            usuario_id: ID del usuario
        """
        try:
            from src.models.colombia_data.ratings.service_ratings import ServiceRatings
            from sqlalchemy import func
            
            # Aquí calcularías los scores basándote en tus calificaciones específicas
            # Por ahora, ejemplo simplificado
            
            etapas = UserStageScore.query.filter_by(usuario_id=usuario_id).all()
            
            for etapa in etapas:
                # Lógica de cálculo específica por etapa
                # Esto es un placeholder - adapta según tu sistema de calificaciones
                score_calculado = 4.5  # Valor de ejemplo
                
                etapa.score = score_calculado
                etapa.fecha_actualizacion = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Scores de etapas calculados para usuario {usuario_id}")
            
        except Exception as e:
            logger.error(f"Error calculando scores de etapas para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
    
    def __repr__(self):
        return f"<UserStageScore usuario_id={self.usuario_id} stage={self.stage_id} score={self.score}>"


# Importación diferida para evitar circular imports
from src.models.usuarios import Usuario