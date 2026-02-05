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
Modelo NegocioPerfilConfig - Configuración del Perfil Público
TuKomercio Suite - BizScore

Permite al negocio personalizar:
- Layout visual (drag & drop de secciones)
- Etapas de calificación habilitadas
- Tema y colores
- Visibilidad de métricas
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Modelo NegocioPerfilConfig cargado correctamente.")


class NegocioPerfilConfig(db.Model):
    __tablename__ = "negocio_perfil_config"

    # ═══════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ═══════════════════════════════════════════════════════════
    id = Column(Integer, primary_key=True)
    negocio_id = Column(Integer, ForeignKey('negocios.id_negocio', ondelete='CASCADE'), unique=True, nullable=False)

    # ═══════════════════════════════════════════════════════════
    # LAYOUT PERSONALIZADO (Drag & Drop)
    # ═══════════════════════════════════════════════════════════
    layout_config = Column(JSON, default=lambda: {
        "sections": [
            {"id": "header", "nombre": "Encabezado", "order": 1, "visible": True, "locked": True},
            {"id": "stats", "nombre": "Estadísticas", "order": 2, "visible": True, "locked": False},
            {"id": "stages", "nombre": "Etapas de Calificación", "order": 3, "visible": True, "locked": False},
            {"id": "videos", "nombre": "Video Portfolio", "order": 4, "visible": True, "locked": False},
            {"id": "reviews", "nombre": "Reseñas", "order": 5, "visible": True, "locked": False},
            {"id": "products", "nombre": "Productos Destacados", "order": 6, "visible": False, "locked": False},
            {"id": "contact", "nombre": "Contacto", "order": 7, "visible": True, "locked": False}
        ]
    })

    # ═══════════════════════════════════════════════════════════
    # ETAPAS DE CALIFICACIÓN HABILITADAS
    # ═══════════════════════════════════════════════════════════
    etapas_habilitadas = Column(JSON, default=lambda: {
        "contratacion": True,      # Etapa 1
        "ejecucion": True,         # Etapa 2
        "finalizacion": True,      # Etapa 3
        "post_servicio": False     # Etapa 4
    })
    
    # Configuración de etapa 4
    dias_post_servicio = Column(Integer, default=7)  # Días para habilitar etapa 4
    
    # Calificación bidireccional (si el contratado puede calificar)
    contratado_puede_calificar = Column(Boolean, default=False)

    # ═══════════════════════════════════════════════════════════
    # TEMA VISUAL
    # ═══════════════════════════════════════════════════════════
    tema = Column(String(20), default="dark")  # dark, light, custom
    color_primario = Column(String(7), default="#a855f7")
    color_secundario = Column(String(7), default="#22d3ee")
    color_acento = Column(String(7), default="#10b981")
    
    # Gradiente personalizado (si tema es custom)
    gradiente_custom = Column(String(200), nullable=True)
    
    # Fondo
    fondo_tipo = Column(String(20), default="aurora")  # aurora, solid, gradient, image
    fondo_valor = Column(String(500), nullable=True)  # Color hex o URL de imagen

    # ═══════════════════════════════════════════════════════════
    # VISIBILIDAD DE MÉTRICAS
    # ═══════════════════════════════════════════════════════════
    mostrar_score_global = Column(Boolean, default=True)
    mostrar_score_contratante = Column(Boolean, default=True)
    mostrar_score_contratado = Column(Boolean, default=True)
    mostrar_total_contratos = Column(Boolean, default=True)
    mostrar_tiempo_respuesta = Column(Boolean, default=True)
    mostrar_tasa_exito = Column(Boolean, default=True)
    mostrar_clientes_recurrentes = Column(Boolean, default=True)
    mostrar_disputas = Column(Boolean, default=False)  # Por defecto oculto
    mostrar_percentil = Column(Boolean, default=True)

    # ═══════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE VIDEOS
    # ═══════════════════════════════════════════════════════════
    max_videos = Column(Integer, default=10)
    max_badges_por_video = Column(Integer, default=4)
    autoplay_videos = Column(Boolean, default=False)
    mostrar_metricas_en_video = Column(Boolean, default=True)

    # ═══════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE RESEÑAS
    # ═══════════════════════════════════════════════════════════
    mostrar_reseñas = Column(Boolean, default=True)
    max_reseñas_visibles = Column(Integer, default=5)
    permitir_respuesta_reseñas = Column(Boolean, default=True)
    mostrar_reseñas_negativas = Column(Boolean, default=True)

    # ═══════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE CONTACTO
    # ═══════════════════════════════════════════════════════════
    mostrar_whatsapp = Column(Boolean, default=True)
    mostrar_email = Column(Boolean, default=True)
    mostrar_telefono = Column(Boolean, default=True)
    mostrar_ubicacion = Column(Boolean, default=True)
    mostrar_horarios = Column(Boolean, default=True)
    mostrar_redes_sociales = Column(Boolean, default=True)

    # ═══════════════════════════════════════════════════════════
    # BOTONES DE ACCIÓN
    # ═══════════════════════════════════════════════════════════
    botones_config = Column(JSON, default=lambda: {
        "ver_tienda": {"visible": True, "texto": "Ver Tienda", "icono": "bi-shop"},
        "contactar": {"visible": True, "texto": "Contactar", "icono": "bi-whatsapp"},
        "calificar": {"visible": True, "texto": "Calificar", "icono": "bi-star"},
        "compartir": {"visible": True, "texto": "Compartir", "icono": "bi-share"}
    })

    # ═══════════════════════════════════════════════════════════
    # SEO Y METADATOS
    # ═══════════════════════════════════════════════════════════
    meta_titulo = Column(String(60), nullable=True)
    meta_descripcion = Column(String(160), nullable=True)
    meta_keywords = Column(String(255), nullable=True)
    og_image = Column(String(500), nullable=True)  # Imagen para compartir en redes

    # ═══════════════════════════════════════════════════════════
    # ANALYTICS
    # ═══════════════════════════════════════════════════════════
    total_visitas = Column(Integer, default=0)
    visitas_mes_actual = Column(Integer, default=0)
    total_compartidos = Column(Integer, default=0)
    total_clicks_tienda = Column(Integer, default=0)
    total_clicks_whatsapp = Column(Integer, default=0)

    # ═══════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, onupdate=datetime.utcnow)

    # ═══════════════════════════════════════════════════════════
    # RELACIÓN
    # ═══════════════════════════════════════════════════════════
    negocio = relationship("Negocio", backref="perfil_config", uselist=False)

    # ═══════════════════════════════════════════════════════════
    # MÉTODOS HELPER
    # ═══════════════════════════════════════════════════════════
    def get_secciones_visibles(self):
        """Retorna las secciones visibles ordenadas"""
        if not self.layout_config or 'sections' not in self.layout_config:
            return []
        
        secciones = self.layout_config['sections']
        visibles = [s for s in secciones if s.get('visible', True)]
        return sorted(visibles, key=lambda x: x.get('order', 0))

    def reordenar_secciones(self, nuevo_orden: list):
        """
        Reordena las secciones según una lista de IDs
        nuevo_orden: ['header', 'videos', 'stats', ...]
        """
        if not self.layout_config or 'sections' not in self.layout_config:
            return False
        
        secciones = {s['id']: s for s in self.layout_config['sections']}
        
        for idx, seccion_id in enumerate(nuevo_orden, 1):
            if seccion_id in secciones and not secciones[seccion_id].get('locked', False):
                secciones[seccion_id]['order'] = idx
        
        self.layout_config['sections'] = list(secciones.values())
        return True

    def toggle_seccion(self, seccion_id: str, visible: bool):
        """Muestra/oculta una sección"""
        if not self.layout_config or 'sections' not in self.layout_config:
            return False
        
        for seccion in self.layout_config['sections']:
            if seccion['id'] == seccion_id and not seccion.get('locked', False):
                seccion['visible'] = visible
                return True
        return False

    def incrementar_visita(self):
        """Incrementa el contador de visitas"""
        self.total_visitas = (self.total_visitas or 0) + 1
        self.visitas_mes_actual = (self.visitas_mes_actual or 0) + 1

    def serialize(self):
        return {
            "id": self.id,
            "negocio_id": self.negocio_id,
            "layout": self.layout_config,
            "etapas_habilitadas": self.etapas_habilitadas,
            "dias_post_servicio": self.dias_post_servicio,
            "contratado_puede_calificar": self.contratado_puede_calificar,
            "tema": {
                "nombre": self.tema,
                "color_primario": self.color_primario,
                "color_secundario": self.color_secundario,
                "color_acento": self.color_acento,
                "fondo": {
                    "tipo": self.fondo_tipo,
                    "valor": self.fondo_valor
                }
            },
            "visibilidad": {
                "score_global": self.mostrar_score_global,
                "total_contratos": self.mostrar_total_contratos,
                "tiempo_respuesta": self.mostrar_tiempo_respuesta,
                "tasa_exito": self.mostrar_tasa_exito,
                "percentil": self.mostrar_percentil
            },
            "botones": self.botones_config,
            "analytics": {
                "total_visitas": self.total_visitas,
                "visitas_mes": self.visitas_mes_actual,
                "compartidos": self.total_compartidos
            }
        }

    def serialize_publico(self):
        """Serialización para vista pública (sin analytics sensibles)"""
        return {
            "layout": self.get_secciones_visibles(),
            "tema": {
                "nombre": self.tema,
                "color_primario": self.color_primario,
                "color_secundario": self.color_secundario,
                "color_acento": self.color_acento
            },
            "botones": self.botones_config,
            "mostrar_reseñas": self.mostrar_reseñas,
            "max_reseñas_visibles": self.max_reseñas_visibles
        }


# Importación diferida
from src.models.colombia_data.negocio import Negocio