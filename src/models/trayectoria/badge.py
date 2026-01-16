"""
BizFlow Studio - Badge Model
Catálogo de badges/logros disponibles en el sistema
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime
from src.models.database import db
import logging

logger = logging.getLogger(__name__)

class Badge(db.Model):
    __tablename__ = "badges"

    # Identificador
    id = Column(Integer, primary_key=True)
    
    # === IDENTIFICACIÓN ===
    badge_id = Column(String(50), unique=True, nullable=False)  # 'primera-estrella', 'rayo-veloz', etc.
    
    # === INFORMACIÓN BÁSICA ===
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=False)
    emoji = Column(String(10), nullable=False)  # 🏆, ⚡, 💯, etc.
    
    # === ESTILO ===
    color = Column(String(7), nullable=False)  # Hex color
    color_rgb = Column(String(15), nullable=False)  # "251,191,36" para efectos
    
    # === CATEGORÍA ===
    categoria = Column(String(50), nullable=True)  # 'rendimiento', 'velocidad', 'calidad', etc.
    
    # === CRITERIOS DE DESBLOQUEO ===
    criterio_tipo = Column(String(50), nullable=True)  # 'calificaciones', 'proyectos', 'velocidad', etc.
    criterio_valor = Column(Integer, nullable=True)  # Valor necesario para desbloquear
    criterio_descripcion = Column(Text, nullable=True)  # Descripción técnica del criterio
    
    # === RAREZA Y ORDEN ===
    rareza = Column(String(20), nullable=True)  # 'comun', 'raro', 'epico', 'legendario'
    orden = Column(Integer, nullable=True, default=0)  # Orden de visualización
    
    # === ESTADO ===
    activo = Column(Boolean, default=True)  # Si el badge está activo en el sistema
    
    # === METADATOS ===
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    def serialize(self):
        """Serializar para API"""
        return {
            "id": self.badge_id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "emoji": self.emoji,
            "color": self.color,
            "rgb": self.color_rgb,
            "categoria": self.categoria,
            "rareza": self.rareza,
            "activo": self.activo
        }
    
    @staticmethod
    def inicializar_badges_sistema():
        """
        Crea los badges predeterminados del sistema si no existen
        Ejecutar una sola vez al inicializar la aplicación
        """
        badges_config = [
            {
                'badge_id': 'primera-estrella',
                'nombre': 'Primera Estrella',
                'descripcion': 'Primera calificación 5⭐',
                'emoji': '🏆',
                'color': '#fbbf24',
                'color_rgb': '251,191,36',
                'categoria': 'calidad',
                'criterio_tipo': 'calificaciones',
                'criterio_valor': 1,
                'rareza': 'comun',
                'orden': 1
            },
            {
                'badge_id': 'rayo-veloz',
                'nombre': 'Rayo Veloz',
                'descripcion': 'Respuesta en <30 min',
                'emoji': '⚡',
                'color': '#10b981',
                'color_rgb': '16,185,129',
                'categoria': 'velocidad',
                'criterio_tipo': 'tiempo_respuesta',
                'criterio_valor': 30,
                'rareza': 'comun',
                'orden': 2
            },
            {
                'badge_id': 'perfeccionista',
                'nombre': 'Perfeccionista',
                'descripcion': '10 trabajos perfectos',
                'emoji': '💯',
                'color': '#a855f7',
                'color_rgb': '168,85,247',
                'categoria': 'calidad',
                'criterio_tipo': 'proyectos_perfectos',
                'criterio_valor': 10,
                'rareza': 'raro',
                'orden': 3
            },
            {
                'badge_id': 'cliente-fiel',
                'nombre': 'Cliente Fiel',
                'descripcion': '5+ clientes recurrentes',
                'emoji': '🔄',
                'color': '#22d3ee',
                'color_rgb': '34,211,238',
                'categoria': 'fidelidad',
                'criterio_tipo': 'clientes_recurrentes',
                'criterio_valor': 5,
                'rareza': 'raro',
                'orden': 4
            },
            {
                'badge_id': 'estrella-ascenso',
                'nombre': 'Estrella en Ascenso',
                'descripcion': 'Score +10 en un mes',
                'emoji': '🚀',
                'color': '#ec4899',
                'color_rgb': '236,72,153',
                'categoria': 'progreso',
                'criterio_tipo': 'incremento_score',
                'criterio_valor': 10,
                'rareza': 'raro',
                'orden': 5
            },
            {
                'badge_id': 'puntual',
                'nombre': 'Puntual',
                'descripcion': '20 entregas a tiempo',
                'emoji': '📅',
                'color': '#3b82f6',
                'color_rgb': '59,130,246',
                'categoria': 'cumplimiento',
                'criterio_tipo': 'entregas_tiempo',
                'criterio_valor': 20,
                'rareza': 'comun',
                'orden': 6
            },
            {
                'badge_id': 'comunicador',
                'nombre': 'Comunicador',
                'descripcion': '100+ mensajes',
                'emoji': '💬',
                'color': '#f59e0b',
                'color_rgb': '245,158,11',
                'categoria': 'comunicacion',
                'criterio_tipo': 'mensajes_enviados',
                'criterio_valor': 100,
                'rareza': 'comun',
                'orden': 7
            },
            {
                'badge_id': 'certero',
                'nombre': 'Certero',
                'descripcion': '95%+ tasa de éxito',
                'emoji': '🎯',
                'color': '#6366f1',
                'color_rgb': '99,102,241',
                'categoria': 'rendimiento',
                'criterio_tipo': 'tasa_exito',
                'criterio_valor': 95,
                'rareza': 'raro',
                'orden': 8
            },
            {
                'badge_id': 'leyenda',
                'nombre': 'Leyenda',
                'descripcion': '100 proyectos exitosos',
                'emoji': '👑',
                'color': '#fbbf24',
                'color_rgb': '251,191,36',
                'categoria': 'volumen',
                'criterio_tipo': 'proyectos_completados',
                'criterio_valor': 100,
                'rareza': 'legendario',
                'orden': 9
            },
            {
                'badge_id': 'diamante',
                'nombre': 'Diamante',
                'descripcion': 'Score 95+ por 6 meses',
                'emoji': '💎',
                'color': '#22d3ee',
                'color_rgb': '34,211,238',
                'categoria': 'consistencia',
                'criterio_tipo': 'score_sostenido',
                'criterio_valor': 95,
                'rareza': 'legendario',
                'orden': 10
            },
            {
                'badge_id': 'super-estrella',
                'nombre': 'Súper Estrella',
                'descripcion': '50 reseñas 5 estrellas',
                'emoji': '🌟',
                'color': '#fbbf24',
                'color_rgb': '251,191,36',
                'categoria': 'calidad',
                'criterio_tipo': 'resenas_5_estrellas',
                'criterio_valor': 50,
                'rareza': 'epico',
                'orden': 11
            },
            {
                'badge_id': 'en-llamas',
                'nombre': 'En Llamas',
                'descripcion': '10 proyectos en un mes',
                'emoji': '🔥',
                'color': '#f59e0b',
                'color_rgb': '245,158,11',
                'categoria': 'velocidad',
                'criterio_tipo': 'proyectos_mes',
                'criterio_valor': 10,
                'rareza': 'epico',
                'orden': 12
            },
            {
                'badge_id': 'mentor',
                'nombre': 'Mentor',
                'descripcion': 'Ayudó a 5+ usuarios',
                'emoji': '🎓',
                'color': '#8b5cf6',
                'color_rgb': '139,92,246',
                'categoria': 'comunidad',
                'criterio_tipo': 'ayudas_prestadas',
                'criterio_valor': 5,
                'rareza': 'raro',
                'orden': 13
            },
            {
                'badge_id': 'innovador',
                'nombre': 'Innovador',
                'descripcion': 'Primer servicio en categoría',
                'emoji': '💡',
                'color': '#eab308',
                'color_rgb': '234,179,8',
                'categoria': 'innovacion',
                'criterio_tipo': 'primero_categoria',
                'criterio_valor': 1,
                'rareza': 'epico',
                'orden': 14
            },
            {
                'badge_id': 'veterano',
                'nombre': 'Veterano',
                'descripcion': '2+ años en la plataforma',
                'emoji': '🎖️',
                'color': '#14b8a6',
                'color_rgb': '20,184,166',
                'categoria': 'antiguedad',
                'criterio_tipo': 'tiempo_plataforma',
                'criterio_valor': 730,  # días
                'rareza': 'raro',
                'orden': 15
            }
        ]
        
        try:
            badges_creados = 0
            
            for config in badges_config:
                # Verificar si ya existe
                existe = Badge.query.filter_by(badge_id=config['badge_id']).first()
                
                if not existe:
                    badge = Badge(**config)
                    db.session.add(badge)
                    badges_creados += 1
            
            if badges_creados > 0:
                db.session.commit()
                logger.info(f"✅ {badges_creados} badges inicializados en el sistema")
            else:
                logger.info("ℹ️  Badges ya existían en el sistema")
            
            return badges_creados
            
        except Exception as e:
            logger.error(f"Error inicializando badges: {str(e)}")
            db.session.rollback()
            return 0
    
    def __repr__(self):
        return f"<Badge {self.badge_id} - {self.nombre}>"