import logging
from flask import Blueprint

# Crear el Blueprint principal que agrupará a todos los demás bajo el prefijo /api
api_bp = Blueprint('api', __name__)

def register_api(app):
    """
    Registra todos los Blueprints en la aplicación Flask con trazabilidad completa.
    """
    print("\n" + "="*60)
    print("🚀 LOG: Iniciando Proceso de Registro de Rutas API")
    print("="*60)

    try:
        # --- 1. IMPORTACIONES DE BLUEPRINTS ---
        from .auth.auth_api import auth_api_bp
        from .auth.close_sesion_api import close_sesion_bp
        from .auth.init_sesion_api import init_sesion_bp
        from .auth.password_api import password_bp

        from .calificaciones.calificaciones_received_contractor_api import calificaciones_recibidas_contractor_bp
        from .calificaciones.calificaciones_received_hiree_api import calificaciones_recibidas_hiree_bp
        from .calificaciones.calificar_api import calificar_bp
        from .calificaciones.rate_contractor_api import rate_contractor_bp
        from .calificaciones.rate_hiree_api import rate_hiree_bp

        from .candidates.details_candidate_api import details_candidate_bp

        from .contracts.contract_requests_api import contract_requests_bp
        from .contracts.contract_vigent_api import contract_vigent_bp
        from .contracts.contratos_roles_api import contratos_roles_bp
        from .contracts.create_contract_api import create_contract_bp

        from .dashboard.dashboard_main_api import dashboard_main_bp
        from .inicio.index_api import index_bp

        from .notifications.accept_notification_api import accept_notification_bp
        from .notifications.chat_api import chat_bp
        from .notifications.detail_notifications_api import detail_notifications_bp
        from .notifications.notifications_api import notifications_bp
        from .notifications.reject_notification_api import reject_notification_bp
        from .notifications.request_more_details_bp import request_more_details_bp
        from .notifications.show_notifications_api import show_notifications_bp

        from .profile.edit_profile_api import edit_profile_bp
        from .profile.logic_delete_user_api import logic_delete_user_bp
        from .profile.view_logged_user_api import view_logged_user_bp
        from .profile.view_user_info_api import view_user_info_bp

        from .search.search_results_api import search_results_bp

        from .services.count_service_api import count_total_service_bp
        from .services.delete_principal_service_api import delete_principal_service_bp
        from .services.delete_service_api import delete_service_bp
        from .services.edit_service_api import edit_service_bp
        from .services.filter_service_results_api import filter_service_results_bp
        from .services.publish_service_api import publish_service_bp
        from .services.search_service_autocomplete_api import search_service_autocomplete_bp
        from .services.total_service_api import total_service_bp
        from .services.view_service_page_bp import view_service_page_bp

        from .utils.get_cities_api import get_cities_bp
        from .utils.register_user_api import register_user_bp

        # --- MÓDULO NEGOCIO (IMPORTACIÓN) ---
        print("📝 LOG: Cargando módulo de Negocio...")
        from .negocio.negocio_api import negocio_api_bp 

        # --- 2. REGISTRO COLECTIVO CON IDENTIFICADORES ÚNICOS ---
        
        # PRIORIDAD: Registramos el de negocio con un nombre interno único. 
        # Esto evita que colisione con el Blueprint 'get_cities_bp' si ambos tienen rutas similares.
        api_bp.register_blueprint(negocio_api_bp, name="modulo_negocio")
        print("✅ LOG: Blueprint 'negocio_api_bp' registrado como 'modulo_negocio'.")
        
        # Lista del resto de blueprints
        blueprints = [
            auth_api_bp, close_sesion_bp, init_sesion_bp, password_bp,
            calificaciones_recibidas_contractor_bp, calificaciones_recibidas_hiree_bp,
            calificar_bp, rate_contractor_bp, rate_hiree_bp,
            details_candidate_bp, contract_requests_bp, contract_vigent_bp,
            contratos_roles_bp, create_contract_bp, dashboard_main_bp, index_bp,
            accept_notification_bp, chat_bp, detail_notifications_bp,
            notifications_bp, reject_notification_bp, request_more_details_bp,
            show_notifications_bp, edit_profile_bp, logic_delete_user_bp,
            view_logged_user_bp, view_user_info_bp, search_results_bp,
            count_total_service_bp, delete_principal_service_bp, delete_service_bp,
            edit_service_bp, filter_service_results_bp, publish_service_bp,
            search_service_autocomplete_bp, total_service_bp, view_service_page_bp,
            get_cities_bp, register_user_bp
        ]

        for bp in blueprints:
            api_bp.register_blueprint(bp)
        
        # --- 3. REGISTRO FINAL EN LA APP ---
        # Todas las rutas dentro de api_bp colgarán de /api/...
        app.register_blueprint(api_bp, url_prefix='/api')
        
        print("✅ LOG: Estructura jerárquica de Blueprints completada.")

        # --- 4. VERIFICACIÓN DE MAPA DE RUTAS ---
        print("\n🔍 INSPECCIÓN DE RUTAS BAJO '/api':")
        routes_found = 0
        for rule in app.url_map.iter_rules():
            rule_str = str(rule)
            if rule_str.startswith('/api'):
                # Resaltamos nuestra ruta objetivo para confirmar que existe
                status_icon = "📍"
                if "/ciudades" in rule_str:
                    status_icon = "⭐ [OBJETIVO]"
                
                print(f"   {status_icon} RUTA: {rule_str.ljust(40)} | Endpoint: {rule.endpoint}")
                routes_found += 1
        
        print(f"\n📊 Total de endpoints registrados en /api: {routes_found}")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO en register_api: {str(e)}")
        import traceback
        traceback.print_exc()

    print("="*60 + "\n")