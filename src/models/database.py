# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import psycopg2
import configparser
import sys
import os

# 1. Instancias globales
db = SQLAlchemy()
migrate = Migrate()

# 2. Función para leer la configuración
def read_config(file_path):
    config = configparser.ConfigParser()
    if not os.path.exists(file_path):
        print(f"❌ ERROR: No se encontró el archivo de configuración en: {file_path}")
        return None
    config.read(file_path, encoding='utf-8')
    return config

# 3. DINÁMICO: Obtener la ruta del archivo database.conf en la carpeta actual
basedir = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(basedir, 'database.conf')

# 4. Cargar configuración
config = read_config(config_path)

if config:
    host = config['database']['host']
    user = config['database']['user']
    password = config['database']['password']
    database = config['database']['database']
    
    # IMPORTANTE: Agregamos sslmode=require para Neon Cloud
    DATABASE_URL = f"postgresql://{user}:{password}@{host}/{database}?sslmode=require"
else:
    print("❌ No se pudo cargar la configuración de la base de datos.")
    sys.exit(1)

# 5. Probar conexión inicial (Opcional pero útil)
try:
    # Usamos la URL completa con SSL para la prueba
    engine = psycopg2.connect(DATABASE_URL)
    print(f"✅ Conexión exitosa a Neon: {host}")
    engine.close()
except Exception as e:
    print(f"⚠️ Nota: No se pudo conectar vía psycopg2 directamente: {e}")

# 6. Crear la base de datos (Solo para Local, en Neon suele dar error de permisos)
def create_database():
    if 'localhost' not in host and '127.0.0.1' not in host:
        print("☁️ [INFO]: Saltando creación de DB (Estás en la nube de Neon).")
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
    db.init_app(app)
    migrate.init_app(app, db)
    print("🚀 Base de datos y migraciones configuradas correctamente.")