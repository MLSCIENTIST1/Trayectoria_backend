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
BizFlow Studio - Inicialización de Aplicación Flask
Backend: Render | Frontend: Firebase
Versión CORREGIDA - Imports arreglados
+ AGREGADO: Sistema de recuperación de contraseñas con Flask-Mail
+ CORREGIDO: Configuración SMTP para Namecheap Private Email
"""

from flask import Flask, jsonify, request
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_session import Session
from datetime import timedelta
import os
import sys
import logging

# Importaciones internas
from src.models.database import db, init_app
from src.api import register_api 
from llenar_colombia import poblar_ciudades 

# --- IMPORTACIÓN DE MODELOS (VITAL PARA SQLALCHEMY / NEON) ---
from src.models.usuarios import Usuario
from src.models.etapa import Etapa
from src.models.foto import Foto
from src.models.audio import Audio
from src.models.video import Video
from src.models.colombia_data.colombia_data import Colombia
from src.models.colombia_data.colombia_feedbacks import Feedback
from src.models.colombia_data.monetization_management import MonetizationManagement
from src.models.colombia_data.ratings.service_overall_scores import ServiceOverallScores
from src.models.colombia_data.ratings.service_qualifiers import ServiceQualifiers
from src.models.colombia_data.ratings.service_ratings import ServiceRatings
from src.models.colombia_data.negocio import Negocio 
from src.models.colombia_data.sucursales import Sucursal 

# CORREGIDO: Import de Servicio desde ubicación correcta
from src.models.servicio import Servicio

# CORREGIDO: Import desde contabilidad (NO catalogo)
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import (
    ProductoCatalogo,
    TransaccionOperativa,
    AlertaOperativa
)

# ==========================================
# NUEVO: Import del modelo de Password Reset
# ==========================================
from src.models.password_reset_token import PasswordResetToken
# ==========================================
# NUEVO: Imports de Modelos de Trayectoria
# ==========================================
from src.models.trayectoria.user_score import UserScore
from src.models.trayectoria.user_score_history import UserScoreHistory
from src.models.trayectoria.user_stage_score import UserStageScore
from src.models.trayectoria.badge import Badge
from src.models.trayectoria.user_badge import UserBadge
from src.models.trayectoria.user_metric import UserMetric
from src.models.trayectoria.portfolio_video import PortfolioVideo

# 🎮 Gamificación v1.0
from src.models.colombia_data.ratings.negocio_gamificacion import (
    NegocioGamificacion,
    NegocioMisionCompletada,
    TuKoinTransaccion,
    TiendaItem,
    TiendaCompra,
)

# 🔧 Vertical Taller v1.0
from src.models.taller.orden_trabajo import (
    OrdenTrabajo,
    ItemOrdenTrabajo,
    CitaTaller,
)

# 🍽️ Vertical Restaurante v1.0
from src.models.restaurante.restaurante import (
    Mesa,
    Comanda,
    ItemComanda,
)
from src.models.leads.lead import LeadCampana, PlantillaMensaje

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)


class Config:
    """Configuración centralizada de la aplicación"""
    
    # ==========================================
    # SEGURIDAD
    # ==========================================
    SECRET_KEY = os.environ.get('SECRET_KEY', 'bizflow_studio_2026_key_CAMBIAR_EN_PRODUCCION')
    
    # ==========================================
    # BASE DE DATOS
    # ==========================================
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10,
        }
    }
    
    # Compatibilidad Neon/Render
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    # ==========================================
    # SESIONES (CRÍTICO PARA CROSS-DOMAIN)
    # ==========================================
    SESSION_TYPE = 'sqlalchemy'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Configuración de cookies para Firebase (frontend) + Render (backend)
    SESSION_COOKIE_NAME = 'bizflow_session'
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = '/'
    
    # Flask-Login cookies
    REMEMBER_COOKIE_NAME = 'bizflow_remember'
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_SAMESITE = 'None'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DOMAIN = None
    
    # ==========================================
    # CORS (CRÍTICO)
    # ==========================================
    CORS_ORIGINS = [
        "https://trayectoria-rxdc1.web.app",
        "https://mitrayectoria.web.app",
        "https://tuko.pages.dev",
        "http://localhost:5001",
        "http://localhost:5173",
        "http://localhost:3000"
    ]
    
    # ==========================================
    # CONFIGURACIÓN DE EMAIL (NAMECHEAP PRIVATE EMAIL)
    # ==========================================
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'mail.privateemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'noreply@tukomercio.store')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('TuKomercio', os.environ.get('MAIL_FROM', 'noreply@tukomercio.store'))
    MAIL_TIMEOUT = 10
    
    # URL del frontend para links en emails
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://trayectoria-rxdc1.web.app')


def create_app():
    """
    Factory pattern para crear la aplicación Flask
    con configuración optimizada para Render + Firebase
    """
    logger.info("🚀 Iniciando BizFlow Studio Factory")
    
    # ==========================================
    # INICIALIZACIÓN DE FLASK
    # ==========================================
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    app = Flask(
        __name__, 
        instance_relative_config=False,
        root_path=base_dir, 
        template_folder='templates',
        static_folder='static'
    )
    
    app.config.from_object(Config)
    
    # ==========================================
    # CORS (DEBE SER LO PRIMERO)
    # ==========================================
    CORS(app, 
         resources={r"/*": {
             "origins": Config.CORS_ORIGINS,
             "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization", "Accept", "X-User-ID", "X-Business-ID", "X-Session-FP", "Cache-Control", "Pragma"],
             "expose_headers": ["Content-Type", "Set-Cookie"],
             "supports_credentials": True,
             "max_age": 3600
         }}
    )
    logger.info("✅ CORS configurado con soporte de credenciales")
    
    # ==========================================
    # BASE DE DATOS
    # ==========================================
    init_app(app)
    migrate = Migrate(app, db)
    logger.info("✅ Base de datos inicializada")
    
    # ==========================================
    # FLASK-MAIL (PARA RESET DE PASSWORD)
    # ==========================================
    from src.api.auth.password_reset_api import init_mail
    init_mail(app)
    logger.info("✅ Flask-Mail inicializado para Namecheap Private Email")
    
    # ==========================================
    # SESIONES (CRÍTICO)
    # ==========================================
    app.config['SESSION_SQLALCHEMY'] = db
    session_manager = Session()
    session_manager.init_app(app)
    logger.info("✅ Sistema de sesiones configurado")
    
    # ==========================================
    # FLASK-LOGIN
    # ==========================================
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'auth_system.login'
    
    @login_manager.unauthorized_handler
    def unauthorized():
        logger.warning("❌ Intento de acceso no autorizado")
        return jsonify({
            "error": "unauthorized", 
            "message": "Sesión expirada o no iniciada",
            "redirect": "/login.html"
        }), 401
    
    @login_manager.user_loader
    def load_user(id_usuario):
        try:
            user = db.session.get(Usuario, int(id_usuario))
            if user and user.active:
                return user
            logger.warning(f"Usuario {id_usuario} no encontrado o inactivo")
            return None
        except Exception as e:
            logger.error(f"Error cargando usuario {id_usuario}: {str(e)}")
            return None
    
    logger.info("✅ Flask-Login configurado")
    
    # ==========================================
    # MIDDLEWARE DE SEGURIDAD
    # ==========================================
    @app.before_request
    def before_request():
        from flask import session
        from flask_login import current_user
        
        if current_user.is_authenticated:
            session.modified = True
    
    @app.after_request
    def after_request(response):
        # CORS credentials ya manejado por Flask-CORS (supports_credentials=True)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        if '/auth/' in request.path or '/ingreso' in request.path or '/logout' in request.path:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
        
        return response
    
    logger.info("✅ Middleware de seguridad configurado")
    
    # ==========================================
    # INICIALIZACIÓN DE BASE DE DATOS
    # ==========================================
    with app.app_context():
        try:
            db.create_all()
            logger.info("✅ Estructura de base de datos verificada en Neon")

            # ==========================================
            # MIGRACIONES AUTOMÁTICAS DE COLUMNAS NUEVAS
            # ADD COLUMN IF NOT EXISTS — seguro en Neon/PostgreSQL
            # ==========================================
            try:
                from sqlalchemy import text
                migraciones = [
                    # Dropshipping en catálogo de productos
                    "ALTER TABLE productos_catalogo ADD COLUMN IF NOT EXISTS es_dropshipping BOOLEAN NOT NULL DEFAULT FALSE",
                    # Anulación en transacciones operativas
                    "ALTER TABLE transacciones_operativas ADD COLUMN IF NOT EXISTS anulada BOOLEAN NOT NULL DEFAULT FALSE",
                    "ALTER TABLE transacciones_operativas ADD COLUMN IF NOT EXISTS motivo_anulacion VARCHAR(255)",
                    # pedido_id nullable en devoluciones (para devoluciones libres)
                    "ALTER TABLE devoluciones ALTER COLUMN pedido_id DROP NOT NULL",
                    # ── Carritos abandonados v1.0 ──────────────────────────────────────────
                    """CREATE TABLE IF NOT EXISTS carritos_abandonados (
                        id          SERIAL PRIMARY KEY,
                        negocio_id  INTEGER NOT NULL REFERENCES negocios(id_negocio) ON DELETE CASCADE,
                        telefono    VARCHAR(25) NOT NULL,
                        nombre      VARCHAR(120),
                        correo      VARCHAR(150),
                        productos   JSONB DEFAULT '[]',
                        total_estimado NUMERIC(12,2) DEFAULT 0,
                        num_items   INTEGER DEFAULT 0,
                        estado      VARCHAR(20) NOT NULL DEFAULT 'abandonado',
                        pedido_id   INTEGER,
                        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at  TIMESTAMPTZ DEFAULT NOW(),
                        CONSTRAINT uq_carrito_negocio_tel UNIQUE (negocio_id, telefono)
                    )""",
                    "CREATE INDEX IF NOT EXISTS ix_carritos_negocio ON carritos_abandonados(negocio_id)",
                    "CREATE INDEX IF NOT EXISTS ix_carritos_estado  ON carritos_abandonados(estado)",
                    # ── Configuración de envíos por negocio v2.7 ──────────────────────────
                    "ALTER TABLE negocios ADD COLUMN IF NOT EXISTS config_envios JSONB DEFAULT '{}'",
                    # ── Variantes de producto v2.5 ─────────────────────────────────────────
                    "ALTER TABLE productos_catalogo ADD COLUMN IF NOT EXISTS variantes TEXT DEFAULT NULL",
                    # ── Sistema de planes / suscripciones v3.0 ────────────────────────────
                    "ALTER TABLE negocios ADD COLUMN IF NOT EXISTS plan_key VARCHAR(50) DEFAULT 'basic'",
                    "ALTER TABLE negocios ADD COLUMN IF NOT EXISTS plan_actual_id INTEGER REFERENCES planes(id) ON DELETE SET NULL",
                    "CREATE INDEX IF NOT EXISTS ix_negocios_plan_key ON negocios(plan_key)",
                ]
                for sql in migraciones:
                    try:
                        db.session.execute(text(sql))
                        db.session.commit()
                    except Exception as col_err:
                        db.session.rollback()
                        logger.debug(f"Migración omitida (ya aplicada o no aplica): {col_err}")
                logger.info("✅ Migraciones automáticas de columnas aplicadas")
            except Exception as mig_err:
                logger.warning(f"⚠️  Error en bloque de migraciones automáticas: {mig_err}")

            # ──────────────────────────────────────────────────────────────────
            # SEED: Feature Flags faltantes en BD
            # INSERT ... ON CONFLICT (key) DO NOTHING — seguro si ya existen
            # ──────────────────────────────────────────────────────────────────
            try:
                from sqlalchemy import text as _text
                nuevas_features = [
                    # Sprint 3
                    ("pedidos_compradores", "Gestión de Compradores",
                     "CRUD de compradores. Magic Links sin contraseña. Múltiples direcciones. Conversión a usuario completo. CRM de historial de compras.", "pedidos", 55),
                    ("pedidos_devoluciones", "Módulo de Devoluciones",
                     "Devolución asociada a pedido o libre. Devuelve stock automáticamente. Con motivo y registro en historial. Devolución libre para casos sin pedido previo.", "pedidos", 56),
                    # Sprint 4
                    ("tienda_email_comprador", "Email automático al comprador",
                     "Al completarse el checkout el comprador recibe confirmación con resumen del pedido y link a Heyden. Solo si tiene correo. Fire-and-forget en background thread.", "tienda", 57),
                    ("tienda_pwa", "PWA — Tienda instalable como app",
                     "manifest.json dinámico por negocio. Service Worker con cache-first para assets. Botón Instalar app con beforeinstallprompt. API nunca interceptada.", "tienda", 58),
                    ("tienda_seo_og", "SEO — og:tags dinámicos por tienda",
                     "og:title, og:description, og:image actualizados con datos del negocio. Mejora previsualización en WhatsApp, Facebook y Twitter.", "tienda", 59),
                    # v2.5
                    ("inv_variantes", "Inventario — Variantes de producto",
                     "Define dimensiones del producto (Talla, Color, Material) con sus opciones. El comprador selecciona combinación antes de agregar al carrito. Variantes distintas son ítems independientes.", "catalogo", 60),
                ]
                for _key, _nombre, _desc, _cat, _orden in nuevas_features:
                    db.session.execute(_text("""
                        INSERT INTO feature_flags
                            (key, nombre, descripcion, categoria, activo_global, visible, orden, created_at, updated_at)
                        VALUES
                            (:key, :nombre, :desc, :cat, true, true, :orden, NOW(), NOW())
                        ON CONFLICT (key) DO NOTHING
                    """), {"key": _key, "nombre": _nombre, "desc": _desc, "cat": _cat, "orden": _orden})
                db.session.commit()
                logger.info("✅ Seed de feature flags nuevas aplicado")
            except Exception as seed_err:
                db.session.rollback()
                logger.warning(f"⚠️  Error en seed de feature flags: {seed_err}")

            # ==========================================
            # INICIALIZAR BADGES DE TRAYECTORIA (AUTOMÁTICO)
            # ==========================================
            try:
                from src.models.trayectoria.badge import Badge
                
                # Verificar si ya existen badges
                if Badge.query.count() == 0:
                    logger.info("🏆 Inicializando catálogo de badges de trayectoria...")
                    badges_creados = Badge.inicializar_badges_sistema()
                    logger.info(f"✅ {badges_creados} badges de trayectoria creados")
                else:
                    logger.info(f"ℹ️  Badges de trayectoria ya inicializados ({Badge.query.count()} badges)")
            except Exception as e:
                logger.warning(f"⚠️  Error inicializando badges de trayectoria: {e}")
            
            # ==========================================
            # POBLAR DATOS DE COLOMBIA
            # ==========================================
            try:
                inspector = db.inspect(db.engine)
                if 'colombia' in inspector.get_table_names():
                    if Colombia.query.first() is None:
                        logger.info("⚠️  Tabla 'colombia' vacía. Poblando...")
                        poblar_ciudades()
                        logger.info("✅ Datos de Colombia poblados")
            except Exception as e:
                logger.warning(f"⚠️  No se pudo poblar datos de Colombia: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error al crear tablas: {e}")
            try:
                db.session.rollback()
            except Exception:
                pass
    
    # ==========================================
    # REGISTRO DE BLUEPRINTS
    # ==========================================
    register_api(app)
    logger.info("✅ Blueprints registrados")
    
    # ==========================================
    # CONFIGURACIÓN DE DIRECTORIO DE UPLOADS
    # ==========================================
    upload_folder = os.path.join(base_dir, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        logger.info(f"✅ Directorio de uploads creado: {upload_folder}")
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    # ==========================================
    # ENDPOINTS DE SALUD Y DIAGNÓSTICO
    # ==========================================
    @app.route('/health', methods=['GET'])
    def health_check():
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = "connected"
        except Exception as e:
            logger.error(f"Error en health check DB: {e}")
            db_status = "disconnected"
        
        return jsonify({
            "status": "healthy",
            "database": db_status,
            "version": "2.1.0",
            "environment": "production" if not app.debug else "development"
        }), 200
    
    @app.route('/api/session-debug', methods=['GET'])
    def session_debug():
        from flask import session
        from flask_login import current_user
        
        if app.debug:
            return jsonify({
                "session_data": dict(session),
                "authenticated": current_user.is_authenticated,
                "user_id": current_user.get_id() if current_user.is_authenticated else None,
                "cookie_config": {
                    "SESSION_COOKIE_SAMESITE": app.config.get('SESSION_COOKIE_SAMESITE'),
                    "SESSION_COOKIE_SECURE": app.config.get('SESSION_COOKIE_SECURE'),
                    "SESSION_COOKIE_HTTPONLY": app.config.get('SESSION_COOKIE_HTTPONLY')
                }
            }), 200
        else:
            return jsonify({"error": "Not available in production"}), 403
    
    # ==========================================
    # MANEJO DE ERRORES
    # ==========================================
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 Not Found: {request.path}")
        return jsonify({"error": "Endpoint no encontrado"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Internal Error: {str(error)}")
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500
    
    logger.info("🎉 BizFlow Studio inicializado correctamente")
    return app