from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
import os
import sys
import logging

# Importaciones internas
from src.models.database import db, init_app
from src.api import api_bp, register_api 
from llenar_colombia import poblar_ciudades # Importamos tu script de ciudades

# Importación de modelos para que Migrate y SQLAlchemy los reconozcan
from src.models.usuarios import Usuario
from src.models.etapa import Etapa
from src.models.foto import Foto
from src.models.audio import Audio
from src.models.video import Video
from src.models.colombia_data.colombia_data import Colombia
from src.models.colombia_data.colombia_feedbacks import Feedback
from src.models.colombia_data.monetization_management import MonetizationManagement
from src.models.colombia_data.ratings.service_overall_scores import ServiceOverallScores
from src.models.colombia_data.ratings.service_qualifiers import ServiceQualifiers
from src.models.colombia_data.ratings.service_ratings import ServiceRatings

logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_predeterminada')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Render usa DATABASE_URL para PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

def create_app():
    logger.info("🚀 Iniciando la Factoría de la Aplicación")
    app = Flask(__name__)
    
    # 1. Configuración de CORS
    CORS(app, resources={r"/*": {"origins": [
        "https://trayectoria-rxdc1.web.app",
        "https://mitrayectoria.web.app",
        "http://localhost:5001"
    ]}})
    
    app.config.from_object(Config)

    # 2. Inicialización de Base de Datos y Migraciones
    try:
        init_app(app)
        Migrate(app, db)
        logger.info("✅ Base de datos y Migrate conectados")
    except Exception as e:
        logger.error(f"❌ Error en base de datos: {e}")
        raise e

    # 3. Configuración de LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'api.init_sesion_bp.login'

    @login_manager.user_loader
    def load_user(id_usuario):
        return Usuario.query.get(int(id_usuario))

    # 4. Registro de Rutas y Auto-poblado
    with app.app_context():
        # Registra todos los sub-blueprints dentro de api_bp y luego api_bp en app
        register_api(app) 
        logger.info("🔗 Rutas registradas exitosamente")

        # --- LÓGICA DE AUTO-POBLADO DE CIUDADES ---
        try:
            # Verificamos si la tabla Colombia está vacía
            if Colombia.query.first() is None:
                logger.info("⚠️ Tabla de ciudades vacía. Poblando datos...")
                poblar_ciudades()
                logger.info("✅ Ciudades cargadas correctamente.")
            else:
                logger.debug("ℹ️ La tabla de ciudades ya tiene datos.")
        except Exception as e:
            logger.error(f"❌ No se pudo verificar/poblar la tabla Colombia: {e}")

    # 5. Configuración de carpetas de archivos (Uploads)
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder

    return app