import logging
import traceback
import sys
from flask import Blueprint, jsonify

# Crear el Blueprint contenedor principal
api_bp = Blueprint('api', __name__)

def register_api(app):
    """
    Registra todos los Blueprints en la aplicación Flask con trazabilidad completa.
    Implementa un sistema de tolerancia a fallos para evitar que errores en módulos 
    secundarios bloqueen rutas críticas como Negocio o Auth.
    """
    print("\n" + "🚀" * 20)
    print("INICIANDO REGISTRO SEGURO DE RUTAS API - BIZFLOW STUDIO")
    print("🚀" * 20)

    # --- 0. RUTA DE SALUD GLOBAL (Para el Monitor de Telemetría) ---
    @app.route('/api/health', methods=['GET'])
    def global_health():
        return jsonify({
            "status": "online",
            "message": "BizFlow Core Engine is running",
            "environment": "production/render"
        }), 200

    def safe_import_and_register(module_path, bp_name, display_name, unique_name=None):
        try:
            # Importación dinámica
            module = __import__(module_path, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            
            # Registro en el app con prefijo /api
            # IMPORTANTE: Al usar url_prefix='/api', todas las rutas del blueprint
            # se sumarán a este prefijo. Ej: /api + /producto/guardar
            if unique_name:
                app.register_blueprint(blueprint, url_prefix='/api', name=unique_name)
            else:
                app.register_blueprint(blueprint, url_prefix='/api')
                
            print(f"✅ [OK] {display_name}")
            return True
        except Exception as e:
            print(f"❌ [FALLO] {display_name}: No se pudo cargar. Error: {str(e)}")
            return False

    try:
        # --- 1. MÓDULO DE NEGOCIO Y CATÁLOGO (PRIORIDAD ALTA) ---
        print("\n--- Cargando Módulos de Negocio y Catálogo ---")
        
        # Módulo de Negocio Principal
        safe_import_and_register(
            'src.api.negocio_api', 
            'catalogo_api_bp', 
            'Módulo Negocio (Ciudades/Registro)', 
            'negocio_refactor'
        )

        # Módulo de Catálogo e Inyección de Productos
        # Este es el que define /producto/guardar
        safe_import_and_register(
            'src.api.negocio_api', 
            'catalogo_api_bp', 
            'Módulo Catálogo (Productos/Inyección)', 
            'catalogo_service'
        )

        # --- 2. CARGA DE MÓDULOS DE AUTENTICACIÓN ---
        print("\n--- Cargando Autenticación ---")
        auth_modulos = {
            'src.api.auth.auth_api': ('auth_api_bp', 'Autenticación Principal'),
            'src.api.auth.close_sesion_api': ('close_sesion_bp', 'Cierre de Sesión'),
            'src.api.auth.init_sesion_api': ('init_sesion_bp', 'Inicio de Sesión'),
            'src.api.auth.password_api': ('password_bp', 'Gestión de Password'),
        }
        for path, info in auth_modulos.items():
            safe_import_and_register(path, info[0], info[info[1] if isinstance(info[1], str) else 1])

        # --- 3. RESTO DE MÓDULOS ---
        print("\n--- Cargando Otros Módulos ---")
        otros_modulos = {
            'src.api.calificaciones.calificar_api': ('calificar_bp', 'Acción Calificar'),
            'src.api.candidates.details_candidate_api': ('details_candidate_bp', 'Detalles Candidato'),
            'src.api.contracts.create_contract_api': ('create_contract_bp', 'Creación de Contratos'),
            'src.api.contracts.contract_vigent_api': ('contract_vigent_bp', 'Contratos Vigentes'),
            'src.api.notifications.notifications_api': ('notifications_bp', 'Módulo Notificaciones'),
            'src.api.notifications.chat_api': ('chat_bp', 'Sistema de Chat'),
            'src.api.profile.view_logged_user_api': ('view_logged_user_bp', 'Ver Usuario Logueado'),
            'src.api.profile.edit_profile_api': ('edit_profile_bp', 'Editar Perfil'),
            'src.api.services.publish_service_api': ('publish_service_bp', 'Publicar Servicio'),
            'src.api.services.search_service_autocomplete_api': ('search_service_autocomplete_bp', 'Búsqueda Autocomplete'),
            'src.api.services.view_service_page_bp': ('view_service_page_bp', 'Vista de Página Servicio'),
            'src.api.utils.register_user_api': ('register_user_bp', 'Registro de Usuario Base')
        }

        for path, info in otros_modulos.items():
            safe_import_and_register(path, info[0], info[1])

        # --- 4. INSPECCIÓN FINAL DE RUTAS ---
        print("\n🔍 VERIFICACIÓN DE MAPA DE RUTAS:")
        for rule in app.url_map.iter_rules():
            if "/api/" in str(rule):
                # Marcamos rutas clave con estrella
                objetivo = "⭐" if any(x in str(rule) for x in ["catalogo", "producto", "negocio", "sucursal"]) else "  "
                print(f" {objetivo} {rule.rule} -> {rule.endpoint} | Métodos: {list(rule.methods)}")

    except Exception as e:
        print(f"🔥 ERROR CRÍTICO TOTAL en register_api: {str(e)}")
        traceback.print_exc()

    print("\n" + "="*60 + "\n")