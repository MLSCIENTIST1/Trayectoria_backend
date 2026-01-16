"""
BizFlow Studio - User Score History Model
Historial de scores del usuario para gráficos de evolución
"""

from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from src.models.database import db
import logging

logger = logging.getLogger(__name__)

class UserScoreHistory(db.Model):
    __tablename__ = "user_score_history"
    
    # Índices para mejorar performance
    __table_args__ = (
        Index('idx_user_score_history_user_date', 'usuario_id', 'fecha'),
        Index('idx_user_score_history_tipo', 'usuario_id', 'tipo_score', 'fecha'),
    )
    
    # Identificador
    id = Column(Integer, primary_key=True)
    
    # Usuario
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    
    # === SCORE ===
    score = Column(Float, nullable=False)
    tipo_score = Column(String(20), nullable=False)  # 'contratante', 'contratado', 'global'
    
    # === METADATOS ===
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # === RELACIONES ===
    usuario = relationship("Usuario", backref="historial_scores", lazy="joined")
    
    def serialize(self):
        """Serializar para API"""
        return {
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "score": round(self.score, 1),
            "tipo": self.tipo_score
        }
    
    @staticmethod
    def registrar_score(usuario_id, score, tipo_score):
        """
        Registra un nuevo punto en el historial de scores
        
        Args:
            usuario_id: ID del usuario
            score: Valor del score
            tipo_score: 'contratante', 'contratado', 'global'
        
        Returns:
            UserScoreHistory creado o None si hubo error
        """
        try:
            # Validar tipo
            tipos_validos = ['contratante', 'contratado', 'global']
            if tipo_score not in tipos_validos:
                logger.error(f"Tipo de score inválido: {tipo_score}")
                return None
            
            # Crear registro
            historial = UserScoreHistory(
                usuario_id=usuario_id,
                score=score,
                tipo_score=tipo_score,
                fecha=datetime.utcnow()
            )
            
            db.session.add(historial)
            db.session.commit()
            
            logger.info(f"Score registrado en historial: usuario={usuario_id}, tipo={tipo_score}, score={score}")
            
            return historial
            
        except Exception as e:
            logger.error(f"Error registrando score en historial: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def obtener_historial(usuario_id, tipo_score='global', periodo='6m'):
        """
        Obtiene el historial de scores del usuario
        
        Args:
            usuario_id: ID del usuario
            tipo_score: 'contratante', 'contratado', 'global'
            periodo: '1m', '3m', '6m', '1y', 'all'
        
        Returns:
            Lista de registros de historial
        """
        try:
            # Calcular fecha inicio según periodo
            fecha_inicio = None
            if periodo == '1m':
                fecha_inicio = datetime.utcnow() - timedelta(days=30)
            elif periodo == '3m':
                fecha_inicio = datetime.utcnow() - timedelta(days=90)
            elif periodo == '6m':
                fecha_inicio = datetime.utcnow() - timedelta(days=180)
            elif periodo == '1y':
                fecha_inicio = datetime.utcnow() - timedelta(days=365)
            # 'all' no tiene filtro de fecha
            
            # Construir query
            query = UserScoreHistory.query.filter_by(
                usuario_id=usuario_id,
                tipo_score=tipo_score
            )
            
            if fecha_inicio:
                query = query.filter(UserScoreHistory.fecha >= fecha_inicio)
            
            # Ordenar por fecha
            historial = query.order_by(UserScoreHistory.fecha.asc()).all()
            
            logger.info(f"Historial obtenido: usuario={usuario_id}, tipo={tipo_score}, periodo={periodo}, registros={len(historial)}")
            
            return historial
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {str(e)}")
            return []
    
    @staticmethod
    def generar_datos_grafico(usuario_id, tipo_score='global', periodo='6m'):
        """
        Genera datos formateados para gráficos
        
        Args:
            usuario_id: ID del usuario
            tipo_score: 'contratante', 'contratado', 'global'
            periodo: '1m', '3m', '6m', '1y', 'all'
        
        Returns:
            dict: {labels: [...], data: [...]}
        """
        try:
            historial = UserScoreHistory.obtener_historial(usuario_id, tipo_score, periodo)
            
            if not historial:
                return {"labels": [], "data": []}
            
            # Formatear datos
            labels = []
            data = []
            
            for registro in historial:
                # Formatear fecha según periodo
                if periodo in ['1m', '3m']:
                    # Formato: "15 Ene"
                    fecha_str = registro.fecha.strftime("%d %b")
                elif periodo == '6m':
                    # Formato: "Ene 2024"
                    fecha_str = registro.fecha.strftime("%b %Y")
                elif periodo == '1y':
                    # Formato: "Ene"
                    fecha_str = registro.fecha.strftime("%b")
                else:
                    # Formato: "2024"
                    fecha_str = registro.fecha.strftime("%Y")
                
                labels.append(fecha_str)
                data.append(round(registro.score, 1))
            
            return {
                "labels": labels,
                "data": data
            }
            
        except Exception as e:
            logger.error(f"Error generando datos de gráfico: {str(e)}")
            return {"labels": [], "data": []}
    
    @staticmethod
    def limpiar_historial_antiguo(dias=365):
        """
        Elimina registros de historial más antiguos que X días
        Útil para limpieza periódica de la BD
        
        Args:
            dias: Número de días a mantener (default: 365)
        """
        try:
            fecha_limite = datetime.utcnow() - timedelta(days=dias)
            
            registros_eliminados = UserScoreHistory.query.filter(
                UserScoreHistory.fecha < fecha_limite
            ).delete()
            
            db.session.commit()
            
            logger.info(f"Limpieza de historial: {registros_eliminados} registros eliminados")
            
            return registros_eliminados
            
        except Exception as e:
            logger.error(f"Error limpiando historial antiguo: {str(e)}")
            db.session.rollback()
            return 0
    
    @staticmethod
    def inicializar_historial_usuario(usuario_id):
        """
        Crea un registro inicial en el historial para un nuevo usuario
        
        Args:
            usuario_id: ID del usuario
        """
        try:
            # Crear registros iniciales para cada tipo
            tipos = ['contratante', 'contratado', 'global']
            
            for tipo in tipos:
                # Verificar si ya existe
                existe = UserScoreHistory.query.filter_by(
                    usuario_id=usuario_id,
                    tipo_score=tipo
                ).first()
                
                if not existe:
                    historial = UserScoreHistory(
                        usuario_id=usuario_id,
                        score=0.0,
                        tipo_score=tipo,
                        fecha=datetime.utcnow()
                    )
                    db.session.add(historial)
            
            db.session.commit()
            logger.info(f"Historial inicializado para usuario {usuario_id}")
            
        except Exception as e:
            logger.error(f"Error inicializando historial para usuario {usuario_id}: {str(e)}")
            db.session.rollback()
    
    def __repr__(self):
        return f"<UserScoreHistory usuario_id={self.usuario_id} tipo={self.tipo_score} score={self.score}>"


# Importación diferida para evitar circular imports
from src.models.usuarios import Usuario