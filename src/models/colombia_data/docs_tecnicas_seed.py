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

]


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
        logger.info(f"✅ Seed docs técnicas: {n} entradas aseguradas")
        return n
    except Exception as ex:
        db.session.rollback()
        logger.warning(f"⚠️  Seed docs técnicas no crítico: {ex}")
        return 0
