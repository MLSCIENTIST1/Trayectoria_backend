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

# --- IMPORTACIÓN DE MODELOS (VITAL PARA SQLALCHEMY) ---
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
from src.models.colombia_data.negocio import Negocio 
# ✅ IMPORTACIÓN CRÍTICA: Sin esto Neon nunca verá la tabla 'sucursales'
from src.models.colombia_data.sucursales import Sucursal 

logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_predeterminada')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Compatibilidad Neon/Render
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    # Configuración de Cookies para Dominios Diferentes (Firebase + Render)
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'None'
    REMEMBER_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = 86400 

def create_app():
    logger.info("🚀 Iniciando la Factoría de la Aplicación")
    app = Flask(__name__)
    app.config.from_object(Config)

    # 1. Configuración de CORS
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
        return jsonify({
            "error": "unauthorized", 
            "message": "La sesión ha expirado o no has iniciado sesión."
        }), 401

    @login_manager.user_loader
    def load_user(id_usuario):
        return db.session.get(Usuario, int(id_usuario))

    # 4. Creación de Estructura en Neon y Registro de Rutas
    with app.app_context():
        try:
            # Esto sincroniza los modelos importados arriba con la BD Neon
            db.create_all()
            logger.info("🛠️ Estructura de base de datos verificada en Neon")
        except Exception as e:
            logger.error(f"🔥 Error al crear tablas: {e}")

        register_api(app) 

        # Poblado automático de ciudades
        try:
            inspector = db.inspect(db.engine)
            if 'colombia' in inspector.get_table_names():
                if Colombia.query.first() is None:
                    logger.info("⚠️ Tabla 'colombia' vacía. Poblando...")
                    poblar_ciudades()
        except Exception as e:
            logger.error(f"❌ Error en auto-poblado: {e}")

    # 5. Directorio de Cargas
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder

    return app