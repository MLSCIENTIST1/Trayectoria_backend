"""
Documentación Maestra — CONTENIDO (Fase 2). Lote 1.

Descripciones reales de cómo está construida la plataforma, en lenguaje
entendible por NO programadores (pero precisas), clasificadas por nivel:
  publico    🟢  cualquier usuario autenticado (visión general, sin secretos)
  admin      🟡  detalle técnico (archivos, estructura, cómo conecta)
  superadmin 🔴  sensible (seguridad, secretos, infraestructura) — requiere step-up

Idempotente: INSERT ... ON CONFLICT (clave) DO NOTHING.
Se irá ampliando lote a lote (todas las vistas, endpoints, plantillas, etc.).

© 2024-2026 Carlos Eduardo Huérfano Bermúdez. CONFIDENCIAL.
"""
import json
import logging
from sqlalchemy import text
from src.models.database import db

logger = logging.getLogger(__name__)

# Cada entrada: area, clave, titulo, resumen, contenido, nivel, orden, datos(opcional)
SEED_DOCS = [
    # ── GLOSARIO 🟢 ──────────────────────────────────────────────────────
    {'area': 'glosario', 'clave': 'doc-glosario', 'nivel': 'publico', 'orden': 1,
     'titulo': 'Glosario rápido (sin tecnicismos)',
     'resumen': 'Qué significan las palabras raras que verás en esta documentación.',
     'contenido': (
        'Para que cualquiera entienda:\n\n'
        '• Backend: el "motor" invisible que vive en un servidor; hace los cálculos, guarda y entrega datos.\n'
        '• Frontend: lo que el usuario ve y toca (pantallas, botones, colores).\n'
        '• Endpoint: una "puerta" del backend a la que el frontend toca para pedir o enviar algo (p. ej. "dame los productos").\n'
        '• Blueprint: una carpeta de puertas (endpoints) agrupadas por tema (pedidos, pagos, etc.).\n'
        '• Base de datos: el "archivador" donde se guarda todo de forma ordenada (tablas).\n'
        '• Tabla: una hoja del archivador (p. ej. la tabla de "negocios").\n'
        '• Multi-tenant: muchos negocios viven en la misma plataforma, pero cada uno solo ve lo suyo.\n'
        '• JSONB: una casillita flexible donde guardamos datos que cambian de forma (configuraciones, listas).\n'
        '• API: el conjunto de todas las puertas del backend.\n'
        '• Despliegue (deploy): publicar los cambios para que entren en producción (lo que usan los clientes).')},

    # ── ARQUITECTURA ─────────────────────────────────────────────────────
    {'area': 'arquitectura', 'clave': 'doc-arq-vision', 'nivel': 'publico', 'orden': 1,
     'titulo': '¿Qué es TuKomercio? (visión general)',
     'resumen': 'Una plataforma para que cualquier negocio venda en línea y se gestione.',
     'contenido': (
        'TuKomercio es una plataforma (un SaaS) que le permite a un negocio colombiano —sobre todo tenderos y '
        'microempresas— tener su tienda online, su catálogo, recibir pedidos, llevar su contabilidad y motivarse '
        'con un sistema de logros (gamificación).\n\n'
        'Una misma cuenta puede manejar varios negocios. Cada negocio tiene su propia tienda con dirección web '
        'para compartir por WhatsApp. Todo está pensado para que sea fácil, rápido y se vea profesional.')},
    {'area': 'arquitectura', 'clave': 'doc-arq-repos', 'nivel': 'admin', 'orden': 2,
     'titulo': 'Los dos "lados": frontend y backend (repositorios)',
     'resumen': 'El proyecto vive en dos partes separadas que trabajan juntas.',
     'contenido': (
        'La plataforma se divide en dos proyectos separados:\n\n'
        '1. FRONTEND (lo que se ve): páginas web hechas con HTML/CSS/JavaScript puro (sin frameworks). '
        'Se publica en Cloudflare Pages y se ve en tukomercio.co.\n'
        '2. BACKEND (el motor): un programa en Python (Flask) que vive en un servidor (Render) y maneja datos, '
        'reglas y seguridad. Se conecta a la base de datos (PostgreSQL en Neon).\n\n'
        'El frontend le "habla" al backend a través de la API. Mantenerlos separados permite actualizar uno sin '
        'romper el otro.')},
    {'area': 'arquitectura', 'clave': 'doc-arq-stack', 'nivel': 'admin', 'orden': 3,
     'titulo': 'Tecnologías que usamos (stack)',
     'resumen': 'Con qué herramientas está construida la plataforma.',
     'contenido': (
        '• Lenguaje del motor: Python con el framework Flask.\n'
        '• Base de datos: PostgreSQL (alojada en Neon).\n'
        '• Frontend: HTML, CSS y JavaScript "vanilla" (sin React/Vue), servido por un Worker de Cloudflare.\n'
        '• Imágenes: Cloudinary (optimiza y entrega las fotos).\n'
        '• Correos: Resend (recuperación de contraseña, avisos).\n'
        '• Pagos: Wompi (tarjetas y PSE).\n'
        '• Inteligencia artificial: Groq (la asistente "Dora").\n'
        '• Servidor del backend: Render (con gunicorn). Frontend: Cloudflare Pages.')},

    # ── BACKEND ──────────────────────────────────────────────────────────
    {'area': 'backend', 'clave': 'doc-back-init', 'nivel': 'admin', 'orden': 1,
     'titulo': 'El corazón del motor: __init__.py (create_app)',
     'resumen': 'El archivo que "enciende" el backend y deja todo listo.',
     'contenido': (
        'El archivo src/__init__.py contiene la función create_app(): es el "interruptor de arranque" del backend. '
        'Cuando la plataforma enciende, este archivo:\n\n'
        '1. Configura la app (clave secreta, conexión a la base de datos, sesiones).\n'
        '2. Define qué páginas (orígenes) pueden hablarle al backend (CORS) y bloquea las demás.\n'
        '3. Crea/repara las tablas de la base de datos automáticamente (migraciones), sin borrar datos.\n'
        '4. Siembra datos iniciales que deben existir (catálogos, insignias, contenido de ayuda) sin duplicar.\n'
        '5. Registra todos los "grupos de puertas" (blueprints).\n'
        '6. Activa la seguridad (login, cabeceras de protección).\n\n'
        'Regla de oro del proyecto: TODA reparación de la base de datos se pone AQUÍ, porque este es el archivo que '
        'realmente corre en producción.')},
    {'area': 'backend', 'clave': 'doc-back-run', 'nivel': 'admin', 'orden': 2,
     'titulo': 'run.py: el punto de entrada',
     'resumen': 'El archivo con el que el servidor pone a correr la aplicación.',
     'contenido': (
        'run.py es el archivo que el servidor usa para iniciar la aplicación. Toma la app creada por create_app() '
        'y la deja "corriendo" para atender peticiones. En producción, el servidor (gunicorn en Render) arranca '
        'con la instrucción "gunicorn run:run".\n\n'
        'Importante: las reparaciones de base de datos NO van aquí (van en __init__.py), porque en producción el '
        'arranque pasa por create_app(), no necesariamente por todo run.py.')},
    {'area': 'backend', 'clave': 'doc-back-blueprints', 'nivel': 'admin', 'orden': 3,
     'titulo': 'Blueprints: cómo se organizan las "puertas"',
     'resumen': 'Los endpoints se agrupan por tema para mantener orden.',
     'contenido': (
        'Un "blueprint" es un grupo de puertas (endpoints) del backend que pertenecen al mismo tema: por ejemplo, '
        'todo lo de pedidos en uno, todo lo de pagos en otro, etc. Hay más de 40 blueprints (auth, negocio, '
        'catálogo, checkout, pedidos, pagos/Wompi, cupones, reseñas, CRM, notificaciones, gamificación, admin, '
        'IA/Dora, taller, restaurante, mecánicos, centro de ayuda, etc.).\n\n'
        'Todos se registran de forma central y "tolerante a fallos": si un grupo tuviera un problema, se anota en '
        'el registro pero la plataforma sigue funcionando. En total hay varios cientos de endpoints.')},
    {'area': 'backend', 'clave': 'doc-back-password-reset', 'nivel': 'admin', 'orden': 4,
     'titulo': 'Recuperación de contraseña',
     'resumen': 'Cómo un usuario recupera el acceso si olvidó su clave.',
     'contenido': (
        'Cuando alguien olvida su contraseña: 1) pide recuperarla con su correo; 2) el backend genera un enlace '
        'seguro con un token que caduca; 3) ese enlace se envía por correo usando Resend; 4) el usuario abre el '
        'enlace y crea una contraseña nueva.\n\n'
        'El token es de un solo uso y con vencimiento, por seguridad. Si el correo no llega, suele ser por la '
        'configuración del dominio de envío (ver sección de Servicios de terceros / Despliegue).')},

    # ── ERRORES 🟡 ───────────────────────────────────────────────────────
    {'area': 'errores', 'clave': 'doc-errores-comunes', 'nivel': 'admin', 'orden': 1,
     'titulo': 'Errores y respuestas del backend',
     'resumen': 'Qué significan los códigos que puede devolver la plataforma.',
     'contenido': (
        'El backend responde con "códigos" estándar. Los más comunes:\n\n'
        '• 200 / 201: todo bien (201 = algo se creó).\n'
        '• 400: faltan datos o vienen mal (el frontend pidió algo incompleto).\n'
        '• 401: no has iniciado sesión.\n'
        '• 403: iniciaste sesión pero no tienes permiso para eso.\n'
        '• 404: lo que se pidió no existe.\n'
        '• 409: conflicto (p. ej. una "clave" que ya existe).\n'
        '• 500: error interno inesperado (se registra para revisarlo).\n\n'
        'Las respuestas siempre vienen en formato JSON con un mensaje claro. Errores 500 hacen "rollback" '
        '(deshacen cambios a medias) para no dejar datos inconsistentes.')},

    # ── SEGURIDAD 🔴 ─────────────────────────────────────────────────────
    {'area': 'seguridad', 'clave': 'doc-seg-passwords', 'nivel': 'superadmin', 'orden': 1,
     'titulo': 'Cómo protegemos las contraseñas',
     'resumen': 'Las contraseñas nunca se guardan "tal cual".',
     'contenido': (
        'Las contraseñas NO se guardan en texto. Se guardan "cifradas" con bcrypt (un algoritmo lento a propósito, '
        'con 12 rondas), de modo que ni nosotros podemos leerlas. Al iniciar sesión, se compara de forma segura.\n\n'
        'Además hay protección contra fuerza bruta: tras varios intentos fallidos en pocos minutos, se bloquea '
        'temporalmente. La identidad del usuario SIEMPRE se toma de la sesión del servidor, nunca de datos que '
        'mande el navegador.')},
    {'area': 'seguridad', 'clave': 'doc-seg-secretos', 'nivel': 'superadmin', 'orden': 2,
     'titulo': 'Secretos y variables de entorno',
     'resumen': 'Las llaves sensibles viven fuera del código.',
     'contenido': (
        'Las "llaves" sensibles (conexión a la base de datos, clave secreta de sesión, llaves de correo, pagos, '
        'imágenes e IA) NO están escritas en el código: se configuran como "variables de entorno" en el servidor '
        '(Render). Así, el código se puede compartir sin exponer secretos.\n\n'
        'Nombres (sin valores): DATABASE_URL, SECRET_KEY, MAIL_* / RESEND_API_KEY, CLOUDINARY_*, GROQ_API_KEY, '
        'VAPID_* (notificaciones push). Los pagos de cada negocio (Wompi) se guardan por negocio en la base de datos.')},
    {'area': 'seguridad', 'clave': 'doc-seg-cors-csrf', 'nivel': 'superadmin', 'orden': 3,
     'titulo': 'Quién puede hablarle al backend (CORS y CSRF)',
     'resumen': 'Solo orígenes confiables pueden usar la API.',
     'contenido': (
        'El backend solo acepta peticiones desde una lista blanca de direcciones (tukomercio.co, el dominio de '
        'Cloudflare y entornos de desarrollo). Cualquier otro origen es rechazado.\n\n'
        'Para acciones que cambian datos (crear/editar/borrar) se valida el "origen" de la petición (protección '
        'CSRF), de modo que otra página no pueda actuar en tu nombre. Las cookies de sesión son seguras '
        '(HttpOnly, Secure, SameSite).')},

    # ── FRONTEND ─────────────────────────────────────────────────────────
    {'area': 'frontend', 'clave': 'doc-front-vision', 'nivel': 'admin', 'orden': 1,
     'titulo': 'Visión general del frontend',
     'resumen': 'Cómo está organizado lo que el usuario ve.',
     'contenido': (
        'El frontend son páginas web (HTML/CSS/JavaScript) sin frameworks. Las principales: la landing '
        '(crea-tu-tienda), el login/registro, la app del negocio (panel y módulos de contabilidad), el Diseñador '
        'de tienda, las tiendas públicas (con varias plantillas), el seguimiento de pedidos y el Centro de Ayuda.\n\n'
        'Todo comparte un "sistema de diseño" común (tipografías Orbitron/Sora/Plus Jakarta, paleta de colores y '
        'componentes) para que se vea coherente y profesional. Es 100% responsivo (se adapta al celular).')},
    {'area': 'frontend', 'clave': 'doc-front-worker', 'nivel': 'admin', 'orden': 2,
     'titulo': 'El enrutador: _worker.js',
     'resumen': 'El "portero" que decide qué página mostrar en cada dirección.',
     'contenido': (
        'En Cloudflare, un archivo especial (_worker.js) decide qué mostrar según la dirección que el visitante '
        'escribe: la landing en "/", la app en "/app", una tienda en "/tienda/<nombre>", el resumen de un pedido, '
        'el Centro de Ayuda en "/ayuda", etc.\n\n'
        'También prepara las "tarjetas de vista previa" cuando compartes un enlace por WhatsApp (con foto, título '
        'y descripción), para que se vea atractivo. Si algo falla, muestra un error limpio sin exponer detalles.')},
]


def seed_docs_tecnicas():
    """Inserta el contenido técnico de forma idempotente (no duplica)."""
    insert = text(
        "INSERT INTO plataforma_kb (tipo, area, clave, titulo, resumen, contenido, datos, orden, publicado, nivel_acceso) "
        "VALUES ('tecnico', :area, :clave, :titulo, :resumen, :contenido, CAST(:datos AS JSONB), :orden, TRUE, :nivel) "
        "ON CONFLICT (clave) DO NOTHING")
    n = 0
    try:
        for d in SEED_DOCS:
            db.session.execute(insert, {
                'area': d['area'], 'clave': d['clave'], 'titulo': d['titulo'],
                'resumen': d.get('resumen'), 'contenido': d.get('contenido'),
                'datos': json.dumps(d.get('datos') or {}), 'orden': d.get('orden', 0),
                'nivel': d.get('nivel', 'admin'),
            })
            n += 1
        db.session.commit()
        logger.info(f"✅ Seed docs técnicas: {n} entradas aseguradas")
        return n
    except Exception as ex:
        db.session.rollback()
        logger.warning(f"⚠️  Seed docs técnicas no crítico: {ex}")
        return 0
