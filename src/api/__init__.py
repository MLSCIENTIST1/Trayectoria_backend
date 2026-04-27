# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗██╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗  ██████╗██╗ ██████╗ 
# ╚══██╔══╝██║   ██║██║ ██╔╝██╔═══██╗████╗ ████║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗
#    ██║   ██║   ██║█████╔╝ ██║   ██║██╔████╔██║█████╗  ██████╔╝██║     ██║██║   ██║
#    ██║   ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║   ██║
#    ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║╚██████╔╝
#    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝ 
# ═══════════════════════════════════════════════════════════════════════════════
#
# TUKOMERCIO - Plataforma de Comercio Electrónico, Gamificación y Gestión Empresarial
# Anteriormente conocido como: Trayectoria / BizFlow Studio
#
# ═══════════════════════════════════════════════════════════════════════════════
# AVISO DE PROPIEDAD INTELECTUAL Y DERECHOS DE AUTOR
# ═══════════════════════════════════════════════════════════════════════════════
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#
# TITULAR DE DERECHOS:
#   Nombre:     Carlos Eduardo Huérfano Bermúdez
#   C.C.:       1.064.986.917 (Cereté, Córdoba, Colombia)
#   Contacto:   carlos-5100@hotmail.com | +57 322 818 8375
#   Ubicación:  Bogotá D.C., Colombia
#
# INFORMACIÓN DEL PROYECTO:
#   Nombre:     TuKomercio
#   Inicio:     Julio 24, 2024
#   Repositorio: github.com/routeres (routeres@gmail.com)
#
# ═══════════════════════════════════════════════════════════════════════════════
# TÉRMINOS DE USO Y RESTRICCIONES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este código fuente es CONFIDENCIAL y constituye un SECRETO COMERCIAL.
#
# QUEDA ESTRICTAMENTE PROHIBIDO sin autorización ESCRITA del titular:
#
#   1. Copiar, reproducir o duplicar este código, total o parcialmente
#   2. Modificar, adaptar o crear obras derivadas
#   3. Distribuir, publicar, sublicenciar o transferir a terceros
#   4. Usar para desarrollo de productos competidores
#   5. Realizar ingeniería inversa, descompilar o desensamblar
#   6. Remover o alterar este aviso de propiedad intelectual
#
# El acceso a este código NO otorga ninguna licencia implícita o explícita.
#
# ═══════════════════════════════════════════════════════════════════════════════
# PROTECCIÓN LEGAL
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este software está protegido por:
#
#   • Ley 23 de 1982 - Derechos de Autor (Colombia)
#   • Ley 1915 de 2018 - Modernización Derechos de Autor (Colombia)
#   • Decisión Andina 351 de 1993 - Régimen Común sobre Derecho de Autor
#   • Convenio de Berna para la Protección de Obras Literarias y Artísticas
#   • Tratado OMPI sobre Derecho de Autor (WCT)
#   • Acuerdo ADPIC/TRIPS - Organización Mundial del Comercio
#
# SANCIONES POR INFRACCIÓN:
#   • Civiles: Indemnización por daños y perjuicios (Art. 57, Ley 23/1982)
#   • Penales: Prisión de 4 a 8 años y multa (Art. 271, Código Penal Colombiano)
#
# ═══════════════════════════════════════════════════════════════════════════════
# JURISDICCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
#
# Cualquier disputa será resuelta exclusivamente por los tribunales de
# Bogotá D.C., Colombia, bajo las leyes de la República de Colombia.
#
# ═══════════════════════════════════════════════════════════════════════════════
#
# Para solicitar autorización de uso: carlos-5100@hotmail.com
#
# ═══════════════════════════════════════════════════════════════════════════════


