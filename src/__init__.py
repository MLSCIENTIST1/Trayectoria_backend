from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api

# Importaciones internas
from src.models.database import db, init_app
from src.api import api_bp  # Blueprint principal

# Importación de modelos para que Migrate los reconozca
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

import os
import sys
import logging

# Variable global para migraciones
migrate = None

# Configuración de logging para ver todo en los logs de Render
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Config:
    # Render usa variables de entorno, si no existe usa la local
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_predeterminada')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def create_app():
    logger.info("🚀 Iniciando la Factoría de la Aplicación")
    
    app = Flask(__name__)
    
    # 1. Configuración de CORS (Permite que tu frontend se conecte)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 2. Configuración de Entorno
    flask_env = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(Config)
    
    if flask_env == 'production':
        app.config['DEBUG'] = False
        app.config['ENV'] = 'production'
    else:
        app.config['DEBUG'] = True
        app.config['ENV'] = 'development'

    # 3. Inicialización de Base de Datos
    try:
        init_app(app)
        global migrate
        migrate = Migrate(app, db)
        logger.info("✅ Base de datos y Migrate conectados")
    except Exception as e:
        logger.error(f"❌ Error en base de datos: {e}")
        # En producción es mejor que la app falle si no hay BD
        raise e

    # 4. Configuración de LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(id_usuario):
        return Usuario.query.get(int(id_usuario))

    # 5. Registro de Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    # 6. Configuración de carpetas de archivos (Uploads)
    # Esto asegura que la carpeta exista en el servidor de Render
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Imprimir rutas en consola para validación técnica
    logger.info("📌 Rutas registradas:")
    for rule in app.url_map.iter_rules():
        logger.debug(f"Endpoint: {rule.endpoint} -> {rule.rule}")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)