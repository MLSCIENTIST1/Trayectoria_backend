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
BizFlow Studio - Lanzador Principal
Optimizado para Render con diagnóstico de rutas
"""

import logging
import os
import sys
from src import create_app

# ==========================================
# CONFIGURACIÓN DE LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,  # Cambié a INFO para reducir ruido en producción
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# INICIALIZACIÓN
# ==========================================
logger.info("="*70)
logger.info("🚀 INICIANDO BIZFLOW STUDIO")
logger.info("="*70)

app = None

try:
    # Crear la aplicación
    app = create_app()

    if app:
        logger.info("✅ Aplicación creada exitosamente")

        # ==========================================
        # MIGRACIONES AUTOMÁTICAS AL ARRANCAR
        # ==========================================
        try:
            from flask_migrate import upgrade as db_upgrade
            with app.app_context():
                logger.info("🔄 Ejecutando migraciones pendientes...")
                db_upgrade()
                logger.info("✅ Migraciones aplicadas correctamente")
        except Exception as mig_err:
            logger.warning(f"⚠️  No se pudieron aplicar migraciones: {mig_err}")
            # No detenemos la app — podría ser que ya estén aplicadas

        # ==========================================
        # VERIFICACIÓN Y REPARACIÓN DE COLUMNAS CRÍTICAS
        # Cubre el caso en que alembic_version marcó la migración a1b2c3d4e5f6
        # como "aplicada" usando la tabla incorrecta ('negocio' en lugar de 'negocios')
        # y la columna tipo_pagina nunca fue creada realmente.
        # ==========================================
        try:
            from sqlalchemy import text as _sql_text
            with app.app_context():
                from src.models.database import db as _db
                conn = _db.engine.connect()

                # Verificar qué columnas faltan en 'negocios'
                _columnas_criticas = {
                    "tipo_pagina":    "VARCHAR(50)",
                    "whatsapp":       "VARCHAR(20)",
                    "logo_url":       "TEXT",
                    "config_tienda":  "JSONB DEFAULT '{}'",
                    "qr_negocio_url": "TEXT",
                    "qr_negocio_data":"VARCHAR(300)",
                    "perfil_publico": "BOOLEAN DEFAULT TRUE NOT NULL",
                }

                _check = _sql_text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'negocios'
                      AND column_name = ANY(:cols)
                """)
                _existentes = {
                    row[0] for row in conn.execute(
                        _check, {"cols": list(_columnas_criticas.keys())}
                    )
                }

                _creadas = []
                for col, defn in _columnas_criticas.items():
                    if col not in _existentes:
                        _alter = f"ALTER TABLE negocios ADD COLUMN IF NOT EXISTS {col} {defn}"
                        conn.execute(_sql_text(_alter))
                        _creadas.append(col)
                        logger.warning(f"⚠️  Columna faltante creada: negocios.{col}")

                if _creadas:
                    conn.execute(_sql_text(
                        "UPDATE negocios SET tipo_pagina = NULL WHERE tipo_pagina = 'landing'"
                    ))
                    conn.commit()
                    logger.warning(f"🔧 Columnas reparadas: {_creadas}")
                else:
                    conn.commit()
                    logger.info("✅ Todas las columnas críticas de 'negocios' existen")

                conn.close()
        except Exception as col_err:
            logger.warning(f"⚠️  No se pudo verificar columnas: {col_err}")

        # ==========================================
        # INSPECTOR DE RUTAS
        # ==========================================
        with app.app_context():
            logger.info("\n" + "="*70)
            logger.info("🔍 MAPA DE RUTAS REGISTRADAS:")
            logger.info("="*70)
            
            routes_by_prefix = {}
            
            # Agrupar rutas por prefijo para mejor visualización
            for rule in app.url_map.iter_rules():
                if "static" not in rule.endpoint:
                    prefix = str(rule).split('/')[1] if len(str(rule).split('/')) > 1 else 'root'
                    
                    if prefix not in routes_by_prefix:
                        routes_by_prefix[prefix] = []
                    
                    routes_by_prefix[prefix].append({
                        'path': str(rule),
                        'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'})),
                        'endpoint': rule.endpoint
                    })
            
            # Imprimir rutas agrupadas
            for prefix, routes in sorted(routes_by_prefix.items()):
                logger.info(f"\n📁 /{prefix}/")
                for route in sorted(routes, key=lambda x: x['path']):
                    methods_str = ','.join(route['methods'])
                    logger.info(f"   [{methods_str:20}] {route['path']:50} → {route['endpoint']}")
            
            logger.info("="*70 + "\n")
            
            # Contar rutas por tipo
            total_routes = sum(len(routes) for routes in routes_by_prefix.values())
            logger.info(f"📊 Total de rutas registradas: {total_routes}")
            
            # Verificar rutas críticas
            critical_routes = [
                '/api/auth/login',
                '/api/auth/logout',
                '/api/auth/session/verify',
                '/health'
            ]
            
            all_paths = [route['path'] for routes in routes_by_prefix.values() for route in routes]
            missing_routes = [route for route in critical_routes if route not in all_paths]
            
            if missing_routes:
                logger.warning(f"⚠️  Rutas críticas faltantes: {missing_routes}")
            else:
                logger.info("✅ Todas las rutas críticas están registradas")
    
    else:
        logger.error("❌ La factoría create_app() devolvió None")
        sys.exit(1)

except Exception as e:
    logger.error(f"❌ Error crítico al inicializar la aplicación:", exc_info=True)
    sys.exit(1)

# ==========================================
# RUTAS BASE (Ya no necesarias si están en __init__.py)
# ==========================================
# Las rutas /health ya están en __init__.py, no duplicar

# ==========================================
# PUNTO DE ENTRADA
# ==========================================
if __name__ == "__main__":
    if app:
        # Render asigna el puerto mediante PORT
        port = int(os.environ.get("PORT", 5000))
        debug = os.environ.get("FLASK_ENV") != "production"
        
        logger.info("="*70)
        logger.info(f"🌐 Servidor iniciando en puerto: {port}")
        logger.info(f"🔧 Modo debug: {'ACTIVADO' if debug else 'DESACTIVADO'}")
        logger.info(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'development')}")
        logger.info("="*70 + "\n")
        
        # IMPORTANTE: En producción con Render, usa gunicorn, no esto
        # Este run() solo se usa en desarrollo local
        if debug:
            logger.info("⚠️  Ejecutando en modo desarrollo (Flask built-in server)")
            app.run(host='0.0.0.0', port=port, debug=True)
        else:
            logger.info("✅ Aplicación lista para Gunicorn")
            # Gunicorn tomará el control aquí
    else:
        logger.error("❌ No se pudo levantar la aplicación")
        sys.exit(1)