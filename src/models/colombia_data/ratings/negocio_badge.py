"""
Modelo NegocioBadge - Catálogo de Insignias
TuKomercio Suite - BizScore

Define todas las insignias disponibles en el sistema.
Cada insignia tiene criterios de desbloqueo automáticos.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Modelo NegocioBadge cargado correctamente.")


class NegocioBadge(db.Model):
    __tablename__ = "negocio_badges"

    # ═══════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ═══════════════════════════════════════════════════════════
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)  # 'perfeccionista', 'rayo_veloz'
    nombre = Column(String(100), nullable=False)              # 'Perfeccionista'
    descripcion = Column(String(255), nullable=True)          # '10 trabajos perfectos'

    # ═══════════════════════════════════════════════════════════
    # APARIENCIA VISUAL
    # ═══════════════════════════════════════════════════════════
    icono = Column(String(50), default="bi-award")            # Bootstrap Icons class
    color_primario = Column(String(7), default="#f59e0b")     # Color hex principal
    color_fondo = Column(String(30), default="rgba(245,158,11,0.15)")  # Color de fondo
    gradiente = Column(String(200), nullable=True)            # Gradiente CSS opcional
    
    # Imagen custom (si no usa icono de Bootstrap)
    imagen_url = Column(String(500), nullable=True)

    # ═══════════════════════════════════════════════════════════
    # CATEGORIZACIÓN
    # ═══════════════════════════════════════════════════════════
    categoria = Column(String(50), default="general")
    # Categorías: calidad, velocidad, confianza, popularidad, trayectoria, especial
    
    nivel = Column(Integer, default=1)  # 1=Bronce, 2=Plata, 3=Oro, 4=Platino
    puntos = Column(Integer, default=10)  # Puntos que otorga al desbloquear

    # ═══════════════════════════════════════════════════════════
    # CRITERIOS DE DESBLOQUEO
    # ═══════════════════════════════════════════════════════════
    criterio_tipo = Column(String(50), nullable=False)
    # Tipos de criterio:
    # - contratos_completados
    # - trabajos_perfectos (5 estrellas)
    # - calificaciones_5
    # - tiempo_respuesta_hrs
    # - entregas_anticipadas
    # - verificado
    # - contratos_sin_disputa
    # - clientes_recurrentes
    # - percentil
    # - dias_activo
    # - videos_subidos
    
    criterio_valor = Column(Float, nullable=False)  # 10, 95, 1 (hora), etc.
    criterio_operador = Column(String(5), default=">=")  # '>=', '<=', '==', '>'

    # ═══════════════════════════════════════════════════════════
    # CONFIGURACIÓN
    # ═══════════════════════════════════════════════════════════
    activo = Column(Boolean, default=True)
    visible_en_catalogo = Column(Boolean, default=True)  # Si se muestra en lista de badges
    es_secreto = Column(Boolean, default=False)  # Badge sorpresa
    
    orden = Column(Integer, default=0)  # Orden de aparición
    
    # Exclusividad
    es_exclusivo = Column(Boolean, default=False)  # Solo uno puede tenerlo
    max_otorgamientos = Column(Integer, nullable=True)  # Límite de cuántos se otorgan

    # ═══════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, onupdate=datetime.utcnow)

    # ═══════════════════════════════════════════════════════════
    # ESTADÍSTICAS
    # ═══════════════════════════════════════════════════════════
    total_otorgados = Column(Integer, default=0)

    # ═══════════════════════════════════════════════════════════
    # RELACIONES
    # ═══════════════════════════════════════════════════════════
    badges_obtenidos = relationship("NegocioBadgeObtenido", back_populates="badge")

    # ═══════════════════════════════════════════════════════════
    # MÉTODOS HELPER
    # ═══════════════════════════════════════════════════════════
    def verificar_criterio(self, valor_actual: float) -> bool:
        """Verifica si un valor cumple el criterio del badge"""
        operadores = {
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '==': lambda a, b: a == b,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '!=': lambda a, b: a != b
        }
        
        operador_fn = operadores.get(self.criterio_operador, operadores['>='])
        return operador_fn(valor_actual, self.criterio_valor)

    def puede_otorgarse(self) -> bool:
        """Verifica si el badge aún puede otorgarse"""
        if not self.activo:
            return False
        if self.max_otorgamientos and self.total_otorgados >= self.max_otorgamientos:
            return False
        return True

    def get_nivel_nombre(self) -> str:
        """Retorna el nombre del nivel"""
        niveles = {1: 'Bronce', 2: 'Plata', 3: 'Oro', 4: 'Platino', 5: 'Diamante'}
        return niveles.get(self.nivel, 'Común')

    def serialize(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "icono": self.icono,
            "color_primario": self.color_primario,
            "color_fondo": self.color_fondo,
            "gradiente": self.gradiente,
            "imagen_url": self.imagen_url,
            "categoria": self.categoria,
            "nivel": self.nivel,
            "nivel_nombre": self.get_nivel_nombre(),
            "puntos": self.puntos,
            "criterio": {
                "tipo": self.criterio_tipo,
                "valor": self.criterio_valor,
                "operador": self.criterio_operador
            },
            "es_secreto": self.es_secreto,
            "total_otorgados": self.total_otorgados
        }

    def serialize_publico(self):
        """Serialización para vista pública (oculta secretos)"""
        if self.es_secreto:
            return {
                "id": self.id,
                "nombre": "???",
                "descripcion": "Badge secreto - Descúbrelo",
                "icono": "bi-question-circle",
                "color_primario": "#64748b",
                "es_secreto": True
            }
        return self.serialize()


# ═══════════════════════════════════════════════════════════════════
# DATOS INICIALES DE BADGES (para seed)
# ═══════════════════════════════════════════════════════════════════
BADGES_INICIALES = [
    # ═══ CALIDAD ═══
    {
        "codigo": "perfeccionista",
        "nombre": "Perfeccionista",
        "descripcion": "10 trabajos con calificación perfecta",
        "icono": "bi-gem",
        "color_primario": "#a855f7",
        "color_fondo": "rgba(168,85,247,0.15)",
        "categoria": "calidad",
        "nivel": 3,
        "puntos": 50,
        "criterio_tipo": "trabajos_perfectos",
        "criterio_valor": 10,
        "criterio_operador": ">="
    },
    {
        "codigo": "primera_estrella",
        "nombre": "Primera Estrella",
        "descripcion": "Primera calificación de 5 estrellas",
        "icono": "bi-star-fill",
        "color_primario": "#f59e0b",
        "color_fondo": "rgba(245,158,11,0.15)",
        "categoria": "calidad",
        "nivel": 1,
        "puntos": 10,
        "criterio_tipo": "calificaciones_5",
        "criterio_valor": 1,
        "criterio_operador": ">="
    },
    {
        "codigo": "cinco_estrellas",
        "nombre": "Coleccionista de Estrellas",
        "descripcion": "50 calificaciones de 5 estrellas",
        "icono": "bi-stars",
        "color_primario": "#fbbf24",
        "color_fondo": "rgba(251,191,36,0.15)",
        "categoria": "calidad",
        "nivel": 3,
        "puntos": 75,
        "criterio_tipo": "calificaciones_5",
        "criterio_valor": 50,
        "criterio_operador": ">="
    },
    
    # ═══ VELOCIDAD ═══
    {
        "codigo": "rayo_veloz",
        "nombre": "Rayo Veloz",
        "descripcion": "Tiempo de respuesta menor a 1 hora",
        "icono": "bi-lightning-charge-fill",
        "color_primario": "#10b981",
        "color_fondo": "rgba(16,185,129,0.15)",
        "categoria": "velocidad",
        "nivel": 2,
        "puntos": 25,
        "criterio_tipo": "tiempo_respuesta_hrs",
        "criterio_valor": 1,
        "criterio_operador": "<="
    },
    {
        "codigo": "entrega_express",
        "nombre": "Entrega Express",
        "descripcion": "5 entregas antes del tiempo estimado",
        "icono": "bi-rocket-takeoff-fill",
        "color_primario": "#22d3ee",
        "color_fondo": "rgba(34,211,238,0.15)",
        "categoria": "velocidad",
        "nivel": 2,
        "puntos": 30,
        "criterio_tipo": "entregas_anticipadas",
        "criterio_valor": 5,
        "criterio_operador": ">="
    },
    {
        "codigo": "supersonic",
        "nombre": "Supersónico",
        "descripcion": "20 entregas anticipadas",
        "icono": "bi-airplane-fill",
        "color_primario": "#06b6d4",
        "color_fondo": "rgba(6,182,212,0.15)",
        "categoria": "velocidad",
        "nivel": 3,
        "puntos": 60,
        "criterio_tipo": "entregas_anticipadas",
        "criterio_valor": 20,
        "criterio_operador": ">="
    },
    
    # ═══ CONFIANZA ═══
    {
        "codigo": "verificado",
        "nombre": "Verificado",
        "descripcion": "Identidad verificada por TuKomercio",
        "icono": "bi-patch-check-fill",
        "color_primario": "#3b82f6",
        "color_fondo": "rgba(59,130,246,0.15)",
        "categoria": "confianza",
        "nivel": 2,
        "puntos": 40,
        "criterio_tipo": "verificado",
        "criterio_valor": 1,
        "criterio_operador": "=="
    },
    {
        "codigo": "sin_disputas",
        "nombre": "Récord Limpio",
        "descripcion": "50 contratos sin ninguna disputa",
        "icono": "bi-shield-check",
        "color_primario": "#10b981",
        "color_fondo": "rgba(16,185,129,0.15)",
        "categoria": "confianza",
        "nivel": 3,
        "puntos": 70,
        "criterio_tipo": "contratos_sin_disputa",
        "criterio_valor": 50,
        "criterio_operador": ">="
    },
    {
        "codigo": "intachable",
        "nombre": "Intachable",
        "descripcion": "100 contratos sin disputas",
        "icono": "bi-shield-fill-check",
        "color_primario": "#059669",
        "color_fondo": "rgba(5,150,105,0.15)",
        "categoria": "confianza",
        "nivel": 4,
        "puntos": 100,
        "criterio_tipo": "contratos_sin_disputa",
        "criterio_valor": 100,
        "criterio_operador": ">="
    },
    
    # ═══ POPULARIDAD ═══
    {
        "codigo": "cliente_frecuente",
        "nombre": "Favorito de Clientes",
        "descripcion": "10 clientes que han vuelto a contratarte",
        "icono": "bi-people-fill",
        "color_primario": "#ec4899",
        "color_fondo": "rgba(236,72,153,0.15)",
        "categoria": "popularidad",
        "nivel": 2,
        "puntos": 35,
        "criterio_tipo": "clientes_recurrentes",
        "criterio_valor": 10,
        "criterio_operador": ">="
    },
    {
        "codigo": "top_10",
        "nombre": "Top 10%",
        "descripcion": "Entre el 10% mejor de tu categoría",
        "icono": "bi-graph-up-arrow",
        "color_primario": "#f59e0b",
        "color_fondo": "rgba(245,158,11,0.15)",
        "categoria": "popularidad",
        "nivel": 3,
        "puntos": 50,
        "criterio_tipo": "percentil",
        "criterio_valor": 90,
        "criterio_operador": ">="
    },
    {
        "codigo": "top_5",
        "nombre": "Top 5%",
        "descripcion": "Entre el 5% mejor de tu categoría",
        "icono": "bi-award-fill",
        "color_primario": "#f59e0b",
        "color_fondo": "rgba(245,158,11,0.15)",
        "gradiente": "linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)",
        "categoria": "popularidad",
        "nivel": 4,
        "puntos": 80,
        "criterio_tipo": "percentil",
        "criterio_valor": 95,
        "criterio_operador": ">="
    },
    
    # ═══ TRAYECTORIA ═══
    {
        "codigo": "novato",
        "nombre": "Novato Prometedor",
        "descripcion": "Primer contrato completado",
        "icono": "bi-rocket-takeoff",
        "color_primario": "#6366f1",
        "color_fondo": "rgba(99,102,241,0.15)",
        "categoria": "trayectoria",
        "nivel": 1,
        "puntos": 10,
        "criterio_tipo": "contratos_completados",
        "criterio_valor": 1,
        "criterio_operador": ">="
    },
    {
        "codigo": "experimentado",
        "nombre": "Experimentado",
        "descripcion": "25 contratos completados",
        "icono": "bi-briefcase-fill",
        "color_primario": "#8b5cf6",
        "color_fondo": "rgba(139,92,246,0.15)",
        "categoria": "trayectoria",
        "nivel": 2,
        "puntos": 30,
        "criterio_tipo": "contratos_completados",
        "criterio_valor": 25,
        "criterio_operador": ">="
    },
    {
        "codigo": "veterano",
        "nombre": "Veterano",
        "descripcion": "100 contratos completados",
        "icono": "bi-trophy-fill",
        "color_primario": "#f59e0b",
        "color_fondo": "rgba(245,158,11,0.15)",
        "gradiente": "linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)",
        "categoria": "trayectoria",
        "nivel": 3,
        "puntos": 75,
        "criterio_tipo": "contratos_completados",
        "criterio_valor": 100,
        "criterio_operador": ">="
    },
    {
        "codigo": "leyenda",
        "nombre": "Leyenda",
        "descripcion": "500 contratos completados",
        "icono": "bi-trophy",
        "color_primario": "#eab308",
        "color_fondo": "rgba(234,179,8,0.15)",
        "gradiente": "linear-gradient(135deg, #eab308 0%, #facc15 50%, #fef08a 100%)",
        "categoria": "trayectoria",
        "nivel": 4,
        "puntos": 150,
        "criterio_tipo": "contratos_completados",
        "criterio_valor": 500,
        "criterio_operador": ">="
    },
    
    # ═══ ESPECIALES ═══
    {
        "codigo": "pioneer",
        "nombre": "Pionero",
        "descripcion": "Entre los primeros 100 negocios registrados",
        "icono": "bi-flag-fill",
        "color_primario": "#ec4899",
        "color_fondo": "rgba(236,72,153,0.15)",
        "categoria": "especial",
        "nivel": 3,
        "puntos": 100,
        "criterio_tipo": "orden_registro",
        "criterio_valor": 100,
        "criterio_operador": "<=",
        "es_exclusivo": True,
        "max_otorgamientos": 100
    },
    {
        "codigo": "creador_contenido",
        "nombre": "Creador de Contenido",
        "descripcion": "5 videos en tu portfolio",
        "icono": "bi-camera-video-fill",
        "color_primario": "#f43f5e",
        "color_fondo": "rgba(244,63,94,0.15)",
        "categoria": "especial",
        "nivel": 2,
        "puntos": 25,
        "criterio_tipo": "videos_subidos",
        "criterio_valor": 5,
        "criterio_operador": ">="
    }
]