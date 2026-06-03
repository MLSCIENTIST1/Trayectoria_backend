# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗██╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗  ██████╗██╗ ██████╗ 
# ╚══██╔══╝██║   ██║██║ ██╔╝██╔═══██╗████╗ ████║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗
#    ██║   ██║   ██║█████╔╝ ██║   ██║██╔████╔██║█████╗  ██████╔╝██║     ██║██║   ██║
#    ██║   ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║   ██║
#    ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║╚██████╔╝
#    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝ 
# ═══════════════════════════════════════════════════════════════════════════════
#
# TUKOMERCIO - Plataforma de Comercio Electrónico, Gamificación y Gestión Empresarial
# Anteriormente conocido como: Trayectoria / BizFlow Studio
#
# ═══════════════════════════════════════════════════════════════════════════════
# AVISO DE PROPIEDAD INTELECTUAL Y DERECHOS DE AUTOR
# ═══════════════════════════════════════════════════════════════════════════════
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#
# TITULAR DE DERECHOS:
#   Nombre:     Carlos Eduardo Huérfano Bermúdez
#   C.C.:       1.064.986.917 (Cereté, Córdoba, Colombia)
#   Contacto:   carlos-5100@hotmail.com | +57 322 818 8375
#   Ubicación:  Bogotá D.C., Colombia
#
# INFORMACIÓN DEL PROYECTO:
#   Nombre:     TuKomercio
#   Inicio:     Julio 24, 2024
#   Repositorio: github.com/routeres (routeres@gmail.com)
#
# ═══════════════════════════════════════════════════════════════════════════════
# TÉRMINOS DE USO Y RESTRICCIONES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este código fuente es CONFIDENCIAL y constituye un SECRETO COMERCIAL.
#
# QUEDA ESTRICTAMENTE PROHIBIDO sin autorización ESCRITA del titular:
#
#   1. Copiar, reproducir o duplicar este código, total o parcialmente
#   2. Modificar, adaptar o crear obras derivadas
#   3. Distribuir, publicar, sublicenciar o transferir a terceros
#   4. Usar para desarrollo de productos competidores
#   5. Realizar ingeniería inversa, descompilar o desensamblar
#   6. Remover o alterar este aviso de propiedad intelectual
#
# El acceso a este código NO otorga ninguna licencia implícita o explícita.
#
# ═══════════════════════════════════════════════════════════════════════════════
# PROTECCIÓN LEGAL
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este software está protegido por:
#
#   • Ley 23 de 1982 - Derechos de Autor (Colombia)
#   • Ley 1915 de 2018 - Modernización Derechos de Autor (Colombia)
#   • Decisión Andina 351 de 1993 - Régimen Común sobre Derecho de Autor
#   • Convenio de Berna para la Protección de Obras Literarias y Artísticas
#   • Tratado OMPI sobre Derecho de Autor (WCT)
#   • Acuerdo ADPIC/TRIPS - Organización Mundial del Comercio
#
# SANCIONES POR INFRACCIÓN:
#   • Civiles: Indemnización por daños y perjuicios (Art. 57, Ley 23/1982)
#   • Penales: Prisión de 4 a 8 años y multa (Art. 271, Código Penal Colombiano)
#
# ═══════════════════════════════════════════════════════════════════════════════
# JURISDICCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
#
# Cualquier disputa será resuelta exclusivamente por los tribunales de
# Bogotá D.C., Colombia, bajo las leyes de la República de Colombia.
#
# ═══════════════════════════════════════════════════════════════════════════════
#
# Para solicitar autorización de uso: carlos-5100@hotmail.com
#
# ═══════════════════════════════════════════════════════════════════════════════



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
    # ═══════════════════════════════════════════════════════════════
    # ★★★ FUNDADOR — insignia premium, exclusiva de los primeros 50 ★★★
    # Es la insignia más prestigiosa de la plataforma. Diseño único.
    # Criterio: el dueño del negocio está entre los primeros 50 usuarios
    # registrados (ver FUNDADOR_CUPO en badge_verification_service).
    # ═══════════════════════════════════════════════════════════════
    {
        "codigo": "fundador",
        "nombre": "Fundador",
        "descripcion": "Miembro fundador de TuKomercio — uno de los primeros 50 en creer en el sueño",
        "icono": "bi-patch-check-fill",
        "color_primario": "#fbbf24",
        "color_fondo": "rgba(251,191,36,0.18)",
        "gradiente": "linear-gradient(135deg, #fde68a 0%, #fbbf24 35%, #a855f7 75%, #6366f1 100%)",
        "categoria": "especial",
        "nivel": 5,                       # Diamante
        "puntos": 250,
        "criterio_tipo": "es_fundador",
        "criterio_valor": 1,
        "criterio_operador": ">=",
        "es_exclusivo": True,
        "max_otorgamientos": None,        # el cupo (50 usuarios) lo gobierna el criterio
        "orden": 0,                       # aparece de primero
    },

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
    },

    # ═══ E-COMMERCE · PEDIDOS COMPLETADOS (S9) ═══
    {
        "codigo": "primera_venta", "nombre": "Primera Venta",
        "descripcion": "Tu primer pedido entregado",
        "icono": "bi-bag-check-fill", "color_primario": "#10b981",
        "color_fondo": "rgba(16,185,129,0.15)", "categoria": "ventas",
        "nivel": 1, "puntos": 15,
        "criterio_tipo": "pedidos_completados", "criterio_valor": 1, "criterio_operador": ">=",
    },
    {
        "codigo": "despegando", "nombre": "Despegando",
        "descripcion": "10 pedidos entregados",
        "icono": "bi-rocket-takeoff-fill", "color_primario": "#3b82f6",
        "color_fondo": "rgba(59,130,246,0.15)", "categoria": "ventas",
        "nivel": 1, "puntos": 25,
        "criterio_tipo": "pedidos_completados", "criterio_valor": 10, "criterio_operador": ">=",
    },
    {
        "codigo": "en_vuelo", "nombre": "En Vuelo",
        "descripcion": "50 pedidos entregados",
        "icono": "bi-airplane-fill", "color_primario": "#6366f1",
        "color_fondo": "rgba(99,102,241,0.15)", "categoria": "ventas",
        "nivel": 2, "puntos": 40,
        "criterio_tipo": "pedidos_completados", "criterio_valor": 50, "criterio_operador": ">=",
    },
    {
        "codigo": "maquina_ventas", "nombre": "Máquina de Ventas",
        "descripcion": "200 pedidos entregados",
        "icono": "bi-gear-wide-connected", "color_primario": "#a855f7",
        "color_fondo": "rgba(168,85,247,0.15)", "categoria": "ventas",
        "nivel": 3, "puntos": 75,
        "criterio_tipo": "pedidos_completados", "criterio_valor": 200, "criterio_operador": ">=",
    },
    {
        "codigo": "leyenda_ventas", "nombre": "Leyenda de Ventas",
        "descripcion": "500 pedidos entregados",
        "icono": "bi-trophy-fill", "color_primario": "#fbbf24",
        "color_fondo": "rgba(251,191,36,0.15)", "categoria": "ventas",
        "nivel": 4, "puntos": 150,
        "criterio_tipo": "pedidos_completados", "criterio_valor": 500, "criterio_operador": ">=",
    },

    # ═══ E-COMMERCE · INGRESOS Y CALIDAD (S10) ═══
    {
        "codigo": "primer_millon", "nombre": "Primer Millón",
        "descripcion": "$1.000.000 en ventas acumuladas",
        "icono": "bi-cash-stack", "color_primario": "#10b981",
        "color_fondo": "rgba(16,185,129,0.15)", "categoria": "ventas",
        "nivel": 2, "puntos": 50,
        "criterio_tipo": "ventas_cop", "criterio_valor": 1000000, "criterio_operador": ">=",
    },
    {
        "codigo": "top_vendedor", "nombre": "Top Vendedor",
        "descripcion": "$10.000.000 en ventas acumuladas",
        "icono": "bi-graph-up-arrow", "color_primario": "#f59e0b",
        "color_fondo": "rgba(245,158,11,0.15)", "categoria": "ventas",
        "nivel": 3, "puntos": 90,
        "criterio_tipo": "ventas_cop", "criterio_valor": 10000000, "criterio_operador": ">=",
    },
    {
        "codigo": "unicornio", "nombre": "Unicornio",
        "descripcion": "$100.000.000 en ventas acumuladas",
        "icono": "bi-stars", "color_primario": "#a855f7",
        "color_fondo": "rgba(168,85,247,0.15)", "categoria": "ventas",
        "nivel": 5, "puntos": 200,
        "criterio_tipo": "ventas_cop", "criterio_valor": 100000000, "criterio_operador": ">=",
    },
    {
        "codigo": "bien_calificado", "nombre": "Bien Calificado",
        "descripcion": "4.5★ o más con 10+ reseñas",
        "icono": "bi-star-fill", "color_primario": "#fbbf24",
        "color_fondo": "rgba(251,191,36,0.15)", "categoria": "calidad",
        "nivel": 2, "puntos": 40,
        "criterio_tipo": "calificacion_calificada", "criterio_valor": 4.5, "criterio_operador": ">=",
    },
    {
        "codigo": "confiable", "nombre": "Confiable",
        "descripcion": "50 entregas netas sin devolución",
        "icono": "bi-shield-fill-check", "color_primario": "#06b6d4",
        "color_fondo": "rgba(6,182,212,0.15)", "categoria": "confianza",
        "nivel": 3, "puntos": 60,
        "criterio_tipo": "pedidos_sin_devolucion", "criterio_valor": 50, "criterio_operador": ">=",
    },
    {
        "codigo": "catalogo_rico", "nombre": "Catálogo Rico",
        "descripcion": "20 o más productos activos",
        "icono": "bi-grid-3x3-gap-fill", "color_primario": "#8b5cf6",
        "color_fondo": "rgba(139,92,246,0.15)", "categoria": "trayectoria",
        "nivel": 1, "puntos": 20,
        "criterio_tipo": "productos_activos", "criterio_valor": 20, "criterio_operador": ">=",
    },

    # ═══ CREADOR / EMPRENDEDOR (S11) — criterio sobre el DUEÑO ═══
    {
        "codigo": "multi_negocio", "nombre": "Multi-negocio",
        "descripcion": "Has creado 3 o más negocios",
        "icono": "bi-buildings-fill", "color_primario": "#3b82f6",
        "color_fondo": "rgba(59,130,246,0.15)", "categoria": "trayectoria",
        "nivel": 2, "puntos": 35,
        "criterio_tipo": "negocios_del_owner", "criterio_valor": 3, "criterio_operador": ">=",
    },
    {
        "codigo": "emprendedor_serial", "nombre": "Emprendedor Serial",
        "descripcion": "Has creado 5 o más negocios",
        "icono": "bi-diagram-3-fill", "color_primario": "#a855f7",
        "color_fondo": "rgba(168,85,247,0.15)", "categoria": "trayectoria",
        "nivel": 3, "puntos": 70,
        "criterio_tipo": "negocios_del_owner", "criterio_valor": 5, "criterio_operador": ">=",
    },
    {
        "codigo": "veterano_tuko", "nombre": "Veterano TuKomercio",
        "descripcion": "180 días desde tu registro",
        "icono": "bi-calendar-heart-fill", "color_primario": "#06b6d4",
        "color_fondo": "rgba(6,182,212,0.15)", "categoria": "trayectoria",
        "nivel": 2, "puntos": 40,
        "criterio_tipo": "dias_registrado_owner", "criterio_valor": 180, "criterio_operador": ">=",
    },
    {
        "codigo": "pilar_comunidad", "nombre": "Pilar de la Comunidad",
        "descripcion": "Un año completo con TuKomercio",
        "icono": "bi-award-fill", "color_primario": "#fbbf24",
        "color_fondo": "rgba(251,191,36,0.15)", "categoria": "trayectoria",
        "nivel": 4, "puntos": 120,
        "criterio_tipo": "dias_registrado_owner", "criterio_valor": 365, "criterio_operador": ">=",
    },

    # ═══ SECRETOS 🔒 (S12) — criterio oculto, se revela al ganarlo ═══
    {
        "codigo": "noctambulo", "nombre": "Noctámbulo",
        "descripcion": "Cerraste una venta entre la medianoche y las 4 a. m.",
        "icono": "bi-moon-stars-fill", "color_primario": "#6366f1",
        "color_fondo": "rgba(99,102,241,0.15)", "categoria": "especial",
        "nivel": 2, "puntos": 30, "es_secreto": True,
        "criterio_tipo": "ventas_madrugada", "criterio_valor": 1, "criterio_operador": ">=",
    },
    {
        "codigo": "velocista", "nombre": "Velocista",
        "descripcion": "10 pedidos entregados en un mismo día",
        "icono": "bi-lightning-charge-fill", "color_primario": "#f59e0b",
        "color_fondo": "rgba(245,158,11,0.15)", "categoria": "especial",
        "nivel": 3, "puntos": 60, "es_secreto": True,
        "criterio_tipo": "max_pedidos_dia", "criterio_valor": 10, "criterio_operador": ">=",
    },
    {
        "codigo": "cumpleanero", "nombre": "En tu Aniversario",
        "descripcion": "Vendiste el día del aniversario de tu negocio",
        "icono": "bi-balloon-heart-fill", "color_primario": "#ec4899",
        "color_fondo": "rgba(236,72,153,0.15)", "categoria": "especial",
        "nivel": 3, "puntos": 50, "es_secreto": True,
        "criterio_tipo": "ventas_aniversario", "criterio_valor": 1, "criterio_operador": ">=",
    },
    {
        "codigo": "guerrero_finde", "nombre": "Guerrero de Fin de Semana",
        "descripcion": "20 pedidos entregados en fines de semana",
        "icono": "bi-emoji-sunglasses-fill", "color_primario": "#10b981",
        "color_fondo": "rgba(16,185,129,0.15)", "categoria": "especial",
        "nivel": 2, "puntos": 45, "es_secreto": True,
        "criterio_tipo": "ventas_fin_semana", "criterio_valor": 20, "criterio_operador": ">=",
    },

    # ═══ TEMPORADA 🎄 (S13) — solo se ganan vendiendo DURANTE la fecha ═══
    # La métrica devuelve >=1 únicamente si HOY cae dentro de la temporada
    # y el negocio vendió en ella. Fuera de temporada → 0 (no otorgable).
    {
        "codigo": "navidad_2026", "nombre": "Espíritu Navideño",
        "descripcion": "Vendiste durante la temporada navideña (diciembre)",
        "icono": "bi-snow2", "color_primario": "#ef4444",
        "color_fondo": "rgba(239,68,68,0.15)", "categoria": "especial",
        "nivel": 2, "puntos": 40, "es_secreto": False,
        "criterio_tipo": "ventas_navidad", "criterio_valor": 1, "criterio_operador": ">=",
    },
    {
        "codigo": "amor_amistad", "nombre": "Amor y Amistad",
        "descripcion": "Vendiste en septiembre, mes del Amor y la Amistad",
        "icono": "bi-heart-fill", "color_primario": "#ec4899",
        "color_fondo": "rgba(236,72,153,0.15)", "categoria": "especial",
        "nivel": 2, "puntos": 40, "es_secreto": False,
        "criterio_tipo": "ventas_amor_amistad", "criterio_valor": 1, "criterio_operador": ">=",
    },
    {
        "codigo": "dia_madre", "nombre": "Para Mamá",
        "descripcion": "Vendiste en mayo, mes de las madres",
        "icono": "bi-flower1", "color_primario": "#f59e0b",
        "color_fondo": "rgba(245,158,11,0.15)", "categoria": "especial",
        "nivel": 2, "puntos": 40, "es_secreto": False,
        "criterio_tipo": "ventas_dia_madre", "criterio_valor": 1, "criterio_operador": ">=",
    },
    {
        "codigo": "black_friday", "nombre": "Black Friday",
        "descripcion": "Vendiste durante el Black Friday (20–30 de noviembre)",
        "icono": "bi-bag-heart-fill", "color_primario": "#0f172a",
        "color_fondo": "rgba(15,23,42,0.35)", "categoria": "especial",
        "nivel": 3, "puntos": 55, "es_secreto": False,
        "criterio_tipo": "ventas_black_friday", "criterio_valor": 1, "criterio_operador": ">=",
    },

    # ═══ COMUNIDAD (S17) ═══
    {
        "codigo": "embajador", "nombre": "Embajador",
        "descripcion": "Apoyaste a la comunidad votando en 10 challenges",
        "icono": "bi-hand-thumbs-up-fill", "color_primario": "#3b82f6",
        "color_fondo": "rgba(59,130,246,0.15)", "categoria": "popularidad",
        "nivel": 2, "puntos": 30,
        "criterio_tipo": "votos_emitidos_owner", "criterio_valor": 10, "criterio_operador": ">=",
    },
    {
        "codigo": "vitrina_visitada", "nombre": "Vitrina Visitada",
        "descripcion": "Tu tienda recibió 100 visitas",
        "icono": "bi-eye-fill", "color_primario": "#06b6d4",
        "color_fondo": "rgba(6,182,212,0.15)", "categoria": "popularidad",
        "nivel": 2, "puntos": 35,
        "criterio_tipo": "visitas_tienda", "criterio_valor": 100, "criterio_operador": ">=",
    },
    {
        "codigo": "primera_resena", "nombre": "Primera Reseña",
        "descripcion": "Recibiste tu primera reseña de un cliente",
        "icono": "bi-chat-heart-fill", "color_primario": "#f59e0b",
        "color_fondo": "rgba(245,158,11,0.15)", "categoria": "popularidad",
        "nivel": 1, "puntos": 15,
        "criterio_tipo": "resenas_recibidas", "criterio_valor": 1, "criterio_operador": ">=",
    },
    {
        "codigo": "fan_club", "nombre": "Club de Fans",
        "descripcion": "25 reseñas de clientes — ¡tienes seguidores!",
        "icono": "bi-people-fill", "color_primario": "#ec4899",
        "color_fondo": "rgba(236,72,153,0.15)", "categoria": "popularidad",
        "nivel": 3, "puntos": 60,
        "criterio_tipo": "resenas_recibidas", "criterio_valor": 25, "criterio_operador": ">=",
    }
]


