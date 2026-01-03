# Modelos Base
from .notification import Notification
from .servicio import Servicio
from .message import Message
from .usuarios import Usuario
from .etapa import Etapa
from .foto import Foto
from .audio import Audio
from .video import Video

# Importaciones desde la subcarpeta colombia_data
from src.models.colombia_data.ratings.service_ratings import ServiceRatings
from src.models.colombia_data.ratings.service_overall_scores import ServiceOverallScores
from src.models.colombia_data.ratings.service_qualifiers import ServiceQualifiers
from src.models.colombia_data.colombia_data import Colombia
from src.models.colombia_data.colombia_feedbacks import Feedback
from src.models.colombia_data.monetization_management import MonetizationManagement
from src.models.colombia_data.sucursales import Sucursal
from src.models.colombia_data.negocio import Negocio

# --- NUEVOS: Módulos de Catálogo BizFlow ---
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo
from src.models.colombia_data.catalogo.producto import Producto

# Configuración de base de datos
from src.models.database import db, init_app, DATABASE_URL

# Exportar funciones y modelos clave para que Flask-Migrate y la App los vean
__all__ = [
    "db",
    "init_app",
    "DATABASE_URL",
    "Notification",
    "Servicio",
    "Message",
    "Usuario",
    "Etapa",
    "Foto",
    "Audio",
    "Video",
    "Colombia",
    "Negocio",
    "Sucursal",
    "ProductoCatalogo",  # Agregado para persistencia en DB
    "Producto",          # Agregado para persistencia en DB
    "ServiceRatings",
    "ServiceOverallScores",
    "ServiceQualifiers",
    "Feedback",
    "MonetizationManagement"
]