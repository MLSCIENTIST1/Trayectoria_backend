"""
Modelo ServiceRatings - ACTUALIZADO con Etapa 4 (Post-Servicio)
TuKomercio Suite - BizScore

Cambios:
- Agregada Etapa 4: Post-Servicio (para calificar después de días/semanas)
- Agregado control de activación de etapa 4
- Agregado soporte para evidencia/archivos
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from src.models.database import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Modelo ServiceRatings v2.0 (con Etapa 4) cargado correctamente.")


class ServiceRatings(db.Model):
    __tablename__ = "service_ratings"

    # ═══════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ═══════════════════════════════════════════════════════════
    id_rating = Column(Integer, primary_key=True)
    servicio_id = Column(Integer, ForeignKey('servicio.id_servicio', ondelete='CASCADE'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)

    # ═══════════════════════════════════════════════════════════
    # ETAPA 1: CONTRATACIÓN (Inicio)
    # ═══════════════════════════════════════════════════════════
    # Calificación que recibe el CONTRATANTE en etapa 1
    calificacion_recived_contratante1 = Column(Integer, nullable=True)
    razon_contratante1 = Column(String(255), nullable=True)
    
    # Calificación que recibe el CONTRATADO en etapa 1
    calificacion_recived_contratado1 = Column(Integer, nullable=True)
    razon_contratado1 = Column(String(255), nullable=True)
    
    # Fecha de calificación etapa 1
    fecha_calificacion_etapa1 = Column(DateTime, nullable=True)
    etapa1_completada = Column(Boolean, default=False)

    # ═══════════════════════════════════════════════════════════
    # ETAPA 2: EJECUCIÓN (Durante)
    # ═══════════════════════════════════════════════════════════
    calificacion_recived_contratante2 = Column(Integer, nullable=True)
    razon_contratante2 = Column(String(255), nullable=True)
    
    calificacion_recived_contratado2 = Column(Integer, nullable=True)
    razon_contratado2 = Column(String(255), nullable=True)
    
    fecha_calificacion_etapa2 = Column(DateTime, nullable=True)
    etapa2_completada = Column(Boolean, default=False)

    # ═══════════════════════════════════════════════════════════
    # ETAPA 3: FINALIZACIÓN (Al cerrar)
    # ═══════════════════════════════════════════════════════════
    calificacion_recived_contratante3 = Column(Integer, nullable=True)
    razon_contratante3 = Column(String(255), nullable=True)
    
    calificacion_recived_contratado3 = Column(Integer, nullable=True)
    razon_contratado3 = Column(String(255), nullable=True)
    
    fecha_calificacion_etapa3 = Column(DateTime, nullable=True)
    etapa3_completada = Column(Boolean, default=False)

    # ═══════════════════════════════════════════════════════════
    # ETAPA 4: POST-SERVICIO (Días/Semanas después) - NUEVO
    # ═══════════════════════════════════════════════════════════
    calificacion_recived_contratante4 = Column(Integer, nullable=True)
    razon_contratante4 = Column(String(255), nullable=True)
    
    calificacion_recived_contratado4 = Column(Integer, nullable=True)
    razon_contratado4 = Column(String(255), nullable=True)
    
    # Control de activación de etapa 4
    fecha_habilitacion_etapa4 = Column(DateTime, nullable=True)
    fecha_calificacion_etapa4 = Column(DateTime, nullable=True)
    etapa4_completada_contratante = Column(Boolean, default=False)
    etapa4_completada_contratado = Column(Boolean, default=False)
    
    # Notificaciones de etapa 4
    notificacion_etapa4_enviada = Column(Boolean, default=False)
    fecha_notificacion_etapa4 = Column(DateTime, nullable=True)

    # ═══════════════════════════════════════════════════════════
    # CALIFICATIVOS GENERALES
    # ═══════════════════════════════════════════════════════════
    id_calificativo_como_contratante = Column(Integer, nullable=True)
    id_calificativo_como_contratado = Column(Integer, nullable=True)
    
    volveria_a_contratar = Column(Boolean, nullable=True)
    volveria_a_ser_contratado = Column(Boolean, nullable=True)

    # ═══════════════════════════════════════════════════════════
    # MÉTODO DE CONEXIÓN (QR / Manual)
    # ═══════════════════════════════════════════════════════════
    qr_o_manual = Column(String(10), nullable=True)  # 'qr' o 'manual'
    id_qr_usado = Column(String(50), nullable=True)

    # ═══════════════════════════════════════════════════════════
    # DURACIÓN DEL CONTRATO
    # ═══════════════════════════════════════════════════════════
    horas = Column(Integer, nullable=True)
    dias = Column(Integer, nullable=True)
    meses = Column(Integer, nullable=True)
    duracion_total = Column(String(50), nullable=True)

    # ═══════════════════════════════════════════════════════════
    # RESULTADOS Y PUNTAJES
    # ═══════════════════════════════════════════════════════════
    puntaje_por_labor = Column(Integer, nullable=True)
    resultado_contratante = Column(Float, nullable=True)
    resultado_contratado = Column(Float, nullable=True)
    
    # Puntaje promedio por etapa
    promedio_etapa1 = Column(Float, nullable=True)
    promedio_etapa2 = Column(Float, nullable=True)
    promedio_etapa3 = Column(Float, nullable=True)
    promedio_etapa4 = Column(Float, nullable=True)
    promedio_global = Column(Float, nullable=True)

    # ═══════════════════════════════════════════════════════════
    # COMENTARIOS
    # ═══════════════════════════════════════════════════════════
    comentary_hired_employer = Column(Text, nullable=True)  # Comentario del contratado al contratante
    comentary_employer_hired = Column(Text, nullable=True)  # Comentario del contratante al contratado
    
    # Comentarios por etapa (NUEVO)
    comentario_etapa1 = Column(Text, nullable=True)
    comentario_etapa2 = Column(Text, nullable=True)
    comentario_etapa3 = Column(Text, nullable=True)
    comentario_etapa4 = Column(Text, nullable=True)

    # ═══════════════════════════════════════════════════════════
    # EVIDENCIA / ARCHIVOS (NUEVO)
    # ═══════════════════════════════════════════════════════════
    # Se maneja con relación a Etapa que ya tiene fotos, audios, videos
    # Aquí solo guardamos referencias rápidas
    tiene_evidencia_etapa1 = Column(Boolean, default=False)
    tiene_evidencia_etapa2 = Column(Boolean, default=False)
    tiene_evidencia_etapa3 = Column(Boolean, default=False)
    tiene_evidencia_etapa4 = Column(Boolean, default=False)

    # ═══════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_modificacion = Column(DateTime, onupdate=datetime.utcnow, nullable=True)

    # ═══════════════════════════════════════════════════════════
    # RELACIONES
    # ═══════════════════════════════════════════════════════════
    overall_score_id = Column(Integer, ForeignKey('service_overall_scores.id_score', ondelete='CASCADE'), nullable=True)
    overall_score = relationship("ServiceOverallScores", back_populates="ratings")

    calificativo_id = Column(Integer, ForeignKey('service_qualifiers.id_qualifier'))
    calificativo = relationship('ServiceQualifiers', back_populates='ratings', lazy='joined')

    usuario = relationship("Usuario", back_populates="calificaciones")
    servicio = relationship("Servicio", back_populates="calificaciones")

    # ═══════════════════════════════════════════════════════════
    # MÉTODOS HELPER
    # ═══════════════════════════════════════════════════════════
    def habilitar_etapa4(self, dias_espera: int = 7):
        """Programa la habilitación de la etapa 4"""
        if self.etapa3_completada and self.servicio and self.servicio.fecha_fin:
            self.fecha_habilitacion_etapa4 = self.servicio.fecha_fin + timedelta(days=dias_espera)

    def etapa4_disponible(self) -> bool:
        """Verifica si la etapa 4 ya está disponible para calificar"""
        if not self.fecha_habilitacion_etapa4:
            return False
        return datetime.utcnow() >= self.fecha_habilitacion_etapa4

    def calcular_promedio_global(self):
        """Calcula el promedio global de todas las etapas completadas"""
        etapas = []
        
        if self.etapa1_completada and self.promedio_etapa1:
            etapas.append(self.promedio_etapa1)
        if self.etapa2_completada and self.promedio_etapa2:
            etapas.append(self.promedio_etapa2)
        if self.etapa3_completada and self.promedio_etapa3:
            etapas.append(self.promedio_etapa3)
        if (self.etapa4_completada_contratante or self.etapa4_completada_contratado) and self.promedio_etapa4:
            etapas.append(self.promedio_etapa4)
        
        if etapas:
            self.promedio_global = sum(etapas) / len(etapas)
        
        return self.promedio_global

    def calcular_promedio_etapa(self, etapa: int):
        """Calcula el promedio de una etapa específica"""
        cal_contratante = getattr(self, f'calificacion_recived_contratante{etapa}', None)
        cal_contratado = getattr(self, f'calificacion_recived_contratado{etapa}', None)
        
        valores = [v for v in [cal_contratante, cal_contratado] if v is not None]
        
        if valores:
            promedio = sum(valores) / len(valores)
            setattr(self, f'promedio_etapa{etapa}', promedio)
            return promedio
        return None

    def serialize(self):
        return {
            "id_rating": self.id_rating,
            "servicio_id": self.servicio_id,
            "usuario_id": self.usuario_id,
            "resultado_contratante": self.resultado_contratante,
            "resultado_contratado": self.resultado_contratado,
            "promedio_global": self.promedio_global,
            "fecha": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "etapas_completadas": {
                "etapa1": self.etapa1_completada,
                "etapa2": self.etapa2_completada,
                "etapa3": self.etapa3_completada,
                "etapa4_contratante": self.etapa4_completada_contratante,
                "etapa4_contratado": self.etapa4_completada_contratado
            }
        }

    def serialize_detallado(self):
        """Serialización completa con todas las etapas"""
        data = self.serialize()
        data.update({
            "etapa1": {
                "calificacion_contratante": self.calificacion_recived_contratante1,
                "razon_contratante": self.razon_contratante1,
                "calificacion_contratado": self.calificacion_recived_contratado1,
                "razon_contratado": self.razon_contratado1,
                "promedio": self.promedio_etapa1,
                "completada": self.etapa1_completada,
                "tiene_evidencia": self.tiene_evidencia_etapa1
            },
            "etapa2": {
                "calificacion_contratante": self.calificacion_recived_contratante2,
                "razon_contratante": self.razon_contratante2,
                "calificacion_contratado": self.calificacion_recived_contratado2,
                "razon_contratado": self.razon_contratado2,
                "promedio": self.promedio_etapa2,
                "completada": self.etapa2_completada,
                "tiene_evidencia": self.tiene_evidencia_etapa2
            },
            "etapa3": {
                "calificacion_contratante": self.calificacion_recived_contratante3,
                "razon_contratante": self.razon_contratante3,
                "calificacion_contratado": self.calificacion_recived_contratado3,
                "razon_contratado": self.razon_contratado3,
                "promedio": self.promedio_etapa3,
                "completada": self.etapa3_completada,
                "tiene_evidencia": self.tiene_evidencia_etapa3
            },
            "etapa4": {
                "calificacion_contratante": self.calificacion_recived_contratante4,
                "razon_contratante": self.razon_contratante4,
                "calificacion_contratado": self.calificacion_recived_contratado4,
                "razon_contratado": self.razon_contratado4,
                "promedio": self.promedio_etapa4,
                "completada_contratante": self.etapa4_completada_contratante,
                "completada_contratado": self.etapa4_completada_contratado,
                "disponible": self.etapa4_disponible(),
                "fecha_habilitacion": self.fecha_habilitacion_etapa4.isoformat() if self.fecha_habilitacion_etapa4 else None,
                "tiene_evidencia": self.tiene_evidencia_etapa4
            },
            "volveria_a_contratar": self.volveria_a_contratar,
            "volveria_a_ser_contratado": self.volveria_a_ser_contratado,
            "comentarios": {
                "contratante_a_contratado": self.comentary_employer_hired,
                "contratado_a_contratante": self.comentary_hired_employer
            }
        })
        return data


# Importaciones diferidas
from src.models.usuarios import Usuario
from src.models.servicio import Servicio
from src.models.colombia_data.ratings.service_overall_scores import ServiceOverallScores
from src.models.colombia_data.ratings.service_qualifiers import ServiceQualifiers