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
        '• Despliegue (deploy): publicar los cambios para que entren en producción (lo que usan los clientes).'),
     'tecnico': "Términos extra para perfiles técnicos: REST (estilo de API por HTTP), ORM (SQLAlchemy mapea tablas a objetos), Blueprint (módulo de rutas Flask), JSONB (columna JSON binaria de PostgreSQL), PWA (app web instalable), CORS (control de orígenes), bcrypt (hash de contraseñas), idempotente (repetible sin efectos duplicados)."},


    # ── ARQUITECTURA ─────────────────────────────────────────────────────
    {'area': 'arquitectura', 'clave': 'doc-arq-vision', 'nivel': 'publico', 'orden': 1,
     'titulo': '¿Qué es TuKomercio? (visión general)',
     'resumen': 'Una plataforma para que cualquier negocio venda en línea y se gestione.',
     'contenido': (
        'TuKomercio es una plataforma (un SaaS) que le permite a un negocio colombiano —sobre todo tenderos y '
        'microempresas— tener su tienda online, su catálogo, recibir pedidos, llevar su contabilidad y motivarse '
        'con un sistema de logros (gamificación).\n\n'
        'Una misma cuenta puede manejar varios negocios. Cada negocio tiene su propia tienda con dirección web '
        'para compartir por WhatsApp. Todo está pensado para que sea fácil, rápido y se vea profesional.'),
     'tecnico': "SaaS de e-commerce multi-tenant para negocios colombianos (tenderos/microempresas); cada usuario puede gestionar uno o varios negocios con micrositio público, catálogo, pedidos, contabilidad y gamificación (XP, niveles, TuKoins, misiones, insignias, ligas, eventos); MVP en producción."},

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
        'romper el otro.'),
     'tecnico': "Dos repositorios en rama main: BACKEND (cloude_first_repositorie_bizflow-backend_render) desplegado en Render (trayectoria-backend.onrender.com); FRONTEND (cloude_first_repositorie_bizflow-frontend) en Cloudflare Pages (tuko.pages.dev -> tukomercio.co). Casi todo cambio funcional toca ambos (endpoint backend + UI frontend)."},

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
        '• Servidor del backend: Render (con gunicorn). Frontend: Cloudflare Pages.'),
     'tecnico': "Backend Flask 3.1.2 (app factory create_app() en src/__init__.py), SQLAlchemy 2.0.45 + Flask-SQLAlchemy 3.1.1, psycopg2-binary 2.9.11, PostgreSQL en Neon; Auth Flask-Login 0.6.3 con sesiones server-side (cookie bizflow_session, SameSite=None, Secure, HttpOnly), NO JWT; Frontend vanilla HTML/CSS/JS sin frameworks; Cloudinary 1.44 imágenes, Resend correos; gunicorn en Render; Cloudflare Pages Advanced Mode (_worker.js)."},


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
        'realmente corre en producción.'),
     'tecnico': "Archivo: src/__init__.py, funcion create_app(). Config: SECRET_KEY (env), SQLALCHEMY_DATABASE_URI (normaliza postgres:// a postgresql://), pool SQLAlchemy (pool_pre_ping, pool_recycle ~280s, pool_size 10, max_overflow 20, statement_timeout 30s). CORS con whitelist + supports_credentials=True. Guard CSRF en before_request (valida Origin en metodos mutantes). db.create_all() + lista 'migraciones' (ALTER/CREATE ... IF NOT EXISTS, cada una en try/except con commit aislado). Seeders idempotentes (feature flags ON CONFLICT DO NOTHING, badges, plataforma_kb, docs). Flask-Login session_protection='strong'. after_request anade X-Content-Type-Options, X-Frame-Options, X-XSS-Protection."},

    {'area': 'backend', 'clave': 'doc-back-run', 'nivel': 'admin', 'orden': 2,
     'titulo': 'run.py: el punto de entrada',
     'resumen': 'El archivo con el que el servidor pone a correr la aplicación.',
     'contenido': (
        'run.py es el archivo que el servidor usa para iniciar la aplicación. Toma la app creada por create_app() '
        'y la deja "corriendo" para atender peticiones. En producción, el servidor (gunicorn en Render) arranca '
        'con la instrucción "gunicorn run:run".\n\n'
        'Importante: las reparaciones de base de datos NO van aquí (van en __init__.py), porque en producción el '
        'arranque pasa por create_app(), no necesariamente por todo run.py.'),
     'tecnico': "Procfile: web: gunicorn run:run. run.py importa create_app() y expone la instancia 'run'. En produccion el arranque instancia la app via el app factory; por eso las migraciones van en create_app() (regla F8), no en run.py."},

    {'area': 'backend', 'clave': 'doc-back-blueprints', 'nivel': 'admin', 'orden': 3,
     'titulo': 'Blueprints: cómo se organizan las "puertas"',
     'resumen': 'Los endpoints se agrupan por tema para mantener orden.',
     'contenido': (
        'Un "blueprint" es un grupo de puertas (endpoints) del backend que pertenecen al mismo tema: por ejemplo, '
        'todo lo de pedidos en uno, todo lo de pagos en otro, etc. Hay más de 40 blueprints (auth, negocio, '
        'catálogo, checkout, pedidos, pagos/Wompi, cupones, reseñas, CRM, notificaciones, gamificación, admin, '
        'IA/Dora, taller, restaurante, mecánicos, centro de ayuda, etc.).\n\n'
        'Todos se registran de forma central y "tolerante a fallos": si un grupo tuviera un problema, se anota en '
        'el registro pero la plataforma sigue funcionando. En total hay varios cientos de endpoints.'),
     'tecnico': "Registro central en src/api/__init__.py::register_api(app) con safe_register(module_path, bp_name, display_name, prefix). Cada dominio define su Blueprint con url_prefix (la mayoria /api; admin /api/admin; verticales /api/<vertical>). +40 blueprints: auth, negocio_completo, catalogo, pagina, qr_generator, checkout, pedidos, resenas, cupones, wompi, analytics, equipo, crm, carritos, gamificacion, notifications/chat, dora(ia), admin, admin_features, leads, taller, restaurante, mecalink, ayuda (centro_ayuda + docs_tecnicas). safe_register es tolerante: si un modulo no importa, registra el error y la app sigue."},

    {'area': 'backend', 'clave': 'doc-back-password-reset', 'nivel': 'admin', 'orden': 4,
     'titulo': 'Recuperación de contraseña',
     'resumen': 'Cómo un usuario recupera el acceso si olvidó su clave.',
     'contenido': (
        'Cuando alguien olvida su contraseña: 1) pide recuperarla con su correo; 2) el backend genera un enlace '
        'seguro con un token que caduca; 3) ese enlace se envía por correo usando Resend; 4) el usuario abre el '
        'enlace y crea una contraseña nueva.\n\n'
        'El token es de un solo uso y con vencimiento, por seguridad. Si el correo no llega, suele ser por la '
        'configuración del dominio de envío (ver sección de Servicios de terceros / Despliegue).'),
     'tecnico': "Blueprint password_reset_api.py. Tabla password_reset_tokens (usuario_id FK, token unico, expires_at, is_used). Flujo: POST /forgot-password genera token con vencimiento -> email via Resend (API HTTPS). GET /verify-reset-token/<token> valida. POST /reset-password aplica Usuario.set_password (bcrypt) y marca el token usado. Nota: peticiones a api.resend.com desde Cloudflare requieren cabecera User-Agent (si falta -> 403/1010). MAIL_FROM por variable de entorno."},


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
        '(deshacen cambios a medias) para no dejar datos inconsistentes.'),
     'tecnico': "Respuestas siempre en JSON. Códigos: 200/201 ok, 400 validación/payload incompleto, 401 sin sesión, 403 sin permiso, 404 no existe, 409 conflicto (p. ej. clave duplicada), 500 error interno. Los manejadores 404/500 están en create_app (el 500 hace db.session.rollback()); los endpoints usan try/except con rollback aislado para no dejar datos a medias."},


    # ── SEGURIDAD 🔴 ─────────────────────────────────────────────────────
    {'area': 'seguridad', 'clave': 'doc-seg-passwords', 'nivel': 'superadmin', 'orden': 1,
     'titulo': 'Cómo protegemos las contraseñas',
     'resumen': 'Las contraseñas nunca se guardan "tal cual".',
     'contenido': (
        'Las contraseñas NO se guardan en texto. Se guardan "cifradas" con bcrypt (un algoritmo lento a propósito, '
        'con 12 rondas), de modo que ni nosotros podemos leerlas. Al iniciar sesión, se compara de forma segura.\n\n'
        'Además hay protección contra fuerza bruta: tras varios intentos fallidos en pocos minutos, se bloquea '
        'temporalmente. La identidad del usuario SIEMPRE se toma de la sesión del servidor, nunca de datos que '
        'mande el navegador.'),
     'tecnico': "Hash bcrypt rounds=12 (Usuario.set_password / Usuario.check_password en src/models/usuarios.py, campo contrasenia). Anti fuerza-bruta: registro de intentos por (ip|email), bloqueo tras ~5 fallos en 15 min (src/api/utils/seguridad.py). El step-up de la documentacion critica reutiliza Usuario.check_password contra una cuenta SuperAdmin."},

    {'area': 'seguridad', 'clave': 'doc-seg-secretos', 'nivel': 'superadmin', 'orden': 2,
     'titulo': 'Secretos y variables de entorno',
     'resumen': 'Las llaves sensibles viven fuera del código.',
     'contenido': (
        'Las "llaves" sensibles (conexión a la base de datos, clave secreta de sesión, llaves de correo, pagos, '
        'imágenes e IA) NO están escritas en el código: se configuran como "variables de entorno" en el servidor '
        '(Render). Así, el código se puede compartir sin exponer secretos.\n\n'
        'Nombres (sin valores): DATABASE_URL, SECRET_KEY, MAIL_* / RESEND_API_KEY, CLOUDINARY_*, GROQ_API_KEY, '
        'VAPID_* (notificaciones push). Los pagos de cada negocio (Wompi) se guardan por negocio en la base de datos.'),
     'tecnico': "Variables de entorno en Render (no versionadas): DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, MAIL_SERVER/PORT/USERNAME/PASSWORD/MAIL_FROM, RESEND_API_KEY, CLOUDINARY_*, GROQ_API_KEY, VAPID_PUBLIC_KEY/PRIVATE_KEY/SUBJECT, FRONTEND_URL. Se leen con os.environ y solo tienen defaults para desarrollo. Wompi: llaves por negocio en tabla wompi_configs (no en env). Nunca commitear valores reales."},

    {'area': 'seguridad', 'clave': 'doc-seg-cors-csrf', 'nivel': 'superadmin', 'orden': 3,
     'titulo': 'Quién puede hablarle al backend (CORS y CSRF)',
     'resumen': 'Solo orígenes confiables pueden usar la API.',
     'contenido': (
        'El backend solo acepta peticiones desde una lista blanca de direcciones (tukomercio.co, el dominio de '
        'Cloudflare y entornos de desarrollo). Cualquier otro origen es rechazado.\n\n'
        'Para acciones que cambian datos (crear/editar/borrar) se valida el "origen" de la petición (protección '
        'CSRF), de modo que otra página no pueda actuar en tu nombre. Las cookies de sesión son seguras '
        '(HttpOnly, Secure, SameSite).'),
     'tecnico': "CORS (flask-cors) whitelist: tukomercio.co, www, tuko.pages.dev, *.web.app (legacy), localhost; supports_credentials=True; metodos GET/POST/PUT/DELETE/PATCH/OPTIONS. CSRF: middleware before_request valida Origin (o lo deriva de Referer) en metodos mutantes y responde 403 si no esta en whitelist; exime webhooks (p. ej. /api/wompi/webhook) y /health. Cookie bizflow_session: SameSite=None, Secure, HttpOnly."},


    # ── FRONTEND ─────────────────────────────────────────────────────────
    {'area': 'frontend', 'clave': 'doc-front-vision', 'nivel': 'admin', 'orden': 1,
     'titulo': 'Visión general del frontend',
     'resumen': 'Cómo está organizado lo que el usuario ve.',
     'contenido': (
        'El frontend son páginas web (HTML/CSS/JavaScript) sin frameworks. Las principales: la landing '
        '(crea-tu-tienda), el login/registro, la app del negocio (panel y módulos de contabilidad), el Diseñador '
        'de tienda, las tiendas públicas (con varias plantillas), el seguimiento de pedidos y el Centro de Ayuda.\n\n'
        'Todo comparte un "sistema de diseño" común (tipografías Orbitron/Sora/Plus Jakarta, paleta de colores y '
        'componentes) para que se vea coherente y profesional. Es 100% responsivo (se adapta al celular).'),
     'tecnico': "Frontend vanilla (HTML/CSS/JS, sin frameworks) servido por Cloudflare Pages + _worker.js; comparte assets/css/design-tokens.css (variables --tk-*, fuentes Orbitron/Sora/Plus Jakarta) y Bootstrap Icons; PWA con sw.js (stale-while-revalidate para .js/.css, network-first para HTML, network-only para la API) y tukomercio-manifest.json."},

    {'area': 'frontend', 'clave': 'doc-front-worker', 'nivel': 'admin', 'orden': 2,
     'titulo': 'El enrutador: _worker.js',
     'resumen': 'El "portero" que decide qué página mostrar en cada dirección.',
     'contenido': (
        'En Cloudflare, un archivo especial (_worker.js) decide qué mostrar según la dirección que el visitante '
        'escribe: la landing en "/", la app en "/app", una tienda en "/tienda/<nombre>", el resumen de un pedido, '
        'el Centro de Ayuda en "/ayuda", etc.\n\n'
        'También prepara las "tarjetas de vista previa" cuando compartes un enlace por WhatsApp (con foto, título '
        'y descripción), para que se vea atractivo. Si algo falla, muestra un error limpio sin exponer detalles.'),
     'tecnico': "public/_worker.js (Cloudflare Pages Advanced Mode). _redirects se ignora. ASSETS.fetch('/foo') -> 200 (clean URL); '/foo.html' -> 307. Rutas: /, /app, /tienda/:slug (sirve tienda/r.html), /pedido/:t/:codigo, /ayuda, /ayuda/:slug, /novedades, /estado, /documentacion. Para bots (BOT_RE: WhatsApp/Telegram/Facebook...) genera HTML con OG tags (buildOgHtml + optimizarOgImage para Cloudinary). Errores 5xx -> 404 limpio. WORKER_VERSION en /_debug/version."},


    # ── LOTE 2: recorrido del frontend (vistas) + base de datos ──────────
    {'area': 'ui-map', 'clave': 'doc-ui-overview', 'nivel': 'publico', 'orden': 1,
     'titulo': 'Mapa rápido de la plataforma',
     'resumen': 'Las grandes zonas y cómo se conectan.',
     'contenido': (
        'En grande, TuKomercio tiene 7 zonas:\n\n'
        '1. La página de inicio pública (landing) que invita a registrarse.\n'
        '2. El acceso/registro (login).\n'
        '3. La app del negocio, con sus módulos de gestión y el Diseñador.\n'
        '4. La tienda pública que ven los compradores (con carrito y pago).\n'
        '5. El seguimiento del pedido (enlace que se comparte).\n'
        '6. El Centro de Ayuda (guías para los tenderos).\n'
        '7. El Panel de Administración (solo para el equipo de TuKomercio).'),
     'tecnico': "Rutas en public/_worker.js: \"/\" landing (crea-tu-tienda.html), \"/app\" shell (TuKomercio.html), \"/app/login\", \"/app/register\", \"/tienda/:slug\" (tienda/r.html), \"/pedido/:tienda/:codigo\" (heyden.html), \"/ayuda\", \"/ayuda/:slug\", \"/novedades\", \"/estado\", \"/documentacion\"; OG dinámico para bots y optimización de imágenes Cloudinary."},

    {'area': 'frontend', 'clave': 'doc-front-landing', 'nivel': 'publico', 'orden': 3,
     'titulo': 'La página de inicio (landing)',
     'resumen': 'Donde llegan los visitantes a conocer la plataforma.',
     'contenido': (
        'Es la página pública (crea-tu-tienda) que presenta TuKomercio: explica qué es, muestra las funciones, los '
        'precios y un botón para crear la tienda gratis. Su meta es convencer al visitante de registrarse. Desde su '
        'menú y pie de página se llega al login, al Centro de Ayuda, a Novedades y a esta Documentación.'),
     'tecnico': "Archivo crea-tu-tienda.html: hero con video, social proof, slider de tiendas, grid de funciones, showcase de pedido (mockup tipo teléfono de heyden), sección comunidad, \"cómo funciona\" (3 pasos), grid de precios (4 planes), FAQ con JSON-LD; tipografías Sora + Plus Jakarta + Bootstrap Icons; enlaces a /ayuda, /novedades y /documentacion."},

    {'area': 'frontend', 'clave': 'doc-front-login', 'nivel': 'admin', 'orden': 4,
     'titulo': 'Acceso: login y registro',
     'resumen': 'Las pantallas para entrar o crear cuenta.',
     'contenido': (
        'login permite iniciar sesión; register crear una cuenta nueva; y hay pantallas para recuperar y '
        'restablecer la contraseña. Todas conversan con el backend de autenticación y, al entrar, llevan a la app '
        'del negocio.'),
     'tecnico': "Archivo login.html: formulario email + contraseña que hace POST a /api/auth/login (sesión Flask-Login con cookie bizflow_session); chequeo de sesión en el <head> redirige a la app si ya está autenticado; manifest PWA tukomercio-manifest.json."},

    {'area': 'frontend', 'clave': 'doc-front-app', 'nivel': 'admin', 'orden': 5,
     'titulo': 'La app del negocio (/app)',
     'resumen': 'El tablero principal del dueño.',
     'contenido': (
        'Tras iniciar sesión, el dueño entra a la app (TuKomercio.html): un "contenedor" que carga por dentro los '
        'módulos (inventario, ventas, pedidos, reportes, Diseñador, etc.). Se puede instalar como app en el '
        'celular (PWA) para entrar de un toque.'),
     'tecnico': "Archivo TuKomercio.html: shell SPA con base href=\"/\" (resuelve assets desde la raíz), sidebar modular colapsable (estado en localStorage), chequeo de auth en el <head> (redirige a login si no hay sesión); carga dinámicamente los módulos de contabilidad/modulos/*.html."},

    {'area': 'frontend', 'clave': 'doc-front-designer', 'nivel': 'admin', 'orden': 6,
     'titulo': 'El Diseñador de tienda',
     'resumen': 'El editor visual para personalizar la tienda.',
     'contenido': (
        'El Diseñador (designer) es donde el dueño define logo, colores, portada, secciones, tipografía y la imagen '
        'que se ve al compartir. Tiene vista previa en vivo y guarda toda la configuración visual de la tienda en '
        'el negocio. Al guardar y recargar, los cambios quedan publicados.'),
     'tecnico': "Archivos modulos_crear_tienda/crear_tienda/designer.html + designer.js: editor visual de la tienda; loadStoreData() (merge config del backend) -> applyConfigToInputs() (puebla el DOM) -> updatePreview() (lee el DOM hacia storeConfig); sube imágenes a Cloudinary (unsigned preset); guarda la configuración del negocio (config_tienda)."},

    {'area': 'frontend', 'clave': 'doc-front-super-designer', 'nivel': 'admin', 'orden': 7,
     'titulo': 'Super Designer (editor avanzado)',
     'resumen': 'Edición visual potente, por módulos.',
     'contenido': (
        'El Super Designer es un editor más avanzado, dividido en cerca de 22 módulos especializados: colores, '
        'tipografía, biblioteca de componentes, arrastrar-y-soltar, animaciones, SEO, redes sociales, asistencia '
        'con IA, deshacer/rehacer, versiones, vista responsive y más. Permite construir páginas con mucho detalle.'),
     'tecnico': "Archivos super_designer.html + super_designer.js (Engine) + módulos sd_*.js (sd_ai, sd_animations, sd_clickedit, sd_collab, sd_colors, sd_components, sd_css, sd_dragdrop, sd_export, sd_intelligence, sd_media, sd_mobile, sd_perf, sd_polish, sd_seo, sd_social, sd_typography, sd_undo, sd_versions); editor avanzado que se comunica con las plantillas por postMessage (tuko-runtime.js), con paletas y fuentes predefinidas."},

    {'area': 'frontend', 'clave': 'doc-front-grilla', 'nivel': 'admin', 'orden': 8,
     'titulo': 'La grilla financiera',
     'resumen': 'Las finanzas del negocio en una cuadrícula clara.',
     'contenido': (
        'La grilla financiera presenta los movimientos del negocio (ventas, compras, gastos e ingresos) en una '
        'cuadrícula ordenada, para llevar las cuentas con claridad y ver el balance del negocio.'),
     'tecnico': "Archivo real contabilidad/grilla_financiera.html (~2059 líneas, title \"Centro de Control Financiero\"); tablero financiero con KPIs animados (statsOrbit, ring1-3, stat-ingresos), búsqueda global (globalSearchBtn) y cabecera con business-name; consume la API del negocio para ingresos/gastos/ventas."},

    {'area': 'frontend', 'clave': 'doc-front-contabilidad', 'nivel': 'admin', 'orden': 9,
     'titulo': 'Los módulos de gestión (contabilidad)',
     'resumen': 'Cerca de 19 pantallas para el día a día.',
     'contenido': (
        'Bajo "contabilidad" viven los módulos del día a día: tablero (dashboard), inventario, pedidos, venta '
        '(punto de venta), gastos, ingresos, reportes, analítica, carritos abandonados, cupones, CRM de clientes, '
        'dropshipping, equipo, carga por CSV, alertas, compras, gamificación, los verticales restaurante y taller, '
        'la integración de pagos (Wompi) y el modo sin conexión.'),
     'tecnico': "Carpeta contabilidad/modulos/ (~21 vistas): dashboard, inventario, pedidos, venta, gastos, ingreso_div, compra, carga_csv, reportes, analytics, wompi, cupones, carritos, crm, gamificacion, alertas, dropshipping, restaurante, taller, equipo, offline; cada una es una pantalla HTML que consume la API del negocio."},

    {'area': 'frontend', 'clave': 'doc-front-inventario', 'nivel': 'admin', 'orden': 10,
     'titulo': 'Inventario',
     'resumen': 'Donde se administran productos y stock.',
     'contenido': (
        'La pantalla de inventario lista los productos y permite crear/editar, subir fotos, fijar precio/costo/'
        'stock, ver alertas de stock bajo y cargar muchos productos de una vez por CSV. Es una de las vistas más '
        'completas de la app.'),
     'tecnico': "Archivo contabilidad/modulos/inventario.html (+ inventario.js): gestión de productos con fotos/variantes (talla-color), precio, costo, stock y alertas de bajo stock; carga vía la API de catálogo del negocio, con edición y carga masiva por CSV."},

    {'area': 'frontend', 'clave': 'doc-front-pedidos-vista', 'nivel': 'admin', 'orden': 11,
     'titulo': 'Gestión de pedidos',
     'resumen': 'Donde el dueño atiende las ventas online.',
     'contenido': (
        'Lista los pedidos, muestra el detalle (qué pidió el cliente, datos de envío), permite confirmar y avanzar '
        'el estado (preparando → enviado → entregado), e incluso saltar directo a un estado con confirmación. Al '
        'marcar "enviado", arma el mensaje de WhatsApp listo para avisarle al cliente.'),
     'tecnico': "Archivo contabilidad/modulos/pedidos.html; FLUJO_ESTADOS real = ['confirmado','preparando','enviado','en_oficina','entregado']; usa cambiarEstadoConConfirm(pedidoId, nuevoEstado, modo) (modos avance|salto|retroceso) y verDetalle() que hace fetch a /pedidos/<id>; al avanzar a \"enviado\" arma el mensaje de WhatsApp para el cliente."},

    {'area': 'frontend', 'clave': 'doc-front-tienda-publica', 'nivel': 'admin', 'orden': 12,
     'titulo': 'La tienda pública',
     'resumen': 'La vitrina que ve el comprador.',
     'contenido': (
        'Cuando alguien abre tukomercio.co/tienda/<nombre>, un "router" (r.html) detecta el negocio y carga la '
        'plantilla elegida con sus productos. Es la vitrina pública donde el cliente navega, ve fotos y precios, y '
        'agrega al carrito.'),
     'tecnico': "Archivo tienda/r.html (router universal): extrae el slug de /tienda/:slug, consulta /api/negocio/slug/<slug> para obtener tipo_pagina, carga la plantilla correspondiente de tienda/plantillas/ e inyecta window.__TUKO_SLUG antes de renderizar; timeout y fallback a error."},

    {'area': 'frontend', 'clave': 'doc-front-plantillas', 'nivel': 'admin', 'orden': 13,
     'titulo': 'Las plantillas de tienda',
     'resumen': 'Distintos diseños listos para cada negocio.',
     'contenido': (
        'Hay varias plantillas (catálogo, Herbal, Pleeness, groove, verde, restaurante, taller, etc.). El dueño '
        'elige una desde el Diseñador y su tienda toma ese estilo, sin perder los productos. Todas muestran la '
        'franja de confianza (verificado, calificación, pedidos entregados, antigüedad).'),
     'tecnico': "Carpeta tienda/plantillas/: catalogo, groove, Herbal, Pleeness, prueba, restaurante, sb_Landing_page, start_level, taller, verde; cada una con su index.html y assets; todas incluyen la franja de confianza (trust-strip.js)."},

    {'area': 'frontend', 'clave': 'doc-front-checkout', 'nivel': 'admin', 'orden': 14,
     'titulo': 'Carrito y checkout',
     'resumen': 'El proceso de compra del cliente.',
     'contenido': (
        'El cliente agrega productos al carrito, llena sus datos de envío, elige el método de pago (contra entrega, '
        'Nequi, transferencia, o tarjeta/PSE con Wompi) y confirma. Al final ve una pantalla de pago exitoso y el '
        'vendedor recibe el pedido en su panel.'),
     'tecnico': "Archivos tienda/checkout.html y tienda/carrito.html: resumen del carrito, datos de envío (nombre, teléfono, dirección, ciudad), pago vía Wompi y otros métodos; integra mensaje automático de WhatsApp a la tienda; pantalla de pago-exitoso al final."},

    {'area': 'frontend', 'clave': 'doc-front-pedido-tracking', 'nivel': 'admin', 'orden': 15,
     'titulo': 'Seguimiento del pedido',
     'resumen': 'El enlace que el cliente sigue.',
     'contenido': (
        'La vista de resumen del pedido (heyden) le muestra al comprador el detalle y el estado de su compra a '
        'través de un enlace limpio que se comparte por WhatsApp, con una vista previa atractiva (foto, nombre y '
        'código del pedido).'),
     'tecnico': "Archivo heyden.html: página de resumen/seguimiento del pedido para el comprador (estados visibles), mockup animado, items con miniaturas, total y guía de envío; colores tematizados por variable CSS de marca; servida en /pedido/:tienda/:codigo con OG para WhatsApp."},

    {'area': 'frontend', 'clave': 'doc-front-centro-ayuda', 'nivel': 'publico', 'orden': 16,
     'titulo': 'El Centro de Ayuda',
     'resumen': 'Las guías de cara al usuario.',
     'contenido': (
        'En tukomercio.co/ayuda están las guías para los tenderos (crear tienda, subir productos, pedidos, pagos, '
        'vender más…), con buscador, categorías, novedades y un estado del sistema. Es la ayuda para el cliente, '
        'distinta de esta documentación técnica.'),
     'tecnico': "Carpeta ayuda/: index.html (home), articulo.html (artículo por slug), novedades.html (changelog), estado.html (estado del sistema); consumen /api/ayuda/* (home, categorias, articulo, buscar, novedades); el worker genera OG por artículo. Es la ayuda de cara al cliente."},


    # ── PANEL ────────────────────────────────────────────────────────────
    {'area': 'panel', 'clave': 'doc-panel-admin', 'nivel': 'admin', 'orden': 1,
     'titulo': 'El Panel de Administración',
     'resumen': 'El centro de control de toda la plataforma.',
     'contenido': (
        'El Panel (admin/panel) es donde el equipo de TuKomercio administra TODO sin tocar código: usuarios, '
        'negocios, planes, funciones (feature flags), gamificación, reseñas, pagos, anuncios, auditoría, Centro de '
        'Ayuda, etc. Cada módulo se protege con permisos.'),
     'tecnico': "Archivo admin/panel/admin.html: SPA con sidebar fijo + área principal; API_BASE apunta a /api/admin; secciones (usuarios, negocios, planes, features, gamificación, reseñas, pagos, auditoría, centro de ayuda, documentación, etc.) cargadas de forma perezosa; usa getHeaders()+credentials para la sesión."},

    {'area': 'panel', 'clave': 'doc-panel-permisos', 'nivel': 'admin', 'orden': 2,
     'titulo': 'Roles y permisos del panel',
     'resumen': 'Quién puede hacer qué.',
     'contenido': (
        'Hay tres roles: SuperAdmin (control total), Admin (con permisos por módulo) y Moderador. El SuperAdmin '
        'asigna a cada sub-admin solo los módulos que necesita. Toda acción importante queda registrada en la '
        'auditoría (quién hizo qué y cuándo).'),
     'tecnico': "En src/api/admin_api.py: tabla administradores (rol superadmin/admin/moderator, permisos JSONB); decoradores @admin_required, @superadmin_required, @requiere_permiso('<modulo>'); catálogo MODULOS_PERMISOS; helpers is_admin(), admin_tiene_permiso(); registrar_auditoria() escribe en admin_audit_log con conexión/commit aislados."},


    # ── BASE DE DATOS ────────────────────────────────────────────────────
    {'area': 'base-datos', 'clave': 'doc-db-overview', 'nivel': 'admin', 'orden': 1,
     'titulo': 'Cómo se guardan los datos',
     'resumen': 'Las tablas principales del "archivador".',
     'contenido': (
        'La información vive en tablas de PostgreSQL. Las principales: usuarios, negocios, sucursales, productos '
        '(catálogo), compradores, pedidos, transacciones (contabilidad), gamificación (XP/TuKoins/insignias), '
        'planes y suscripciones, notificaciones, administradores y auditoría, y la base de conocimiento '
        '(ayuda + esta documentación). Cada negocio solo ve sus propios datos.'),
     'tecnico': "PostgreSQL (Neon) con SQLAlchemy 2.0. Tablas (PK): usuarios(id_usuario), negocios(id_negocio), sucursales(id_sucursal), productos_catalogo(id_producto), compradores(id_comprador), pedidos(id_pedido, codigo_pedido UK), transacciones_operativas, negocio_gamificacion(negocio_id UK), negocio_badges/_obtenidos, planes/negocio_plan/suscripciones_negocio, feature_flags/overrides, wompi_configs(negocio_id UK), notification, administradores(permisos JSONB), admin_audit_log, plataforma_kb(clave UK, tipo, nivel_acceso). FKs con CASCADE en dependientes del negocio. Indices en FKs y campos de busqueda (correo, slug, codigo_pedido)."},

    {'area': 'base-datos', 'clave': 'doc-db-multitenant', 'nivel': 'admin', 'orden': 2,
     'titulo': 'Un sistema, muchos negocios (multi-tenant)',
     'resumen': 'Cómo conviven todos sin mezclarse.',
     'contenido': (
        'Todos los negocios usan la misma plataforma y la misma base de datos, pero cada registro lleva el '
        'identificador de su negocio. Así, cada dueño solo ve y maneja lo suyo. Además, un mismo usuario puede '
        'tener varios negocios.'),
     'tecnico': "Aislamiento LOGICO (no fisico): casi toda tabla operativa lleva negocio_id (FK -> negocios.id_negocio). Relacion Usuario(1)->Negocios(N) por usuarios.id -> negocios.usuario_id. Las consultas filtran por negocio_id y se valida pertenencia (guard tenant/IDOR): la identidad viene de current_user (sesion), nunca de headers X-User-ID/X-Business-ID."},

    {'area': 'base-datos', 'clave': 'doc-db-jsonb', 'nivel': 'admin', 'orden': 3,
     'titulo': 'Datos flexibles (JSONB)',
     'resumen': 'Casillas que se adaptan sin rehacer el archivador.',
     'contenido': (
        'Algunas configuraciones (horarios, redes sociales, diseño de la tienda, tarifas de envío, permisos, los '
        'datos de un pedido) se guardan en un formato flexible llamado JSONB. Permite agregar o cambiar campos sin '
        'reconstruir la estructura de la base de datos.'),
     'tecnico': "Columnas JSONB reales: Negocio.config_tienda (Store Designer), Negocio.config_envios (tarifas), Negocio.horario_atencion, Negocio.redes_sociales; Administrador.permisos; Pedido.datos_comprador/datos_envio/datos_negocio/productos (snapshots); gamif_config.valor (overrides de gamificación); plataforma_kb.datos (incl. el detalle técnico de esta documentación)."},


    # ── LOTE 3: completar todas las secciones ────────────────────────────
    # AUTH
    {'area': 'auth', 'clave': 'doc-auth-sesiones', 'nivel': 'admin', 'orden': 1,
     'titulo': 'Sesiones y cookies',
     'resumen': 'Cómo recuerda la plataforma que ya iniciaste sesión.',
     'contenido': (
        'Al iniciar sesión, el servidor crea una "sesión" y le entrega al navegador una cookie segura '
        '(protegida, solo por HTTPS y sin acceso desde scripts). En cada petición, esa cookie identifica al '
        'usuario. La identidad SIEMPRE se decide en el servidor, nunca con datos que mande el navegador. No se '
        'usan "tokens JWT" como método principal, sino sesiones.'),
     'tecnico': "Flask-Login (UserMixin) + Flask-Session sobre SQLAlchemy. Cookie bizflow_session (SameSite=None, Secure, HttpOnly), PERMANENT_SESSION_LIFETIME ~7 dias, session_protection='strong'. user_loader carga Usuario y valida active. En login se regenera un session_token (secrets.token_urlsafe). Existe auth_jwt.py pero NO es el metodo principal."},

    # GAMIFICACIÓN
    {'area': 'gamificacion', 'clave': 'doc-gami-overview', 'nivel': 'publico', 'orden': 1,
     'titulo': '¿Qué es la gamificación?',
     'resumen': 'Convertir el uso de la plataforma en un juego que motiva.',
     'contenido': (
        'La gamificación premia al tendero por usar la plataforma y vender: gana experiencia (XP), sube de nivel, '
        'acumula una moneda virtual (TuKoins), completa misiones, gana insignias, compite en ligas y duelos, y '
        'puede invitar a otros (referidos). El objetivo es que sea divertido crecer el negocio.'),
     'tecnico': "Blueprint gamificacion_bp (src/api/gamificacion/gamificacion_api.py): dashboard (XP/nivel/TuKoins/racha), leaderboard, tienda de premios, duelos, referidos, feed de logros; el estado vive en NegocioGamificacion (agregar_xp, agregar_tukoins, calcular_nivel) e integra con Pedido (estado='entregado'), productos y videos."},

    {'area': 'gamificacion', 'clave': 'doc-gami-tecnico', 'nivel': 'admin', 'orden': 2,
     'titulo': 'Cómo funciona la gamificación por dentro',
     'resumen': 'Puntos automáticos, configurables y "a prueba de fallos".',
     'contenido': (
        'Cada acción importante (una venta, subir un producto, entrar a diario) dispara un "hook" que suma XP y '
        'TuKoins. Esos hooks están aislados: si la gamificación fallara, la venta o acción principal NO se ve '
        'afectada. Los valores (cuánto XP da cada cosa, misiones, eventos) son configurables desde el panel sin '
        'tocar código, con un valor por defecto de respaldo.'),
     'tecnico': "Hooks en src/api/gamificacion/gamificacion_hooks.py (on_venta_completada, on_login, etc.) en try/except con commit/rollback propio: si fallan no afectan la operación principal; config_gamificacion.py usa la tabla gamif_config (columna valor JSONB) con patrón DEFAULT-en-código + override-en-BD y helpers puros merge_*/validar_*/get_* que caen al DEFAULT si la BD falla."},

    # E-COMMERCE
    {'area': 'ecommerce', 'clave': 'doc-ecom-overview', 'nivel': 'admin', 'orden': 1,
     'titulo': 'El flujo de e-commerce',
     'resumen': 'Del catálogo a la venta.',
     'contenido': (
        'El dueño crea su catálogo (productos con foto, precio, stock). El cliente entra a la tienda, agrega al '
        'carrito, hace checkout (datos + envío + pago) y se genera un pedido. El dueño lo gestiona desde su panel y '
        'el stock se ajusta automáticamente al confirmar.'),
     'tecnico': "src/api/tiendas/checkout_api.py expone POST /api/tiendas/<slug>/checkout que crea Pedido con snapshots JSONB (datos_comprador, datos_envio, datos_negocio, productos), crea Comprador/DireccionComprador, envía email (Resend) y notificación, y dispara hooks de gamificación; soporta Wompi (claves en WompiConfig), Nequi, transferencia y efectivo."},

    {'area': 'ecommerce', 'clave': 'doc-ecom-estados', 'nivel': 'admin', 'orden': 2,
     'titulo': 'Estados de un pedido',
     'resumen': 'El ciclo de vida de una venta online.',
     'contenido': (
        'Un pedido avanza por estados: confirmado → preparando → enviado → en oficina → entregado (o cancelado). '
        'El dueño puede avanzar paso a paso o saltar directo a un estado con confirmación. Cada cambio queda en el '
        'historial del pedido, y al "enviar" se arma el aviso de WhatsApp para el cliente.'),
     'tecnico': "Modelo src/models/compradores/pedido.py: Pedido.estado (default 'pendiente', indexado) con estados reales pendiente, confirmado, preparando, enviado, en_camino, en_oficina, entregado, cancelado, devuelto; estado_pago aparte; el cambio (PUT /api/.../pedidos/<id>) registra en PedidoHistorial y dispara on_venta_completada() solo al llegar a 'entregado'."},

    # INTEGRACIONES
    {'area': 'integraciones', 'clave': 'doc-int-overview', 'nivel': 'admin', 'orden': 1,
     'titulo': 'Servicios externos que usamos',
     'resumen': 'Las herramientas de terceros conectadas.',
     'contenido': (
        '• Cloudinary: guarda y optimiza las fotos (las hace livianas).\n'
        '• Resend: envía los correos (recuperar contraseña, avisos).\n'
        '• Wompi: procesa pagos con tarjeta y PSE.\n'
        '• Groq: el motor de inteligencia artificial detrás de la asistente "Dora".\n'
        '• Cloudflare y Render: publican el frontend y el backend. Neon: la base de datos.'),
     'tecnico': "Cloudinary: cloudinary.uploader.upload en src/api/negocio/catalogo_api.py (folder productos_bizflow); Resend: envío de correos transaccionales (password_reset y checkout); Wompi: src/api/tiendas/wompi_api.py gestiona public_key/integrity_key en WompiConfig; Groq: src/api/ia/dora_api.py llama a api.groq.com (modelo llama-3.1-8b-instant) para la asistente Dora."},

    # FLUJOS
    {'area': 'flujos', 'clave': 'doc-flujo-pedido', 'nivel': 'publico', 'orden': 1,
     'titulo': 'El viaje de un pedido',
     'resumen': 'Qué pasa, paso a paso, cuando alguien compra.',
     'contenido': (
        '1. El cliente arma su carrito en la tienda pública.\n'
        '2. Llena sus datos y elige cómo pagar y recibir.\n'
        '3. El backend crea el pedido y descuenta stock; guarda una "foto" de los datos (cliente, envío, productos).\n'
        '4. Al dueño le llega una notificación.\n'
        '5. El dueño confirma y avanza estados; al enviar, avisa por WhatsApp.\n'
        '6. El cliente sigue su pedido con un enlace de resumen.'),
     'tecnico': "checkout_api.py crea el Pedido (snapshots JSONB) y descuenta stock; al cambiar el estado a 'entregado' en pedidos_api se llama gamificacion_hooks.on_venta_completada(negocio_id): otorga XP, verifica misiones y badges (BadgeVerificationService), emite notificaciones y procesa la recompensa de referido; el cliente sigue su pedido con el enlace de resumen."},

    {'area': 'flujos', 'clave': 'doc-flujo-login', 'nivel': 'admin', 'orden': 2,
     'titulo': 'El viaje de un inicio de sesión',
     'resumen': 'Cómo se valida quién entra.',
     'contenido': (
        '1. El usuario escribe correo y contraseña.\n'
        '2. El backend compara la contraseña de forma segura (cifrada con bcrypt) y revisa intentos fallidos.\n'
        '3. Si todo está bien, crea la sesión y entrega la cookie segura.\n'
        '4. A partir de ahí, cada pantalla sabe quién es sin volver a pedir clave.'),
     'tecnico': "src/api/auth/auth_system.py POST /api/auth/login valida el usuario y check_password() (bcrypt) con control de intentos; crea la sesión (current_user); luego on_login actualiza la racha en NegocioGamificacion/UsuarioGamificacion y otorga XP diario; nivel recalculado y notificación si sube."},

    {'area': 'flujos', 'clave': 'doc-flujo-imagen', 'nivel': 'admin', 'orden': 3,
     'titulo': 'El viaje de una imagen',
     'resumen': 'Qué pasa cuando subes una foto.',
     'contenido': (
        'Cuando subes la foto de un producto o tu logo, se envía a Cloudinary, que la guarda y genera versiones '
        'optimizadas (livianas) para que la tienda cargue rápido y los enlaces compartidos por WhatsApp se vean '
        'bien. En la base de datos solo se guarda la dirección (URL) de la imagen, no la imagen en sí.'),
     'tecnico': "En src/api/negocio/catalogo_api.py la subida usa cloudinary.uploader.upload(file, folder=\"productos_bizflow\", resource_type=\"auto\", overwrite=True) y guarda upload_result['secure_url'] en ProductoCatalogo (imagen principal o galería JSONB); en la BD solo se guarda la URL, no el binario."},

    # TERCEROS
    {'area': 'terceros', 'clave': 'doc-terceros-fallos', 'nivel': 'admin', 'orden': 1,
     'titulo': 'Servicios de terceros y qué pasa si fallan',
     'resumen': 'De qué dependemos y cómo se mitiga.',
     'contenido': (
        '• Neon (base de datos): si falla, la plataforma no opera; por eso usa conexiones con reintento.\n'
        '• Render (backend) y Cloudflare (frontend): si uno cae, la otra parte puede seguir mostrándose.\n'
        '• Cloudinary: si falla, las fotos nuevas no suben, pero la tienda sigue.\n'
        '• Resend: si falla, los correos no salen (la recuperación de clave se afecta).\n'
        '• Wompi: si falla, no se cobra en línea, pero quedan los otros métodos (contra entrega, Nequi…).\n'
        '• Groq: si falla, "Dora" no responde, pero el resto funciona.'),
     'tecnico': "Resiliencia real: hooks de gamificación en try/except con rollback aislado; wompi_api retorna {activo:false} si falla; notificaciones/emails del checkout atrapan y registran sin bloquear el pedido; dora_api.call_groq() maneja timeout/ConnectionError; el frontend _worker.js usa AbortController (timeout ~5s) en sus fetch."},

    # DESPLIEGUE
    {'area': 'despliegue', 'clave': 'doc-deploy-overview', 'nivel': 'admin', 'orden': 1,
     'titulo': 'Cómo se publica la plataforma',
     'resumen': 'Dónde vive y cómo sale a producción.',
     'contenido': (
        'El backend vive en Render y el frontend en Cloudflare Pages; la base de datos en Neon. Cuando se suben '
        'cambios al repositorio, Render y Cloudflare los publican automáticamente. El dominio principal es '
        'tukomercio.co.'),
     'tecnico': "Procfile: web: gunicorn run:run; run.py importa create_app() (src/__init__.py) que registra blueprints con safe_register() (src/api/__init__.py) e inicializa la BD con migraciones idempotentes; DATABASE_URL se normaliza postgres:// -> postgresql://. Hosting: Render (backend) + Cloudflare Pages (frontend) + Neon (BD)."},

    {'area': 'despliegue', 'clave': 'doc-deploy-migraciones', 'nivel': 'superadmin', 'orden': 2,
     'titulo': 'Cómo se actualizan las tablas (migraciones)',
     'resumen': 'Regla interna importante para no romper producción.',
     'contenido': (
        'Las reparaciones/ajustes de la base de datos se ejecutan automáticamente al ARRANCAR el backend, dentro '
        'de create_app(), de forma idempotente (no rompen ni duplican). Es una regla del proyecto (lección '
        'aprendida): poner las migraciones en el arranque y NO en run.py, porque en producción el inicio pasa por '
        'create_app(). Así los cambios de estructura aplican solos en cada despliegue.'),
     'tecnico': "Migraciones como lista de SQL en src/__init__.py::create_app() (ALTER TABLE ADD COLUMN IF NOT EXISTS, CREATE TABLE/INDEX IF NOT EXISTS), cada una en try/except con commit/rollback aislado. Idempotentes. Flask-Migrate/Alembic existe pero el flujo de prod es este. Regla F8: NO ponerlas solo en run.py o no corren en produccion. Publicaciones puntuales con flags en config_global (kb_publicacion_inicial, kb_iconos_bi_v1)."},

    # OPERACIÓN
    {'area': 'operacion', 'clave': 'doc-op-subadmins', 'nivel': 'admin', 'orden': 1,
     'titulo': 'Dar de alta sub-administradores',
     'resumen': 'Cómo el SuperAdmin reparte accesos.',
     'contenido': (
        'Desde el Panel, el SuperAdmin agrega administradores y les asigna SOLO los módulos que necesitan '
        '(por ejemplo, alguien que solo modere reseñas). El SuperAdmin tiene control total. Todo queda auditado.'),
     'tecnico': "En src/api/admin_api.py: tabla administradores (rol, permisos JSONB, activo); endpoints /api/admin/check, /api/admin/list, /api/admin/add (solo superadmin), /api/admin/remove/<id>; el SuperAdmin asigna permisos por módulo; cada acción se registra en admin_audit_log (admin_id, accion, entidad, detalle JSONB)."},

    {'area': 'operacion', 'clave': 'doc-op-feature-flags', 'nivel': 'admin', 'orden': 2,
     'titulo': 'Funciones y planes (feature flags)',
     'resumen': 'Encender/apagar funciones sin programar.',
     'contenido': (
        'Las funciones se pueden activar o desactivar desde el panel (feature flags), e incluso liberar poco a poco '
        '(a un % de negocios). Los planes (Básico, Pro, Premium, Deluxe) definen qué funciones incluye cada uno. '
        'Todo se administra sin tocar código.'),
     'tecnico': "src/api/admin_features_api.py + tablas feature_flags (key, activo_global, visible, orden) y feature_overrides (negocio_id, feature_key, habilitado); GET /api/admin/features, PUT /api/admin/features/<id>/toggle, POST/PUT para crear/editar; soporta rollout por porcentaje; el getter cae al default si la BD falla."},

    # RESPALDO
    {'area': 'respaldo', 'clave': 'doc-respaldo', 'nivel': 'superadmin', 'orden': 1,
     'titulo': 'Respaldo y recuperación de datos',
     'resumen': 'Cómo se protege la información.',
     'contenido': (
        'La base de datos (Neon) ofrece copias y recuperación a un punto en el tiempo. Recomendación: verificar '
        'periódicamente los respaldos y mantener export de datos clave. Es uno de los puntos críticos a cuidar al '
        'operar o entregar la plataforma.'),
     'tecnico': "Motor PostgreSQL en Neon (sslmode=require). src/models/database.py: pool_size=10, pool_recycle~280s, pool_pre_ping=True, connect_timeout=10, statement_timeout=30000ms; DATABASE_URL desde entorno con fallback. Neon ofrece copias y recuperación a un punto en el tiempo; conviene verificar respaldos periódicamente."},

    # PRUEBAS
    {'area': 'pruebas', 'clave': 'doc-pruebas', 'nivel': 'admin', 'orden': 1,
     'titulo': 'Cómo se prueba que todo funciona',
     'resumen': 'La plataforma tiene cientos de pruebas automáticas.',
     'contenido': (
        'El proyecto incluye una batería grande de pruebas automáticas (500+). Cada una valida una parte (por '
        'ejemplo, que la gamificación dé el XP correcto, que el acceso a la documentación respete los niveles, '
        'etc.) e imprime cuántas pasaron. Se corren antes de publicar cambios para no romper nada.'),
     'tecnico': "Carpeta src/tests_apis/ con decenas de scripts test_*.py (admin A1-A51, gamificación S1-S40, fixes y módulos nuevos); cada script imprime \"RESULTADO: N pasaron, M fallaron\" y retorna exit code; se ejecutan con PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_X.py antes de publicar."},

    # HANDOVER
    {'area': 'handover', 'clave': 'doc-handover', 'nivel': 'superadmin', 'orden': 1,
     'titulo': 'Entrega de la plataforma',
     'resumen': 'Qué se necesita para traspasarla a un comprador o técnico.',
     'contenido': (
        'Para entregar la plataforma se traspasan: los dos repositorios de código, las cuentas de los servicios '
        '(Render, Cloudflare, Neon, Cloudinary, Resend, Wompi, Groq), las variables de entorno (secretos) y los '
        'dominios. Más esta documentación. Un técnico nuevo puede entender el sistema leyendo estas secciones de '
        'arriba hacia abajo.'),
     'tecnico': "Para entregar: los 2 repositorios; cuentas de servicios (Render, Cloudflare, Neon, Cloudinary, Resend, Wompi, Groq); variables de entorno por nombre (DATABASE_URL, SECRET_KEY, MAIL_*, RESEND_API_KEY, CLOUDINARY_*, GROQ_API_KEY, VAPID_*, FRONTEND_URL); el Procfile/run.py; la suite de tests; y esta documentación. Un técnico nuevo puede leer estas secciones de arriba a abajo."},

    # LEGAL
    {'area': 'legal', 'clave': 'doc-legal', 'nivel': 'publico', 'orden': 1,
     'titulo': 'Propiedad y confidencialidad',
     'resumen': 'A quién pertenece y cómo se maneja.',
     'contenido': (
        'TuKomercio es propiedad de Carlos Eduardo Huérfano Bermúdez. El código y esta documentación son '
        'CONFIDENCIALES y constituyen un secreto comercial. La idea está en construcción y aún no patentada: no '
        'debe divulgarse ni compartirse sin autorización. Por eso esta documentación vive detrás de inicio de '
        'sesión y con niveles de acceso.'),
     'tecnico': "Cabecera (c) 2024-2026 Carlos Eduardo Huérfano Bermúdez en los archivos clave. Código y documentación CONFIDENCIALES (secreto comercial). Prohibido copiar, distribuir o hacer ingeniería inversa sin autorización. Jurisdicción: Colombia. Por eso esta documentación vive tras login y con niveles de acceso."},

    # NEGOCIO
    {'area': 'negocio', 'clave': 'doc-negocio-planes', 'nivel': 'publico', 'orden': 1,
     'titulo': 'Modelo de negocio y planes',
     'resumen': 'Cómo genera ingresos la plataforma.',
     'contenido': (
        'TuKomercio funciona por suscripción: el tendero usa la plataforma gratis el primer mes y luego elige un '
        'plan (Básico, Pro, Premium, Deluxe) que desbloquea más funciones. No cobra comisión por venta. El objetivo '
        'es masificar la digitalización de las tiendas de barrio en Colombia.'),
     'tecnico': "Tablas planes y suscripciones_negocio (negocio_id, plan_id, estado activa/cancelada/vencida, trial); endpoints en src/api/admin_features_api.py: GET /api/admin/planes, PUT /api/admin/negocios/<id>/plan, GET /api/planes (público). Planes con límites por nivel (productos, usuarios, funciones). Modelo: suscripción mensual, primer mes gratis, sin comisión por venta."},


    # ── LOTE 4 · DIAGRAMAS ───────────────────────────────────────────────
    {'area': 'diagramas', 'clave': 'diag-arquitectura', 'nivel': 'publico', 'orden': 1,
     'titulo': 'Diagrama: arquitectura general',
     'resumen': 'Cómo se conectan las piezas.',
     'contenido': (
        'Visitante / Comprador / Tendero\n'
        '            |\n'
        '            v\n'
        '   [ Navegador / App (PWA) ]\n'
        '            |  (HTTPS)\n'
        '            v\n'
        '   [ Cloudflare Pages + Worker ]   <- FRONTEND (HTML/CSS/JS)\n'
        '            |  (API, con cookie de sesión)\n'
        '            v\n'
        '   [ Render: Flask (gunicorn) ]    <- BACKEND (motor)\n'
        '            |\n'
        '   +--------+--------+----------------+-----------+\n'
        '   |        |        |                |           |\n'
        '   v        v        v                v           v\n'
        ' [Neon]  [Cloudinary] [Resend]      [Wompi]     [Groq]\n'
        '  BD      imágenes     correos       pagos     IA (Dora)\n'),
     'tecnico': "Componentes reales: navegador/PWA -> Cloudflare Pages (_worker.js) -> API -> Render (Flask/gunicorn, create_app) -> Neon (PostgreSQL); servicios externos Cloudinary (imágenes), Resend (correos), Wompi (pagos), Groq (IA Dora)."},

    {'area': 'diagramas', 'clave': 'diag-flujo-pedido', 'nivel': 'publico', 'orden': 2,
     'titulo': 'Diagrama: flujo de un pedido',
     'resumen': 'Del carrito a la entrega.',
     'contenido': (
        'Cliente -> arma carrito -> checkout (datos + envío + pago)\n'
        '   |\n'
        '   v\n'
        'Backend crea PEDIDO + descuenta stock + guarda "foto" de datos\n'
        '   |\n'
        '   v\n'
        'Notificación al tendero (campanita)\n'
        '   |\n'
        '   v\n'
        'Tendero: confirmado -> preparando -> enviado -> en_oficina -> entregado\n'
        '                                  |\n'
        '                                  v\n'
        '                       Aviso por WhatsApp al cliente (con guía)\n'
        '   |\n'
        '   v\n'
        'Cliente sigue su pedido con el enlace de resumen.'),
     'tecnico': "Traza real: checkout_api crea Pedido (snapshots JSONB) y descuenta stock; estados confirmado->preparando->enviado->en_oficina->entregado (FLUJO_ESTADOS del front); on_venta_completada() al entregar; aviso de WhatsApp al enviar."},

    {'area': 'diagramas', 'clave': 'diag-flujo-login', 'nivel': 'admin', 'orden': 3,
     'titulo': 'Diagrama: inicio de sesión',
     'resumen': 'Cómo se valida quién entra.',
     'contenido': (
        'Usuario -> (correo + contraseña)\n'
        '   |\n'
        '   v\n'
        'Backend: ¿demasiados intentos fallidos? --sí--> bloqueo temporal\n'
        '   | no\n'
        '   v\n'
        'Compara contraseña (bcrypt, segura)\n'
        '   |--- incorrecta ---> error\n'
        '   v correcta\n'
        'Crea sesión + entrega cookie segura (HttpOnly/Secure)\n'
        '   |\n'
        '   v\n'
        'Cada pantalla ya sabe quién eres (sin volver a pedir clave).'),
     'tecnico': "Traza real: auth_system.login -> control de intentos (seguridad.py) -> Usuario.check_password (bcrypt) -> sesión Flask-Login (cookie bizflow_session) -> hooks de racha/XP diario."},

    {'area': 'diagramas', 'clave': 'diag-niveles', 'nivel': 'publico', 'orden': 4,
     'titulo': 'Diagrama: niveles de acceso a esta documentación',
     'resumen': 'Quién ve qué.',
     'contenido': (
        'Visitante sin login            -> NADA (todo está detrás de login)\n'
        'Usuario autenticado            -> 🟢 Público\n'
        'Admin con permiso documentación-> 🟢 Público + 🟡 Interno\n'
        'Admin + step-up de SuperAdmin  -> 🟢 + 🟡 + 🔴 Crítico (30 min)\n'
        '\n'
        'El backend filtra por nivel; el navegador nunca decide qué se muestra.'),
     'tecnico': "Implementación: docs_tecnicas_api.niveles_visibles(unlocked) decide publico/admin/superadmin; el endpoint filtra por nivel; superadmin requiere el flag de sesión docs_superadmin_unlocked_at con TTL 1800s (step-up)."},


    # ── LOTE 4 · REFERENCIA DE ENDPOINTS (por dominio) ───────────────────
    {'area': 'endpoints', 'clave': 'ep-intro', 'nivel': 'admin', 'orden': 0,
     'titulo': 'Cómo leer esta referencia',
     'resumen': 'Las "puertas" del backend, agrupadas por tema.',
     'contenido': (
        'El backend expone varios cientos de endpoints (más de 500), agrupados en blueprints por tema. Aquí va un '
        'resumen de los principales: MÉTODO ruta → para qué sirve. La mayoría requiere sesión iniciada y que el '
        'recurso pertenezca al negocio del usuario.'),
     'tecnico': "Registro central en src/api/__init__.py::register_api(app) con safe_register(module_path, bp_name, display_name, prefix): importa el módulo, toma el blueprint y lo registra; tolerante a fallos (try/except por módulo, cuenta éxitos/fallos). Orden: auth primero, admin al final."},

    {'area': 'endpoints', 'clave': 'ep-auth', 'nivel': 'admin', 'orden': 1,
     'titulo': 'Endpoints · Autenticación',
     'resumen': 'Login, sesión y recuperación de contraseña.',
     'contenido': (
        'POST /api/auth/login → iniciar sesión\n'
        'POST /api/auth/logout → cerrar sesión\n'
        'GET  /api/auth/session/verify → ¿sesión activa?\n'
        'GET  /api/auth/user/profile → perfil del usuario\n'
        'POST /forgot-password → pedir recuperación\n'
        'GET  /verify-reset-token/<token> → validar token\n'
        'POST /reset-password → cambiar contraseña'),
     'tecnico': "Archivos src/api/auth/auth_system.py (auth_bp, url_prefix=/api/auth) y password_reset_api.py (password_reset_bp). Rutas: POST /api/auth/login, POST /api/auth/logout, GET /api/auth/session/verify; reset vía Resend usando RESEND_API_KEY/MAIL_FROM y enlace con FRONTEND_URL + token."},

    {'area': 'endpoints', 'clave': 'ep-negocio', 'nivel': 'admin', 'orden': 2,
     'titulo': 'Endpoints · Negocio y sucursales',
     'resumen': 'Crear y administrar negocios.',
     'contenido': (
        'POST /api/negocios/crear → crear negocio (genera QR)\n'
        'GET  /api/mis-negocios → listar mis negocios\n'
        'GET  /api/negocios/<id> → detalle\n'
        'PUT  /api/negocios/<id> → actualizar\n'
        'DELETE /api/negocios/<id> → eliminar (papelera)\n'
        'GET  /api/negocio/slug/<slug> → datos públicos por slug (lo usa la tienda)\n'
        'POST /api/sucursales/crear → crear sucursal'),
     'tecnico': "Archivo src/api/negocio/negocio_completo_api.py (negocio_api_bp, url_prefix=/api): crear/listar/ver/editar/eliminar negocios, auto-generación de QR (qrcode), slug, multi-sucursal e integración con MecaLink."},

    {'area': 'endpoints', 'clave': 'ep-catalogo', 'nivel': 'admin', 'orden': 3,
     'titulo': 'Endpoints · Catálogo e inventario',
     'resumen': 'Productos y stock.',
     'contenido': (
        'GET  /api/inventario/productos → listar productos\n'
        'POST /api/catalogo/producto/guardar → crear\n'
        'PUT  /api/producto/actualizar/<id> → actualizar\n'
        'DELETE /api/producto/eliminar/<id> → eliminar\n'
        'POST /api/producto/<id>/stock → ajustar stock\n'
        'GET  /api/stock/alertas → productos con stock bajo\n'
        'GET  /api/inventario/estadisticas → resumen'),
     'tecnico': "Archivo src/api/negocio/catalogo_api.py (catalogo_api_bp, url_prefix=/api): CRUD de productos del negocio (nombre, descripción, precio, costo, stock, categoría, variantes, dropshipping), subida de imágenes a Cloudinary y acumulado de ventas."},

    {'area': 'endpoints', 'clave': 'ep-tienda-pedidos', 'nivel': 'admin', 'orden': 4,
     'titulo': 'Endpoints · Tienda, checkout y pedidos',
     'resumen': 'La compra y su gestión.',
     'contenido': (
        'GET  /api/tiendas/<slug>/catalogo → catálogo público\n'
        'POST /api/tiendas/<slug>/checkout → procesar compra\n'
        'GET  /api/pedidos → listar pedidos del negocio\n'
        'GET  /api/pedidos/<id> → detalle del pedido\n'
        'PUT  /api/pedidos/<id>/estado → cambiar estado\n'
        'POST /api/pedidos/<id>/cancelar → cancelar\n'
        'POST /api/devoluciones/crear → registrar devolución'),
     'tecnico': "Archivos src/api/tiendas/checkout_api.py (checkout_api_bp) y pedidos_api.py (tiendas_pedidos_bp). Checkout: POST /api/tiendas/<slug>/checkout (crea Comprador + DireccionComprador + Pedido). Gestión: listar pedidos del negocio y cambiar estado; crea notificación en la tabla notification."},

    {'area': 'endpoints', 'clave': 'ep-pagos', 'nivel': 'admin', 'orden': 5,
     'titulo': 'Endpoints · Pagos y cupones',
     'resumen': 'Cobros en línea y descuentos.',
     'contenido': (
        'POST /api/wompi/transaccion → crear pago (tarjeta/PSE)\n'
        'GET  /api/wompi/status/<tx> → estado del pago\n'
        'POST /api/negocio/<id>/cupones → crear cupón\n'
        'GET  /api/negocio/<id>/cupones → listar cupones\n'
        'POST /api/cupones/validar → validar código en checkout'),
     'tecnico': "Archivo src/api/tiendas/wompi_api.py (wompi_bp): GET /api/negocio/<id>/wompi/config-pub (público: activo + public_key), GET/PUT config (panel del tendero); modelo WompiConfig (public_key, integrity_key, activo, ambiente). Cupones en src/api/tiendas/cupones_api.py."},

    {'area': 'endpoints', 'clave': 'ep-crm-analytics', 'nivel': 'admin', 'orden': 6,
     'titulo': 'Endpoints · CRM, reseñas y analítica',
     'resumen': 'Clientes, opiniones y métricas.',
     'contenido': (
        'GET  /api/negocio/<id>/crm/compradores → clientes\n'
        'GET  /api/negocio/<id>/crm/resumen → métricas CRM\n'
        'POST /api/compradores/magic-link → enlace sin contraseña\n'
        'POST /api/resena → crear reseña\n'
        'GET  /api/negocio/<id>/resenas → reseñas públicas\n'
        'GET  /api/negocio/<id>/analytics/resumen → visitas/conversión\n'
        'GET  /api/negocio/<id>/trust → franja de confianza'),
     'tecnico': "Archivos src/api/tiendas/crm_api.py (crm_bp): resumen, lista de compradores e historial; analytics_api.py: dashboard y /trust (rating, reseñas, \"miembro desde\"); resenas_api.py: crear/moderar reseñas de productos."},

    {'area': 'endpoints', 'clave': 'ep-gamificacion', 'nivel': 'admin', 'orden': 7,
     'titulo': 'Endpoints · Gamificación',
     'resumen': 'XP, TuKoins, misiones, ligas.',
     'contenido': (
        'GET  /api/gamificacion/dashboard → estado (XP/nivel/TuKoins/racha)\n'
        'GET  /api/gamificacion/leaderboard → ranking\n'
        'GET  /api/gamificacion/tienda → tienda de premios\n'
        'POST /api/gamificacion/tienda/comprar → canjear TuKoins\n'
        'POST /api/gamificacion/duelos/retar → duelo\n'
        'GET  /api/gamificacion/referidos/mi-codigo → referidos'),
     'tecnico': "Archivo src/api/gamificacion/gamificacion_api.py (gamificacion_bp, url_prefix=/api): dashboard, misiones/completar, leaderboard, tukoins/<id>, tienda y tienda/comprar; motor NegocioGamificacion + tabla gamif_config (JSONB) configurable sin redeploy."},

    {'area': 'endpoints', 'clave': 'ep-notificaciones', 'nivel': 'admin', 'orden': 8,
     'titulo': 'Endpoints · Notificaciones y chat',
     'resumen': 'La campanita y los mensajes.',
     'contenido': (
        'GET  /api/notificaciones → listar (campanita)\n'
        'PUT  /api/notificaciones/<id>/marcar-leida → marcar leída\n'
        'POST /api/notificaciones/<id>/aceptar → aceptar\n'
        'GET  /api/chat → conversaciones\n'
        'POST /api/chat/<user_id> → enviar mensaje'),
     'tecnico': "Archivos src/api/notifications/*.py (show/accept/reject/detail + chat). Tabla notification (user_id, sender_id, titulo, message, type, prioridad, is_read, referencia_*, action_url, extra_data JSONB, timestamp). Rutas: listar, marcar leída, aceptar/rechazar; chat con sus mensajes."},

    {'area': 'endpoints', 'clave': 'ep-ia', 'nivel': 'admin', 'orden': 9,
     'titulo': 'Endpoints · Dora IA',
     'resumen': 'La asistente con inteligencia artificial.',
     'contenido': (
        'POST /api/ia/chat → conversar con Dora\n'
        'POST /api/ia/describir-producto → descripción automática\n'
        'POST /api/ia/generar-promo → texto de promoción\n'
        'POST /api/ia/analizar-ventas → análisis\n'
        'POST /api/ia/sugerir-precio → sugerencia de precio'),
     'tecnico': "Archivo src/api/ia/dora_api.py (dora_bp, url_prefix=/api): /ia/chat, /ia/describir-producto, /ia/generar-promo, /ia/clasificar-gasto, /ia/analizar-ventas, /ia/sugerir-precio; usa GROQ_API_KEY (modelo llama-3.1-8b-instant) e inyecta contexto del negocio (productos, transacciones, alertas)."},

    {'area': 'endpoints', 'clave': 'ep-admin', 'nivel': 'admin', 'orden': 10,
     'titulo': 'Endpoints · Panel de administración',
     'resumen': 'Lo que usa el equipo de TuKomercio.',
     'contenido': (
        'GET  /api/admin/check → ¿soy admin?\n'
        'GET  /api/admin/stats → estadísticas generales\n'
        'GET  /api/admin/audit → log de auditoría\n'
        'GET/POST /api/admin/features → feature flags\n'
        'GET  /api/admin/planes → planes\n'
        'CRUD /api/admin/ayuda → Centro de Ayuda\n'
        'CRUD /api/admin/docs → esta documentación (+ /unlock, /export)'),
     'tecnico': "Archivo src/api/admin_api.py (admin_bp, url_prefix=/api/admin): check, list, add (superadmin), remove, challenges, stats, audit, asignar plan; decoradores de permiso + psycopg2 para consultas puntuales; auditoría con registrar_auditoria() a admin_audit_log."},

    {'area': 'endpoints', 'clave': 'ep-verticales', 'nivel': 'admin', 'orden': 11,
     'titulo': 'Endpoints · Verticales (taller, restaurante, mecánicos)',
     'resumen': 'Funciones especializadas por rubro.',
     'contenido': (
        'Taller:      /api/taller/ordenes, /api/taller/citas, /api/taller/stats\n'
        'Restaurante: /api/restaurante/mesas, /api/restaurante/comandas, carta pública\n'
        'MecaLink:    /api/mecalink/buscar, /api/mecalink/perfil/<id>, verificación'),
     'tecnico': "Archivos src/api/taller/taller_api.py (taller_bp), restaurante/restaurante_api.py (restaurante_bp) y mecalink/mecalink_api.py (mecalink_bp, url_prefix=/api/mecalink). Taller: órdenes y citas. Restaurante: mesas y comandas (carta pública). MecaLink: búsqueda de mecánicos, perfil público y verificación."},


    # ── AUDITORIA DB (Sprint 1): tablas nucleo con columnas reales ──
    {'area': 'base-datos', 'clave': "db-tabla-usuarios", 'nivel': 'admin', 'orden': 10,
     'titulo': "Tabla: usuarios",
     'resumen': "Las cuentas que inician sesión (dueños/empleados).",
     'contenido': "Guarda las cuentas de las personas que usan la plataforma (dueños de negocio y empleados). Su contraseña va cifrada.",
     'tecnico': "Tabla 'usuarios'. Columnas: id_usuario (PK), nombre, apellidos, correo (UK, idx), contrasenia (hash bcrypt), confirmacion_contrasenia, profesion, cedula (BigInteger, UK, idx), celular (BigInteger), foto_url, active, validate, black_list, pais_id, ciudad_id (FK->colombia.ciudad_id), created_at, updated_at, last_login, acepto_terminos, fecha_aceptacion_terminos."},
    {'area': 'base-datos', 'clave': "db-tabla-negocios", 'nivel': 'admin', 'orden': 11,
     'titulo': "Tabla: negocios",
     'resumen': "El corazón multi-tenant: cada tienda/empresa.",
     'contenido': "Cada negocio (tienda) de la plataforma. Pertenece a un usuario y de él cuelga casi todo (productos, pedidos, etc.).",
     'tecnico': "Tabla 'negocios'. Columnas: id_negocio (PK), nombre_negocio (idx), descripcion, direccion, telefono, categoria (idx), email, sitio_web, horario_atencion (JSONB), video_portafolio, redes_sociales (JSONB), tiene_pagina, plantilla_id, slug (UK, idx), color_tema, whatsapp, tipo_pagina, logo_url, config_tienda (JSONB - Store Designer), config_envios (JSONB - tarifas), verificado, ciudad, qr_negocio_url, qr_negocio_data, perfil_publico, fecha_registro, fecha_actualizacion, activo, plan_key (idx), plan_actual_id (FK->planes.id, ondelete SET NULL), ciudad_id (FK->colombia), usuario_id (FK->usuarios)."},
    {'area': 'base-datos', 'clave': "db-tabla-sucursales", 'nivel': 'admin', 'orden': 12,
     'titulo': "Tabla: sucursales",
     'resumen': "Las sedes de un negocio.",
     'contenido': "Los puntos de venta/sedes de un negocio (si maneja varios locales).",
     'tecnico': "Tabla 'sucursales'. Columnas: id_sucursal (PK), nombre_sucursal, direccion, ciudad, departamento, codigo_postal, latitud, longitud, telefono, email, activo, es_principal, cajeros, administradores, fecha_registro, fecha_actualizacion, negocio_id (FK->negocios)."},
    {'area': 'base-datos', 'clave': "db-tabla-productos", 'nivel': 'admin', 'orden': 13,
     'titulo': "Tabla: productos_catalogo",
     'resumen': "Los productos de cada tienda.",
     'contenido': "El catálogo: cada producto con su precio, costo, stock, fotos, variantes, badges y promociones.",
     'tecnico': "Tabla 'productos_catalogo'. Columnas: id_producto (PK), nombre, descripcion, precio, precio_original, costo, precio_historico_min, referencia_sku, codigo_barras, imagen_url, imagenes, videos, categoria, plan, etiquetas, stock, stock_minimo, stock_critico, stock_bajo, total_ventas, rating_promedio, total_reviews, velocidad_venta, badge_destacado, badge_mas_vendido, badge_envio_gratis, badges_data, personalizacion_activa, personalizacion_config, variantes, promo_inicio, promo_fin, promo_badge_texto, es_dropshipping, activo, estado_publicacion, fecha_creacion, fecha_actualizacion, negocio_id (FK->negocios)."},
    {'area': 'base-datos', 'clave': "db-tabla-categorias", 'nivel': 'admin', 'orden': 14,
     'titulo': "Tabla: categorias_producto",
     'resumen': "Las categorías para organizar el catálogo.",
     'contenido': "Las categorías con las que el dueño organiza sus productos (aparecen como filtros en la tienda).",
     'tecnico': "Tabla 'categorias_producto'. Columnas: id_categoria (PK), usuario_id, negocio_id, nombre, icono, color, orden, activo, featured, fecha_creacion."},
    {'area': 'base-datos', 'clave': "db-tabla-movimientos-stock", 'nivel': 'admin', 'orden': 15,
     'titulo': "Tabla: movimientos_stock",
     'resumen': "El historial de cambios de inventario (kardex).",
     'contenido': "Cada entrada/salida de stock queda registrada aquí para auditar el inventario.",
     'tecnico': "Tabla 'movimientos_stock'. Columnas: id_movimiento (PK), producto_id, transaccion_id, usuario_id, negocio_id, sucursal_id, tipo (entrada/salida), cantidad, stock_anterior, stock_nuevo, nota, fecha."},
    {'area': 'base-datos', 'clave': "db-tabla-transacciones", 'nivel': 'admin', 'orden': 16,
     'titulo': "Tabla: transacciones_operativas",
     'resumen': "El libro financiero del negocio.",
     'contenido': "Los movimientos de dinero del negocio (ventas, compras, gastos, ingresos) para la contabilidad.",
     'tecnico': "Tabla 'transacciones_operativas'. Columnas: id_transaccion (PK), negocio_id, usuario_id, sucursal_id, tipo (venta/compra/gasto/ingreso), concepto, monto, categoria, metodo_pago, referencia_guia, fecha, notas, anulada, motivo_anulacion."},
    {'area': 'base-datos', 'clave': "db-tabla-compradores", 'nivel': 'admin', 'orden': 17,
     'titulo': "Tabla: compradores",
     'resumen': "Los clientes que compran en las tiendas.",
     'contenido': "Los clientes (registrados o invitados) que hacen pedidos. Los invitados acceden por un enlace mágico (token).",
     'tecnico': "Tabla 'compradores'. Columnas: id_comprador (PK), nombre, apellidos, correo (UK, idx), telefono (idx), password_hash (NULL si invitado), tipo_documento, numero_documento (idx), token_acceso (UK, magic link), usuario_id (FK->usuarios, SET NULL), es_registrado, verificado, activo, acepta_marketing, preferencias (JSONB), fecha_registro, ultima_compra, total_compras, total_gastado."},
    {'area': 'base-datos', 'clave': "db-tabla-pedidos", 'nivel': 'admin', 'orden': 18,
     'titulo': "Tabla: pedidos",
     'resumen': "Las órdenes de compra de las tiendas.",
     'contenido': "Cada pedido que llega a una tienda. Guarda una 'foto' (snapshot) de los datos del cliente, envío, negocio y productos al momento de la compra.",
     'tecnico': "Tabla 'pedidos'. Columnas: id_pedido (PK), codigo_pedido (UK, idx), comprador_id (FK), negocio_id (idx), sucursal_id, direccion_id (FK), datos_comprador (JSONB), datos_envio (JSONB), datos_negocio (JSONB), productos (JSONB), subtotal, descuento, costo_envio, impuestos, total (Numeric 12,2), metodo_pago, estado_pago, referencia_pago, metodo_contacto, estado (idx), notas_cliente, notas_vendedor, fecha_pedido (idx), fecha_confirmacion, fecha_preparacion, fecha_envio, fecha_entrega, fecha_cancelacion, motivo_cancelacion, numero_guia, transportadora, url_tracking, imagen_guia_url, ip_cliente, user_agent, origen, fecha_creacion, fecha_actualizacion."},
    {'area': 'base-datos', 'clave': "db-tabla-pedido-historial", 'nivel': 'admin', 'orden': 19,
     'titulo': "Tabla: pedido_historial",
     'resumen': "El rastro de cambios de estado de un pedido.",
     'contenido': "Cada vez que un pedido cambia de estado, queda registrado aquí (quién y cuándo).",
     'tecnico': "Tabla 'pedido_historial'. Columnas: id_historial (PK), pedido_id (FK->pedidos), estado_anterior, estado_nuevo, comentario, usuario_id, fecha."},

    # ── AUDITORIA DB (Sprint 2): tablas de gamificacion (columnas reales) ──
    {'area': 'base-datos', 'clave': "db-tabla-negocio-gamificacion", 'nivel': 'admin', 'orden': 20,
     'titulo': "Tabla: negocio_gamificacion",
     'resumen': "El estado de juego de cada negocio.",
     'contenido': "Guarda el progreso de gamificación del negocio: experiencia, nivel, monedas y rachas.",
     'tecnico': "Tabla 'negocio_gamificacion'. Columnas: id (PK), negocio_id (UK), xp_total, nivel, tukoins, prestigio, onboarding_completado, racha_actividad_dias, racha_actividad_max, racha_actividad_fecha, created_at, updated_at."},
    {'area': 'base-datos', 'clave': "db-tabla-usuario-gamificacion", 'nivel': 'admin', 'orden': 21,
     'titulo': "Tabla: usuario_gamificacion",
     'resumen': "El progreso de juego por usuario (empleado).",
     'contenido': "Progreso de gamificación a nivel de usuario (XP personal, racha de inicios de sesión).",
     'tecnico': "Tabla 'usuario_gamificacion'. Columnas: id (PK), usuario_id (UK), xp_personal, nivel, racha_login_dias, racha_login_max, racha_login_fecha, created_at, updated_at."},
    {'area': 'base-datos', 'clave': "db-tabla-misiones-completadas", 'nivel': 'admin', 'orden': 22,
     'titulo': "Tabla: negocio_misiones_completadas",
     'resumen': "Las misiones que ha cumplido cada negocio.",
     'contenido': "Registra cada misión completada por un negocio y la recompensa que dio.",
     'tecnico': "Tabla 'negocio_misiones_completadas'. Columnas: id (PK), negocio_id, gamificacion_id, mision_codigo, fecha, xp_ganado, tukoins_ganados, tipo (diaria/semanal/mensual), created_at."},
    {'area': 'base-datos', 'clave': "db-tabla-tukoins-transacciones", 'nivel': 'admin', 'orden': 23,
     'titulo': "Tabla: tukoins_transacciones",
     'resumen': "El movimiento de la moneda virtual (TuKoins).",
     'contenido': "Cada ingreso o gasto de TuKoins, con el saldo resultante (como un extracto).",
     'tecnico': "Tabla 'tukoins_transacciones'. Columnas: id (PK), negocio_id, gamificacion_id, tipo (ingreso/gasto), concepto, cantidad, balance_tras, fecha."},
    {'area': 'base-datos', 'clave': "db-tabla-tienda-items", 'nivel': 'admin', 'orden': 24,
     'titulo': "Tabla: tienda_items",
     'resumen': "El catálogo de premios canjeables con TuKoins.",
     'contenido': "Los artículos que se pueden comprar con TuKoins (plantillas, destacados, cosméticos).",
     'tecnico': "Tabla 'tienda_items'. Columnas: id (PK), codigo, nombre, descripcion, tipo, icono, precio_tukoins, nivel_requerido, css_value, imagen_preview, activo, created_at."},
    {'area': 'base-datos', 'clave': "db-tabla-tienda-compras", 'nivel': 'admin', 'orden': 25,
     'titulo': "Tabla: tienda_compras",
     'resumen': "Lo que cada negocio ha canjeado en la tienda de premios.",
     'contenido': "Historial de compras de items con TuKoins por negocio.",
     'tecnico': "Tabla 'tienda_compras'. Columnas: id (PK), negocio_id, item_id (FK->tienda_items), tukoins_gastados, activo, fecha_compra."},
    {'area': 'base-datos', 'clave': "db-tabla-gamif-config", 'nivel': 'admin', 'orden': 26,
     'titulo': "Tabla: gamif_config",
     'resumen': "La configuración editable de la gamificación.",
     'contenido': "Patrón 'constante en código con override en BD': aquí viven los valores ajustables (XP por evento, misiones, bonos) sin tocar código.",
     'tecnico': "Tabla 'gamif_config'. Columnas: clave (PK), valor (JSONB), updated_at. Llaves típicas en valor: xp_eventos, misiones_override, bono_tukoins, eventos_especiales, retos_mensuales, recompensas_liga, referidos_config, rachas."},
    {'area': 'base-datos', 'clave': "db-tabla-negocio-badges", 'nivel': 'admin', 'orden': 27,
     'titulo': "Tabla: negocio_badges",
     'resumen': "El catálogo de insignias disponibles.",
     'contenido': "Define cada insignia: cómo se ve, su categoría/nivel y el criterio para ganarla.",
     'tecnico': "Tabla 'negocio_badges'. Columnas: id (PK), codigo, nombre, descripcion, icono, color_primario, color_fondo, gradiente, imagen_url, categoria, nivel, puntos, criterio_tipo, criterio_valor, criterio_operador, activo, visible_en_catalogo, es_secreto, orden, es_exclusivo, max_otorgamientos, fecha_creacion, fecha_actualizacion, total_otorgados, editado_admin, vigencia_inicio, vigencia_fin."},
    {'area': 'base-datos', 'clave': "db-tabla-badges-obtenidos", 'nivel': 'admin', 'orden': 28,
     'titulo': "Tabla: negocio_badges_obtenidos",
     'resumen': "Las insignias que cada negocio ya ganó.",
     'contenido': "Relaciona negocios con las insignias ganadas (y si las vieron, si están activas, etc.).",
     'tecnico': "Tabla 'negocio_badges_obtenidos'. Columnas: id (PK), negocio_id, badge_id (FK->negocio_badges), fecha_obtencion, valor_al_desbloquear, contexto, notificado, fecha_notificacion, visto, fecha_visto, activo, fecha_revocacion, motivo_revocacion, veces_asignado_videos, es_favorito."},
    {'area': 'base-datos', 'clave': "db-tabla-duelos", 'nivel': 'admin', 'orden': 29,
     'titulo': "Tabla: duelos",
     'resumen': "Los retos 1v1 entre negocios.",
     'contenido': "Competencias entre dos negocios durante un periodo; gana quien venda más.",
     'tecnico': "Tabla 'duelos'. Columnas: id (PK), retador_negocio_id, retado_negocio_id, estado, fecha_inicio, fecha_fin, creado_en, ganador_negocio_id, ventas_retador, ventas_retado."},
    {'area': 'base-datos', 'clave': "db-tabla-referidos", 'nivel': 'admin', 'orden': 30,
     'titulo': "Tabla: referidos",
     'resumen': "El programa de invitaciones entre usuarios.",
     'contenido': "Quién invitó a quién y si esa invitación se convirtió (primera venta) y fue recompensada.",
     'tecnico': "Tabla 'referidos'. Columnas: id (PK), referidor_usuario_id, referido_usuario_id, fecha_registro, convertido, fecha_conversion, recompensado."},

    # ── AUDITORIA DB (Sprint 3): tablas admin/plataforma (columnas reales) ──
    {'area': 'base-datos', 'clave': "db-tabla-administradores", 'nivel': 'admin', 'orden': 40,
     'titulo': "Tabla: administradores",
     'resumen': "Quiénes administran la plataforma.",
     'contenido': "Las cuentas del equipo de TuKomercio con acceso al panel, su rol y sus permisos.",
     'tecnico': "Tabla 'administradores'. Columnas: id (PK), email (UK), nombre, rol (superadmin/admin/moderator), permisos (JSONB - lista de módulos), activo, created_at, created_by, updated_at."},
    {'area': 'base-datos', 'clave': "db-tabla-admin-audit", 'nivel': 'admin', 'orden': 41,
     'titulo': "Tabla: admin_audit_log",
     'resumen': "El registro de todo lo que hacen los admins.",
     'contenido': "Auditoría: cada acción del panel queda registrada (quién, qué, cuándo, desde dónde).",
     'tecnico': "Tabla 'admin_audit_log'. Columnas: id (PK), admin_id (FK->administradores), admin_email, accion, entidad, entidad_id, detalle (JSONB), ip, user_agent, created_at (idx)."},
    {'area': 'base-datos', 'clave': "db-tabla-feature-flags", 'nivel': 'admin', 'orden': 42,
     'titulo': "Tabla: feature_flags",
     'resumen': "Los interruptores de funciones.",
     'contenido': "Permite encender/apagar funciones de la plataforma (globalmente o por % de negocios) sin tocar código.",
     'tecnico': "Tabla 'feature_flags'. Columnas: id (PK), key (UK), nombre, descripcion, categoria, activo_global, visible, icono, orden, rollout_pct, created_at, updated_at."},
    {'area': 'base-datos', 'clave': "db-tabla-feature-overrides", 'nivel': 'admin', 'orden': 43,
     'titulo': "Tabla: feature_overrides",
     'resumen': "Excepciones de funciones por negocio.",
     'contenido': "Activa o desactiva una función para un negocio específico (override del flag global).",
     'tecnico': "Tabla 'feature_overrides'. Columnas: id (PK), negocio_id, feature_key, habilitado, created_by, created_at."},
    {'area': 'base-datos', 'clave': "db-tabla-planes", 'nivel': 'admin', 'orden': 44,
     'titulo': "Tabla: planes",
     'resumen': "Los planes de suscripción.",
     'contenido': "Define los planes (Básico, Pro, etc.): nombre, precios, color e ícono.",
     'tecnico': "Tabla 'planes'. Columnas: id (PK), key, nombre, descripcion, precio_mensual, precio_anual, orden, color, icono, activo, created_at."},
    {'area': 'base-datos', 'clave': "db-tabla-plan-features", 'nivel': 'admin', 'orden': 45,
     'titulo': "Tabla: plan_features",
     'resumen': "Qué funciones incluye cada plan.",
     'contenido': "Relaciona planes con funciones y sus límites/configuración.",
     'tecnico': "Tabla 'plan_features'. Columnas: id (PK), plan_id (FK->planes), feature_id, limite, config_json."},
    {'area': 'base-datos', 'clave': "db-tabla-negocio-plan", 'nivel': 'admin', 'orden': 46,
     'titulo': "Tabla: negocio_plan",
     'resumen': "El plan asignado actualmente a cada negocio.",
     'contenido': "Qué plan tiene un negocio en este momento, desde/hasta cuándo y quién lo asignó.",
     'tecnico': "Tabla 'negocio_plan'. Columnas: id (PK), negocio_id, plan_id (FK->planes), fecha_inicio, fecha_fin, activo, asignado_por, notas, created_at."},
    {'area': 'base-datos', 'clave': "db-tabla-suscripciones", 'nivel': 'admin', 'orden': 47,
     'titulo': "Tabla: suscripciones_negocio",
     'resumen': "El ciclo de suscripción del negocio (trial, renovación).",
     'contenido': "Maneja el periodo de prueba, fechas, estado y renovación de la suscripción de cada negocio.",
     'tecnico': "Tabla 'suscripciones_negocio'. Columnas: id (PK), negocio_id, plan_id, estado, es_trial, fecha_inicio_trial, fecha_fin_trial, fecha_inicio, fecha_fin, fecha_renovacion, dias_gracia, renovacion_automatica, trial_usado, alertas_enviadas, creado_por, modificado_por, notas, created_at, updated_at."},
    {'area': 'base-datos', 'clave': "db-tabla-pagos-suscripcion", 'nivel': 'admin', 'orden': 48,
     'titulo': "Tabla: pagos_suscripcion",
     'resumen': "Los pagos que hace el tendero por su plan.",
     'contenido': "Cómo paga cada negocio su suscripción a TuKomercio (montos, estado, comprobante).",
     'tecnico': "Tabla 'pagos_suscripcion'. Columnas: id (PK), suscripcion_id (FK), negocio_id, monto, moneda, metodo_pago, estado, referencia, comprobante_url, periodo_inicio, periodo_fin, notas, registrado_por, created_at, updated_at."},
    {'area': 'base-datos', 'clave': "db-tabla-config-global", 'nivel': 'admin', 'orden': 49,
     'titulo': "Tabla: config_global",
     'resumen': "Ajustes globales de la plataforma.",
     'contenido': "Configuración general clave-valor (p. ej. flags internos como kb_publicacion_inicial, modo mantenimiento).",
     'tecnico': "Tabla 'config_global'. Columnas: clave (PK), valor (JSONB), updated_at."},
    {'area': 'base-datos', 'clave': "db-tabla-plataforma-kb", 'nivel': 'admin', 'orden': 50,
     'titulo': "Tabla: plataforma_kb",
     'resumen': "La base de conocimiento (ayuda + esta documentación).",
     'contenido': "Tabla flexible que alimenta el Centro de Ayuda, Novedades y ESTA documentación técnica.",
     'tecnico': "Tabla 'plataforma_kb'. Columnas: id (PK), tipo (feature/categoria/articulo/changelog/tecnico/visual), area (idx), clave (UK), titulo, resumen, contenido, datos (JSONB - incluye 'tecnico'), orden, publicado (idx), nivel_acceso (idx: publico/admin/superadmin), created_at, updated_at."},
    {'area': 'base-datos', 'clave': "db-tabla-notification", 'nivel': 'admin', 'orden': 51,
     'titulo': "Tabla: notification",
     'resumen': "Las notificaciones de la campanita.",
     'contenido': "Avisos in-app para los usuarios (nuevos pedidos, pagos, logros, etc.).",
     'tecnico': "Tabla 'notification'. Columnas: id (PK), user_id, sender_id, negocio_id, type, titulo, message, referencia_tipo, referencia_id, action_url, is_read, is_accepted, prioridad, request_id, response, request_message_details, questions, extra_data (JSONB), timestamp, fecha_lectura."},
    {'area': 'base-datos', 'clave': "db-tabla-message", 'nivel': 'admin', 'orden': 52,
     'titulo': "Tabla: message",
     'resumen': "Los mensajes del chat.",
     'contenido': "Mensajes directos asociados a una notificación/conversación.",
     'tecnico': "Tabla 'message'. Columnas: id (PK), notification_id (FK), sender_id, receiver_id, content, timestamp."},
    {'area': 'base-datos', 'clave': "db-tabla-leads", 'nivel': 'admin', 'orden': 53,
     'titulo': "Tabla: leads_campana",
     'resumen': "Los prospectos de venta de TuKomercio.",
     'contenido': "Leads de la campaña comercial (a quién contactar para que se una), con su estado y recordatorios.",
     'tecnico': "Tabla 'leads_campana'. Columnas: id (PK), nombre, telefono, nicho, info_adicional, estado, prioridad, origen, fecha_primer_contacto, fecha_ultimo_mensaje, proximo_recordatorio, mensajes_enviados, created_at, updated_at."},
    {'area': 'base-datos', 'clave': "db-tabla-plantillas-mensajes", 'nivel': 'admin', 'orden': 54,
     'titulo': "Tabla: plantillas_mensajes",
     'resumen': "Las plantillas de mensajes para leads.",
     'contenido': "Textos reutilizables para contactar leads por WhatsApp/correo.",
     'tecnico': "Tabla 'plantillas_mensajes'. Columnas: id (PK), nombre, cuerpo, orden, activa, created_at, updated_at."},

    # ── AUDITORIA DB (Sprints 4-5): tienda/extra + verticales + legacy ──
    {'area': 'base-datos', 'clave': "db-tabla-cupones", 'nivel': 'admin', 'orden': 60,
     'titulo': "Tabla: cupones",
     'resumen': "Los códigos de descuento.",
     'contenido': "Cupones de descuento por negocio que el cliente aplica en el checkout.",
     'tecnico': "Tabla 'cupones'. Columnas: id (PK), negocio_id, codigo, descripcion, tipo (porcentaje/monto), valor, min_compra, max_descuento, usos_max, usos_actuales, fecha_inicio, fecha_fin, activo, created_at."},
    {'area': 'base-datos', 'clave': "db-tabla-carritos", 'nivel': 'admin', 'orden': 61,
     'titulo': "Tabla: carritos_abandonados",
     'resumen': "Carritos que no terminaron en compra.",
     'contenido': "Guarda carritos abandonados para hacer seguimiento y recuperarlos.",
     'tecnico': "Tabla 'carritos_abandonados'. Columnas: id (PK), negocio_id, telefono, nombre, correo, productos (JSONB), total_estimado, num_items, estado, pedido_id, created_at, updated_at."},
    {'area': 'base-datos', 'clave': "db-tabla-tienda-visitas", 'nivel': 'admin', 'orden': 62,
     'titulo': "Tabla: tienda_visitas",
     'resumen': "El conteo de visitas a la tienda.",
     'contenido': "Métrica de tráfico: visitas por día a la tienda del negocio.",
     'tecnico': "Tabla 'tienda_visitas'. Columnas: id (PK), negocio_id, fecha, contador."},
    {'area': 'base-datos', 'clave': "db-tabla-wompi-configs", 'nivel': 'admin', 'orden': 63,
     'titulo': "Tabla: wompi_configs",
     'resumen': "Las llaves de pago Wompi por negocio.",
     'contenido': "Configuración de la pasarela Wompi de cada negocio (claves y ambiente).",
     'tecnico': "Tabla 'wompi_configs'. Columnas: id (PK), negocio_id, public_key, integrity_key, events_key, ambiente (test/prod), activo, updated_at. (Las llaves son sensibles.)"},
    {'area': 'base-datos', 'clave': "db-tabla-direcciones", 'nivel': 'admin', 'orden': 64,
     'titulo': "Tabla: direcciones_comprador",
     'resumen': "Las direcciones de envío de los clientes.",
     'contenido': "Direcciones guardadas de cada comprador (puede tener varias).",
     'tecnico': "Tabla 'direcciones_comprador'. Columnas: id_direccion (PK), comprador_id (FK), tipo_direccion, alias, pais, departamento, ciudad, localidad, barrio, codigo_postal, direccion, complemento, referencias, nombre_establecimiento, datos_especiales, latitud, longitud, es_principal, activo, fecha_creacion, fecha_actualizacion."},
    {'area': 'base-datos', 'clave': "db-tabla-producto-estadisticas", 'nivel': 'admin', 'orden': 65,
     'titulo': "Tabla: producto_estadisticas",
     'resumen': "Métricas por producto.",
     'contenido': "Estadísticas diarias de cada producto (visitas, agregados al carrito, compras, ingresos).",
     'tecnico': "Tabla 'producto_estadisticas'. Columnas: id (PK), producto_id, negocio_id, fecha, visitas, agregados_carrito, compras, ingresos, created_at."},
    {'area': 'base-datos', 'clave': "db-tabla-producto-precios", 'nivel': 'admin', 'orden': 66,
     'titulo': "Tabla: producto_precios_historico",
     'resumen': "El historial de precios de un producto.",
     'contenido': "Cada cambio de precio queda registrado para análisis.",
     'tecnico': "Tabla 'producto_precios_historico'. Columnas: id (PK), producto_id, negocio_id, precio, precio_original, fecha, created_at."},
    {'area': 'base-datos', 'clave': "db-tabla-producto-reviews", 'nivel': 'admin', 'orden': 67,
     'titulo': "Tabla: producto_reviews",
     'resumen': "Las reseñas de productos.",
     'contenido': "Opiniones de clientes sobre productos (estrellas + comentario), con moderación.",
     'tecnico': "Tabla 'producto_reviews'. Columnas: id (PK), producto_id, negocio_id, cliente_nombre, cliente_email, rating, titulo, comentario, verificado, aprobado, fecha, created_at."},
    {'area': 'base-datos', 'clave': "db-tabla-alertas", 'nivel': 'admin', 'orden': 68,
     'titulo': "Tabla: alertas_operativas",
     'resumen': "Tareas/alertas del negocio.",
     'contenido': "Recordatorios y alertas operativas (tareas con prioridad y fecha).",
     'tecnico': "Tabla 'alertas_operativas'. Columnas: id_alerta (PK), negocio_id, usuario_id, tarea, prioridad, tipo, completada, fecha_programada, fecha_completada, fecha_creacion."},
    {'area': 'base-datos', 'clave': "db-tabla-link-invitaciones", 'nivel': 'admin', 'orden': 69,
     'titulo': "Tabla: link_invitaciones",
     'resumen': "Enlaces para invitar empleados.",
     'contenido': "Tokens de invitación para que alguien se una al equipo de un negocio.",
     'tecnico': "Tabla 'link_invitaciones'. Columnas: id (PK), negocio_id, rol, token, activo, usos, created_at, updated_at."},
    {'area': 'base-datos', 'clave': "db-tabla-empleados", 'nivel': 'admin', 'orden': 70,
     'titulo': "Tabla: empleados_negocio",
     'resumen': "El equipo de cada negocio.",
     'contenido': "Los usuarios que forman parte del equipo de un negocio y su rol.",
     'tecnico': "Tabla 'empleados_negocio'. Columnas: id (PK), negocio_id, usuario_id, link_id, nombre, email, rol, estado, unido_en."},
    {'area': 'base-datos', 'clave': "db-tabla-negocio-perfil", 'nivel': 'admin', 'orden': 71,
     'titulo': "Tabla: negocio_perfil_config",
     'resumen': "La configuración del perfil público avanzado.",
     'contenido': "Ajustes finos del perfil público del negocio (qué métricas/secciones mostrar, SEO, contadores).",
     'tecnico': "Tabla 'negocio_perfil_config'. Columnas: id, negocio_id, layout_config, etapas_habilitadas, dias_post_servicio, contratado_puede_calificar, tema, color_primario, color_secundario, color_acento, gradiente_custom, fondo_tipo, fondo_valor, mostrar_score_global, mostrar_score_contratante, mostrar_score_contratado, mostrar_total_contratos, mostrar_tiempo_respuesta, mostrar_tasa_exito, mostrar_clientes_recurrentes, mostrar_disputas, mostrar_percentil, max_videos, max_badges_por_video, autoplay_videos, mostrar_metricas_en_video, mostrar_resenas, max_resenas_visibles, permitir_respuesta_resenas, mostrar_resenas_negativas, mostrar_whatsapp, mostrar_email, mostrar_telefono, mostrar_ubicacion, mostrar_horarios, mostrar_redes_sociales, botones_config, meta_titulo, meta_descripcion, meta_keywords, og_image, total_visitas, visitas_mes_actual, total_compartidos, total_clicks_tienda, total_clicks_whatsapp, fecha_creacion, fecha_actualizacion."},
    {'area': 'base-datos', 'clave': "db-tabla-negocio-videos", 'nivel': 'admin', 'orden': 72,
     'titulo': "Tabla: negocio_videos",
     'resumen': "Los videos del negocio (portafolio/feed).",
     'contenido': "Videos cortos del negocio con sus métricas y estado de moderación (feed tipo Reels).",
     'tecnico': "Tabla 'negocio_videos'. Columnas: id, negocio_id, titulo, descripcion, url_video, url_thumbnail, url_video_hd, fuente, video_id_externo, duracion_segundos, ancho, alto, formato, tamanio_bytes, calidad, metrica_nombre, metrica_valor, metrica_tendencia, metrica_icono, metrica_color, vistas, vistas_unicas, likes, compartidos, tiempo_visto_promedio, porcentaje_completado, clicks_tienda, clicks_whatsapp, clicks_perfil, orden, visible, destacado, en_feed_publico, autoplay, loop, muted_default, estado_moderacion, fecha_moderacion, motivo_rechazo, moderado_por, fecha_creacion, fecha_actualizacion, fecha_publicacion."},
    {'area': 'base-datos', 'clave': "db-tabla-ordenes-trabajo", 'nivel': 'admin', 'orden': 73,
     'titulo': "Tabla: ordenes_trabajo",
     'resumen': "Las órdenes de trabajo (vertical Taller).",
     'contenido': "Órdenes de servicio del taller: vehículo, diagnóstico, estado y totales.",
     'tecnico': "Tabla 'ordenes_trabajo'. Columnas: id (PK), numero_ot, negocio_id, placa, marca, modelo, anio, kilometraje, color, tipo_vehiculo, cliente_nombre, cliente_telefono, cliente_email, problema_reportado, diagnostico, observaciones, estado, estado_pago, metodo_pago, fecha_ingreso, fecha_entrega_estimada, fecha_entrega_real, fecha_actualizacion, subtotal_servicios, subtotal_repuestos, descuento, total."},
    {'area': 'base-datos', 'clave': "db-tabla-items-ot", 'nivel': 'admin', 'orden': 74,
     'titulo': "Tabla: items_orden_trabajo",
     'resumen': "Los ítems de una orden de trabajo.",
     'contenido': "Servicios/repuestos que componen una orden de taller.",
     'tecnico': "Tabla 'items_orden_trabajo'. Columnas: id (PK), orden_id (FK), tipo (servicio/repuesto), descripcion, cantidad, precio_unitario, subtotal, producto_id."},
    {'area': 'base-datos', 'clave': "db-tabla-citas-taller", 'nivel': 'admin', 'orden': 75,
     'titulo': "Tabla: citas_taller",
     'resumen': "Las citas del taller.",
     'contenido': "Agendamiento de citas que pueden convertirse en órdenes de trabajo.",
     'tecnico': "Tabla 'citas_taller'. Columnas: id (PK), numero_cita, negocio_id, cliente_nombre, cliente_telefono, placa, tipo_vehiculo, servicio_solicitado, notas, fecha_cita, duracion_minutos, estado, orden_trabajo_id, fecha_creacion."},
    {'area': 'base-datos', 'clave': "db-tabla-mesas", 'nivel': 'admin', 'orden': 76,
     'titulo': "Tabla: mesas_restaurante",
     'resumen': "Las mesas (vertical Restaurante).",
     'contenido': "Las mesas del restaurante y su estado.",
     'tecnico': "Tabla 'mesas_restaurante'. Columnas: id (PK), negocio_id, numero, nombre, capacidad, estado, activa."},
    {'area': 'base-datos', 'clave': "db-tabla-comandas", 'nivel': 'admin', 'orden': 77,
     'titulo': "Tabla: comandas",
     'resumen': "Las comandas del restaurante.",
     'contenido': "Pedidos por mesa o para llevar, con su estado y totales.",
     'tecnico': "Tabla 'comandas'. Columnas: id (PK), numero_comanda, negocio_id, mesa_id (FK), tipo, cliente_nombre, cliente_telefono, direccion_entrega, estado, estado_pago, metodo_pago, subtotal, descuento, propina, total, notas, fecha_apertura, fecha_cierre."},
    {'area': 'base-datos', 'clave': "db-tabla-items-comanda", 'nivel': 'admin', 'orden': 78,
     'titulo': "Tabla: items_comanda",
     'resumen': "Los ítems de una comanda.",
     'contenido': "Los platos/productos de cada comanda.",
     'tecnico': "Tabla 'items_comanda'. Columnas: id (PK), comanda_id (FK), producto_id, nombre_item, precio_unitario, cantidad, subtotal, notas, estado."},
    {'area': 'base-datos', 'clave': "db-tabla-mecanicos", 'nivel': 'admin', 'orden': 79,
     'titulo': "Tabla: mecanicos_mecalink",
     'resumen': "Los mecánicos (vertical MecaLink).",
     'contenido': "Perfil de mecánicos: zonas, servicios, disponibilidad, calificación y verificación.",
     'tecnico': "Tabla 'mecanicos_mecalink'. Columnas: id (PK), negocio_id, zonas_texto, zonas_array, ciudad_operacion, servicios, precios_servicios, disponibilidad_texto, disponibilidad_detalle, tiene_vehiculo, tipo_vehiculo, tiene_herramientas, herramientas_detalle, experiencia, experiencia_anios, especialidades, certificaciones, calificacion_promedio, total_calificaciones, total_servicios, calificaciones_desglose, estado, verificado_mecalink, fecha_verificacion, nivel, comision_porcentaje, total_comisiones_pagadas, total_ingresos_generados, fecha_registro, fecha_actualizacion, notas_admin."},
    {'area': 'base-datos', 'clave': "db-tabla-colombia", 'nivel': 'admin', 'orden': 80,
     'titulo': "Tabla: colombia",
     'resumen': "Catálogo de ciudades + estadísticas (legacy).",
     'contenido': "Catálogo de ciudades de Colombia (usado para ubicación de usuarios/negocios). Incluye métricas agregadas heredadas del sistema anterior (Trayectoria).",
     'tecnico': "Tabla 'colombia'. Columnas clave: ciudad_id (PK), ciudad_nombre; + ~40 métricas legacy (servicios_insatisfechos, precio_promedio_servicios, porcentajes demográficos por edad, usuarios_N_servicios, tasas de crecimiento/retención/churn, valor_envio, etc.). En TuKomercio se usa principalmente como catálogo de ciudades."},
    {'area': 'base-datos', 'clave': "db-tabla-password-reset", 'nivel': 'admin', 'orden': 81,
     'titulo': "Tabla: password_reset_tokens",
     'resumen': "Los tokens de recuperación de contraseña.",
     'contenido': "Tokens temporales de un solo uso para restablecer la contraseña.",
     'tecnico': "Tabla 'password_reset_tokens'. Columnas: id (PK), user_id (FK->usuarios), token, created_at, expires_at, used, used_at."},
    {'area': 'base-datos', 'clave': "db-tabla-monetization", 'nivel': 'admin', 'orden': 82,
     'titulo': "Tabla: monetization_management",
     'resumen': "Gestión de monetización por usuario (legacy).",
     'contenido': "Registro de pagos/planes a nivel de usuario heredado del sistema anterior.",
     'tecnico': "Tabla 'monetization_management' (legacy). Columnas: id_monetizacion (PK), usuario_id, rol_usuario, plan, monto_pago, moneda, metodo_pago, fecha_pago, codigo_qr, estado_qr, fecha_transaccion_qr, funcionalidades_habilitadas, duracion_plan, fecha_expiracion, estado_pago, notificacion_pago."},
    {'area': 'base-datos', 'clave': "db-tabla-badges-traj", 'nivel': 'admin', 'orden': 83,
     'titulo': "Tabla: badges (Trayectoria)",
     'resumen': "Catálogo de insignias del sistema anterior (legacy).",
     'contenido': "Insignias de aprendizaje del sistema Trayectoria (distinto de negocio_badges de TuKomercio).",
     'tecnico': "Tabla 'badges' (legacy Trayectoria). Columnas: id (PK), badge_id, nombre, descripcion, emoji, color, color_rgb, categoria, criterio_tipo, criterio_valor, criterio_descripcion, rareza, orden, activo, fecha_creacion."},
    {'area': 'base-datos', 'clave': "db-tabla-user-badges", 'nivel': 'admin', 'orden': 84,
     'titulo': "Tabla: user_badges (legacy)",
     'resumen': "Insignias ganadas por usuario (legacy).",
     'contenido': "Relación usuario-insignia del sistema Trayectoria.",
     'tecnico': "Tabla 'user_badges' (legacy). Columnas: id (PK), usuario_id, badge_id, desbloqueado, fecha_desbloqueo, motivo_desbloqueo, valor_alcanzado, mostrar_en_perfil, fecha_creacion."},
    {'area': 'base-datos', 'clave': "db-tabla-etapas", 'nivel': 'admin', 'orden': 85,
     'titulo': "Tabla: etapas / fotos / audios / videos (legacy)",
     'resumen': "Contenido por etapas del sistema anterior (legacy).",
     'contenido': "Estructura de etapas y multimedia del sistema Trayectoria. Poco usada en TuKomercio.",
     'tecnico': "Legacy Trayectoria. 'etapas': id_etapa, nombre, servicio_id. 'fotos': id_foto, url, etapa_id. 'audios': id_audio, url, etapa_id. 'videos': id_video, url, etapa_id."},
    {'area': 'base-datos', 'clave': "db-tabla-portfolio", 'nivel': 'admin', 'orden': 86,
     'titulo': "Tabla: portfolio_videos (legacy)",
     'resumen': "Videos de portafolio de usuario (legacy).",
     'contenido': "Portafolio de videos por usuario del sistema anterior.",
     'tecnico': "Tabla 'portfolio_videos' (legacy). Columnas: id (PK), usuario_id, titulo, descripcion, url, thumbnail_url, duracion, duracion_segundos, vistas, likes, metricas_asociadas, badges_asociados, activo, destacado, promovido, fecha_promocion, fecha_subida, fecha_actualizacion, orden."},
    {'area': 'base-datos', 'clave': "db-tabla-user-scores", 'nivel': 'admin', 'orden': 87,
     'titulo': "Tabla: user_scores / *_history / *_stage / metrics (legacy)",
     'resumen': "Puntajes y métricas de usuario (legacy).",
     'contenido': "Sistema de puntajes del sistema Trayectoria (contratante/contratado/global) y métricas configurables.",
     'tecnico': "Legacy Trayectoria. 'user_scores': id, usuario_id, score_contratante, score_contratado, score_global, cambios, percentil, fechas. 'user_score_history': id, usuario_id, score, tipo_score, fecha. 'user_stage_scores': id, usuario_id, stage_id, stage_number, stage_name, score, is_public, metrics, color, fechas. 'user_metrics': id, usuario_id, metric_key, metric_value, metric_display, metric_name, metric_icon, metric_color, cambios, is_public, is_system, categoria, orden, fechas."},
    {'area': 'base-datos', 'clave': "db-tabla-servicio", 'nivel': 'admin', 'orden': 88,
     'titulo': "Tabla: servicio (legacy/B2B)",
     'resumen': "Servicios contratados entre usuarios (legacy).",
     'contenido': "Modelo de servicios/contratos del sistema anterior (contratante-contratado), con calificación bidireccional.",
     'tecnico': "Tabla 'servicio' (legacy). Columnas: id_servicio (PK), nombre_servicio, descripcion, categoria, fechas (solicitud/aceptacion/inicio/fin), id_usuario, id_contratante, id_contratado, nombre_contratante, negocio_contratante_id, negocio_contratado_id, tipo_contrato, service_active, estado, precio, moneda, etapas_calificacion, etapas_habilitadas, dias_post_servicio, calificacion_bidireccional, aditional_service, viajar_dentro_pais, viajar_fuera_pais, domicilios, incluye_asesoria, requiere_presencia_cliente, experiencia_previa, facturacion_formal, modelos_negocio, qr_code, qr_data, ciudad_id, fechas."},

    # ── AUDITORIA FRONTEND/DEPLOY (DA11/DA16): archivos reales ──
    {'area': "frontend", 'clave': "bf-designer-js", 'nivel': "admin", 'orden': 90,
     'titulo': "Archivo: designer.js (el Diseñador por dentro)",
     'contenido': "El JavaScript que hace funcionar el editor visual de la tienda (el Diseñador).",
     'tecnico': "designer.js (~245KB). Flujo de datos: loadStoreData() (merge de la config del backend) -> applyConfigToInputs() (puebla el DOM con esa config) -> updatePreview() (lee el DOM de vuelta hacia storeConfig); el orden importa (poblar antes de leer, leccion F18). Funciones clave: applyFonts, applyPreset/aplicarPaquete, applyTemplateSections, applyPlanGating (gating por plan), debounce, _renderOgImageEstado, createUpgradeModal/closeUpgradeModal/contactForUpgrade. Editores por seccion con add*/delete*: categorias, hero badges, horarios y carta (restaurante), pasos y servicios (taller), stats, testimonios, videos, why-items, slider y galeria."},
    {'area': "frontend", 'clave': "bf-super-designer-js", 'nivel': "admin", 'orden': 91,
     'titulo': "Archivo: super_designer y módulos sd_*",
     'contenido': "El editor avanzado de páginas y sus módulos.",
     'tecnico': "super_designer.html + super_designer.js (Engine) + 19 modulos sd_*.js: sd_ai, sd_animations, sd_clickedit, sd_collab, sd_colors, sd_components, sd_css, sd_dragdrop, sd_export, sd_intelligence, sd_media, sd_mobile, sd_perf, sd_polish, sd_seo, sd_social, sd_typography, sd_undo, sd_versions. Se comunica con las plantillas por postMessage (tuko-runtime.js)."},
    {'area': "frontend", 'clave': "bf-sw", 'nivel': "admin", 'orden': 92,
     'titulo': "Archivo: sw.js (Service Worker / PWA)",
     'contenido': "Hace que la plataforma funcione como app instalable y cargue rápido (offline-friendly).",
     'tecnico': "sw.js SW_VERSION='2.1.0'. Estrategias por tipo: la API (onrender) network-only (no cachea); HTML network-first (con cache como respaldo offline); .js/.css y /assets stale-while-revalidate (responde de cache y revalida en segundo plano). En install precachea assets base; en activate purga caches viejos (tukomercio-v*) y toma control. Maneja push y notificationclick (enfoca/abre el panel). Manifest: tukomercio-manifest.json."},
    {'area': "frontend", 'clave': "bf-contabilidad-modulos", 'nivel': "admin", 'orden': 93,
     'titulo': "Archivos: módulos de contabilidad (21 pantallas)",
     'contenido': "Las pantallas de gestión del día a día del negocio (la app del tendero).",
     'tecnico': "Carpeta contabilidad/modulos/ (21 .html): alertas, analytics, carga_csv, carritos, compra, crm, cupones, dashboard, dropshipping, equipo, gamificacion, gastos, ingreso_div, inventario, offline, pedidos, reportes, restaurante, taller, venta, wompi. Mas contabilidad/grilla_financiera.html (Centro de Control Financiero). Cada vista consume la API del negocio."},
    {'area': "despliegue", 'clave': "bf-create-app-migraciones", 'nivel': "admin", 'orden': 94,
     'titulo': "create_app: migraciones y seeders",
     'contenido': "Cómo se crean/actualizan las tablas y se siembran los datos al arrancar el backend.",
     'tecnico': "src/__init__.py::create_app() ejecuta ~62 sentencias idempotentes (ALTER TABLE ADD COLUMN IF NOT EXISTS / CREATE TABLE IF NOT EXISTS / CREATE INDEX IF NOT EXISTS) en una lista 'migraciones', cada una en try/except con commit aislado (regla F8: van aqui, no en run.py). Seeders idempotentes: inicializar_badges_sistema (catalogo de insignias), poblar_ciudades() (Colombia), seed_plataforma_kb() (ayuda/novedades), seed_docs_tecnicas() (esta documentacion). Flags one-time en config_global: kb_publicacion_inicial, kb_iconos_bi_v1, kb_ep_rutas_v2."},

    # ── SISTEMA VISUAL / MARCA (paleta, tipografia, tokens) ──
    {'area': 'diseno', 'clave': "doc-diseno-vision", 'nivel': "publico", 'orden': 1,
     'titulo': "La visión: un editor visual con alma de red social",
     'contenido': "TuKomercio no es solo un creador de tiendas: es un EDITOR VISUAL —al estilo de un software de diseño como Photoshop, Adobe o Sony Vegas— pero orientado a RED SOCIAL, para crear tiendas virtuales. La idea es que diseñar y administrar tu tienda se sienta tan fácil, visual y atractivo como usar una app social: arrastrar elementos, elegir colores y tipografías, secciones y animaciones, con ayuda de IA; y al mismo tiempo vivir como red social (perfiles públicos, seguir, me gusta, feed de videos, logros y gamificación). El objetivo: bajar la barrera técnica y volver divertido crear tu negocio en línea.",
     'tecnico': "Esta visión se materializa en el Diseñador (designer.js) y el Super Designer (motor + módulos sd_*: drag&drop, colors, typography, animations, ai, components, versions), que editan visualmente la config de la tienda; y en la capa social (interacciones de Seguir/Me gusta, feed de videos negocio_videos, gamificación: XP/TuKoins/insignias/ligas). El sistema visual común vive en assets/css/design-tokens.css (variables --tk-*)."},
    {'area': 'diseno', 'clave': "doc-diseno-paleta", 'nivel': "admin", 'orden': 2,
     'titulo': "Paleta de colores",
     'contenido': "Los colores oficiales de la marca, usados en toda la plataforma para que se vea coherente.",
     'tecnico': "Definidos en assets/css/design-tokens.css. Marca: --tk-indigo #4F46E5, --tk-indigo-dark #4338CA, --tk-indigo-soft #EEF2FF, --tk-violet #7C3AED. Gradientes: --tk-grad-1 #667eea + --tk-grad-2 #764ba2 -> --tk-gradient (135deg); --tk-gradient-hero (claro). Neutros (slate): --tk-ink #0F172A (texto), --tk-slate #475569, --tk-slate-2 #64748B, --tk-line #E7E9F0 (bordes), --tk-bg #F7F8FC (fondo app), --tk-card #FFFFFF, --tk-soft #F1F2F9. Estados: --tk-success #10B981, --tk-warning/--tk-amber #F59E0B, --tk-danger #EF4444, --tk-wa #25D366 (WhatsApp); soft: success-soft #D1FAE5, amber-soft #FEF3C7. Modo oscuro: --tk-dark #0F0F1A, --tk-dark-2 #1E293B, --tk-dark-line rgba(255,255,255,.10), --tk-on-dark #E4E4F0."},
    {'area': 'diseno', 'clave': "doc-diseno-tipografia", 'nivel': "admin", 'orden': 3,
     'titulo': "Tipografías",
     'contenido': "Las familias de letra y los tamaños que usa la plataforma.",
     'tecnico': "3 familias (Google Fonts), en design-tokens.css: --tk-font-wordmark 'Orbitron' (SOLO el logotipo/wordmark), --tk-font-display 'Sora' (títulos), --tk-font-ui 'Plus Jakarta Sans' (texto/cuerpo). Escala fluida (clamp): --tk-fs-d1 clamp(2rem,6vw,3.2rem), --tk-fs-h1 clamp(1.7rem,4.5vw,2.5rem), --tk-fs-h2 clamp(1.35rem,3vw,1.8rem), --tk-fs-h3 1.25rem, --tk-fs-body 1rem, --tk-fs-sm .9rem, --tk-fs-xs .8rem. Tracking: --tk-tracking-tight -.02em (títulos), --tk-tracking-wordmark .01em. Íconos: Bootstrap Icons 1.13.1 (<i class='bi bi-...'>)."},
    {'area': 'diseno', 'clave': "doc-diseno-fondos", 'nivel': "admin", 'orden': 4,
     'titulo': "Fondos, bordes, sombras y estructura",
     'contenido': "Cómo se ven los fondos, las esquinas redondeadas, las sombras y el espaciado.",
     'tecnico': "design-tokens.css. Fondos: --tk-bg #F7F8FC (app), --tk-card #FFFFFF (superficies), --tk-soft #F1F2F9, gradientes --tk-gradient y --tk-gradient-hero. Radios: --tk-r-xs 8px, --tk-r-sm 12px, --tk-r 16px (default), --tk-r-lg 22px, --tk-r-pill 999px. Sombras: --tk-shadow, --tk-shadow-lg, --tk-shadow-hover, --tk-glow (todas con tinte índigo). Espaciado/estructura: --tk-gap 16px, --tk-pad 20px, --tk-maxw 1120px. Movimiento: --tk-ease cubic-bezier(.4,0,.2,1), --tk-fast .15s, --tk-med .25s. Capas: --tk-z-header 50, --tk-z-modal 1000, --tk-z-toast 1500."},
    {'area': 'diseno', 'clave': "doc-diseno-tokens", 'nivel': "admin", 'orden': 5,
     'titulo': "El sistema de diseño (design-tokens.css)",
     'contenido': "Un solo archivo define toda la apariencia, para que cada vista se vea igual de profesional.",
     'tecnico': "assets/css/design-tokens.css es la ÚNICA fuente de verdad visual: importa las fuentes (Sora/Plus Jakarta/Orbitron) y Bootstrap Icons 1.13.1, y declara ~56 variables --tk-* (paleta, gradientes, tipografía, radios, sombras, espaciado, motion, z-index, modo oscuro) + utilidades opt-in (.tk-wordmark, etc.) y prefers-reduced-motion. Cualquier vista que lo incluya hereda la identidad. Aplicado en: login, landing (crea-tu-tienda), resumen de pedido, app/studio, panel admin, designer, Centro de Ayuda y /documentacion."},
]

