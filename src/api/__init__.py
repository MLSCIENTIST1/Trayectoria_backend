import traceback
from flask import Blueprint, jsonify

# Blueprint principal de la API
api_bp = Blueprint('api', __name__)

def register_api(app):
    """
    Registra de forma segura todos los Blueprints en la aplicación Flask.
    """
    print("\n🚀 Iniciando registro de rutas API...")

    # Ruta de salud global
    @app.route('/api/health', methods=['GET'])
    def global_health():
        return jsonify({"status": "online", "message": "API Core is running"}), 200

    def safe_import_and_register(module_path, bp_name, display_name):
        try:
            module = __import__(module_path, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            app.register_blueprint(blueprint, url_prefix='/api')
            print(f"✅ [OK] Módulo cargado: {display_name}")
            return True
        except Exception as e:
            print(f"❌ [FALLO] No se pudo cargar {display_name}. Error: {e}")
            # Descomentar para depuración profunda en desarrollo
            # traceback.print_exc()
            return False

    # --- Módulos de Negocio y Catálogo ---
    print("\n--- Cargando Módulos de Negocio y Catálogo ---")
    safe_import_and_register('src.api.negocio.negocio_api', 'negocio_api_bp', 'Negocio')
    safe_import_and_register('src.api.negocio.catalogo_api', 'catalogo_api_bp', 'Catálogo')

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

    # --- Otros Módulos ---
    print("\n--- Cargando Otros Módulos ---")
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

    print("\n✨ Registro de API completado.")
    print("="*60 + "\n")
