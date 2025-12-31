import logging
import os
from src import create_app
from flask_cors import CORS 
from flask_migrate import Migrate

# --- Configuración del Logger ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Manejador para consola (importante para ver en Render)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Manejador para archivo
file_handler = logging.FileHandler('app_startup.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.info("🚀 Inicializando la aplicación desde run.py")

try:
    # 1. Crear la aplicación usando tu fábrica
    app = create_app()  
    
    # 2. Configurar CORS (Vital para que Firebase pueda hablar con Render)
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
    
    logger.info("✅ Aplicación creada y CORS configurado.")

    # 3. INSPECTOR DE RUTAS (Esto imprimirá las rutas en los logs de Render)
    with app.app_context():
        print("\n" + "="*50)
        print("🔍 MAPA DE RUTAS REGISTRADAS EN EL SERVIDOR:")
        for rule in app.url_map.iter_rules():
            # Filtrar las rutas estáticas para leer mejor
            if "static" not in rule.endpoint:
                print(f"   MÉTODO: {list(rule.methods)} | RUTA: {rule.rule} --> ENDPOINT: {rule.endpoint}")
        print("="*50 + "\n")

except Exception as e:
    logger.error(f"❌ Error crítico al inicializar la aplicación: {e}", exc_info=True)
    app = None

if app:
    @app.route('/')
    def home():
        logger.debug("Ruta de inicio accesada")
        return "¡Hola, Flask está funcionando, CORS activo y Rutas mapeadas!"

    if __name__ == "__main__":
        # Render asigna automáticamente un puerto dinámico
        port = int(os.environ.get("PORT", 5000))
        logger.info(f"🛰️ Servidor listo en puerto: {port}")
        app.run(host='0.0.0.0', port=port, debug=True)
else:
    logger.warning("⚠️ La aplicación no se pudo iniciar.")