# DA6 — rutas REALES extraídas de los archivos (refresco forzado una vez, flag kb_ep_rutas_v2)
EP_REFRESH = {
 'ep-auth': "Archivo src/api/auth/auth_system.py (auth_bp, /api/auth). Rutas reales: POST /login, POST /ingreso (alias), POST /refresh, GET /session/verify, GET /session_status, POST|GET /logout, GET /user/profile, GET /health. Recuperación (password_reset_api.py, password_reset_bp): POST /forgot-password, GET /verify-reset-token/<token>, POST /reset-password, GET /test-smtp, GET /test-send/<email>. Login Flask-Login + bcrypt (cookie bizflow_session).",
 'ep-negocio': "Archivo src/api/negocio/negocio_completo_api.py (negocio_api_bp, /api). Rutas reales: GET /mis_negocios, POST /registrar_negocio, GET|PUT|DELETE /negocio/<id>, GET /negocio/slug/<slug> (+ /manifest.json), GET|PUT /negocio/<id>/config-tienda, GET|PATCH /negocio/<id>/config-envios, GET /negocios/<id>/sucursales, POST /registrar_sucursal, GET|PUT|DELETE /sucursal/<id>, POST /sucursal/<id>/set_principal, POST /sucursal/<id>/personal (+ DELETE /<identificacion>), GET /ciudades, POST /contexto/establecer, GET /contexto/actual, GET /negocio/<id>/suscripcion, GET /negocio/<id>/pagos.",
 'ep-catalogo': "Archivo src/api/negocio/catalogo_api.py (catalogo_api_bp, /api) — 38 rutas. Principales: GET /inventario/productos, GET /mis-productos, POST /catalogo/producto/guardar, PUT /producto/actualizar/<id>, DELETE /producto/eliminar/<id>, GET /producto/<id>, PATCH /producto/edicion-rapida/<id>, POST /producto/duplicar/<id>, POST /producto/<id>/toggle-activo, POST /producto/<id>/stock, GET /producto/<id>/movimientos, GET /stock/alertas, GET /inventario/estadisticas, CRUD /categorias (+ /categorias/reordenar), POST /producto/<id>/imagenes (+ DELETE /<index>), idem /videos, GET /producto/buscar-codigo, GET /productos/buscar, POST /productos/importar, GET|POST /productos/exportar, GET /tienda/<slug>/producto/<id>/og, GET /productos/publicos/<negocio_id>.",
 'ep-tienda-pedidos': "checkout_api.py (checkout_api_bp): POST /tiendas/<slug>/checkout, GET /tiendas/<slug>/checkout/test. pedidos_api.py (tiendas_pedidos_bp) — 18 rutas: GET /pedidos/negocio/<negocio_id>, GET /pedidos/<id>, PUT|PATCH /pedidos/<id>/estado, PATCH /pedidos/<id>/corregir, POST /pedidos/<id>/cancelar, POST /pedidos/<id>/pago, POST /pedidos/<id>/notas, POST /pedidos/<id>/enviar, POST /pedidos/<id>/subir-guia, POST /pedidos/<id>/devolucion, POST /pedidos/devolucion/<id>/recibir, POST /pedidos/devolucion/libre, GET /pedidos/negocio/<id>/devoluciones, GET /pedidos/negocio/<id>/stats, GET /pedidos/<id>/historial, GET /pedidos/buscar, POST /pedidos/manual.",
 'ep-pagos': "wompi_api.py (wompi_bp): GET /negocio/<id>/wompi/config-pub (público), GET|PUT /negocio/<id>/wompi/config, POST /negocio/<id>/wompi/session, GET /negocio/<id>/wompi/verify, POST /wompi/webhook. cupones_api.py (cupones_bp): POST|GET /negocio/<id>/cupones, PUT|DELETE /negocio/<id>/cupones/<cupon_id>, POST /cupones/validar.",
 'ep-crm-analytics': "crm_api.py (crm_bp, /api): GET /negocio/<id>/crm/resumen, GET /negocio/<id>/crm/compradores, GET /negocio/<id>/crm/comprador/<cid>/pedidos, GET /negocio/<id>/crm/invitado/pedidos. analytics_api.py (analytics_bp): POST /negocio/<id>/analytics/visita, GET /negocio/<id>/analytics/resumen, GET /negocio/<id>/trust. resenas_api.py (resenas_bp): POST|GET /resenas/<negocio_id>/productos/<producto_id>, GET /resenas/<negocio_id>/resumen, GET /negocio/<id>/resenas, PUT /negocio/<id>/resenas/<id>/moderar, DELETE /negocio/<id>/resenas/<id>.",
 'ep-gamificacion': "gamificacion_api.py (gamificacion_bp, /api) — 29 rutas. Principales: GET /gamificacion/dashboard, /usuario, /leaderboard, /ligas, /reto-mes, /bono-hoy, /evento-activo, /referidos/mi-codigo, /tukoins/<negocio_id>, /feed-logros, /sugerencias, /proximos-badges, /resumen-mensual, /anio-revision; POST /gamificacion/onboarding-completado, /prestigio, /misiones/completar, /duelos/retar, /duelos/<id>/responder, /referidos/registrar; GET /creador/<usuario_id>, /widget/badges/<slug>.",
 'ep-notificaciones': "notifications/*.py. Rutas reales: GET /negocio/<id> (listar), /negocio/<id>/count, /negocio/<id>/stats, /negocio/<id>/stream (SSE); POST /negocio/<id>/crear; GET /negocio/<id>/detalle/<notif_id>; POST /negocio/<id>/marcar-leida/<notif_id>, /negocio/<id>/marcar-todas-leidas; DELETE /negocio/<id>/eliminar/<notif_id>, /negocio/<id>/limpiar; GET /negocio/<id>/pedidos-pendientes; POST /negocio/<id>/aprobar-pedido/<pedido_id>, /negocio/<id>/rechazar-pedido/<pedido_id>; chat (POST /chat) y push (POST /push/subscribe, /push/unsubscribe).",
 'ep-ia': "dora_api.py (dora_bp, /api) — 12 rutas: POST /ia/chat, /ia/describir-producto, /ia/generar-promo, /ia/clasificar-gasto, /ia/analizar-ventas, /ia/sugerir-precio, /ia/generar-campana, /ia/contexto-modulo, /ia/buscar-producto, /ia/auditar-categorias, /ia/corregir-categoria, /ia/actualizar-stock. Usa GROQ_API_KEY (modelo llama-3.1-8b-instant) con contexto del negocio.",
 'ep-admin': "admin_api.py (admin_bp, /api/admin) — 113 rutas. Grupos: admins (/check, /list, /add, /remove/<id>, /reactivate/<id>), challenges (CRUD + /finalizar + recompensas-config), participaciones, /stats, /metrics, /search, usuarios (+ papelera/restaurar), negocios, planes/features, auditoría (/audit), gamificación/insignias, reseñas, pagos, anuncios, etc. Decoradores @admin_required/@superadmin_required/@requiere_permiso + registrar_auditoria.",
 'ep-verticales': "taller_api.py (taller_bp): /taller/ordenes (CRUD + /items + /pdf), /taller/citas (+ /convertir), /taller/stats, /taller/historial/<placa>. restaurante_api.py (restaurante_bp): /restaurante/mesas (CRUD), /restaurante/comandas (CRUD + /cerrar + /items), /restaurante/stats, /restaurante/carta y /restaurante/publica/<slug>/carta. mecalink_api.py (mecalink_bp, /api/mecalink): /buscar, /perfil/<id>, /perfil/slug/<slug>, /mi-perfil (GET/PUT), /mis-estadisticas, /calificar/<id>, /servicios, /admin/pendientes, /admin/verificar/<id>, /admin/suspender/<id>.",
}


