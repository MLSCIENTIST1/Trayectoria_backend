# -*- coding: utf-8 -*-
import logging
from run import create_app
from src.models.database import db

# IMPORTANTE: Importamos todos los modelos para que SQLAlchemy 'sepa' que existen
from src.models.usuarios import Usuario
from src.models.servicio import Servicio
from src.models.notification import Notification
from src.models.message import Message
from src.models.usuario_servicio import usuario_servicio
from src.models.colombia_data.colombia_data import Colombia
# Agregamos los modelos de ratings y feedbacks que vimos en tus logs
from src.models.colombia_data.colombia_feedbacks import Feedback
from src.models.colombia_data.monetization_management import MonetizationManagement

# Configurar logs para ver detalles en consola
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    print("🚀 [INICIO]: Iniciando proceso de saneamiento de base de datos...")
    app = create_app()
    
    with app.app_context():
        # 1. Mostrar qué tablas reconoce el código
        tablas_detectadas = list(db.metadata.tables.keys())
        print(f"📦 [MODELOS]: Tablas detectadas para crear: {tablas_detectadas}")
        
        # 2. Verificar conexión
        uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        print(f"📡 [DEBUG]: Conectando a: {uri.split('@')[-1]}") # Muestra solo el host por seguridad

        # 3. LIMPIEZA FORZADA (Esto soluciona el error UndefinedFile)
        print("🧹 [LOG]: Borrando tablas existentes (Limpiando archivos corruptos)...")
        db.drop_all()
        
        # 4. CREACIÓN DESDE CERO
        print("⏳ [LOG]: Creando todas las tablas con estructura limpia...")
        db.create_all()
        
        print("✅ [EXITO]: ¡Base de datos saneada y tablas creadas correctamente en Neon!")

except Exception as e:
    print(f"❌ [ERROR CRÍTICO]: {e}")