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
from src.models.colombia_data.negocio import Negocio 

logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_predeterminada')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Manejo de la URL de base de datos para compatibilidad con Render/Postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    # ✅ CONFIGURACIÓN PARA SESIONES CROSS-DOMAIN (Firebase + Render)
    # Sin esto, el navegador bloquea la cookie de sesión por ser dominios distintos
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'None'
    REMEMBER_COOKIE_SECURE = True
    # Tiempo de vida de la sesión (ej. 1 día)
    PERMANENT_SESSION_LIFETIME = 86400 

def create_app():
    logger.info("🚀 Iniciando la Factoría de la Aplicación")
    app = Flask(__name__)
    app.config.from_object(Config)

    # 1. Configuración de CORS REFORZADA
    # Permitimos explícitamente el origen de tu frontend en Firebase
    CORS(app, resources={r"/api/*": {
        "origins": [
            "https://trayectoria-rxdc1.web.app",
            "https://mitrayectoria.web.app",
            "http://localhost:5001",
            "http://localhost:5173"
        ],
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True  # Permite el envío de cookies
    }})
    
    # 2. Inicialización de Base de Datos y Migraciones
    init_app(app)
    Migrate(app, db)

    # 3. Configuración de LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    # Apuntamos a la ruta de login definida en tu blueprint de auth
    login_manager.login_view = 'api.init_sesion_bp.ingreso'

    # Evita redirecciones 302 que rompen el frontend (AJAX/Fetch)
    @login_manager.unauthorized_handler
    def unauthorized():
        logger.warning("🚫 Acceso no autorizado: Enviando 401 en lugar de redirección")
        return jsonify({
            "error": "unauthorized", 
            "message": "La sesión ha expirado o no has iniciado sesión."
        }), 401

    @login_manager.user_loader
    def load_user(id_usuario):
        # Usamos session.get para compatibilidad con SQLAlchemy 2.0
        return db.session.get(Usuario, int(id_usuario))

    # 4. Registro de Rutas y Estructura de Datos
    with app.app_context():
        # ✅ CREACIÓN DE TABLAS: Soluciona el error 'UndefinedTable'
        try:
            db.create_all()
            logger.info("🛠️ Estructura de base de datos verificada/creada con éxito")
        except Exception as e:
            logger.error(f"🔥 Error al crear tablas: {e}")

        # Registro de Blueprints
        register_api(app) 
        logger.info("🔗 Rutas API registradas")

        # --- LÓGICA DE AUTO-POBLADO DE CIUDADES ---
        try:
            inspector = db.inspect(db.engine)
            if 'colombia' in inspector.get_table_names():
                if Colombia.query.first() is None:
                    logger.info("⚠️ Tabla 'colombia' vacía. Iniciando poblado...")
                    poblar_ciudades()
                else:
                    logger.debug("ℹ️ Datos de ciudades ya presentes.")
        except Exception as e:
            logger.error(f"❌ Error en auto-poblado: {e}")

    # 5. Gestión de archivos estáticos
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder

    return app