def seed_docs_tecnicas():
    """Inserta el contenido técnico de forma idempotente (no duplica)."""
    insert = text(
        "INSERT INTO plataforma_kb (tipo, area, clave, titulo, resumen, contenido, datos, orden, publicado, nivel_acceso) "
        "VALUES ('tecnico', :area, :clave, :titulo, :resumen, :contenido, CAST(:datos AS JSONB), :orden, TRUE, :nivel) "
        "ON CONFLICT (clave) DO NOTHING")
    # Rellena el detalle técnico (datos.tecnico) SOLO si aún no existe → no pisa
    # lo que se edite desde el panel; completa también las filas ya creadas.
    fill_tec = text(
        "UPDATE plataforma_kb SET datos = jsonb_set(COALESCE(datos,'{}'::jsonb), '{tecnico}', to_jsonb(CAST(:t AS text))) "
        "WHERE clave = :c AND (datos->>'tecnico') IS NULL")
    n = 0
    try:
        for d in SEED_DOCS:
            datos = dict(d.get('datos') or {})
            if d.get('tecnico'):
                datos.setdefault('tecnico', d['tecnico'])
            db.session.execute(insert, {
                'area': d['area'], 'clave': d['clave'], 'titulo': d['titulo'],
                'resumen': d.get('resumen'), 'contenido': d.get('contenido'),
                'datos': json.dumps(datos), 'orden': d.get('orden', 0),
                'nivel': d.get('nivel', 'admin'),
            })
            n += 1
        db.session.commit()
        for d in SEED_DOCS:
            if d.get('tecnico'):
                db.session.execute(fill_tec, {'t': d['tecnico'], 'c': d['clave']})
        db.session.commit()
        # DA6: refresco ÚNICO de rutas reales en las fichas ep-* (sobre-escribe), por flag
        try:
            ya = db.session.execute(text("SELECT 1 FROM config_global WHERE clave = 'kb_ep_rutas_v2'")).fetchone()
            if not ya:
                force = text("UPDATE plataforma_kb SET datos = jsonb_set(COALESCE(datos,'{}'::jsonb), '{tecnico}', to_jsonb(CAST(:t AS text))) WHERE clave = :c")
                for ck, tx in EP_REFRESH.items():
                    db.session.execute(force, {'t': tx, 'c': ck})
                db.session.execute(text("INSERT INTO config_global (clave, valor, updated_at) VALUES ('kb_ep_rutas_v2', CAST('true' AS JSONB), NOW()) ON CONFLICT (clave) DO NOTHING"))
                db.session.commit()
        except Exception as _er:
            db.session.rollback()
            logger.warning(f"[docs] refresco ep rutas omitido: {_er}")
        logger.info(f"✅ Seed docs técnicas: {n} entradas aseguradas")
        return n
    except Exception as ex:
        db.session.rollback()
        logger.warning(f"⚠️  Seed docs técnicas no crítico: {ex}")
        return 0
