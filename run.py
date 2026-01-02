import logging
import os
import sys
from src import create_app

# --- Configuración del Logger ---
# En Render, sys.stdout es vital para ver los logs en tiempo real
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app_startup.log')
    ]
)
logger = logging.getLogger(__name__)

logger.info("🚀 Inicializando lanzador run.py")

try:
    # 1. Crear la aplicación usando tu fábrica (CORS ya se configura dentro de create_app)
    app = create_app()  
    
    if app:
        logger.info("✅ Aplicación creada exitosamente desde la factoría.")
        
        # 2. INSPECTOR DE RUTAS 
        # Útil para confirmar que /api/ciudades existe realmente al arrancar
        with app.app_context():
            print("\n" + "="*70)
            print("🔍 MAPA DE RUTAS REGISTRADAS (Inspección de Arranque):")
            for rule in app.url_map.iter_rules():
                if "static" not in rule.endpoint:
                    # Buscamos nuestra ruta objetivo para resaltarla en el log
                    marker = " ⭐ [OBJETIVO]" if "/ciudades" in str(rule) else ""
                    print(f"   {list(rule.methods)} {str(rule).ljust(40)} --> {rule.endpoint}{marker}")
            print("="*70 + "\n")
    else:
        logger.error("❌ La factoría create_app() devolvió None.")

except Exception as e:
    logger.error(f"❌ Error crítico al inicializar la aplicación: {e}", exc_info=True)
    app = None

# 3. Definición de rutas base de salud del servidor
if app:
    @app.route('/health')
    @app.route('/')
    def home():
        logger.debug("Ping a ruta de salud del servidor")
        return {
            "status": "online",
            "message": "Servidor Flask activo",
            "cors": "configurado"
        }, 200

# 4. Punto de entrada para Gunicorn (Render) y ejecución local
if __name__ == "__main__":
    if app:
        # Render asigna el puerto mediante la variable de entorno PORT
        port = int(os.environ.get("PORT", 5000))
        logger.info(f"🛰️ Servidor listo y escuchando en puerto: {port}")
        
        # debug=True en local ayuda a ver errores, Render lo ignora si usas gunicorn
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        print("Fallo crítico: No se pudo levantar la aplicación.")
        sys.exit(1)