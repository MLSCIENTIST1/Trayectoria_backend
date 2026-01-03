# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import psycopg2
import configparser
import sys
import os

# 1. Instancias globales con SOPORTE PARA RECONEXIÓN
# Añadimos engine_options para evitar el error "SSL connection has been closed unexpectedly"
db = SQLAlchemy(engine_options={
    "pool_pre_ping": True,    # Verifica si la conexión está viva antes de cada consulta
    "pool_recycle": 280,      # Cierra conexiones inactivas antes de que Render/Neon las corte (300s)
    "pool_size": 10,          # Mantiene un grupo base de conexiones
    "max_overflow": 20        # Permite conexiones extra en picos de tráfico
})
migrate = Migrate()

# 2. Función para leer la configuración
def read_config(file_path):
    config = configparser.ConfigParser()
    if not os.path.exists(file_path):
        print(f"❌ ERROR: No se encontró el archivo de configuración en: {file_path}")
        return None
    config.read(file_path, encoding='utf-8')
    return config

# 3. DINÁMICO: Obtener la ruta del archivo database.conf
basedir = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(basedir, 'database.conf')

# 4. Cargar configuración
config = read_config(config_path)

if config:
    host = config['database']['host']
    user = config['database']['user']
    password = config['database']['password']
    database = config['database']['database']
    
    # IMPORTANTE: Aseguramos el esquema postgresql:// y el sslmode=require
    # Neon Cloud requiere sslmode para mantener la estabilidad
    DATABASE_URL = f"postgresql://{user}:{password}@{host}/{database}?sslmode=require"
else:
    # Fallback para variables de entorno (útil en Render si no encuentra el .conf)
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    if not DATABASE_URL:
        print("❌ No se pudo cargar la configuración de la base de datos (.conf o ENV).")
        sys.exit(1)

# 5. Probar conexión inicial
try:
    engine_test = psycopg2.connect(DATABASE_URL)
    print(f"✅ Conexión exitosa a la DB: {host}")
    engine_test.close()
except Exception as e:
    print(f"⚠️ Nota: Prueba de conexión directa falló (pero Flask puede funcionar): {e}")

# 6. Crear la base de datos (Local únicamente)
def create_database():
    if 'localhost' not in host and '127.0.0.1' not in host:
        return

    print("🏠 [LOCAL]: Verificando base de datos local...")
    try:
        conn = psycopg2.connect(
            dbname='postgres', user=user, password=password, host=host
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", [database])
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {database}")
            print(f"✅ Base de datos '{database}' creada.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error en creación local: {e}")

# 7. Inicializar Flask
def init_app(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Vinculación de instancias
    db.init_app(app)
    migrate.init_app(app, db)
    
    print("🚀 Base de datos inicializada con Pool Management (Pre-Ping habilitado).")