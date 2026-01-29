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

# ==========================================
# MODELOS DE NEGOCIO
# ==========================================
from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.sucursales import Sucursal
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo

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

# ==========================================
# BIZSCORE - PERFIL PÚBLICO Y VIDEOS
# ==========================================
from src.models.colombia_data.negocio_perfil_config import NegocioPerfilConfig
from src.models.colombia_data.negocio_video import NegocioVideo

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
    "Administrador"
]