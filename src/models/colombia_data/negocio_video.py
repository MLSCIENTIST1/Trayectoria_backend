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
Modelo NegocioVideo - Video Portfolio del Negocio
TuKomercio Suite - BizScore

Almacena los videos que el negocio sube para mostrar su trabajo.
Permite asociar badges e insignias a cada video.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.database import db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Modelo NegocioVideo cargado correctamente.")


class NegocioVideo(db.Model):
    __tablename__ = "negocio_videos"

    # ═══════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ═══════════════════════════════════════════════════════════
    id = Column(Integer, primary_key=True)
    negocio_id = Column(Integer, ForeignKey('negocios.id_negocio', ondelete='CASCADE'), nullable=False)

    # ═══════════════════════════════════════════════════════════
    # INFORMACIÓN DEL VIDEO
    # ═══════════════════════════════════════════════════════════
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # URLs del video
    url_video = Column(String(500), nullable=False)          # Cloudinary/YouTube/Vimeo
    url_thumbnail = Column(String(500), nullable=True)       # Miniatura
    url_video_hd = Column(String(500), nullable=True)        # Versión HD si existe
    
    # Tipo de fuente
    fuente = Column(String(20), default="cloudinary")        # cloudinary, youtube, vimeo, local
    video_id_externo = Column(String(100), nullable=True)    # ID de YouTube/Vimeo si aplica

    # ═══════════════════════════════════════════════════════════
    # METADATOS DEL VIDEO
    # ═══════════════════════════════════════════════════════════
    duracion_segundos = Column(Integer, nullable=True)
    ancho = Column(Integer, nullable=True)                    # Resolución
    alto = Column(Integer, nullable=True)
    formato = Column(String(10), nullable=True)               # mp4, webm, etc.
    tamanio_bytes = Column(Integer, nullable=True)
    calidad = Column(String(10), default="HD")                # SD, HD, FHD, 4K

    # ═══════════════════════════════════════════════════════════
    # MÉTRICA DESTACADA (opcional)
    # ═══════════════════════════════════════════════════════════
    metrica_nombre = Column(String(100), nullable=True)       # 'Tasa de éxito'
    metrica_valor = Column(String(50), nullable=True)         # '+15%'
    metrica_tendencia = Column(String(10), nullable=True)     # 'up', 'down', 'neutral'
    metrica_icono = Column(String(50), nullable=True)         # 'bi-graph-up'
    metrica_color = Column(String(7), nullable=True)          # '#10b981'

    # ═══════════════════════════════════════════════════════════
    # ESTADÍSTICAS
    # ═══════════════════════════════════════════════════════════
    vistas = Column(Integer, default=0)
    vistas_unicas = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    compartidos = Column(Integer, default=0)
    
    # Engagement
    tiempo_visto_promedio = Column(Float, nullable=True)      # Segundos promedio
    porcentaje_completado = Column(Float, nullable=True)      # % que ve completo
    
    # Clicks desde el video
    clicks_tienda = Column(Integer, default=0)
    clicks_whatsapp = Column(Integer, default=0)
    clicks_perfil = Column(Integer, default=0)

    # ═══════════════════════════════════════════════════════════
    # CONFIGURACIÓN
    # ═══════════════════════════════════════════════════════════
    orden = Column(Integer, default=0)                        # Orden de aparición
    visible = Column(Boolean, default=True)
    destacado = Column(Boolean, default=False)                # Aparece primero
    en_feed_publico = Column(Boolean, default=True)           # Aparece en scroll infinito
    
    # Autoplay
    autoplay = Column(Boolean, default=False)
    loop = Column(Boolean, default=False)
    muted_default = Column(Boolean, default=True)

    # ═══════════════════════════════════════════════════════════
    # MODERACIÓN
    # ═══════════════════════════════════════════════════════════
    estado_moderacion = Column(String(20), default="pendiente")  # pendiente, aprobado, rechazado
    fecha_moderacion = Column(DateTime, nullable=True)
    motivo_rechazo = Column(String(255), nullable=True)
    moderado_por = Column(Integer, nullable=True)              # ID del moderador

    # ═══════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, onupdate=datetime.utcnow)
    fecha_publicacion = Column(DateTime, nullable=True)

    # ═══════════════════════════════════════════════════════════
    # RELACIONES
    # ═══════════════════════════════════════════════════════════
    negocio = relationship("Negocio", backref="videos")
    # TODO: Crear modelo NegocioVideoBadge cuando se implemente
    # badges = relationship("NegocioVideoBadge", back_populates="video", cascade="all, delete-orphan")

    # ═══════════════════════════════════════════════════════════
    # MÉTODOS HELPER
    # ═══════════════════════════════════════════════════════════
    def get_duracion_formateada(self) -> str:
        """Retorna la duración en formato mm:ss o hh:mm:ss"""
        if not self.duracion_segundos:
            return "0:00"
        
        horas = self.duracion_segundos // 3600
        minutos = (self.duracion_segundos % 3600) // 60
        segundos = self.duracion_segundos % 60
        
        if horas > 0:
            return f"{horas}:{minutos:02d}:{segundos:02d}"
        return f"{minutos}:{segundos:02d}"

    def incrementar_vista(self, es_unica: bool = False):
        """Incrementa contadores de vistas"""
        self.vistas = (self.vistas or 0) + 1
        if es_unica:
            self.vistas_unicas = (self.vistas_unicas or 0) + 1

    def incrementar_like(self):
        """Incrementa likes"""
        self.likes = (self.likes or 0) + 1

    def aprobar_moderacion(self, moderador_id: int = None):
        """Aprueba el video para publicación"""
        self.estado_moderacion = "aprobado"
        self.fecha_moderacion = datetime.utcnow()
        self.moderado_por = moderador_id
        self.fecha_publicacion = datetime.utcnow()

    def rechazar_moderacion(self, motivo: str, moderador_id: int = None):
        """Rechaza el video"""
        self.estado_moderacion = "rechazado"
        self.fecha_moderacion = datetime.utcnow()
        self.motivo_rechazo = motivo
        self.moderado_por = moderador_id

    def get_badges_asignados(self) -> list:
        """Retorna los badges asignados a este video"""
        # TODO: Implementar cuando exista NegocioVideoBadge
        return []

    def puede_agregar_badge(self, max_badges: int = 4) -> bool:
        """Verifica si se puede agregar más badges"""
        # TODO: Implementar cuando exista NegocioVideoBadge
        return True

    def serialize(self):
        return {
            "id": self.id,
            "negocio_id": self.negocio_id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "url_video": self.url_video,
            "url_thumbnail": self.url_thumbnail,
            "duracion": self.get_duracion_formateada(),
            "duracion_segundos": self.duracion_segundos,
            "calidad": self.calidad,
            "fuente": self.fuente,
            "metrica": {
                "nombre": self.metrica_nombre,
                "valor": self.metrica_valor,
                "tendencia": self.metrica_tendencia,
                "icono": self.metrica_icono,
                "color": self.metrica_color
            } if self.metrica_nombre else None,
            "estadisticas": {
                "vistas": self.vistas,
                "likes": self.likes,
                "compartidos": self.compartidos
            },
            "badges": self.get_badges_asignados(),
            "visible": self.visible,
            "destacado": self.destacado,
            "estado": self.estado_moderacion,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

    def serialize_para_feed(self):
        """Serialización compacta para el feed de scroll infinito"""
        return {
            "id": self.id,
            "negocio_id": self.negocio_id,
            "negocio_nombre": self.negocio.nombre_negocio if self.negocio else None,
            "negocio_logo": self.negocio.logo_url if self.negocio else None,
            "titulo": self.titulo,
            "url_thumbnail": self.url_thumbnail,
            "duracion": self.get_duracion_formateada(),
            "calidad": self.calidad,
            "vistas": self.vistas,
            "likes": self.likes,
            "metrica": {
                "nombre": self.metrica_nombre,
                "valor": self.metrica_valor,
                "tendencia": self.metrica_tendencia
            } if self.metrica_nombre else None,
            "badges": self.get_badges_asignados()[:3]
        }

    def serialize_para_edicion(self):
        """Serialización completa para el editor"""
        data = self.serialize()
        data.update({
            "url_video_hd": self.url_video_hd,
            "ancho": self.ancho,
            "alto": self.alto,
            "formato": self.formato,
            "tamaño_bytes": self.tamaño_bytes,
            "autoplay": self.autoplay,
            "loop": self.loop,
            "muted_default": self.muted_default,
            "en_feed_publico": self.en_feed_publico,
            "orden": self.orden,
            "estadisticas_detalle": {
                "vistas_unicas": self.vistas_unicas,
                "tiempo_visto_promedio": self.tiempo_visto_promedio,
                "porcentaje_completado": self.porcentaje_completado,
                "clicks_tienda": self.clicks_tienda,
                "clicks_whatsapp": self.clicks_whatsapp
            }
        })
        return data


# Importación diferida
from src.models.colombia_data.negocio import Negocio