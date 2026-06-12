# Changelog — TuKomercio

Todas las versiones notables del proyecto. Formato inspirado en [Keep a Changelog](https://keepachangelog.com/es/).

> **Regla:** actualizar este archivo en **cada versión nueva**. Añadir una entrada `## [vX.Y.Z] — AAAA-MM-DD`
> arriba del todo con secciones *Añadido / Cambiado / Arreglado / Eliminado* según aplique. La versión también
> se refleja en el endpoint `/api/health` del backend.

---

## [2.24.4] — 2026-06-11

### Arreglado
- **Métricas de producto daban error 500** (`name 'ProductoEstadisticas' is not defined`): el modelo
  `ProductoEstadisticas` no estaba importado en `catalogo_api.py`, así que `GET /producto/<id>/estadisticas`
  fallaba. El mismo bug rompía `POST /producto/<id>/vista`, por lo que **las vistas de producto nunca se
  registraban**. Añadido el import → ahora las métricas cargan y el conteo de vistas empieza a acumular.
  *(Las métricas mostrarán números bajos al inicio hasta que se acumulen visitas con el tracking ya
  funcionando.)*

## [2.24.3] — 2026-06-11

### Añadido — Métricas por producto + Actividad en vivo (Split View Fase 3)
- **Métricas de cada producto:** nueva vista `producto_metricas.html` que muestra visitas (7/30 días),
  agregados al carrito, compras, ingresos, **tasa de conversión** y un gráfico diario, con un **embudo**
  (vieron → al carrito → compraron). Consume el endpoint que ya existía `GET /api/producto/<id>/estadisticas`
  (solo faltaba la interfaz). Se abre con el botón **"Ver métricas"** en el modal de producto de Inventario:
  dentro del Split se abre en el panel de al lado; en cualquier otro caso (incluido móvil) en un overlay.
- **Barra de actividad en vivo (Fase 3):** en el panel "Mi tienda (vista previa)" del Split, una barra
  inferior minimizada/expandible muestra **visitas y pedidos de hoy** y los **últimos pedidos entrando**,
  refrescando cada ~45 s (visitas: `/analytics/resumen`; pedidos: `/pedidos/negocio/<id>`). El nombre del
  cliente va escapado (anti-XSS) y el polling se detiene al cambiar de módulo / salir del split.

### Pendiente (deuda técnica)
- Sincronización fina entre paneles (Fase 3), Comparar en Pedidos/CRM y el badge "Multitasker" real.
  Ver `DEUDA_TECNICA.md`.

## [2.24.2] — 2026-06-11

### Añadido — Modo Comparar en la Vista Dividida (productos)
- En **Inventario** dentro de la Vista Dividida (escritorio), un botón **"⚖️ Comparar"** activa el modo
  selección: eliges **2 productos** y se abren **lado a lado** (50/50) para comparar precio, stock y margen de
  un vistazo — ideal para decidir precios. El shell expone `openCompare({paths,titles})` (evento
  `TUKO_SPLIT_COMPARE`). Aditivo y gated: fuera del split (uso normal y móvil), nada cambia.
- Verificado en navegador (harness): abre 2 paneles con los 2 productos; bridge de postMessage OK.
  `split-view.js?v=4`.

## [2.24.1] — 2026-06-11

### Añadido — Split contextual (master-detail) en la Vista Dividida
- En la Vista Dividida (escritorio), al seleccionar un ítem de una lista se abre su **detalle en el panel de
  al lado**, sin navegar y sin perder la lista (patrón master-detail). El panel de detalle aparece solo al
  seleccionar (cerrado por defecto). Integrado en **Pedidos, Inventario y CRM**: clic en un ítem → su
  detalle al lado.
- Arquitectura reutilizable: el shell (`window.SplitView`) escucha el evento `TUKO_SPLIT_DETAIL` (postMessage,
  mismo origen) y abre/actualiza el panel de detalle; los módulos de lista reciben un flag (`tukoSplit=1`)
  para avisar al shell en vez de abrir su modal local. **Mobile-safe y sin regresión:** los cambios en los
  módulos son aditivos y gated — fuera del split (uso normal y en móvil) el comportamiento es idéntico a hoy.
- Verificado en navegador (harness): el flag llega a la lista, `openDetail` crea el panel de detalle y el
  bridge de postMessage lo abre. `split-view.js?v=2`.

### Pendiente (deuda técnica)
- Modo Comparar (2 ítems lado a lado), pulir el panel de detalle (modo "solo detalle") y la barra de
  actividad en vivo (Fase 3). Ver `DEUDA_TECNICA.md`.

## [2.24.0] — 2026-06-11

### Añadido — Vista Dividida (Split View) en el Studio · SOLO escritorio
- **Workspace dividido** estilo Firebase Studio / Adobe: trabaja con 2–3 módulos lado a lado en la misma
  pantalla (ej. registrar ventas a la izquierda mientras ves tu tienda a la derecha). El botón de la barra
  superior abre un menú de layouts: 1 panel, 50/50, 70/30 y 3 paneles (50/25/25).
- Cada panel tiene su **selector de módulo** (los mismos del menú lateral) + botón refrescar; **divisor
  arrastrable** (y con teclado ←/→) con ancho mínimo por panel; **persistencia** del layout por usuario;
  **atajos** Ctrl+\\ para dividir/quitar y Ctrl+\\ luego 1/2/3 para enfocar un panel. Incluye un panel
  **"Mi tienda (vista previa)"** que carga la tienda pública del negocio activo.
- Toques TuKomercio: animación de apertura suave, **logro "Multitasker"** la primera vez (confetti + aviso),
  tip de descubrimiento y sugerencia de pareja útil (descartables). Accesible (roles ARIA, foco visible,
  navegación por teclado).
- **⚠️ Protección móvil (regla de oro):** el split es EXCLUSIVO de escritorio (≥1024px). En móvil/tablet
  vertical el botón está oculto y su JS/CSS **ni siquiera se cargan**; el CSS vive 100% dentro de
  `@media (min-width:1024px)` (cero impacto en móvil). Si achicas la ventana se vuelve a la vista normal sin
  romper nada y se restaura al volver a escritorio. Verificado: la experiencia móvil queda intacta.

### Pendiente (deuda técnica)
- Split contextual master-detail (Fase 2), barra de actividad en vivo dentro del preview (Fase 3) y el badge
  "Multitasker" real en el motor de gamificación. Ver `DEUDA_TECNICA.md`.

## [2.23.2] — 2026-06-11

### Añadido — Ayuda "¿Para qué sirve?" en cada sección del Designer
- Cada recuadro de configuración del Designer ahora tiene una **explicación en lenguaje de tendero**
  (para qué sirve, cómo se usa, por qué conviene), **colapsada por defecto** detrás de un botón ℹ️ en el
  encabezado. No alarga la vista: suma 0 de alto cerrada y se despliega con un toque (funciona en táctil,
  a diferencia de un tooltip de hover). **38 secciones** cubiertas.
- Arquitectura **escalable**: las explicaciones viven en un único mapa `SECTION_HELP` (clave = título de la
  sección) y una función genérica `injectSectionHelp()` inyecta el botón y el panel en todas. Añadir/editar
  una explicación = tocar el mapa, sin editar el HTML de cada recuadro. El botón ℹ️ no interfiere con el
  colapso de la sección (`stopPropagation`); si la sección está cerrada, el ℹ️ la abre y muestra la ayuda.

## [2.23.1] — 2026-06-11

### Añadido — Orden de los productos (configurable, todas las plantillas)
- **El dueño puede elegir cómo aparecen sus productos** al entrar a la tienda, desde el Designer
  (sección dedicada y prominente "Orden de los productos", visible en **todas** las plantillas, con
  explicación). 10 opciones: más nuevos, más antiguos, más vendidos, más vistos, precio ↑/↓,
  nombre A→Z / Z→A, destacados primero, y aleatorio (mezcla en cada visita).
- **Función de orden canónica y compartida** (`assets/tienda/orden-productos.js` →
  `window.TukoOrden.ordenar`) aplicada de forma consistente en las 6 plantillas. Antes, **verde,
  taller y restaurante NO ordenaban** (pintaban el orden crudo del backend) y ecommerce/catálogo/groove
  usaban claves inconsistentes; ahora todas usan el mismo motor (con alias de compatibilidad).
- El orden del dueño **aplica aunque la barra de filtros del comprador esté oculta**; si está visible,
  es el orden inicial (el comprador puede recambiarlo). Se refleja **en vivo** en el previsualizador.
- Config nueva `config_tienda.orden_productos` (fallback a `filtros.ordenDefault` → `recientes`).
  Cache-busting: `orden-productos.js`/`tienda.js` `?v=20260611b`, `SW_VERSION` 2.3.4.

## [2.23.0] — 2026-06-11

### Añadido — Sprint Referidos "Comparte y gana" (TuKoins canjeables por plan)
- **Programa de referidos de dos niveles** que premia con TuKoins canjeables como abono al plan.
  - **Fase 1 — Captura del referido:** la landing y el registro capturan `?ref=TKxxx` (localStorage +
    payload), y el backend vincula al nuevo usuario con quien lo invitó (`Referido.vincular`, a prueba
    de fallos: un código inválido/propio no afecta el registro). Antes el código se perdía.
  - **Fase 2 — Gatillo de dos niveles:** **Nivel 1 (activación)** cuando el referido **publica su tienda**
    → +30 TuKoins y +50 XP al referidor. **Nivel 2 (primer pago)** cuando el referido **paga su 1ª
    mensualidad** (cualquier plan) → **+1.000 TuKoins**. Ambos idempotentes. Todo cuelga del **punto de
    enganche único** `on_pago_confirmado(negocio_id, es_primer_pago, origen)` — hoy lo dispara el registro
    manual del pago; mañana el webhook de Wompi, sin reescribir nada.
  - **Fase 3 — TuKoins como abono al plan:** al registrar un pago manual, el admin ve el saldo de TuKoins
    del negocio y puede aplicar un canje. **Tasa 100 TuKoins = $1.000 COP** y **tope 50% de la mensualidad**
    (parametrizables desde el panel admin). El pago queda con desglose (efectivo + TuKoins). Valida saldo y
    tope; rechaza el exceso.
  - **Fase 4 — Vista propia "Invita y gana":** módulo `referidos.html` con link + código, copiar, compartir
    por WhatsApp, contador (registrados / publicaron / pagaron), TuKoins ganados y explicación de los dos
    niveles y del canje. Accesible desde el menú lateral (sección Principal, junto a Challenge, badge NEW) y
    desde una tarjeta en la home del Studio.
- **Tests:** 44 nuevos (Fase 1: 14, Fase 2: 12, Fase 3: 18) + regresión verde (S29, hooks, A27).

### Cambiado
- El gatillo de recompensa de referido se movió de "primera venta" a "publicar tienda" (nivel 1).

### Pendiente (deuda técnica)
- Pasarela Wompi de planes: conectar su webhook a `on_pago_confirmado()` (ver `DEUDA_TECNICA.md`).
  La cuenta Wompi debe ser de TuKomercio SAS, no personal.

## [2.22.3] — 2026-06-11

### Arreglado
- **El precio de los productos quedaba invisible según el color/tema de la tienda.** Reportado en una tienda con
  tema morado (vibrant): el precio (`.price-current`) tenía un color fijo oscuro (`#1f2937`) y ningún tema oscuro
  lo repintaba (solo se repintaba `.product-price`, una clase ya en desuso) → texto oscuro sobre fondo oscuro.
  **Fix con relación de colores inteligente:** helpers de contraste (luminancia WCAG + ratio + mezcla) calculan un
  color de precio que **respeta la marca** del comerciante si ya contrasta (AA ≥ 4.5), o lo aclara/oscurece hasta
  que se vea. Las tiendas claras que ya funcionaban **no se tocan**. Aplicado a la tienda **ecommerce** (por tema
  light/dark/vibrant) y a las plantillas **taller** (card oscura fija) y **verde** (card según tema). Verificado:
  vibrant→`#aa7ff3` (5.11), taller con color oscuro→`#8d8d8d` (4.62), verde tema oscuro→`#67ac81` (5.54). Cache-bust
  `tienda.js/css?v=20260611a` + `SW_VERSION` 2.3.3.
- **`tukomercio.co` (landing) no mostraba el logo al compartir por WhatsApp.** El `OG_FALLBACK` del worker era
  `tuko-logo.gif`, un **GIF de 10.5 MB** que WhatsApp ni renderiza (no soporta GIF) ni acepta por peso. Cambiado a
  `pwa-512.png` (PNG liviano, 209 KB) + el worker declara `og:image:type/width/height`. `WORKER_VERSION` 1.31.
  Beneficia también ayuda/novedades/estado (mismo fallback). *(Deuda técnica anotada: el GIF de 10.5 MB se usa como
  logo en varias pantallas — reemplazar por SVG/PNG/WebP.)*

### Cambiado
- **Centro Financiero (grilla): un solo clic despliega todo.** El botón central abría por niveles (clic 1 = stats,
  clic 2 = módulos/inventarios). Ahora un clic muestra todo y otro cierra.
- **Pantalla de carga inteligente en el Centro Financiero** para cuando el servidor (Render) está dormido: barra de
  progreso asintótica + mensajes por tiempo ("Cargando…" → "Conectando…" → "Despertando el servidor 😴☕"); pinga
  `/api/health` (ligero) y al responder salta a 100% y entra. Salvaguarda de 60 s; respeta `prefers-reduced-motion`.

### Añadido
- **Panel admin · modal "Información del Negocio":** ahora muestra la **Plantilla** que usa el negocio
  (`tipo_pagina`: ecommerce/restaurante/taller/catálogo/verde/groove), útil para diagnóstico de soporte.

## [2.22.2] — 2026-06-08

### Cambiado
- **Los enlaces de tienda/perfil ahora usan el dominio propio `tukomercio.co`** (antes seguían generándose con el
  dominio de Cloudflare Pages `tuko.pages.dev`). Cambiada la fuente canónica `TUKO_BASE` y reemplazado el dominio
  en todos los generadores de enlaces (designer, wizard, mis_negocios, mi_pagina_web, plantillas_registry, perfil,
  worker OG_FALLBACK…). El formato limpio `/tienda/{slug}` ya estaba. **Retrocompatible:** los enlaces viejos
  (`tuko.pages.dev` y `?slug=`) siguen abriendo (HTTP 200), así que nadie con el enlace guardado se rompe.
  *(Nota: si un cliente pegó el enlace viejo en su bio/WhatsApp, debe re-copiarlo desde el panel para que muestre
  el dominio nuevo; el sistema ya lo genera así.)*

### Arreglado
- **El preview al compartir el resumen de pedido por WhatsApp no mostraba la imagen.** La `og:image` (la que el
  dueño carga desde el designer, `seo.ogImage`) estaba correcta y se servía, pero el worker no declaraba
  `og:image:width/height`, así que el scraper de WhatsApp tenía que descargar la imagen para medirla; si tardaba
  o fallaba en el primer intento mostraba el preview pequeño **sin imagen** y lo cacheaba así. Fix en `_worker.js`:
  `optimizarOgImage()` ahora fuerza el tamaño exacto **1200×630** (`c_fill,g_auto`, el formato `summary_large_image`)
  y `buildOgHtml()` declara `og:image:width=1200`/`height=630`. `WORKER_VERSION` 1.30. *(Nota: WhatsApp cachea el
  preview por días; los pedidos nuevos lo muestran bien de inmediato; los enlaces ya compartidos se refrescan con
  el tiempo o cambiando la URL.)*

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
  - **Botón "Refrescar"** en el previsualizador: `refreshPreview()` ahora **recarga el iframe** de la plantilla
    real (re-fetch + re-aplica), no solo reenvía la config — útil si un cambio no se reflejó solo. Con etiqueta + tooltip.

### Añadido
- **Slider con tamaño y forma configurables.** Nuevos controles en el designer (Tamaño: pequeño/mediano/grande;
  Forma/bordes: cuadrado/redondeado/muy redondeado) → `slider.height`/`slider.shape`. `renderSlider` aplica el
  alto (180/300/440px) y el `border-radius` (0/16/32px) al `.slider-container`.
- **Posición configurable de "Seguir + Me gusta" y de las Insignias** (ecommerce). Controles en el designer →
  `config.social = {socialPos, insigniasPos}` con valores `top` (junto al buscador/nombre) o `stats` (barra de
  confianza). Default = `stats`. `tienda.js::aplicarPosicionesSociales()` (idempotente) coloca `#tkSocial` y
  `#tukoTrustBadges` en el sitio configurado; `loadTrustData` re-crea y recoloca tras su `innerHTML`
  (resuelve el timing async); `social-actions.js` expone `__tkSocialRepaint`.

### Arreglado
- **El menú de categorías (☰) en móvil hacía desaparecer los productos.** El 1er toque no abría el menú y
  desaparecían todos los productos. Causa: `toggleSidebar` ataba el drawer a `!sidebarCollapsed` (estado
  invertido) y al añadir `.main-container.sidebar-collapsed` el grid pasaba a `0 1fr`; como el sidebar está
  `display:none` en móvil, los productos caían en la columna de 0px. Ahora en móvil es un drawer limpio
  (abrir/cerrar) sin tocar `sidebar-collapsed`, + CSS que fuerza `1fr` en móvil.
- **Botón "volver al inicio" detrás del de Facebook.** El back-to-top estaba en la esquina inferior derecha
  (`bottom:100px;right:24px;z-index:99`), solapado con el stack de redes sociales (Facebook, `z-index:999`) →
  quedaba oculto detrás. Ahora va en la esquina inferior **izquierda** (opuesto a WhatsApp/redes, `z-index:1001`).
- **Botón de Favoritos (❤️) duplicado en las tarjetas de producto.** Con `buttons.favorite` activo, el corazón
  se renderizaba en la fila de acciones **y** en la esquina superior derecha → ahora solo en la esquina sup. der.
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
