"""
BizFlow Studio - Lanzador Principal
Optimizado para Render con diagnóstico de rutas
"""

import logging
import os
import sys
from src import create_app

# ==========================================
# CONFIGURACIÓN DE LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,  # Cambié a INFO para reducir ruido en producción
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# INICIALIZACIÓN
# ==========================================
logger.info("="*70)
logger.info("🚀 INICIANDO BIZFLOW STUDIO")
logger.info("="*70)

app = None

try:
    # Crear la aplicación
    app = create_app()
    
    if app:
        logger.info("✅ Aplicación creada exitosamente")
        
        # ==========================================
        # INSPECTOR DE RUTAS
        # ==========================================
        with app.app_context():
            logger.info("\n" + "="*70)
            logger.info("🔍 MAPA DE RUTAS REGISTRADAS:")
            logger.info("="*70)
            
            routes_by_prefix = {}
            
            # Agrupar rutas por prefijo para mejor visualización
            for rule in app.url_map.iter_rules():
                if "static" not in rule.endpoint:
                    prefix = str(rule).split('/')[1] if len(str(rule).split('/')) > 1 else 'root'
                    
                    if prefix not in routes_by_prefix:
                        routes_by_prefix[prefix] = []
                    
                    routes_by_prefix[prefix].append({
                        'path': str(rule),
                        'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'})),
                        'endpoint': rule.endpoint
                    })
            
            # Imprimir rutas agrupadas
            for prefix, routes in sorted(routes_by_prefix.items()):
                logger.info(f"\n📁 /{prefix}/")
                for route in sorted(routes, key=lambda x: x['path']):
                    methods_str = ','.join(route['methods'])
                    logger.info(f"   [{methods_str:20}] {route['path']:50} → {route['endpoint']}")
            
            logger.info("="*70 + "\n")
            
            # Contar rutas por tipo
            total_routes = sum(len(routes) for routes in routes_by_prefix.values())
            logger.info(f"📊 Total de rutas registradas: {total_routes}")
            
            # Verificar rutas críticas
            critical_routes = [
                '/api/auth/login',
                '/api/auth/logout',
                '/api/auth/session/verify',
                '/health'
            ]
            
            all_paths = [route['path'] for routes in routes_by_prefix.values() for route in routes]
            missing_routes = [route for route in critical_routes if route not in all_paths]
            
            if missing_routes:
                logger.warning(f"⚠️  Rutas críticas faltantes: {missing_routes}")
            else:
                logger.info("✅ Todas las rutas críticas están registradas")
    
    else:
        logger.error("❌ La factoría create_app() devolvió None")
        sys.exit(1)

except Exception as e:
    logger.error(f"❌ Error crítico al inicializar la aplicación:", exc_info=True)
    sys.exit(1)

# ==========================================
# RUTAS BASE (Ya no necesarias si están en __init__.py)
# ==========================================
# Las rutas /health ya están en __init__.py, no duplicar

# ==========================================
# PUNTO DE ENTRADA
# ==========================================
if __name__ == "__main__":
    if app:
        # Render asigna el puerto mediante PORT
        port = int(os.environ.get("PORT", 5000))
        debug = os.environ.get("FLASK_ENV") != "production"
        
        logger.info("="*70)
        logger.info(f"🌐 Servidor iniciando en puerto: {port}")
        logger.info(f"🔧 Modo debug: {'ACTIVADO' if debug else 'DESACTIVADO'}")
        logger.info(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'development')}")
        logger.info("="*70 + "\n")
        
        # IMPORTANTE: En producción con Render, usa gunicorn, no esto
        # Este run() solo se usa en desarrollo local
        if debug:
            logger.info("⚠️  Ejecutando en modo desarrollo (Flask built-in server)")
            app.run(host='0.0.0.0', port=port, debug=True)
        else:
            logger.info("✅ Aplicación lista para Gunicorn")
            # Gunicorn tomará el control aquí
    else:
        logger.error("❌ No se pudo levantar la aplicación")
        sys.exit(1)