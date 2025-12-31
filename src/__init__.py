from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
import os
import sys
import logging

# Importaciones internas
from src.models.database import db, init_app
# 1. IMPORTANTE: Importamos tanto el blueprint como la función de registro
from src.api import api_bp, register_api 

# Importación de modelos
from src.models.usuarios import Usuario
# ... (el resto de tus modelos se mantienen igual)

logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_predeterminada')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Agrega la URI de tu base de datos aquí si no está en init_app
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 

def create_app():
    logger.info("🚀 Iniciando la Factoría de la Aplicación")
    app = Flask(__name__)
    
    # 2. CORS GLOBAL (Permite peticiones desde tus dominios de Firebase)
    CORS(app, resources={r"/*": {"origins": [
        "https://trayectoria-rxdc1.web.app",
        "https://mitrayectoria.web.app",
        "http://localhost:5001"
    ]}})
    
    app.config.from_object(Config)

    # 3. Inicialización de Base de Datos
    try:
        init_app(app)
        Migrate(app, db)
        logger.info("✅ Base de datos y Migrate conectados")
    except Exception as e:
        logger.error(f"❌ Error en base de datos: {e}")
        raise e

    # 4. Configuración de LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'api.init_sesion_bp.login' # Ajustado al nombre del blueprint

    @login_manager.user_loader
    def load_user(id_usuario):
        return Usuario.query.get(int(id_usuario))

    # 5. REGISTRO DE RUTAS (EL CAMBIO CLAVE)
    # Primero: Ejecutamos la función que llena el api_bp con todas las sub-rutas
    with app.app_context():
        register_api(app) 
        logger.info("🔗 Rutas internas vinculadas al Blueprint principal")

    # Segundo: El blueprint ya se registró dentro de la función register_api(app) 
    # que me pasaste antes, así que NO hace falta repetirlo aquí si register_api ya hace:
    # app.register_blueprint(api_bp, url_prefix='/api')

    # 6. Carpetas de carga
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder

    return app