# Changelog — TuKomercio

Todas las versiones notables del proyecto. Formato inspirado en [Keep a Changelog](https://keepachangelog.com/es/).

> **Regla:** actualizar este archivo en **cada versión nueva**. Añadir una entrada `## [vX.Y.Z] — AAAA-MM-DD`
> arriba del todo con secciones *Añadido / Cambiado / Arreglado / Eliminado* según aplique. La versión también
> se refleja en el endpoint `/api/health` del backend.

---

## [2.22.1] — 2026-06-08

### Arreglado
- **Slider superior de la tienda en blanco.** Las imágenes del banner se guardan como `data:image/` (base64) y
  el helper `safeUrl()` (endurecido) bloqueaba **todo** `data:` → banners rotos. Ahora permite `data:image/`
  (seguro, no ejecuta script) y sigue bloqueando `data:text/html`/`javascript:`/`vbscript:`.
- **Insignias del negocio como círculos vacíos** (junto al buscador). Los badges usan clases `bi-*` (Bootstrap
  Icons) pero la tienda solo cargaba **Font Awesome** → sin glifo. Añadido el CSS de Bootstrap Icons al
  `tienda/index.html`.

### Cambiado
- **Insignias del negocio con medallas SVG (TKMedal) en TODAS las plantillas.** Antes el strip de medallas solo
  existía en ecommerce (`renderTrustBadges`) y se veía distinto al perfil. Ahora:
  - **Ecommerce**: `renderTrustBadges` usa `TKMedal.html(badge,{size:26})` — el mismo componente del perfil.
  - **Las 10 plantillas no-ecommerce**: `trust-strip.js` (compartido) renderiza las medallas `TKMedal` (size 22)
    en la barra de stats, en vez del conteo plano. Carga `badge-medal.css`/`badge-medal.js` de forma perezosa.
  → las insignias se ven **iguales que en el perfil** en todas partes. Cache-bust `tienda.js?v=20260608e`,
  `trust-strip.js?v=20260608d`, `SW_VERSION` 2.2.7.

## [2.22.0] — 2026-06-07

### Cambiado
- **Previsualizador del Diseñador = la tienda real (v7.0).** La vista previa dejó de ser una maqueta
  paralela (que divergía de la tienda publicada) y pasó a ser la **plantilla real dentro de un `<iframe>`**,
  alimentada con el `storeConfig` en vivo por `postMessage` (`type: 'TUKO_PREVIEW_CONFIG'`). Lo que ves es
  exactamente lo que se publica, se repinta al instante con cada cambio (sin guardar) y es responsivo de
  verdad. Migradas **las 5 verticales**: ecommerce, restaurante, taller, catálogo y verde.
  - Frontend `assets/tienda/tienda.js`: modo preview (`isPreviewMode()` + `initPreviewBridge()`),
    `applyStoreConfig(opts)` con `skipSplash`/`skipCategorias` (no relanza el splash ni re-pide categorías
    en cada tecla), y `buildConfigToSave()` como fuente única en el designer (guardar = previsualizar).
  - Cada plantilla aplica el config en vivo: restaurante/taller con `applyPreviewConfig()` (mapea
    carta/servicios/slogan/color al DOM real), catálogo vía `applyConfig()`, verde vía `applyNegocio()`.

### Arreglado
- **Bugs del previsualizador (v6.1).** `renderPreviewVerde()` escribía en `#previewContainer` (destruía el
  marco del dispositivo y congelaba el preview al cambiar de plantilla) → ahora `#previewContent`. Testimonios
  de taller/restaurante inyectaban `undefined` por claves de tema inexistentes (`textSecondary`/`cartaBg`) →
  corregido. El toggle del slider (`sliderEnabled`) no se reflejaba → ahora se lee en `updatePreview()`.
- **Fuga de memoria:** `setupLogoImageRotation()` creaba un `setInterval` por cada re-aplicado sin limpiar el
  anterior → ahora hace `clearInterval` previo.
- **Catálogo roto en producción (`escapeAttr is not defined`).** `catalogo.js::renderChips()` llamaba a
  `escapeAttr()` (función inexistente; la real es `escAttr`) → `init()` lanzaba y la tienda de catálogo no
  cargaba. Corregido el nombre.
- **Preview de restaurante/taller no reflejaba todos los campos.** `applyPreviewConfig` mapeaba solo un
  subconjunto (color/slogan/carta/servicios) → al editar **dirección, teléfono** (ambos) o **especialidad**
  (taller) no pasaba nada ("no se ve en tiempo real"). Ahora se mapean al DOM real. *(verde/catálogo ya eran
  completos porque reusan `applyNegocio`/`applyConfig`.)* Pendiente: `garantia`/`pasos` (taller) y
  `mostrarPrecios`/`tema` (restaurante) no tienen elemento en la plantilla real → controles "muertos" a decidir.

### Seguridad
- **Validación de origen en `postMessage`.** Los 3 listeners del puente de preview (designer, tienda,
  restaurante) rechazan mensajes de orígenes externos (`ev.origin !== location.origin`).
- **Escape de contenido del tenant (XSS almacenado).** `escapeHtml()` endurecida (coerción a `String`, antes
  `escapeHtml(número)` lanzaba `TypeError`) + nueva `safeImageUrl()` (solo `http(s)`/relativa/`data:image`;
  bloquea `javascript:`/`data:text/html`). Escapados los puntos que faltaban en `tienda.js` (galería —se quitó
  el `src` del `onclick`—, stats, categorías, hero-badges), el nombre/teléfono en **restaurante** y **taller**,
  y el nombre/logo en **verde**. Catálogo ya estaba escapado (productos con `escAttr`/`escHtml`, hero con
  `textContent`).
- **Hardening anti–inyección CSS (catálogo).** El color (`primaryColor`) y la fuente del config se
  interpolaban en el `textContent` de un `<style>` (CSS crudo) → un valor con `;}` podía inyectar reglas
  CSS. Nuevas `safeColor()`/`safeFont()` validan el valor antes de inyectarlo (`applyTheme`/`applyFont`).
  Verificado en vivo: un `primaryColor`/fuente malicioso cae al fallback y no oculta la página. *(Pendiente:
  mismo patrón en `tienda.js` —fuente y colores de badges— para una próxima tanda.)*
- **Cache-busting de `tienda.js`** (`?v=20260607` en `tienda/index.html` + precache del SW) y bump de
  `SW_VERSION` 2.2.1 → 2.2.2, para que los cambios de JS lleguen tras cada deploy.

### Documentación
- Nueva guía técnica `doc-front-previsualizador` (área *frontend*) en `docs_tecnicas_seed.py`.

## [2.21.0] — 2026-06-07

### Cambiado
- **Insignias con look premium (medallas SVG).** Nuevo componente front `TKMedal`
  (`assets/js/badge-medal.js` + `badge-medal.css`) que reemplaza el "icono en círculo" por medallas
  SVG en marca (aro metálico por tier, volumen, gemas/brillo), reutilizando los datos actuales de cada
  badge (sin cambios de backend). Aplicado en perfil, modal de celebración, dashboard de gamificación,
  widget embebible y feed de videos. Preview: `admin/panel/badges_medallas_preview.html`.

### Añadido
- **Gamificación social — 12 insignias por seguidores y me gusta.** El negocio gana badges al acumular
  seguidores (Primer Seguidor → Ídolo de Masas 1.000) y me gusta (Primer Me Gusta → Leyenda Imparable
  10.000), escalera ampliable. Métricas `seguidores`/`me_gusta` en `badge_verification_service.py`;
  badges en `BADGES_INICIALES` (seeder idempotente); se verifican al seguir/like (`interacciones_api`,
  fail-safe). El **perfil público del negocio** muestra conteo de seguidores y me gusta + las insignias
  ganadas (`perfil_publico_negocio_api` → `seguidores`/`me_gusta`; front `negocio_perfil`). Tests
  `test_badges_sociales.py` 56/0.
- **Interacciones sociales de tienda — Seguir 👥 y Me gusta ❤️.** El comprador puede *seguir* un negocio
  y darle *me gusta* desde cualquier tienda. Botones en el header (junto al carrito) y **conteo de
  seguidores** en la barra de confianza, al lado de "badges ganados".
  - Tabla nueva `negocio_interacciones` (`negocio_id`, `usuario_id`, `tipo` ∈ {seguir, like}, UNIQUE) —
    migración en `create_app()` + modelo `NegocioInteraccion`.
  - Endpoints `GET /api/negocio/<id>/social`, `POST /api/negocio/<id>/seguir`, `POST /api/negocio/<id>/like`
    (toggle, auth híbrida sesión/`X-User-ID`; invitado → `401 {requiere_login:true}`). `/trust` ahora
    incluye `seguidores`.
  - Frontend: widget autocontenido `assets/tienda/social-actions.js` (en las 11 vistas de tienda),
    con **modal propio** que invita a iniciar sesión / registrarse cuando el visitante no está logueado.
    Bonus: notificación `seguidor_nuevo` al dueño (fail-safe).
  - Tests: `test_interacciones.py` (20/0).

---

## [2.19.0] — 2026-06 — *Estado actual*

Versión que consolida lo grande ya construido. Resumen de capacidades a la fecha:

### Plataforma e-commerce
- SaaS **multi-tenant**: un usuario, varios negocios; cada negocio con tienda online pública, catálogo,
  inventario, pedidos, contabilidad y micrositio con slug propio.
- **Checkout** con envíos configurables, **cupones**, **CRM** de compradores, **reseñas** de producto,
  **carritos abandonados**, **analytics** de tienda y pasarela de pago **Wompi** (con webhook).
- **Dora IA** (asistente), generador de **QR**, **feed de videos**, y verticales (taller, restaurante, MecaLink).

### Gamificación (40 sprints, S1–S40) ✅
- Motor de eventos a prueba de fallos; 30 niveles, XP, 4 rachas, misiones diarias/semanales/mensuales.
- **49 insignias** con 5 tiers; **TuKoins** + tienda de ítems; bonos por fecha; eventos especiales (XP ×).
- Ligas, reto del mes, duelos, referidos, prestigio, comparativas, sugerencias, feeds de logros,
  resúmenes mensual/anual, perfil público del creador, widget embebible y onboarding gamificado.

### Panel de administración (en curso, A1–A10 de 49)
- Cimientos: log de **auditoría**, **permisos granulares** por módulo, dashboard de **KPIs**, buscador global.
- Control de gamificación **sin código**: editor de XP por evento, misiones, tienda de TuKoins,
  economía (ajuste manual + bono configurable) y ficha de gamificación por negocio.

### Infra y calidad
- Backend Flask en Render (`gunicorn run:run`), PostgreSQL en Neon, frontend vanilla JS en Cloudflare Pages.
- Auto-reparación de esquema y seeders idempotentes al arranque. Suite de **500+ tests** (scripts en `src/tests_apis/`).

---

<!-- Plantilla para nuevas versiones (copiar arriba):

## [vX.Y.Z] — AAAA-MM-DD
### Añadido
- ...
### Cambiado
- ...
### Arreglado
- ...
### Eliminado
- ...
-->
