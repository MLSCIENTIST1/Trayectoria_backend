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
        # REPARACIÓN COLUMNA CRÍTICA: movimientos_stock.transaccion_id
        # La migración c3d4e5f6a7b2 agrega esta columna, pero si Alembic
        # falla silenciosamente en Render, el INSERT de venta manual explota
        # con "column transaccion_id does not exist".
        # ==========================================
        try:
            from sqlalchemy import text as _sql_text2
            with app.app_context():
                from src.models.database import db as _db2
                conn2 = _db2.engine.connect()

                _check2 = _sql_text2("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'movimientos_stock'
                      AND column_name = 'transaccion_id'
                """)
                _existe_transaccion_id = conn2.execute(_check2).fetchone()

                if not _existe_transaccion_id:
                    conn2.execute(_sql_text2(
                        "ALTER TABLE movimientos_stock "
                        "ADD COLUMN IF NOT EXISTS transaccion_id INTEGER"
                    ))
                    conn2.commit()
                    logger.warning("⚠️  Columna faltante creada: movimientos_stock.transaccion_id")
                else:
                    conn2.commit()
                    logger.info("✅ movimientos_stock.transaccion_id ya existe")

                conn2.close()
        except Exception as ms_err:
            logger.warning(f"⚠️  No se pudo verificar movimientos_stock.transaccion_id: {ms_err}")

        # ==========================================
        # REPARACIÓN COLUMNA CRÍTICA: pedidos.imagen_guia_url
        # La migración g7b8c9d0e1f6 agrega esta columna; si Alembic falla
        # silenciosamente en Render el upload de imagen de guía explotaría.
        # ==========================================
        try:
            from sqlalchemy import text as _sql_text3
            with app.app_context():
                from src.models.database import db as _db3
                conn3 = _db3.engine.connect()
                _check3 = _sql_text3("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'pedidos'
                      AND column_name = 'imagen_guia_url'
                """)
                if not conn3.execute(_check3).fetchone():
                    conn3.execute(_sql_text3(
                        "ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS imagen_guia_url VARCHAR(500)"
                    ))
                    conn3.commit()
                    logger.warning("⚠️  Columna faltante creada: pedidos.imagen_guia_url")
                else:
                    conn3.commit()
                    logger.info("✅ pedidos.imagen_guia_url ya existe")
                conn3.close()
        except Exception as pg_err:
            logger.warning(f"⚠️  No se pudo verificar pedidos.imagen_guia_url: {pg_err}")

        # ── feedback.url_contexto + feedback.negocio_id ──────────────────────
        try:
            from sqlalchemy import text as _sql_text4
            from src.models.database import db as _db4
            conn4 = _db4.engine.connect()
            for _col, _defn in [
                ('url_contexto', 'VARCHAR(500)'),
                ('negocio_id',   'INTEGER'),
            ]:
                _exists = conn4.execute(_sql_text4("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'feedback' AND column_name = :col
                """), {'col': _col}).fetchone()
                if not _exists:
                    conn4.execute(_sql_text4(
                        f"ALTER TABLE feedback ADD COLUMN IF NOT EXISTS {_col} {_defn}"
                    ))
                    conn4.commit()
                    logger.warning(f"⚠️  Columna creada: feedback.{_col}")
                else:
                    logger.info(f"✅ feedback.{_col} ya existe")
            conn4.close()
        except Exception as pg_err4:
            logger.warning(f"⚠️  No se pudo verificar columnas de feedback: {pg_err4}")
        # ─────────────────────────────────────────────────────────────────────

        # ── Seed idempotente del catálogo de badges (incluye Fundador) ───────
        try:
            from src.models.database import db as _db5
            from src.models.colombia_data.ratings.negocio_badge import seed_badges_catalogo
            _res = seed_badges_catalogo(_db5.session, actualizar_visual=True)
            logger.warning(
                f"🏅 Catálogo de badges sembrado: "
                f"{_res['creados']} creados, {_res['actualizados']} actualizados, "
                f"{_res['total']} en total"
            )
            # Catálogo de items de la tienda TuKoins (idempotente)
            from src.models.colombia_data.ratings.negocio_gamificacion import seed_tienda_items
            _resi = seed_tienda_items(_db5.session)
            logger.warning(
                f"🛒 Tienda TuKoins sembrada: {_resi['creados']} creados, "
                f"{_resi['actualizados']} actualizados, {_resi['total']} en total"
            )
        except Exception as seed_err:
            logger.warning(f"⚠️  No se pudo sembrar catálogo de badges/tienda: {seed_err}")

        # ── negocio_gamificacion.prestigio (S33) ─────────────────────────────
        try:
            from sqlalchemy import text as _sql_text6
            from src.models.database import db as _db6
            conn6 = _db6.engine.connect()
            conn6.execute(_sql_text6(
                "ALTER TABLE negocio_gamificacion ADD COLUMN IF NOT EXISTS prestigio INTEGER NOT NULL DEFAULT 0"
            ))
            conn6.commit()
            conn6.close()
            logger.info("✅ negocio_gamificacion.prestigio verificada")
        except Exception as pg_err6:
            logger.warning(f"⚠️  No se pudo verificar prestigio: {pg_err6}")
        # ─────────────────────────────────────────────────────────────────────

        # ── negocio_gamificacion.onboarding_completado (S40) ─────────────────
        try:
            from sqlalchemy import text as _sql_text7
            from src.models.database import db as _db7
            conn7 = _db7.engine.connect()
            conn7.execute(_sql_text7(
                "ALTER TABLE negocio_gamificacion ADD COLUMN IF NOT EXISTS onboarding_completado BOOLEAN NOT NULL DEFAULT FALSE"
            ))
            conn7.commit()
            conn7.close()
            logger.info("✅ negocio_gamificacion.onboarding_completado verificada")
        except Exception as pg_err7:
            logger.warning(f"⚠️  No se pudo verificar onboarding_completado: {pg_err7}")
        # ─────────────────────────────────────────────────────────────────────

        # ── admin_audit_log: log de auditoría del panel admin (A2) ───────────
        try:
            from sqlalchemy import text as _sql_text8
            from src.models.database import db as _db8
            conn8 = _db8.engine.connect()
            conn8.execute(_sql_text8("""
                CREATE TABLE IF NOT EXISTS admin_audit_log (
                    id           SERIAL PRIMARY KEY,
                    admin_id     INTEGER,
                    admin_email  VARCHAR(255),
                    accion       VARCHAR(50) NOT NULL,
                    entidad      VARCHAR(100),
                    entidad_id   VARCHAR(100),
                    detalle      JSONB DEFAULT '{}'::jsonb,
                    ip           VARCHAR(64),
                    user_agent   VARCHAR(300),
                    created_at   TIMESTAMP DEFAULT NOW()
                )
            """))
            conn8.execute(_sql_text8(
                "CREATE INDEX IF NOT EXISTS idx_audit_created ON admin_audit_log (created_at DESC)"))
            conn8.execute(_sql_text8(
                "CREATE INDEX IF NOT EXISTS idx_audit_entidad ON admin_audit_log (entidad)"))
            conn8.execute(_sql_text8(
                "CREATE INDEX IF NOT EXISTS idx_audit_admin ON admin_audit_log (admin_id)"))
            conn8.commit()
            conn8.close()
            logger.info("✅ admin_audit_log verificada")
        except Exception as pg_err8:
            logger.warning(f"⚠️  No se pudo verificar admin_audit_log: {pg_err8}")
        # ─────────────────────────────────────────────────────────────────────

        # ── gamif_config: config editable de gamificación (A6) ───────────────
        try:
            from sqlalchemy import text as _sql_text9
            from src.models.database import db as _db9
            conn9 = _db9.engine.connect()
            conn9.execute(_sql_text9("""
                CREATE TABLE IF NOT EXISTS gamif_config (
                    clave      VARCHAR(50) PRIMARY KEY,
                    valor      JSONB DEFAULT '{}'::jsonb,
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """))
            conn9.commit()
            conn9.close()
            logger.info("✅ gamif_config verificada")
        except Exception as pg_err9:
            logger.warning(f"⚠️  No se pudo verificar gamif_config: {pg_err9}")
        # ─────────────────────────────────────────────────────────────────────

        # ── negocio_badges.editado_admin (A15) ───────────────────────────────
        try:
            from sqlalchemy import text as _sql_text10
            from src.models.database import db as _db10
            conn10 = _db10.engine.connect()
            conn10.execute(_sql_text10(
                "ALTER TABLE negocio_badges ADD COLUMN IF NOT EXISTS editado_admin BOOLEAN DEFAULT FALSE"))
            conn10.commit()
            conn10.close()
            logger.info("✅ negocio_badges.editado_admin verificada")
        except Exception as pg_err10:
            logger.warning(f"⚠️  No se pudo verificar editado_admin: {pg_err10}")
        # ─────────────────────────────────────────────────────────────────────

        # ── intentos_login: rate limiting de fuerza bruta (A-SEC-1) ──────────
        try:
            from sqlalchemy import text as _sql_text11
            from src.models.database import db as _db11
            conn11 = _db11.engine.connect()
            conn11.execute(_sql_text11("""
                CREATE TABLE IF NOT EXISTS intentos_login (
                    clave      VARCHAR(160) PRIMARY KEY,
                    intentos   INTEGER NOT NULL DEFAULT 0,
                    primer_ts  DOUBLE PRECISION,
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """))
            conn11.commit()
            conn11.close()
            logger.info("✅ intentos_login verificada")
        except Exception as pg_err11:
            logger.warning(f"⚠️  No se pudo verificar intentos_login: {pg_err11}")
        # ─────────────────────────────────────────────────────────────────────

        # ── negocio_badges.vigencia_inicio/fin (A19) ─────────────────────────
        try:
            from sqlalchemy import text as _sql_text12
            from src.models.database import db as _db12
            conn12 = _db12.engine.connect()
            conn12.execute(_sql_text12("ALTER TABLE negocio_badges ADD COLUMN IF NOT EXISTS vigencia_inicio DATE"))
            conn12.execute(_sql_text12("ALTER TABLE negocio_badges ADD COLUMN IF NOT EXISTS vigencia_fin DATE"))
            conn12.commit()
            conn12.close()
            logger.info("✅ negocio_badges.vigencia_inicio/fin verificadas")
        except Exception as pg_err12:
            logger.warning(f"⚠️  No se pudo verificar vigencia de badges: {pg_err12}")
        # ─────────────────────────────────────────────────────────────────────

        # ── liga_recompensas: log idempotente de premios de liga (A25) ───────
        try:
            from sqlalchemy import text as _sql_text13
            from src.models.database import db as _db13
            conn13 = _db13.engine.connect()
            conn13.execute(_sql_text13("""
                CREATE TABLE IF NOT EXISTS liga_recompensas (
                    id          SERIAL PRIMARY KEY,
                    periodo     VARCHAR(7)  NOT NULL,   -- AAAA-MM del mes premiado
                    liga        VARCHAR(80) NOT NULL,   -- 'Nacional' | ciudad | categoria
                    negocio_id  INTEGER     NOT NULL,
                    posicion    INTEGER     NOT NULL,
                    xp          INTEGER     NOT NULL DEFAULT 0,
                    tukoins     INTEGER     NOT NULL DEFAULT 0,
                    otorgado_en TIMESTAMP   DEFAULT NOW(),
                    CONSTRAINT uq_liga_recompensa UNIQUE (periodo, liga, negocio_id)
                )
            """))
            conn13.commit()
            conn13.close()
            logger.info("✅ liga_recompensas verificada")
        except Exception as pg_err13:
            logger.warning(f"⚠️  No se pudo verificar liga_recompensas: {pg_err13}")
        # ─────────────────────────────────────────────────────────────────────

        # ── suscripciones_negocio: columnas tardías del modelo (fix schema drift) ──
        #    La tabla se creó antes de añadir estas columnas al modelo; sin ellas,
        #    CUALQUIER SELECT del ORM sobre suscripciones_negocio falla
        #    (UndefinedColumn alertas_enviadas), rompiendo activación de plan/trial
        #    y dejando al negocio atascado en plan básico (límite de productos).
        try:
            from sqlalchemy import text as _sql_text14
            from src.models.database import db as _db14
            conn14 = _db14.engine.connect()
            for _col, _defn in [
                ("alertas_enviadas", "JSON"),
                ("creado_por",       "VARCHAR(50)"),
                ("modificado_por",   "VARCHAR(50)"),
                ("notas",            "TEXT"),
            ]:
                conn14.execute(_sql_text14(
                    f"ALTER TABLE suscripciones_negocio ADD COLUMN IF NOT EXISTS {_col} {_defn}"))
            conn14.commit()
            conn14.close()
            logger.info("✅ suscripciones_negocio (columnas tardías) verificadas")
        except Exception as pg_err14:
            logger.warning(f"⚠️  No se pudo verificar suscripciones_negocio: {pg_err14}")
        # ─────────────────────────────────────────────────────────────────────

        # ── Challenges 2.0: flags de idempotencia para premios de gamificación (A28) ──
        try:
            from sqlalchemy import text as _sql_text15
            from src.models.database import db as _db15
            conn15 = _db15.engine.connect()
            conn15.execute(_sql_text15(
                "ALTER TABLE challenge_participaciones ADD COLUMN IF NOT EXISTS gamif_otorgado BOOLEAN DEFAULT FALSE"))
            conn15.execute(_sql_text15(
                "ALTER TABLE challenges ADD COLUMN IF NOT EXISTS gamif_premiado BOOLEAN DEFAULT FALSE"))
            conn15.commit()
            conn15.close()
            logger.info("✅ challenges/participaciones (flags gamif A28) verificadas")
        except Exception as pg_err15:
            logger.warning(f"⚠️  No se pudo verificar flags gamif de challenges: {pg_err15}")
        # ─────────────────────────────────────────────────────────────────────

        # ── Soft-delete + papelera para negocios y usuarios (A30) ────────────
        try:
            from sqlalchemy import text as _sql_text16
            from src.models.database import db as _db16
            conn16 = _db16.engine.connect()
            for _tabla in ('negocios', 'usuarios'):
                conn16.execute(_sql_text16(
                    f"ALTER TABLE {_tabla} ADD COLUMN IF NOT EXISTS eliminado BOOLEAN DEFAULT FALSE"))
                conn16.execute(_sql_text16(
                    f"ALTER TABLE {_tabla} ADD COLUMN IF NOT EXISTS eliminado_en TIMESTAMP"))
                conn16.execute(_sql_text16(
                    f"ALTER TABLE {_tabla} ADD COLUMN IF NOT EXISTS eliminado_por VARCHAR(120)"))
            conn16.commit()
            conn16.close()
            logger.info("✅ soft-delete/papelera (negocios, usuarios) verificada")
        except Exception as pg_err16:
            logger.warning(f"⚠️  No se pudo verificar soft-delete/papelera: {pg_err16}")
        # ─────────────────────────────────────────────────────────────────────

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