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
BizFlow Studio - Configuración de Base de Datos
Optimizado para Neon/Render con gestión de conexiones persistentes
"""

import os
import sys
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text

# Configurar logging
logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURACIÓN DE ENGINE OPTIONS
# ==========================================
# Definir opciones una sola vez para reutilizar
ENGINE_OPTIONS = {
    "pool_pre_ping": True,          # CRÍTICO: Verifica conexión antes de usar
    "pool_recycle": 280,            # Recicla conexiones antes de timeout de Neon (300s)
    "pool_size": 10,                # Pool base de conexiones
    "max_overflow": 20,             # Conexiones extra en picos
    "pool_timeout": 30,             # Timeout al esperar conexión del pool
    "connect_args": {
        "connect_timeout": 10,      # Timeout de conexión inicial
        "options": "-c statement_timeout=30000"  # 30s timeout para queries
    }
}

# ==========================================
# INSTANCIAS GLOBALES
# ==========================================
db = SQLAlchemy(engine_options=ENGINE_OPTIONS)
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
    
    # NOTA: Las engine_options ya se configuraron en el constructor de SQLAlchemy
    # No es necesario (ni posible) asignarlas de nuevo aquí
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    logger.info("✅ SQLAlchemy inicializado con pool management")
    logger.info(f"   - Pool size: {ENGINE_OPTIONS['pool_size']}")
    logger.info(f"   - Max overflow: {ENGINE_OPTIONS['max_overflow']}")
    logger.info(f"   - Pool pre-ping: {ENGINE_OPTIONS['pool_pre_ping']}")
    
    # Probar conexión
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text('SELECT 1'))
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
        db.session.execute(text('SELECT 1'))
        
        # Obtener info del pool (si está disponible)
        try:
            pool = db.engine.pool
            pool_info = {
                "pool_size": pool.size(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "checked_in": pool.checkedin()
            }
        except Exception:
            pool_info = {"pool_info": "not available"}
        
        return {
            "status": "healthy",
            "connection": "active",
            **pool_info
        }
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }