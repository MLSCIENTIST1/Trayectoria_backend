"""
Modelo NegocioBadgeObtenido - Insignias Ganadas por Negocio
TuKomercio Suite - BizScore

Registra qué insignias ha desbloqueado cada negocio.
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Modelo NegocioBadgeObtenido cargado correctamente.")


class NegocioBadgeObtenido(db.Model):
    __tablename__ = "negocio_badges_obtenidos"

    # ═══════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ═══════════════════════════════════════════════════════════
    id = Column(Integer, primary_key=True)
    negocio_id = Column(Integer, ForeignKey('negocios.id_negocio', ondelete='CASCADE'), nullable=False)
    badge_id = Column(Integer, ForeignKey('negocio_badges.id', ondelete='CASCADE'), nullable=False)

    # ═══════════════════════════════════════════════════════════
    # DETALLES DE OBTENCIÓN
    # ═══════════════════════════════════════════════════════════
    fecha_obtencion = Column(DateTime, default=datetime.utcnow)
    
    # Valor con el que se desbloqueó (para historial)
    valor_al_desbloquear = Column(Float, nullable=True)  # Ej: 10 contratos
    
    # Contexto de desbloqueo
    contexto = Column(String(255), nullable=True)  # "Completaste tu contrato #10"

    # ═══════════════════════════════════════════════════════════
    # NOTIFICACIONES
    # ═══════════════════════════════════════════════════════════
    notificado = Column(Boolean, default=False)
    fecha_notificacion = Column(DateTime, nullable=True)
    
    # Visto por el usuario en la UI
    visto = Column(Boolean, default=False)
    fecha_visto = Column(DateTime, nullable=True)

    # ═══════════════════════════════════════════════════════════
    # ESTADO
    # ═══════════════════════════════════════════════════════════
    activo = Column(Boolean, default=True)  # Por si se revoca
    fecha_revocacion = Column(DateTime, nullable=True)
    motivo_revocacion = Column(String(255), nullable=True)

    # ═══════════════════════════════════════════════════════════
    # SHOWCASING (mostrar en videos)
    # ═══════════════════════════════════════════════════════════
    # Cuántas veces se ha asignado a videos
    veces_asignado_videos = Column(Integer, default=0)
    
    # Si es favorito del negocio (aparece primero)
    es_favorito = Column(Boolean, default=False)

    # ═══════════════════════════════════════════════════════════
    # RELACIONES
    # ═══════════════════════════════════════════════════════════
    negocio = relationship("Negocio", backref="badges_obtenidos")
    badge = relationship("NegocioBadge", back_populates="badges_obtenidos")
    
    # Relación con videos donde se muestra este badge
    videos = relationship("NegocioVideoBadge", back_populates="badge_obtenido")

    # ═══════════════════════════════════════════════════════════
    # MÉTODOS HELPER
    # ═══════════════════════════════════════════════════════════
    def marcar_como_notificado(self):
        """Marca el badge como notificado"""
        self.notificado = True
        self.fecha_notificacion = datetime.utcnow()

    def marcar_como_visto(self):
        """Marca el badge como visto por el usuario"""
        self.visto = True
        self.fecha_visto = datetime.utcnow()

    def revocar(self, motivo: str = None):
        """Revoca el badge (ej: por fraude)"""
        self.activo = False
        self.fecha_revocacion = datetime.utcnow()
        self.motivo_revocacion = motivo

    def serialize(self):
        return {
            "id": self.id,
            "negocio_id": self.negocio_id,
            "badge": self.badge.serialize() if self.badge else None,
            "fecha_obtencion": self.fecha_obtencion.isoformat() if self.fecha_obtencion else None,
            "valor_al_desbloquear": self.valor_al_desbloquear,
            "contexto": self.contexto,
            "visto": self.visto,
            "es_favorito": self.es_favorito,
            "veces_asignado_videos": self.veces_asignado_videos,
            "activo": self.activo
        }

    def serialize_para_video(self):
        """Serialización compacta para mostrar en videos"""
        if not self.badge:
            return None
        return {
            "id": self.id,
            "badge_id": self.badge_id,
            "nombre": self.badge.nombre,
            "icono": self.badge.icono,
            "color_primario": self.badge.color_primario,
            "color_fondo": self.badge.color_fondo,
            "nivel": self.badge.nivel
        }


# ═══════════════════════════════════════════════════════════════════
# SERVICIO DE VERIFICACIÓN DE BADGES
# ═══════════════════════════════════════════════════════════════════
class BadgeVerificationService:
    """
    Servicio para verificar y otorgar badges automáticamente
    Uso: BadgeVerificationService.verificar_y_otorgar(negocio_id)
    """
    
    @staticmethod
    def obtener_metricas_negocio(negocio) -> dict:
        """Obtiene las métricas actuales del negocio"""
        # Aquí se conecta con los otros modelos para calcular métricas
        # Por ahora retorna estructura base
        return {
            "contratos_completados": 0,
            "trabajos_perfectos": 0,
            "calificaciones_5": 0,
            "tiempo_respuesta_hrs": 24,
            "entregas_anticipadas": 0,
            "verificado": negocio.verificado if hasattr(negocio, 'verificado') else 0,
            "contratos_sin_disputa": 0,
            "clientes_recurrentes": 0,
            "percentil": 50,
            "orden_registro": negocio.id_negocio if hasattr(negocio, 'id_negocio') else 999999,
            "videos_subidos": 0,
            "dias_activo": 0
        }

    @staticmethod
    def verificar_y_otorgar(negocio_id: int, db_session) -> list:
        """
        Verifica todos los badges y otorga los que correspondan
        Retorna lista de badges nuevos otorgados
        """
        from src.models.colombia_data.negocio import Negocio
        
        negocio = db_session.query(Negocio).filter_by(id_negocio=negocio_id).first()
        if not negocio:
            return []
        
        # Obtener badges ya obtenidos
        badges_obtenidos_ids = [
            bo.badge_id for bo in negocio.badges_obtenidos if bo.activo
        ]
        
        # Obtener métricas actuales
        metricas = BadgeVerificationService.obtener_metricas_negocio(negocio)
        
        # Obtener todos los badges activos
        badges_disponibles = db_session.query(NegocioBadge).filter(
            NegocioBadge.activo == True,
            NegocioBadge.id.notin_(badges_obtenidos_ids) if badges_obtenidos_ids else True
        ).all()
        
        nuevos_badges = []
        
        for badge in badges_disponibles:
            # Verificar si puede otorgarse
            if not badge.puede_otorgarse():
                continue
            
            # Obtener valor de la métrica correspondiente
            valor_actual = metricas.get(badge.criterio_tipo, 0)
            
            # Verificar si cumple el criterio
            if badge.verificar_criterio(valor_actual):
                # Otorgar badge
                nuevo_badge = NegocioBadgeObtenido(
                    negocio_id=negocio_id,
                    badge_id=badge.id,
                    valor_al_desbloquear=valor_actual,
                    contexto=f"Alcanzaste {valor_actual} en {badge.criterio_tipo}"
                )
                db_session.add(nuevo_badge)
                
                # Incrementar contador del badge
                badge.total_otorgados += 1
                
                nuevos_badges.append(nuevo_badge)
        
        if nuevos_badges:
            db_session.commit()
        
        return nuevos_badges


# Importaciones diferidas
from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.badges.negocio_badge import NegocioBadge