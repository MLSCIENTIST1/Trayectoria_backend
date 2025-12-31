import logging
import os
from src import create_app
from flask_cors import CORS  # <--- 1. Importar CORS
from flask_migrate import Migrate

# Configurar el logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configuración de manejadores de log
file_handler = logging.FileHandler('app_startup.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Iniciar la aplicación
logger.info("Inicializando la aplicación desde run.py")

try:
    app = create_app()  # Crear la aplicación
    
    # --- 2. CONFIGURACIÓN DE CORS ---
    # Esto permite que Firebase (tu frontend) entre al servidor
    CORS(app, resources={
        r"/*": {
            "origins": [
                "https://trayectoria-rxdc1.web.app",
                "https://mitrayectoria.web.app"
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    logger.info("Aplicación creada y CORS configurado exitosamente")
except Exception as e:
    logger.error(f"Error crítico al inicializar la aplicación: {e}", exc_info=True)
    app = None

if app:
    @app.route('/')
    def home():
        logger.debug("Ruta de inicio accesada")
        return "¡Hola, Flask está funcionando y CORS está activo!"

    if __name__ == "__main__":
        # Render usa la variable PORT, si no existe usa 5000 o 5001
        port = int(os.environ.get("PORT", 5000))
        logger.info(f"Ejecutando la aplicación en el puerto: {port}")
        app.run(host='0.0.0.0', port=port, debug=True)
else:
    logger.warning("La aplicación no se pudo iniciar debido a un error.")