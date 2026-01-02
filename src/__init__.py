from flask import Flask, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
import os
import sys
import logging

# Importaciones internas
from src.models.database import db, init_app
from src.api import api_bp, register_api 
from llenar_colombia import poblar_ciudades 

# Importación de modelos para asegurar el registro en SQLAlchemy
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
from src.models.colombia_data.negocio import Negocio # Asegúrate de importar Negocio

logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_predeterminada')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    # ✅ CONFIGURACIÓN PARA SESIONES CROSS-DOMAIN (Firebase + Render)
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SAMESITE = 'None'
    REMEMBER_COOKIE_SECURE = True

def create_app():
    logger.info("🚀 Iniciando la Factoría de la Aplicación")
    app = Flask(__name__)
    app.config.from_object(Config)

    # 1. Configuración de CORS REFORZADA
    CORS(app, resources={r"/api/*": {
        "origins": [
            "https://trayectoria-rxdc1.web.app",
            "https://mitrayectoria.web.app",
            "http://localhost:5001",
            "http://localhost:5173"
        ],
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True
    }})
    
    # 2. Inicialización de Base de Datos y Migraciones
    init_app(app)
    Migrate(app, db)

    # 3. Configuración de LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'api.init_sesion_bp.ingreso'

    @login_manager.unauthorized_handler
    def unauthorized():
        logger.warning("🚫 Acceso no autorizado: Enviando 401 en lugar de redirección")
        return jsonify({"error": "unauthorized", "message": "Sesión requerida"}), 401

    @login_manager.user_loader
    def load_user(id_usuario):
        return db.session.get(Usuario, int(id_usuario))

    # 4. Registro de Rutas y Creación de Tablas
    with app.app_context():
        # ✅ PASO CRÍTICO: Crea las tablas si no existen (soluciona UndefinedTable)
        db.create_all()
        logger.info("🛠️ Estructura de base de datos verificada/creada")

        register_api(app) 
        logger.info("🔗 Rutas registradas exitosamente")

        # --- LÓGICA DE AUTO-POBLADO ---
        try:
            inspector = db.inspect(db.engine)
            if 'colombia' in inspector.get_table_names():
                if Colombia.query.first() is None:
                    logger.info("⚠️ Tabla de ciudades vacía. Poblando datos...")
                    poblar_ciudades()
                else:
                    logger.debug("ℹ️ La tabla de ciudades ya tiene datos.")
        except Exception as e:
            logger.error(f"❌ Error al verificar/poblar tabla Colombia: {e}")

    # 5. Configuración de carpetas de archivos
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder

    return app