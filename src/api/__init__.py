"""
BizFlow Studio - Registro de APIs v2.10
Sistema de carga segura de blueprints
Actualizado: Agregado módulo de Perfil Público BizScore
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
    logger.info("🔌 INICIANDO REGISTRO DE BLUEPRINTS v2.10")
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
            "version": "2.10.0"
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
            # Importar el módulo
            module = __import__(module_path, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            
            # Registrar el blueprint
            if prefix:
                app.register_blueprint(blueprint, url_prefix=prefix)
            else:
                app.register_blueprint(blueprint)
            
            prefix_display = prefix if prefix else '/'
            logger.info(f"✅ {display_name:35} → {prefix_display}")
            return True
            
        except ImportError as e:
            logger.error(f"❌ {display_name:35} → ImportError: {str(e)}")
            traceback.print_exc()
            return False
            
        except AttributeError as e:
            logger.error(f"❌ {display_name:35} → Blueprint '{bp_name}' no encontrado: {str(e)}")
            traceback.print_exc()
            return False
            
        except Exception as e:
            logger.error(f"❌ {display_name:35} → Error: {str(e)}")
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
    logger.info("\n🔐 Cargando sistema de autenticación...")
    
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
    # 🔑 RECUPERACIÓN DE CONTRASEÑA
    # ==========================================
    logger.info("\n🔑 Cargando módulo de recuperación de contraseña...")
    
    if safe_register('src.api.auth.password_reset_api', 'password_reset_bp', 'Password Reset API', prefix=None):
        success_count += 1
    else:
        fail_count += 1
        logger.warning("⚠️  Módulo de recuperación de contraseña no cargado")
    
    # ==========================================
    # 🏢 NEGOCIO Y SUCURSALES (CRÍTICO)
    # ==========================================
    logger.info("\n🏢 Cargando módulos de negocio y sucursales...")
    
    negocio_loaded = False
    
    # Intentar cargar negocio_completo_api.py
    try:
        from src.api.negocio.negocio_completo_api import negocio_api_bp
        app.register_blueprint(negocio_api_bp, url_prefix='/api')
        logger.info(f"✅ {'Gestión Negocios/Sucursales':35} → /api")
        success_count += 1
        negocio_loaded = True
    except ImportError as e:
        logger.error(f"❌ Error importando negocio_completo_api: {e}")
        traceback.print_exc()
        
        # Fallback: intentar negocio_api.py
        try:
            from src.api.negocio.negocio_completo_api import negocio_api_bp
            app.register_blueprint(negocio_api_bp, url_prefix='/api')
            logger.info(f"✅ {'Gestión Negocios (legacy)':35} → /api")
            success_count += 1
            negocio_loaded = True
        except ImportError as e2:
            logger.error(f"❌ Error importando negocio_api (fallback): {e2}")
            fail_count += 1
    except Exception as e:
        logger.error(f"❌ Error general cargando negocios: {e}")
        traceback.print_exc()
        fail_count += 1
    
    # Catálogo de productos
    if safe_register('src.api.negocio.catalogo_api', 'catalogo_api_bp', 'Catálogo de Productos', '/api'):
        success_count += 1
    else:
        fail_count += 1
    
    # Micrositios públicos
    if safe_register('src.api.negocio.pagina_api', 'pagina_api_bp', 'Micrositios Públicos', None):
        success_count += 1
    else:
        fail_count += 1
    
    # ==========================================
    # 🔲 GENERADOR DE QR
    # ==========================================
    logger.info("\n🔲 Cargando módulo de generación de QR...")
    
    # Las rutas ya incluyen /api/ en el blueprint
    if safe_register('src.api.negocio.qr_generator_api', 'qr_generator_bp', 'Generador de QR', prefix=None):
        success_count += 1
    else:
        fail_count += 1
        logger.warning("⚠️  Módulo de QR no cargado - pip install qrcode[pil]")
    
    # ==========================================
    # 🛒 COMPRADORES Y PEDIDOS (ECOSISTEMA TRAYECTORIA)
    # ==========================================
    logger.info("\n🛒 Cargando módulos de compradores y pedidos...")
    
    compradores_modules = [
        ('src.api.compradores.compradores_api', 'compradores_api_bp', 'Gestión de Compradores'),
        ('src.api.compradores.pedidos_api', 'pedidos_api_bp', 'Gestión de Pedidos'),
    ]
    
    for module_path, bp_name, display_name in compradores_modules:
        if safe_register(module_path, bp_name, display_name):
            success_count += 1
        else:
            fail_count += 1
    
    # ==========================================
    # 🏪 CHECKOUT API (Tiendas Online)
    # ==========================================
    logger.info("\n🏪 Cargando módulo de checkout para tiendas online...")
    
    if safe_register('src.api.tiendas.checkout_api', 'checkout_api_bp', 'Checkout Tiendas Online'):
        success_count += 1
    else:
        fail_count += 1
        logger.warning("⚠️  Módulo de checkout no cargado - Las tiendas no podrán procesar pedidos")
    
    # 📦 Pedidos API (Gestión de pedidos para el dueño)
    if safe_register('src.api.tiendas.pedidos_api', 'pedidos_api_bp', 'Gestión de Pedidos'):
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
        ('src.api.profile.avatar_api', 'avatar_api_bp', 'Avatar/Foto de Perfil'),
        ('src.api.utils.register_user_api', 'register_user_bp', 'Registro de Usuarios'),
    ]
    
    for module_path, bp_name, display_name in profile_modules:
        if safe_register(module_path, bp_name, display_name):
            success_count += 1
        else:
            fail_count += 1
    
    # ==========================================
    # 🎯 PERFIL PÚBLICO NEGOCIO (BizScore)
    # ==========================================
    logger.info("\n🎯 Cargando módulo de perfil público BizScore...")
    
    # Perfil público del negocio - /api/negocio/perfil-publico/<slug>
    if safe_register('src.api.profile.perfil_publico_negocio_api', 'perfil_publico_negocio_bp', 'Perfil Público Negocio', prefix=None):
        success_count += 1
    else:
        fail_count += 1
        logger.warning("⚠️  Módulo de perfil público no cargado")
    
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
    
    # 🔔 Notificaciones para Negocios (campanita BizFlow)
    # Nota: prefix=None porque las rutas ya incluyen /api/
    if safe_register('src.api.notifications.notifications_negocio_api', 'notifications_negocio_bp', 'Notificaciones Negocio', prefix=None):
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
    # 🎯 TRAYECTORIA (SCORES, BADGES, MÉTRICAS, PORTFOLIO)
    # ==========================================
    logger.info("\n🎯 Cargando módulos de trayectoria...")
    
    trayectoria_modules = [
        ('src.api.trayectoria.scores_api', 'scores_bp', 'Scores de Usuario'),
        ('src.api.trayectoria.stages_api', 'stages_bp', 'Etapas de Trayectoria'),
        ('src.api.trayectoria.badges_api', 'badges_bp', 'Sistema de Badges'),
        ('src.api.trayectoria.metrics_api', 'metrics_bp', 'Métricas de Usuario'),
        ('src.api.trayectoria.portfolio_api', 'portfolio_bp', 'Portfolio de Videos'),
    ]
    
    for module_path, bp_name, display_name in trayectoria_modules:
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
    
    # Listar rutas registradas para negocios
    logger.info("\n📍 Rutas de negocios registradas:")
    for rule in app.url_map.iter_rules():
        if 'negocio' in rule.rule or 'sucursal' in rule.rule or 'mis_negocios' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # 🔲 Listar rutas de QR
    logger.info("\n🔲 Rutas de QR registradas:")
    for rule in app.url_map.iter_rules():
        if '/qr' in rule.rule or '/n/' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # 🎯 Listar rutas de perfil público
    logger.info("\n🎯 Rutas de perfil público BizScore:")
    for rule in app.url_map.iter_rules():
        if 'perfil-publico' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Listar rutas de compradores y pedidos
    logger.info("\n🛒 Rutas de compradores y pedidos registradas:")
    for rule in app.url_map.iter_rules():
        if 'comprador' in rule.rule or 'pedido' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Listar rutas de checkout/tiendas
    logger.info("\n🏪 Rutas de checkout/tiendas registradas:")
    for rule in app.url_map.iter_rules():
        if 'tienda' in rule.rule or 'checkout' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Listar rutas de recuperación de contraseña
    logger.info("\n🔑 Rutas de recuperación de contraseña registradas:")
    for rule in app.url_map.iter_rules():
        if 'reset' in rule.rule or 'forgot' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Listar rutas de avatar/perfil
    logger.info("\n📸 Rutas de avatar registradas:")
    for rule in app.url_map.iter_rules():
        if 'avatar' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Listar rutas de notificaciones
    logger.info("\n🔔 Rutas de notificaciones registradas:")
    for rule in app.url_map.iter_rules():
        if 'notification' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")

    if fail_count > 0:
        logger.warning(f"⚠️  {fail_count} módulo(s) no se cargaron. Revisa los logs.")
    else:
        logger.info("🎉 Todos los módulos cargados exitosamente")
    
    # Listar rutas de trayectoria
    logger.info("\n🎯 Rutas de trayectoria registradas:")
    for rule in app.url_map.iter_rules():
        if 'scores' in rule.rule or 'stages' in rule.rule or 'badges' in rule.rule or 'metrics' in rule.rule or 'portfolio' in rule.rule or '/videos' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    logger.info("")
    
    return success_count, fail_count