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
BizFlow Studio - Inicialización de Modelos
Organiza todos los modelos de la aplicación
"""
# ==========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ==========================================
from src.models.database import db, init_app, DATABASE_URL

# ==========================================
# MODELOS CORE
# ==========================================
from .usuarios import Usuario
from .servicio import Servicio
from .notification import Notification
from .message import Message
from .etapa import Etapa
from .foto import Foto
from .audio import Audio
from .video import Video

# ==========================================
# MODELOS DE COLOMBIA Y LOCALIZACIÓN
# ==========================================
from src.models.colombia_data.colombia_data import Colombia
from src.models.colombia_data.colombia_feedbacks import Feedback
from src.models.colombia_data.config_plataforma import ConfigGlobal  # A38: config global
from src.models.colombia_data.plataforma_kb import PlataformaKB  # base de conocimiento (Centro de Ayuda)

# ==========================================
# MODELOS DE NEGOCIO
# ==========================================
from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.sucursales import Sucursal
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo, ProductoReview
# CarritoAbandonado se importa directamente en carritos_api.py — no se registra
# en db.create_all() para evitar problemas de startup. La tabla se crea vía SQL
# en las migraciones de src/__init__.py.
from src.models.colombia_data.contabilidad.cupones import Cupon
from src.models.colombia_data.contabilidad.wompi_config import WompiConfig
from src.models.colombia_data.contabilidad.tienda_visita import TiendaVisita
from src.models.colombia_data.equipo import EmpleadoNegocio, LinkInvitacion

# ==========================================
# MODELOS DE CALIFICACIONES Y RATINGS
# ==========================================
from src.models.colombia_data.ratings.service_ratings import ServiceRatings
from src.models.colombia_data.ratings.service_overall_scores import ServiceOverallScores
from src.models.colombia_data.ratings.service_qualifiers import ServiceQualifiers

# ==========================================
# BIZSCORE - BADGES Y GAMIFICACIÓN
# ==========================================
from src.models.colombia_data.ratings.negocio_badge import NegocioBadge, BADGES_INICIALES
from src.models.colombia_data.ratings.negocio_badge_obtenido import NegocioBadgeObtenido, BadgeVerificationService
from src.models.colombia_data.ratings.usuario_gamificacion import UsuarioGamificacion
from src.models.colombia_data.ratings.referido import Referido
from src.models.colombia_data.ratings.duelo import Duelo

# ==========================================
# BIZSCORE - PERFIL PÚBLICO Y VIDEOS
# ==========================================
from src.models.colombia_data.negocio_perfil_config import NegocioPerfilConfig
from src.models.colombia_data.negocio_video import NegocioVideo

# Interacciones sociales (seguir / like de comprador a negocio)
from src.models.colombia_data.negocio_interaccion import NegocioInteraccion

# ==========================================
# MODELOS DE MONETIZACIÓN
# ==========================================
from src.models.colombia_data.monetization_management import MonetizationManagement

# ==========================================
# MODELOS DE COMPRADORES (ECOSISTEMA GLOBAL)
# ==========================================
from src.models.compradores.comprador import Comprador
from src.models.compradores.direccion import DireccionComprador
from src.models.compradores.pedido import Pedido, PedidoHistorial

# ==========================================
# MODELO DE RECUPERACIÓN DE CONTRASEÑA
# ==========================================
from .password_reset_token import PasswordResetToken

# ==========================================
# MODELOS DE ADMINISTRACIÓN
# ==========================================
from .administrador import Administrador
from .admin_audit import AdminAuditLog

from src.models.feature_models import FeatureFlag, Plan, PlanFeature, NegocioPlan

# ==========================================
# MODELOS DE mecalink
# ==========================================
from .mecalink_model import MecanicoMecalink

# ==========================================
# EXPORTACIÓN
# ==========================================
__all__ = [
    # Base de datos
    "db",
    "init_app",
    "DATABASE_URL",
    
    # Modelos Core
    "Usuario",
    "Servicio",
    "Notification",
    "Message",
    "Etapa",
    "Foto",
    "Audio",
    "Video",
    
    # Colombia
    "Colombia",
    "Feedback",
    
    # Negocio
    "Negocio",
    "Sucursal",
    "ProductoCatalogo",
    
    # Ratings
    "ServiceRatings",
    "ServiceOverallScores",
    "ServiceQualifiers",
    
    # BizScore - Badges
    "NegocioBadge",
    "BADGES_INICIALES",
    "NegocioBadgeObtenido",
    "BadgeVerificationService",
    
    # BizScore - Perfil y Videos
    "NegocioPerfilConfig",
    "NegocioVideo",

    # Interacciones sociales
    "NegocioInteraccion",
    
    # Monetización
    "MonetizationManagement",
    
    # Compradores (Ecosistema Global)
    "Comprador",
    "DireccionComprador",
    "Pedido",
    "PedidoHistorial",
    
    # Password Reset
    "PasswordResetToken",
    
    # Administración
    "Administrador",
    "AdminAuditLog",

# Feature Flags y Planes
    "FeatureFlag",
    "Plan",
    "PlanFeature",
    "NegocioPlan",


# mecalink
    "MecanicoMecalink"
]