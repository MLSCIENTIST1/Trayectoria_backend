import logging
import traceback
from flask import Blueprint

# Crear el Blueprint contenedor de la API
api_bp = Blueprint('api', __name__)

def register_api(app):
    """
    Registra todos los Blueprints en la aplicación Flask con trazabilidad completa.
    Implementa un sistema de tolerancia a fallos para evitar que un error de importación
    detenga el registro de otras rutas críticas.
    """
    print("\n" + "🚀" * 20)
    print("INICIANDO REGISTRO SEGURO DE RUTAS API")
    print("🚀" * 20)

    # 1. Función auxiliar para intentar registros sin romper el flujo principal
    def safe_import_and_register(module_path, bp_name, display_name, unique_name=None):
        try:
            # Importación dinámica del módulo
            module = __import__(module_path, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            
            # Registro en el api_bp principal
            if unique_name:
                api_bp.register_blueprint(blueprint, name=unique_name)
            else:
                api_bp.register_blueprint(blueprint)
                
            print(f"✅ [OK] {display_name}")
            return True
        except Exception as e:
            print(f"❌ [FALLO] {display_name}: No se pudo cargar. Error: {str(e)}")
            return False

    try:
        # --- 2. MÓDULO DE NEGOCIO (PRIORIDAD ALTA) ---
        # Lo registramos primero con un nombre único para evitar que colisione con /ciudades de utils
        print("\n--- Cargando Módulos de Negocio ---")
        safe_import_and_register(
            'src.api.negocio.negocio_api', 
            'negocio_api_bp', 
            'Módulo Negocio (Ciudades/Registro)', 
            'negocio_refactor'
        )

        # --- 3. CARGA DEL RESTO DE MÓDULOS ---
        print("\n--- Cargando Otros Módulos ---")
        
        # Diccionario de módulos a cargar: { 'Ruta del módulo': ('Nombre del BP', 'Nombre descriptivo') }
        modulos = {
            # Auth
            'src.api.auth.auth_api': ('auth_api_bp', 'Autenticación Principal'),
            'src.api.auth.close_sesion_api': ('close_sesion_bp', 'Cierre de Sesión'),
            'src.api.auth.init_sesion_api': ('init_sesion_bp', 'Inicio de Sesión'),
            'src.api.auth.password_api': ('password_bp', 'Gestión de Password'),

            # Calificaciones (Donde estaba el error crítico)
            'src.api.calificaciones.calificaciones_received_contractor_api': ('calificaciones_recibidas_contractor_bp', 'Calific. Recibidas Contractor'),
            'src.api.calificaciones.calificaciones_received_hiree_api': ('calificaciones_recibidas_hiree_bp', 'Calific. Recibidas Hiree'),
            'src.api.calificaciones.calificar_api': ('calificar_bp', 'Acción Calificar'),
            
            # Contratos y Candidatos
            'src.api.candidates.details_candidate_api': ('details_candidate_bp', 'Detalles Candidato'),
            'src.api.contracts.create_contract_api': ('create_contract_bp', 'Creación de Contratos'),
            'src.api.contracts.contract_vigent_api': ('contract_vigent_bp', 'Contratos Vigentes'),

            # Notificaciones
            'src.api.notifications.notifications_api': ('notifications_bp', 'Módulo Notificaciones'),
            'src.api.notifications.chat_api': ('chat_bp', 'Sistema de Chat'),

            # Perfil
            'src.api.profile.view_logged_user_api': ('view_logged_user_bp', 'Ver Usuario Logueado'),
            'src.api.profile.edit_profile_api': ('edit_profile_bp', 'Editar Perfil'),

            # Servicios
            'src.api.services.publish_service_api': ('publish_service_bp', 'Publicar Servicio'),
            'src.api.services.search_service_autocomplete_api': ('search_service_autocomplete_bp', 'Búsqueda Autocomplete'),
            'src.api.services.view_service_page_bp': ('view_service_page_bp', 'Vista de Página Servicio'),

            # Utils
            'src.api.utils.get_cities_api': ('get_cities_bp', 'Utils: Obtener Ciudades'),
            'src.api.utils.register_user_api': ('register_user_bp', 'Registro de Usuario Base')
        }

        for path, info in modulos.items():
            safe_import_and_register(path, info[0], info[1])

        # --- 4. REGISTRO DEL CONTENEDOR EN LA APP ---
        app.register_blueprint(api_bp, url_prefix='/api')
        print("\n✅ LOG: Estructura de Blueprints anclada a /api")

        # --- 5. INSPECCIÓN FINAL DE RUTAS ---
        print("\n🔍 VERIFICACIÓN DE MAPA DE RUTAS:")
        for rule in app.url_map.iter_rules():
            if "/api/ciudades" in str(rule):
                status = "⭐ [ACTIVA]" if "OPTIONS" in rule.methods else "⚠️ [FALTA OPTIONS]"
                print(f"   {status} {rule.rule} -> {rule.endpoint} | Métodos: {list(rule.methods)}")

    except Exception as e:
        print(f"🔥 ERROR CRÍTICO TOTAL en register_api: {str(e)}")
        traceback.print_exc()

    print("\n" + "="*60 + "\n")