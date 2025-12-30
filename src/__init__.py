from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from src.models.database import db, init_app
from src.api import api_bp  # Importa el Blueprint principal de las APIs

from flask_cors import CORS
from flask_restful import Api


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

# Inicializar la variable global de Flask-Migrate
migrate = None

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app_startup.log')
    ]
)

logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_predeterminada')

def create_app():
    logger.info("Inicializando la aplicación Flask")
    flask_env = os.environ.get('FLASK_ENV', 'development')
    logger.info(f"El valor de FLASK_ENV es: {flask_env}")

    app = Flask(__name__)
    app.config.from_object(Config)
    logger.info("Flask app creada y configuración cargada")

    app.config['SECRET_KEY'] = Config.SECRET_KEY
    logger.info("Clave secreta configurada")

    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True

    try:
        logger.info("Intentando inicializar la base de datos...")
        init_app(app)
        global migrate
        migrate = Migrate(app, db)
        logger.info("Base de datos y migración inicializadas correctamente")
    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {e}", exc_info=True)
        raise

    logger.info("Inicializando LoginManager...")
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    logger.info("Login Manager inicializado")

    @login_manager.user_loader
    def load_user(id_usuario):
        logger.debug(f"Intentando cargar el usuario con ID: {id_usuario}")
        return Usuario.query.get(int(id_usuario))

    logger.info("Registrando Blueprint principal de APIs...")
    app.register_blueprint(api_bp, url_prefix='/api')  # Registra el Blueprint principal de APIs

    logger.info("Blueprints registrados correctamente")
    print(app.url_map)

    # Mostrar las rutas registradas
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint}, Ruta: {rule.rule}")

    # Inicializar CORS
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    logger.info("CORS inicializado correctamente")

    # Inicializar Flask-RESTful y registrar recursos
    api = Api(app)
    
    logger.info("API RESTful inicializada y recurso registrado")

    app.config['UPLOAD_FOLDER'] = 'static/uploads/'

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
