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
# MODELOS DE MONETIZACIÓN
# ==========================================
from src.models.colombia_data.monetization_management import MonetizationManagement

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
    
    # Monetización
    "MonetizationManagement"
]