# ═══════════════════════════════════════════════════════════════════
# SEEDER IDEMPOTENTE DEL CATÁLOGO DE BADGES
# ═══════════════════════════════════════════════════════════════════
# IMPORTANTE: BADGES_INICIALES estaba definido pero NUNCA se insertaba en
# la base de datos. Esta función siembra/actualiza el catálogo de forma
# idempotente (upsert por 'codigo'). Se llama al arranque (run.py).
# ═══════════════════════════════════════════════════════════════════

# Campos visuales/textuales que SÍ se actualizan en cada arranque (permite
# mejorar diseños sin perder los badges ya otorgados). Los criterios NO se
# tocan si el badge ya existe, para no alterar reglas en caliente sin querer.
_CAMPOS_ACTUALIZABLES = (
    'nombre', 'descripcion', 'icono', 'color_primario',
    'color_fondo', 'gradiente', 'categoria', 'nivel', 'puntos', 'orden',
)


def seed_badges_catalogo(db_session, actualizar_visual=True):
    """
    Inserta los badges de BADGES_INICIALES que falten y (opcionalmente)
    refresca los campos visuales de los existentes. Idempotente.

    Returns: dict {creados, actualizados, total}
    """
    creados = 0
    actualizados = 0

    existentes = {b.codigo: b for b in db_session.query(NegocioBadge).all()}

    for data in BADGES_INICIALES:
        codigo = data['codigo']
        existente = existentes.get(codigo)

        if existente is None:
            badge = NegocioBadge(
                codigo=codigo,
                nombre=data['nombre'],
                descripcion=data.get('descripcion'),
                icono=data.get('icono', 'bi-award'),
                color_primario=data.get('color_primario', '#f59e0b'),
                color_fondo=data.get('color_fondo', 'rgba(245,158,11,0.15)'),
                gradiente=data.get('gradiente'),
                imagen_url=data.get('imagen_url'),
                categoria=data.get('categoria', 'general'),
                nivel=data.get('nivel', 1),
                puntos=data.get('puntos', 10),
                criterio_tipo=data['criterio_tipo'],
                criterio_valor=data['criterio_valor'],
                criterio_operador=data.get('criterio_operador', '>='),
                activo=data.get('activo', True),
                visible_en_catalogo=data.get('visible_en_catalogo', True),
                es_secreto=data.get('es_secreto', False),
                orden=data.get('orden', 0),
                es_exclusivo=data.get('es_exclusivo', False),
                max_otorgamientos=data.get('max_otorgamientos'),
            )
            db_session.add(badge)
            creados += 1
        elif actualizar_visual:
            cambio = False
            for campo in _CAMPOS_ACTUALIZABLES:
                if campo in data and getattr(existente, campo, None) != data[campo]:
                    setattr(existente, campo, data[campo])
                    cambio = True
            if cambio:
                actualizados += 1

    db_session.commit()
    return {'creados': creados, 'actualizados': actualizados, 'total': len(BADGES_INICIALES)}