"""
BizFlow Studio - Registro de APIs v2.18
Sistema de carga segura de blueprints
Actualizado: MecaLink - Mecánicos a Domicilio
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
    print("🔌 REGISTER_API: INICIANDO REGISTRO DE BLUEPRINTS v2.18")
    print("=" * 70)
    
    logger.info("="*70)
    logger.info("🔌 INICIANDO REGISTRO DE BLUEPRINTS v2.18")
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
            "version": "2.18.0"
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
            print(f"   🔄 Importando módulo '{module_path}'...")
            module = __import__(module_path, fromlist=[bp_name])
            print(f"   ✅ Módulo importado exitosamente")
            
            print(f"   🔄 Obteniendo blueprint '{bp_name}' del módulo...")
            blueprint = getattr(module, bp_name)
            print(f"   ✅ Blueprint obtenido: {blueprint}")
            
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
    
    if safe_register('src.api.auth.auth_system', 'auth_bp', 'Auth System (api/auth)', prefix=None):
        success_count += 1
        auth_loaded = True
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
    if safe_register('src.api.tiendas.pedidos_api', 'tiendas_pedidos_bp', 'Gestión de Pedidos (Tiendas)'):
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
    
    if safe_register('src.api.profile.perfil_publico_negocio_api', 'perfil_publico_negocio_bp', 'Perfil Público Negocio', prefix=None):
        success_count += 1
        print("🎯 ✅✅✅ PERFIL PÚBLICO NEGOCIO CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🎯 ❌❌❌ PERFIL PÚBLICO NEGOCIO FALLÓ AL CARGAR ❌❌❌")
    
    print("=" * 70)
    
    # ==========================================
    # 🎬 FEED DE VIDEOS (Scroll Infinito)
    # ==========================================
    print("\n" + "=" * 70)
    print("🎬🎬🎬 SECCIÓN: FEED DE VIDEOS (Scroll Infinito) 🎬🎬🎬")
    print("=" * 70)
    logger.info("\n🎬 Cargando módulo de feed de videos...")
    
    if safe_register('src.api.videos.videos_api', 'videos_api', 'Feed de Videos', prefix='/api/videos'):
        success_count += 1
        print("🎬 ✅✅✅ FEED DE VIDEOS CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🎬 ❌❌❌ FEED DE VIDEOS FALLÓ AL CARGAR ❌❌❌")
    
    print("=" * 70)
    
    # ==========================================
    # 🏆 CHALLENGE #MiNegocioEn15Segundos
    # ==========================================
    print("\n" + "=" * 70)
    print("🏆🏆🏆 SECCIÓN: CHALLENGE #MiNegocioEn15Segundos 🏆🏆🏆")
    print("=" * 70)
    logger.info("\n🏆 Cargando módulo de Challenge viral...")
    
    if safe_register('src.api.challenge_api', 'challenge_bp', 'Challenge #MiNegocioEn15Segundos', prefix=None):
        success_count += 1
        print("🏆 ✅✅✅ CHALLENGE API CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🏆 ❌❌❌ CHALLENGE API FALLÓ AL CARGAR ❌❌❌")
    
    print("=" * 70)
    
    # ==========================================
    # 🔐 ADMIN API (Panel de Administración)
    # ==========================================
    print("\n" + "=" * 70)
    print("🔐🔐🔐 SECCIÓN: ADMIN API (Panel de Administración) 🔐🔐🔐")
    print("=" * 70)
    logger.info("\n🔐 Cargando módulo de administración...")
    
    print("🔐 Endpoints disponibles:")
    print("   → /api/admin/check - Verificar si es admin")
    print("   → /api/admin/list - Listar administradores")
    print("   → /api/admin/add - Agregar admin (superadmin)")
    print("   → /api/admin/remove/<id> - Desactivar admin")
    print("   → /api/admin/challenges - CRUD challenges")
    print("   → /api/admin/participaciones - Gestionar participaciones")
    print("   → /api/admin/stats - Estadísticas generales")
    
    if safe_register('src.api.admin_api', 'admin_bp', 'Admin API', prefix=None):
        success_count += 1
        print("🔐 ✅✅✅ ADMIN API CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🔐 ❌❌❌ ADMIN API FALLÓ AL CARGAR ❌❌❌")
    
    print("=" * 70)
    
    # ==========================================
    # 🎛️ FEATURE FLAGS + PLANES API
    # ==========================================
    print("\n" + "=" * 70)
    print("🎛️🎛️🎛️ SECCIÓN: FEATURE FLAGS + PLANES API 🎛️🎛️🎛️")
    print("=" * 70)
    logger.info("\n🎛️ Cargando módulo de Feature Flags y Planes de Suscripción...")
    
    print("🎛️ Endpoints disponibles:")
    print("   → GET    /api/admin/features - Listar features")
    print("   → PUT    /api/admin/features/<id>/toggle - Toggle feature")
    print("   → PUT    /api/admin/features/<id> - Editar feature")
    print("   → POST   /api/admin/features - Crear feature")
    print("   → GET    /api/admin/planes - Listar planes")
    print("   → PUT    /api/admin/planes/<id>/features - Actualizar features de plan")
    print("   → PUT    /api/admin/negocios/<id>/plan - Asignar plan a negocio")
    print("   → GET    /api/admin/negocios/planes - Listar negocios con plan")
    print("   → GET    /api/features/my - Features del negocio actual")
    print("   → GET    /api/features/check/<key> - Verificar acceso a feature")
    print("   → GET    /api/planes - Listar planes públicos")
    
    if safe_register('src.api.admin_features_api', 'admin_features_bp', 'Feature Flags + Planes API', prefix=None):
        success_count += 1
        print("🎛️ ✅✅✅ FEATURE FLAGS + PLANES API CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🎛️ ❌❌❌ FEATURE FLAGS + PLANES API FALLÓ AL CARGAR ❌❌❌")
        logger.warning("⚠️  Módulo de Feature Flags no cargado")
    
    print("=" * 70)
    
    # ==========================================
    # 📊 CONTRATOS ADMIN API (Fase 0.5 - Métricas)
    # ==========================================
    print("\n" + "=" * 70)
    print("📊📊📊 SECCIÓN: CONTRATOS ADMIN API (Fase 0.5) 📊📊📊")
    print("=" * 70)
    logger.info("\n📊 Cargando módulo de contratos admin para métricas...")
    
    print("📊 Endpoints disponibles:")
    print("   → POST   /api/admin/contratos - Crear contrato")
    print("   → GET    /api/admin/contratos - Listar contratos")
    print("   → GET    /api/admin/contratos/<id> - Obtener contrato")
    print("   → PUT    /api/admin/contratos/<id> - Actualizar contrato")
    print("   → DELETE /api/admin/contratos/<id> - Eliminar contrato")
    print("   → GET    /api/admin/contratos/estadisticas/<negocio_id> - Stats")
    print("   → POST   /api/admin/contratos/seed/<negocio_id> - Crear datos prueba")
    
    if safe_register('src.api.utils.contratos_admin_api', 'contratos_admin_api', 'Contratos Admin API', prefix='/api/admin/contratos'):
        success_count += 1
        print("📊 ✅✅✅ CONTRATOS ADMIN API CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("📊 ❌❌❌ CONTRATOS ADMIN API FALLÓ AL CARGAR ❌❌❌")
    
    print("=" * 70)
    
    # ==========================================
    # 🎖️ BADGE VERIFICATION SERVICE (Fase 0.5 - Auto-badges)
    # ==========================================
    print("\n" + "=" * 70)
    print("🎖️🎖️🎖️ SECCIÓN: BADGE VERIFICATION SERVICE (Fase 0.5) 🎖️🎖️🎖️")
    print("=" * 70)
    logger.info("\n🎖️ Cargando módulo de verificación automática de badges...")
    
    print("🎖️ Endpoints disponibles:")
    print("   → GET  /api/admin/badges/verificar/<negocio_id> - Verificar badges")
    print("   → POST /api/admin/badges/verificar-todos - Verificar todos")
    print("   → GET  /api/admin/badges/status/<negocio_id> - Estado badges")
    
    if safe_register('src.api.utils.badge_verification_service', 'badge_verification_bp', 'Badge Verification Service', prefix='/api/admin/badges'):
        success_count += 1
        print("🎖️ ✅✅✅ BADGE VERIFICATION SERVICE CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🎖️ ❌❌❌ BADGE VERIFICATION SERVICE FALLÓ AL CARGAR ❌❌❌")
    
    print("=" * 70)
    # ==========================================
    # 🔧 MECALINK - Mecánicos a Domicilio
    # ==========================================
    print("\n" + "=" * 70)
    print("🔧🔧🔧 SECCIÓN: MECALINK - Mecánicos a Domicilio 🔧🔧🔧")
    print("=" * 70)
    logger.info("\n🔧 Cargando módulo MecaLink...")
    
    print("🔧 Endpoints disponibles:")
    print("   → GET  /api/mecalink/health - Health check")
    print("   → GET  /api/mecalink/servicios - Lista de servicios")
    print("   → GET  /api/mecalink/buscar - Buscar mecánicos por ciudad/zona/servicio")
    print("   → GET  /api/mecalink/perfil/<id> - Perfil público de mecánico")
    print("   → GET  /api/mecalink/perfil/slug/<slug> - Perfil por slug del negocio")
    print("   → GET  /api/mecalink/mi-perfil - Mi perfil (auth)")
    print("   → PUT  /api/mecalink/mi-perfil - Actualizar mi perfil (auth)")
    print("   → GET  /api/mecalink/mis-estadisticas - Dashboard del mecánico (auth)")
    print("   → POST /api/mecalink/calificar/<id> - Calificar mecánico (auth)")
    print("   → GET  /api/mecalink/admin/pendientes - Listar pendientes (admin)")
    print("   → POST /api/mecalink/admin/verificar/<id> - Verificar mecánico (admin)")
    print("   → POST /api/mecalink/admin/suspender/<id> - Suspender mecánico (admin)")
    
    if safe_register('src.api.mecalink.mecalink_api', 'mecalink_bp', 'MecaLink - Mecánicos a Domicilio', prefix='/api/mecalink'):
        success_count += 1
        print("🔧 ✅✅✅ MECALINK API CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🔧 ❌❌❌ MECALINK API FALLÓ AL CARGAR ❌❌❌")
        logger.warning("⚠️  Módulo MecaLink no cargado - Verifica que existe src/api/mecalink/mecalink_api.py")
    
    print("=" * 70)
    

    # ==========================================
    # 🛍️ DROPSHIPPING - Mastershop / Dropi
    # ==========================================
    print("\n" + "=" * 70)
    print("🛍️🛍️🛍️ SECCIÓN: DROPSHIPPING MULTI-PROVEEDOR 🛍️🛍️🛍️")
    print("=" * 70)
    logger.info("\n🛍️ Cargando módulo de Dropshipping...")
    
    print("🛍️ Endpoints disponibles:")
    print("   → POST /api/dropshipping/importar - Importar CSV/JSON")
    print("   → POST /api/dropshipping/conectar/<proveedor> - Conectar API")
    print("   → POST /api/dropshipping/sincronizar/<proveedor> - Sincronizar")
    print("   → GET  /api/dropshipping/estado - Estado proveedores")
    
    if safe_register('src.api.dropshipping.dropshipping_api', 'dropshipping_bp', 'Dropshipping Multi-Proveedor', prefix='/api'):
        success_count += 1
        print("🛍️ ✅✅✅ DROPSHIPPING API CARGADO EXITOSAMENTE ✅✅✅")
    else:
        fail_count += 1
        print("🛍️ ❌❌❌ DROPSHIPPING API FALLÓ AL CARGAR ❌❌❌")
    
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
    
    # ==========================================
    # 🔍 VERIFICACIÓN DE RUTAS
    # ==========================================
    
    # Rutas de negocios
    logger.info("\n📍 Rutas de negocios registradas:")
    for rule in app.url_map.iter_rules():
        if 'negocio' in rule.rule or 'sucursal' in rule.rule or 'mis_negocios' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Rutas de QR
    print("\n🔲 Verificando rutas de QR Generator v2.0:")
    for rule in app.url_map.iter_rules():
        if '/qr' in rule.rule or '/n/' in rule.rule:
            print(f"   ✅ {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Rutas de Admin
    print("\n🔐 Verificando rutas de Admin API:")
    for rule in app.url_map.iter_rules():
        if '/admin' in rule.rule:
            print(f"   ✅ {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Rutas de Features y Planes
    print("\n🎛️ Verificando rutas de Feature Flags + Planes:")
    features_encontrado = False
    for rule in app.url_map.iter_rules():
        if '/features' in rule.rule or '/planes' in rule.rule:
            print(f"   ✅ ENCONTRADA: {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            features_encontrado = True
    
    if not features_encontrado:
        print("   ❌ NO SE ENCONTRARON RUTAS DE FEATURES/PLANES")
    
    # Rutas de MecaLink
    print("\n🔧 Verificando rutas de MecaLink:")
    mecalink_encontrado = False
    for rule in app.url_map.iter_rules():
        if '/mecalink' in rule.rule:
            print(f"   ✅ {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
            mecalink_encontrado = True
    
    if not mecalink_encontrado:
        print("   ❌ NO SE ENCONTRARON RUTAS DE MECALINK")
    
    # Rutas de compradores y pedidos
    logger.info("\n🛒 Rutas de compradores y pedidos:")
    for rule in app.url_map.iter_rules():
        if 'comprador' in rule.rule or 'pedido' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Rutas de checkout/tiendas
    logger.info("\n🏪 Rutas de checkout/tiendas:")
    for rule in app.url_map.iter_rules():
        if 'tienda' in rule.rule or 'checkout' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Rutas de recuperación
    logger.info("\n🔑 Rutas de recuperación de contraseña:")
    for rule in app.url_map.iter_rules():
        if 'reset' in rule.rule or 'forgot' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Rutas de trayectoria
    logger.info("\n🎯 Rutas de trayectoria:")
    for rule in app.url_map.iter_rules():
        if 'scores' in rule.rule or 'stages' in rule.rule or 'badges' in rule.rule or 'metrics' in rule.rule or 'portfolio' in rule.rule:
            logger.info(f"   → {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    if fail_count > 0:
        logger.warning(f"⚠️  {fail_count} módulo(s) no se cargaron. Revisa los logs.")
        print(f"\n⚠️  {fail_count} módulo(s) no se cargaron. Revisa los logs.")
    else:
        logger.info("🎉 Todos los módulos cargados exitosamente")
        print("\n🎉 Todos los módulos cargados exitosamente")
    
    print("\n" + "=" * 70)
    print("🔌 REGISTER_API: FINALIZADO")
    print("=" * 70)
    print("\n")
    return success_count, fail_count


print("=" * 70)
print("🔌 API __INIT__.PY: MÓDULO CARGADO")
print("=" * 70)