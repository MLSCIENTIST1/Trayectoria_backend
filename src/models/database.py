"""
BizFlow Studio - Configuración de Base de Datos
Optimizado para Neon/Render con gestión de conexiones persistentes
"""

import os
import sys
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Configurar logging
logger = logging.getLogger(__name__)

# ==========================================
# INSTANCIAS GLOBALES
# ==========================================
db = SQLAlchemy(
    engine_options={
        "pool_pre_ping": True,      # CRÍTICO: Verifica conexión antes de usar
        "pool_recycle": 280,         # Recicla conexiones antes de timeout de Neon (300s)
        "pool_size": 10,             # Pool base de conexiones
        "max_overflow": 20,          # Conexiones extra en picos
        "pool_timeout": 30,          # Timeout al esperar conexión del pool
        "connect_args": {
            "connect_timeout": 10,   # Timeout de conexión inicial
            "options": "-c statement_timeout=30000"  # 30s timeout para queries
        }
    }
)

migrate = Migrate()

# ==========================================
# OBTENCIÓN DE DATABASE_URL
# ==========================================
def get_database_url():
    """
    Obtiene la URL de la base de datos desde múltiples fuentes.
    Prioridad: ENV > database.conf > Error
    
    Returns:
        str: URL de conexión a PostgreSQL
    """
    # 1. PRIMERA PRIORIDAD: Variable de entorno (Render)
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Convertir postgres:// a postgresql:// (Render legacy)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            logger.info("✅ DATABASE_URL obtenida desde variable de entorno")
        
        # Asegurar que tenga sslmode=require para Neon
        if 'sslmode' not in database_url:
            separator = '&' if '?' in database_url else '?'
            database_url += f'{separator}sslmode=require'
        
        return database_url
    
    # 2. SEGUNDA PRIORIDAD: Archivo database.conf (desarrollo local)
    try:
        import configparser
        basedir = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(basedir, 'database.conf')
        
        if os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.read(config_path, encoding='utf-8')
            
            host = config['database']['host']
            user = config['database']['user']
            password = config['database']['password']
            database = config['database']['database']
            
            database_url = f"postgresql://{user}:{password}@{host}/{database}?sslmode=require"
            logger.info(f"✅ DATABASE_URL obtenida desde database.conf: {host}")
            return database_url
    
    except Exception as e:
        logger.warning(f"⚠️ No se pudo leer database.conf: {e}")
    
    # 3. ERROR: No se encontró configuración
    logger.error("❌ No se pudo obtener DATABASE_URL desde ENV ni database.conf")
    logger.error("   Asegúrate de tener la variable DATABASE_URL configurada en Render")
    sys.exit(1)

# Obtener URL una sola vez al importar
DATABASE_URL = get_database_url()

# ==========================================
# INICIALIZACIÓN DE FLASK
# ==========================================
def init_app(app):
    """
    Inicializa SQLAlchemy y Flask-Migrate en la aplicación.
    
    Args:
        app: Instancia de Flask
    """
    # Configurar URI de base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = app.debug  # Solo logs SQL en debug
    
    # Configuración adicional para sesiones en DB
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = db.engine_options
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    logger.info("✅ SQLAlchemy inicializado con pool management")
    logger.info(f"   - Pool size: {db.engine_options['pool_size']}")
    logger.info(f"   - Max overflow: {db.engine_options['max_overflow']}")
    logger.info(f"   - Pool pre-ping: {db.engine_options['pool_pre_ping']}")
    
    # Probar conexión
    with app.app_context():
        try:
            db.engine.connect()
            logger.info("✅ Conexión a base de datos verificada")
        except Exception as e:
            logger.error(f"❌ Error al conectar con la base de datos: {e}")
            raise

# ==========================================
# UTILIDADES DE BASE DE DATOS
# ==========================================
def create_tables(app):
    """
    Crea todas las tablas definidas en los modelos.
    Solo usar en desarrollo o primera inicialización.
    
    Args:
        app: Instancia de Flask
    """
    with app.app_context():
        try:
            db.create_all()
            logger.info("✅ Tablas creadas/verificadas en la base de datos")
        except Exception as e:
            logger.error(f"❌ Error al crear tablas: {e}")
            raise

def drop_all_tables(app):
    """
    PELIGRO: Elimina todas las tablas.
    Solo usar en desarrollo.
    
    Args:
        app: Instancia de Flask
    """
    if not app.debug:
        raise RuntimeError("⛔ drop_all_tables solo puede ejecutarse en modo DEBUG")
    
    with app.app_context():
        logger.warning("⚠️ ELIMINANDO TODAS LAS TABLAS...")
        db.drop_all()
        logger.warning("✅ Todas las tablas eliminadas")

def reset_database(app):
    """
    PELIGRO: Elimina y recrea todas las tablas.
    Solo usar en desarrollo.
    
    Args:
        app: Instancia de Flask
    """
    if not app.debug:
        raise RuntimeError("⛔ reset_database solo puede ejecutarse en modo DEBUG")
    
    drop_all_tables(app)
    create_tables(app)
    logger.info("✅ Base de datos reiniciada")

# ==========================================
# HEALTH CHECK
# ==========================================
def check_database_health():
    """
    Verifica el estado de la conexión a la base de datos.
    
    Returns:
        dict: Estado de la conexión
    """
    try:
        # Ejecutar query simple
        db.session.execute('SELECT 1')
        
        # Obtener info del pool
        pool = db.engine.pool
        
        return {
            "status": "healthy",
            "connection": "active",
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "checked_in": pool.checkedin()
        }
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }