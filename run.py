import logging
from src import create_app
from flask_migrate import Migrate
# Configurar el logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Crear un manejador para que los logs se guarden en un archivo
file_handler = logging.FileHandler('app_startup.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Iniciar la aplicación
logger.info("Inicializando la aplicación desde run.py")

try:
    app = create_app()  # Crear la aplicación
    logger.info("Aplicación creada exitosamente")
except Exception as e:
    logger.error(f"Error crítico al inicializar la aplicación: {e}", exc_info=True)
    app = None

if app:
    @app.route('/')
    def home():
        logger.debug("Ruta de inicio accesada")
        return "¡Hola, Flask está funcionando!"

    if __name__ == "__main__":
        logger.info("Ejecutando la aplicación en modo depuración")
        app.run(debug=True)  # Esto garantiza que Flask se ejecute en modo debug
else:
    logger.warning("La aplicación no se pudo iniciar debido a un error.")