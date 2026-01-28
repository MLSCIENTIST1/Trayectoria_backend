"""
BizFlow Studio - Registro de APIs v2.14
Sistema de carga segura de blueprints
Actualizado: Admin API para gestión de challenges y administradores
"""

import traceback
import logging
from flask import jsonify

logger = logging.getLogger(__name__)

print("=" * 70)
print("🔌 API __INIT__.PY: INICIANDO CARGA DEL MÓDULO")
print("=" * 70)


def register_api(app):
    """
    Registra de forma segura todos los Blueprints en la aplicación Flask.
    """
    
    print("=" * 70)
    print("🔌 REGISTER_API: INICIANDO REGISTRO DE BLUEPRINTS v2.14")
    print("=" * 70)
    
    logger.info("="*70)
    logger.info("🔌 INICIANDO REGISTRO DE BLUEPRINTS v2.14")
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
            "version": "2.14.0"
        }), 200
    
    logger.info("✅ Ruta de salud global registrada: /api/health")
    print("✅ Ruta de salud global registrada: /api/health")
    
    # ==========================================
    # FUNCIÓN DE REGISTRO SEGURO
    # ==========================================
    def safe_register(module_path, bp_name, display_name, prefix='/api'):
        """
        Intenta importar y registrar un blueprint de manera segura.
        """
        print(f"\n🔄 SAFE_REGISTER: Intentando cargar '{display_name}'...")
        print(f"   📦 Module path: {module_path}")
        print(f"   📦 Blueprint name: {bp_name}")
        print(f"   📦 Prefix: {prefix}")
        
        try:
            # Importar el módulo
            print(f"   🔄 Importando módulo '{module_path}'...")
            module = __import__(module_path, fromlist=[bp_name])
            print(f"   ✅ Módulo importado exitosamente")
            
            print(f"   🔄 Obteniendo blueprint '{bp_name}' del módulo...")
            blueprint = getattr(module, bp_name)
            print(f"   ✅ Blueprint obtenido: {blueprint}")
            
            # Registrar el blueprint
            print(f"   🔄 Registrando blueprint en la app...")
            if prefix:
                app.register_blueprint(blueprint, url_prefix=prefix)
            else:
                app.register_blueprint(blueprint)
            
            prefix_display = prefix if prefix else '/'
            print(f"   ✅ ÉXITO: {display_name} → {prefix_display}")
            logger.info(f"✅ {display_name:35} → {prefix_display}")
            return True
            
        except ImportError as e:
            print(f"   ❌ IMPORT ERROR en '{display_name}': {str(e)}")
            logger.error(f"❌ {display_name:35} → ImportError: {str(e)}")
            traceback.print_exc()
            return False
            
        except AttributeError as e:
            print(f"   ❌ ATTRIBUTE ERROR en '{display_name}': Blueprint '{bp_name}' no encontrado: {str(e)}")
            logger.error(f"❌ {display_name:35} → Blueprint '{bp_name}' no encontrado: {str(e)}")
            traceback.print_exc()
            return False
            
        except Exception as e:
            print(f"   ❌ ERROR GENERAL en '{display_name}': {str(e)}")
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
    print("\n" + "=" * 50)
    print("🔐 SECCIÓN: AUTENTICACIÓN")
    print("=" * 50)
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
        print("❌ CRÍTICO: No se pudo cargar el sistema de autenticación")
    
    # ==========================================
    # 🔑 RECUPERACIÓN DE CONTRASEÑA
    # ==========================================
    print("\n" + "=" * 50)
    print("🔑 SECCIÓN: RECUPERACIÓN DE CONTRASEÑA")
    print("=" * 50)
    logger.info("\n🔑 Cargando módulo de recuperación de contraseña...")
    
    if safe_register('src.api.auth.password_reset_api', 'password_reset_bp', 'Password Reset API', prefix=None):
        success_count += 1
    else:
        fail_count += 1
        logger.warning("⚠️  Módulo de recuperación de contraseña no cargado")
    
    # ==========================================
    # 🏢 NEGOCIO Y SUCURSALES (CRÍTICO)
    # ==========================================
    print("\n" + "=" * 50)
    print("🏢 SECCIÓN: NEGOCIO Y SUCURSALES")
    print("=" * 50)
    logger.info("\n🏢 Cargando módulos de negocio y sucursales...")
    
    negocio_loaded = False
    
    # Intentar cargar negocio_completo_api.py
    try:
        print("🔄 Intentando cargar negocio_completo_api directamente...")
        from src.api.negocio.negocio_completo_api import negocio_api_bp
        app.register_blueprint(negocio_api_bp, url_prefix='/api')
        logger.info(f"✅ {'Gestión Negocios/Sucursales':35} → /api")
        print("✅ Gestión Negocios/Sucursales cargado")
        success_count += 1
        negocio_loaded = True
    except ImportError as e:
        logger.error(f"❌ Error importando negocio_completo_api: {e}")
        print(f"❌ Error importando negocio_completo_api: {e}")
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
        print(f"❌ Error general cargando negocios: {e}")
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
    # 🔲 GENERADOR DE QR v2.0 (Página + Negocio)
    # ==========================================
    print("\n" + "=" * 70)
    print("🔲🔲🔲 SECCIÓN: GENERADOR DE QR v2.0 🔲🔲🔲")
    print("=" * 70)
    logger.info("\n🔲 Cargando módulo de generación de QR v2.0...")
    
    print("🔲 Endpoints disponibles:")
    print("   → /api/negocio/<id>/qr - QR del perfil público")
    print("   → /api/negocio/<id>/qr/download - Descargar QR perfil")
    print("   → /api/negocio/<id>/pagina/qr - QR de la tienda/página")
    print("   → /api/negocio/<id>/pagina/qr/download - Descargar QR página")
    print("   → /api/negocio/<id>/qr/all - Todos los QRs del negocio")
    print("   → /api/n/<slug> - Perfil público (donde apunta el QR)")
    print("   → /api/qr/generate - Generar QR genérico")
    print("   → /api/qr/health - Health check del módulo")
    
    # Las rutas ya incluyen /api/ en el blueprint
    if safe_register('src.api.negocio.qr_generator_api', 'qr_generator_bp', 'QR Generator v2.0 (Página+Perfil)', prefix=None):
        success_count += 1
        print("🔲 ✅✅✅ QR GENERATOR v2.0 CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🔲 ❌❌❌ QR GENERATOR FALLÓ AL CARGAR ❌❌❌")
        logger.warning("⚠️  Módulo de QR no cargado - pip install qrcode[pil]")
    
    print("=" * 70)
    
    # ==========================================
    # 🛒 COMPRADORES Y PEDIDOS (ECOSISTEMA TRAYECTORIA)
    # ==========================================
    print("\n" + "=" * 50)
    print("🛒 SECCIÓN: COMPRADORES Y PEDIDOS")
    print("=" * 50)
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
    print("\n" + "=" * 50)
    print("🏪 SECCIÓN: CHECKOUT API")
    print("=" * 50)
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
    print("\n" + "=" * 50)
    print("💰 SECCIÓN: CONTABILIDAD E INVENTARIO")
    print("=" * 50)
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
    print("\n" + "=" * 50)
    print("🔍 SECCIÓN: SERVICIOS Y BÚSQUEDA")
    print("=" * 50)
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
    print("\n" + "=" * 50)
    print("⭐ SECCIÓN: CALIFICACIONES")
    print("=" * 50)
    logger.info("\n⭐ Cargando módulos de calificaciones...")
    
    if safe_register('src.api.calificaciones.calificar_api', 'calificar_bp', 'Sistema de Calificaciones'):
        success_count += 1
    else:
        fail_count += 1
    
    # ==========================================
    # 👤 PERFIL DE USUARIO
    # ==========================================
    print("\n" + "=" * 50)
    print("👤 SECCIÓN: PERFIL DE USUARIO")
    print("=" * 50)
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
    # 🎯 PERFIL PÚBLICO NEGOCIO (BizScore) - CRÍTICO
    # ==========================================
    print("\n" + "=" * 70)
    print("🎯🎯🎯 SECCIÓN CRÍTICA: PERFIL PÚBLICO NEGOCIO (BizScore) 🎯🎯🎯")
    print("=" * 70)
    logger.info("\n🎯 Cargando módulo de perfil público BizScore...")
    
    print("🎯 Intentando cargar: src.api.profile.perfil_publico_negocio_api")
    print("🎯 Blueprint esperado: perfil_publico_negocio_bp")
    print("🎯 Prefix: None (rutas incluyen /api/)")
    
    # Perfil público del negocio - /api/negocio/perfil-publico/<slug>
    if safe_register('src.api.profile.perfil_publico_negocio_api', 'perfil_publico_negocio_bp', 'Perfil Público Negocio', prefix=None):
        success_count += 1
        print("🎯 ✅✅✅ PERFIL PÚBLICO NEGOCIO CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🎯 ❌❌❌ PERFIL PÚBLICO NEGOCIO FALLÓ AL CARGAR ❌❌❌")
        logger.warning("⚠️  Módulo de perfil público no cargado")
    
    print("=" * 70)
    
    # ==========================================
    # 🎬 FEED DE VIDEOS (Scroll Infinito)
    # ==========================================
    print("\n" + "=" * 70)
    print("🎬🎬🎬 SECCIÓN: FEED DE VIDEOS (Scroll Infinito) 🎬🎬🎬")
    print("=" * 70)
    logger.info("\n🎬 Cargando módulo de feed de videos...")
    
    print("🎬 Intentando cargar: src.api.videos.videos_api")
    print("🎬 Blueprint esperado: videos_api")
    print("🎬 Prefix: /api/videos")
    
    # Feed de videos - /api/videos/feed, /api/videos/<id>, etc.
    if safe_register('src.api.videos.videos_api', 'videos_api', 'Feed de Videos', prefix='/api/videos'):
        success_count += 1
        print("🎬 ✅✅✅ FEED DE VIDEOS CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🎬 ❌❌❌ FEED DE VIDEOS FALLÓ AL CARGAR ❌❌❌")
        logger.warning("⚠️  Módulo de feed de videos no cargado")
    
    print("=" * 70)
    
    # ==========================================
    # 🏆 CHALLENGE #MiNegocioEn15Segundos
    # ==========================================
    print("\n" + "=" * 70)
    print("🏆🏆🏆 SECCIÓN: CHALLENGE #MiNegocioEn15Segundos 🏆🏆🏆")
    print("=" * 70)
    logger.info("\n🏆 Cargando módulo de Challenge viral...")
    
    print("🏆 Intentando cargar: src.api.challenge_api")
    print("🏆 Blueprint esperado: challenge_bp")
    print("🏆 Prefix: None (rutas ya incluyen /api/challenge)")
    
    # Challenge API - /api/challenge/active, /api/challenge/votar, etc.
    if safe_register('src.api.challenge_api', 'challenge_bp', 'Challenge #MiNegocioEn15Segundos', prefix=None):
        success_count += 1
        print("🏆 ✅✅✅ CHALLENGE API CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🏆 ❌❌❌ CHALLENGE API FALLÓ AL CARGAR ❌❌❌")
        logger.warning("⚠️  Módulo de Challenge no cargado")
    
    print("=" * 70)
    
    # ==========================================
    # 🔐 ADMIN API (Panel de Administración)
    # ==========================================
    print("\n" + "=" * 70)
    print("🔐🔐🔐 SECCIÓN: ADMIN API (Panel de Administración) 🔐🔐🔐")
    print("=" * 70)
    logger.info("\n🔐 Cargando módulo de administración...")
    
    print("🔐 Intentando cargar: src.api.admin_api")
    print("🔐 Blueprint esperado: admin_bp")
    print("🔐 Prefix: None (rutas ya incluyen /api/admin)")
    print("🔐 Endpoints disponibles:")
    print("   → /api/admin/check - Verificar si es admin")
    print("   → /api/admin/list - Listar administradores")
    print("   → /api/admin/add - Agregar admin (superadmin)")
    print("   → /api/admin/remove/<id> - Desactivar admin")
    print("   → /api/admin/challenges - CRUD challenges")
    print("   → /api/admin/participaciones - Gestionar participaciones")
    print("   → /api/admin/stats - Estadísticas generales")
    
    # Admin API - /api/admin/check, /api/admin/challenges, etc.
    if safe_register('src.api.admin_api', 'admin_bp', 'Admin API', prefix=None):
        success_count += 1
        print("🔐 ✅✅✅ ADMIN API CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🔐 ❌❌❌ ADMIN API FALLÓ AL CARGAR ❌❌❌")
        logger.warning("⚠️  Módulo de Admin no cargado")
    
    print("=" * 70)
    
    # ==========================================
    # 💬 NOTIFICACIONES Y CHAT
    # ==========================================
    print("\n" + "=" * 50)
    print("💬 SECCIÓN: NOTIFICACIONES Y CHAT")
    print("=" * 50)
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
    print("\n" + "=" * 50)
    print("📋 SECCIÓN: CONTRATOS Y CANDIDATOS")
    print("=" * 50)
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
    print("\n" + "=" * 50)
    print("🎯 SECCIÓN: TRAYECTORIA")
    print("=" * 50)
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
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL DE REGISTRO DE BLUEPRINTS")
    print("=" * 70)
    print(f"   ✅ Exitosos:  {success_count}")
    print(f"   ❌ Fallidos:  {fail_count}")
    print(f"   📦 Total:     {success_count + fail_count}")
    print("=" * 70)
    
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
    print("\n🔲 Verificando rutas de QR Generator v2.0:")
    logger.info("\n🔲 Rutas de QR registradas:")
    qr_encontrado = False
    for rule in app.url_map.iter_rules():
        if '/qr' in rule.rule or '/n/' in rule.rule:
            print(f"   ✅ ENCONTRADA: {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            qr_encontrado = True
    
    if not qr_encontrado:
        print("   ❌ NO SE ENCONTRARON RUTAS DE QR")
    
    # 🎯 Listar rutas de perfil público
    print("\n🎯 Verificando rutas de perfil público BizScore:")
    logger.info("\n🎯 Rutas de perfil público BizScore:")
    perfil_publico_encontrado = False
    for rule in app.url_map.iter_rules():
        if 'perfil-publico' in rule.rule:
            print(f"   ✅ ENCONTRADA: {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            perfil_publico_encontrado = True
    
    if not perfil_publico_encontrado:
        print("   ❌ NO SE ENCONTRARON RUTAS DE PERFIL PÚBLICO")
    
    # 🎬 Listar rutas de videos
    print("\n🎬 Verificando rutas de feed de videos:")
    logger.info("\n🎬 Rutas de feed de videos:")
    videos_encontrado = False
    for rule in app.url_map.iter_rules():
        if '/videos' in rule.rule:
            print(f"   ✅ ENCONTRADA: {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            videos_encontrado = True
    
    if not videos_encontrado:
        print("   ❌ NO SE ENCONTRARON RUTAS DE VIDEOS")
    
    # 🏆 Listar rutas de Challenge
    print("\n🏆 Verificando rutas de Challenge:")
    logger.info("\n🏆 Rutas de Challenge #MiNegocioEn15Segundos:")
    challenge_encontrado = False
    for rule in app.url_map.iter_rules():
        if '/challenge' in rule.rule:
            print(f"   ✅ ENCONTRADA: {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            challenge_encontrado = True
    
    if not challenge_encontrado:
        print("   ❌ NO SE ENCONTRARON RUTAS DE CHALLENGE")
    
    # 🔐 Listar rutas de Admin
    print("\n🔐 Verificando rutas de Admin API:")
    logger.info("\n🔐 Rutas de Admin API:")
    admin_encontrado = False
    for rule in app.url_map.iter_rules():
        if '/admin' in rule.rule:
            print(f"   ✅ ENCONTRADA: {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            admin_encontrado = True
    
    if not admin_encontrado:
        print("   ❌ NO SE ENCONTRARON RUTAS DE ADMIN")
    
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
        print(f"⚠️  {fail_count} módulo(s) no se cargaron. Revisa los logs.")
    else:
        logger.info("🎉 Todos los módulos cargados exitosamente")
        print("🎉 Todos los módulos cargados exitosamente")
    
    # Listar rutas de trayectoria
    logger.info("\n🎯 Rutas de trayectoria registradas:")
    for rule in app.url_map.iter_rules():
        if 'scores' in rule.rule or 'stages' in rule.rule or 'badges' in rule.rule or 'metrics' in rule.rule or 'portfolio' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    logger.info("")
    
    print("\n" + "=" * 70)
    print("🔌 REGISTER_API: FINALIZADO")
    print("=" * 70)
    
    return success_count, fail_count


print("=" * 70)
print("🔌 API __INIT__.PY: MÓDULO CARGADO")
print("=" * 70)