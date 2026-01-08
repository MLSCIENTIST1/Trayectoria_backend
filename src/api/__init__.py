import traceback
from flask import Blueprint, jsonify, request
from flask_cors import CORS

# Blueprint principal de la API
api_bp = Blueprint('api', __name__)

def register_api(app):
    """
    Registra de forma segura todos los Blueprints en la aplicación Flask.
    Asegura que el Centro de Control Operativo incluya las rutas de Reportes.
    """
    # Aplica CORS a toda la aplicación, permitiendo credenciales para el frontend en Web.app
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

    print("\n🚀 Iniciando registro de rutas API...")

    # Ruta de salud global para monitoreo de Render
    @app.route('/api/health', methods=['GET'])
    def global_health():
        return jsonify({
            "status": "online", 
            "message": "BizFlow Studio API Core is running",
            "version": "1.1.0"
        }), 200

    def safe_import_and_register(module_path, bp_name, display_name, prefix='/api'):
        try:
            # Importación dinámica del módulo
            module = __import__(module_path, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            
            # Registro en la app de Flask
            app.register_blueprint(blueprint, url_prefix=prefix)
            print(f"✅ [OK] Módulo cargado: {display_name.ljust(20)} -> {prefix if prefix else '/'}")
            return True
        except Exception as e:
            print(f"❌ [FALLO] No se pudo cargar {display_name}. Error: {e}")
            # Descomentar para debug profundo en consola de Render
            # traceback.print_exc() 
            return False

    # --- Módulos de Negocio y Catálogo ---
    print("\n--- Cargando Módulos de Negocio y Catálogo ---")
    safe_import_and_register('src.api.negocio.negocio_api', 'negocio_api_bp', 'Negocio')
    safe_import_and_register('src.api.negocio.catalogo_api', 'catalogo_api_bp', 'Catálogo')
    
    # --- Centro de Control Operativo (Contabilidad e Inventario) ---
    # IMPORTANTE: Aquí reside la ruta /control/reporte/<id> que fallaba
    print("\n--- Cargando Centro de Control Operativo ---")
    safe_import_and_register('src.api.contabilidad.control_api', 'control_api_bp', 'Control Operativo')
    safe_import_and_register('src.api.contabilidad.carga_masiva_api', 'carga_masiva_bp', 'Carga Masiva')
    safe_import_and_register('src.api.contabilidad.alertas_api', 'alertas_api_bp', 'Alertas Operativas')

    # Registro del Micrositio Público (URL limpia para clientes)
    safe_import_and_register('src.api.negocio.pagina_api', 'pagina_api_bp', 'Micrositios Públicos', prefix=None)

    # --- Módulos de Autenticación ---
    print("\n--- Cargando Autenticación ---")
    auth_modules = {
        'src.api.auth.auth_api': 'auth_api_bp',
        'src.api.auth.close_sesion_api': 'close_sesion_bp',
        'src.api.auth.init_sesion_api': 'init_sesion_bp',
        'src.api.auth.password_api': 'password_bp',
    }
    for path, bp in auth_modules.items():
        safe_import_and_register(path, bp, path.split('.')[-1])

    # --- Módulos de Perfil y Servicios ---
    print("\n--- Cargando Módulos de Usuario y Servicios ---")
    other_modules = {
        'src.api.calificaciones.calificar_api': 'calificar_bp',
        'src.api.candidates.details_candidate_api': 'details_candidate_bp',
        'src.api.contracts.create_contract_api': 'create_contract_bp',
        'src.api.contracts.contract_vigent_api': 'contract_vigent_bp',
        'src.api.notifications.notifications_api': 'notifications_bp',
        'src.api.notifications.chat_api': 'chat_bp',
        'src.api.profile.view_logged_user_api': 'view_logged_user_bp',
        'src.api.profile.edit_profile_api': 'edit_profile_bp',
        'src.api.services.publish_service_api': 'publish_service_bp',
        'src.api.services.search_service_autocomplete_api': 'search_service_autocomplete_bp',
        'src.api.services.view_service_page_bp': 'view_service_page_bp',
        'src.api.utils.register_user_api': 'register_user_bp'
    }
    for path, bp in other_modules.items():
        safe_import_and_register(path, bp, path.split('.')[-1])

    # Imprimir resumen de rutas para verificar en los logs de Render
    print("\n✨ Registro de API completado.")
    print("="*60 + "\n")