"""
BizFlow Studio - Registro de APIs v2.1
Sistema de carga segura de blueprints
Actualizado: Auth unificado en auth_system.py
"""

import traceback
import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def register_api(app):
    """
    Registra de forma segura todos los Blueprints en la aplicación Flask.
    """
    
    logger.info("="*70)
    logger.info("🔌 INICIANDO REGISTRO DE BLUEPRINTS v2.1")
    logger.info("="*70)
    
    # ==========================================
    # RUTA DE SALUD GLOBAL
    # ==========================================
    @app.route('/api/health', methods=['GET'])
    def api_health():
        """Endpoint de salud específico de la API"""
        return jsonify({
            "status": "online", 
            "message": "BizFlow Studio API operativa",
            "version": "2.1.0"
        }), 200
    
    logger.info("✅ Ruta de salud global registrada: /api/health")
    
    # ==========================================
    # FUNCIÓN DE REGISTRO SEGURO
    # ==========================================
    def safe_register(module_path, bp_name, display_name, prefix='/api'):
        """
        Intenta importar y registrar un blueprint de manera segura.
        """
        try:
            module = __import__(module_path, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            
            if prefix:
                app.register_blueprint(blueprint, url_prefix=prefix)
            else:
                app.register_blueprint(blueprint)
            
            prefix_display = prefix if prefix else '/'
            logger.info(f"✅ {display_name:35} → {prefix_display}")
            return True
            
        except ImportError as e:
            logger.error(f"❌ {display_name:35} → ImportError: {str(e)}")
            if app.debug:
                traceback.print_exc()
            return False
            
        except AttributeError as e:
            logger.error(f"❌ {display_name:35} → Blueprint '{bp_name}' no encontrado")
            return False
            
        except Exception as e:
            logger.error(f"❌ {display_name:35} → Error: {str(e)}")
            if app.debug:
                traceback.print_exc()
            return False
    
    # ==========================================
    # CONTADORES
    # ==========================================
    success_count = 0
    fail_count = 0
    
    # ==========================================
    # 🔐 AUTENTICACIÓN (CRÍTICO - PRIMERO)
    # ==========================================
    logger.info("\n🔐 Cargando sistema de autenticación UNIFICADO...")
    
    # Intentar primero en src.api.auth, luego en src.routes
    auth_loaded = False
    
    # Opción 1: src.api.auth.auth_system
    if safe_register('src.api.auth.auth_system', 'auth_bp', 'Auth System (api/auth)', prefix=None):
        success_count += 1
        auth_loaded = True
    # Opción 2: src.routes.auth_system_api
    elif safe_register('src.routes.auth_system_api', 'auth_bp', 'Auth System (routes)', prefix=None):
        success_count += 1
        auth_loaded = True
    else:
        fail_count += 1
        logger.error("❌ CRÍTICO: No se pudo cargar el sistema de autenticación")
    
    # ==========================================
    # 🏢 NEGOCIO Y CATÁLOGO
    # ==========================================
    logger.info("\n🏢 Cargando módulos de negocio...")
    
    business_modules = [
        ('src.api.negocio.negocio_api', 'negocio_api_bp', 'Gestión de Negocios', '/api'),
        ('src.api.negocio.catalogo_api', 'catalogo_api_bp', 'Catálogo de Productos', '/api'),
        ('src.api.negocio.pagina_api', 'pagina_api_bp', 'Micrositios Públicos', None),
    ]
    
    for item in business_modules:
        module_path, bp_name, display_name, prefix = item
        if safe_register(module_path, bp_name, display_name, prefix):
            success_count += 1
        else:
            fail_count += 1
    
    # ==========================================
    # 💰 CONTABILIDAD E INVENTARIO
    # ==========================================
    logger.info("\n💰 Cargando centro de control operativo...")
    
    accounting_modules = [
        ('src.api.contabilidad.control_api', 'control_api_bp', 'Control Operativo'),
        ('src.api.contabilidad.carga_masiva_api', 'carga_masiva_bp', 'Carga Masiva CSV'),
        ('src.api.contabilidad.alertas_api', 'alertas_api_bp', 'Sistema de Alertas'),
    ]
    
    for module_path, bp_name, display_name in accounting_modules:
        if safe_register(module_path, bp_name, display_name):
            success_count += 1
        else:
            fail_count += 1
    
    # ==========================================
    # 🔍 SERVICIOS Y BÚSQUEDA
    # ==========================================
    logger.info("\n🔍 Cargando módulos de servicios...")
    
    service_modules = [
        ('src.api.services.publish_service_api', 'publish_service_bp', 'Publicación de Servicios'),
        ('src.api.services.search_service_autocomplete_api', 'search_service_autocomplete_bp', 'Búsqueda Autocomplete'),
        ('src.api.services.view_service_page_bp', 'view_service_page_bp', 'Vista de Servicios'),
    ]
    
    for module_path, bp_name, display_name in service_modules:
        if safe_register(module_path, bp_name, display_name):
            success_count += 1
        else:
            fail_count += 1
    
    # ==========================================
    # ⭐ CALIFICACIONES
    # ==========================================
    logger.info("\n⭐ Cargando módulos de calificaciones...")
    
    if safe_register('src.api.calificaciones.calificar_api', 'calificar_bp', 'Sistema de Calificaciones'):
        success_count += 1
    else:
        fail_count += 1
    
    # ==========================================
    # 👤 PERFIL DE USUARIO
    # ==========================================
    logger.info("\n👤 Cargando módulos de perfil...")
    
    profile_modules = [
        ('src.api.profile.view_logged_user_api', 'view_logged_user_bp', 'Ver Perfil de Usuario'),
        ('src.api.profile.edit_profile_api', 'edit_profile_bp', 'Editar Perfil'),
        ('src.api.utils.register_user_api', 'register_user_bp', 'Registro de Usuarios'),
    ]
    
    for module_path, bp_name, display_name in profile_modules:
        if safe_register(module_path, bp_name, display_name):
            success_count += 1
        else:
            fail_count += 1
    
    # ==========================================
    # 💬 NOTIFICACIONES Y CHAT
    # ==========================================
    logger.info("\n💬 Cargando módulos de comunicación...")
    
    communication_modules = [
        ('src.api.notifications.notifications_api', 'notifications_bp', 'Sistema de Notificaciones'),
        ('src.api.notifications.chat_api', 'chat_bp', 'Sistema de Chat'),
    ]
    
    for module_path, bp_name, display_name in communication_modules:
        if safe_register(module_path, bp_name, display_name):
            success_count += 1
        else:
            fail_count += 1
    
    # ==========================================
    # 📋 CONTRATOS Y CANDIDATOS
    # ==========================================
    logger.info("\n📋 Cargando módulos de contratos...")
    
    contract_modules = [
        ('src.api.contracts.create_contract_api', 'create_contract_bp', 'Creación de Contratos'),
        ('src.api.contracts.contract_vigent_api', 'contract_vigent_bp', 'Contratos Vigentes'),
        ('src.api.candidates.details_candidate_api', 'details_candidate_bp', 'Detalles de Candidatos'),
    ]
    
    for module_path, bp_name, display_name in contract_modules:
        if safe_register(module_path, bp_name, display_name):
            success_count += 1
        else:
            fail_count += 1
    
    # ==========================================
    # 📊 RESUMEN FINAL
    # ==========================================
    logger.info("\n" + "="*70)
    logger.info("📊 RESUMEN DE REGISTRO DE BLUEPRINTS")
    logger.info("="*70)
    logger.info(f"   ✅ Exitosos:  {success_count}")
    logger.info(f"   ❌ Fallidos:  {fail_count}")
    logger.info(f"   📦 Total:     {success_count + fail_count}")
    logger.info("="*70)
    
    if fail_count > 0:
        logger.warning(f"⚠️  {fail_count} módulo(s) no se cargaron. Revisa los logs.")
    else:
        logger.info("🎉 Todos los módulos cargados exitosamente")
    
    logger.info("")
    
    return success_count, fail_count