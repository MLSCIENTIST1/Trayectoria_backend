# BITÁCORA DE SPRINTS — TuKomercio

> Registro cronológico del trabajo. Se actualiza **al terminar cada tarea**.
> Estructura por entrada: Fecha · Sprint actual · Completado · Pendiente · Problemas · Siguiente paso.
> Roadmaps detallados: `memory/admin_panel_roadmap.md`, `memory/gamification_roadmap.md`, `memory/fixes_tienda_checkout.md`.

> 📌 **Nota de alcance:** el "sistema de reportes de error" **ya existe** en el código
> (sección *Reportes* del panel admin + `src/api/feedback_api.py` + tabla de reportes). El **sprint
> en curso real** es el **Panel de Administración** (roadmap A1–A49), que entre otras cosas integra
> y amplía la administración de esos reportes.

---

## 2026-06-06 — 🔴 F19 (CRÍTICO) · NINGÚN correo se enviaba (reset bloqueado)

**Tipo:** bug crítico (backend / envío de email). Carlos quedó bloqueado fuera (no llegó el correo de recuperación).

### Diagnóstico en vivo
- `GET /api/auth/test-smtp` → RESEND_API_KEY ✅ pero `MAIL_FROM=onboarding@resend.dev` (sandbox).
- `GET /api/auth/test-send/<email>` → **HTTP 403 error 1010** = **Cloudflare** bloqueando (no Resend).

### Causa raíz
- Las peticiones a `api.resend.com` vía `urllib` no enviaban `User-Agent` → urllib manda `Python-urllib/x.y` y Cloudflare lo bloquea (403/1010) antes de llegar a Resend. Afectaba TODOS los emails.

### Solución (backend)
- Añadir `User-Agent` + `Accept` en `api/auth/password_reset_api.py::send_email_resend` y `services/suscripcion_email_service.py`.
- ⏳ Pendiente operativo: `MAIL_FROM=onboarding@resend.dev` solo envía al dueño de la cuenta Resend → verificar dominio en Resend + `MAIL_FROM=noreply@dominio` para enviar a todos los clientes. Detalle en `memory/fixes_tienda_checkout.md` (F19).

---

## 2026-06-06 — 🔴 F18.6 (CAUSA RAÍZ REAL) · updatePreview borraba seo antes de poblar el form

**Tipo:** bug crítico (frontend / designer). Corrige una conclusión prematura (F18.5).

### Causa (confirmada por grep)
- En `initNuevosBloques()`, `renderTestimonios` (x4), `renderStats` (x3), `applyFonts` (x1) e `initRedesSocialesListeners` (x1) llaman `updatePreview()` ANTES de poblar los inputs SEO. `updatePreview` hace `storeConfig.seo = {titulo:g('seoTitulo'),...,ogImage:g('seoOgImage')}` leyendo el DOM **vacío** → borraba el seo cargado del backend. Por eso, aunque `window.__ogDebug` mostraba la data cargada, los campos salían vacíos y el preview mostraba la portada.

### Solución (`designer.js`)
- Poblar SEO + toggles (testimonios/stats/galeria) + redes en `applyConfigToInputs()` (corre tras mergeConfig y ANTES de cualquier updatePreview). El DOM ya tiene los valores cuando updatePreview los lee.
- cache-busting og6; `designer.regression.test.js` 14/14. Detalle en `memory/fixes_tienda_checkout.md` (F18.6).

---

## 2026-06-06 — 🔴 F18.4 (CRÍTICO) · Service Worker cacheaba el JS → los fixes no llegaban

**Tipo:** bug de infraestructura (Service Worker, frontend).

### Causa raíz
- El SW activo `/sw.js` (scope `/`) usaba **cache-first para todo `.js`/`.css`** → servía `designer.js` viejo desde caché, ignorando red y Ctrl+F5. Con el JS viejo persistía el bug de localStorage (F18.3), por eso las correcciones "no aparecían". El API es network-first (datos frescos) → el backend SÍ tenía el `ogImage`, pero el designer mostraba la portada por correr código viejo.

### Solución (`sw.js` v2.1.0)
- `.js`/`.css` → **stale-while-revalidate** (revalida en 2º plano; siguiente load fresco).
- Bump `SW_VERSION 2.0.0→2.1.0` → `activate` purga todos los cachés `tukomercio-*` viejos (desatasca el navegador).
- Test de regresión `designer.regression.test.js` (node, 12 checks).

### Desatascar manual (si hiciera falta)
- DevTools → Application → Service Workers → Unregister (o "Clear site data") y recargar. Detalle en `memory/fixes_tienda_checkout.md` (F18.4).

---

## 2026-06-06 — 🔴 F18.3 (CRÍTICO) · auditoría profunda designer → 2 causas más de pérdida de datos

**Tipo:** auditoría (3 agentes en paralelo) + fix (frontend / designer).

### Hallazgos
- **A) localStorage pisaba al backend:** `loadStoreData()` mergeaba `localStorage.tienda_personalizacion_<id>` DESPUÉS del backend; un guardado viejo con SEO vacío sobreescribía la config buena en cada recarga (por eso `seo.ogImage`, presente en backend, salía como "se usa portada"). **Fix:** backend = fuente de verdad; localStorage solo como respaldo si el fetch falló.
- **B) Campos leídos al guardar pero no poblados al cargar:** `testimoniosEnabled/titulo`, `statsEnabled`, `galeriaEnabled/titulo/columnas` → se persistían vacíos en cada save. **Fix:** poblarlos en `initNuevosBloques()`.
- **Backend OK:** `PUT /negocio/<id>` reemplaza config_tienda completo; el designer manda config completo → seguro ahora que storeConfig está completo. (Existe `PATCH /config-tienda` con deep_merge como mejora futura.)

### Notas
- cache-busting `designer.js?v=20260606-og3`. Riesgo residual: mergeConfig shallow (mitigado). Detalle en `memory/fixes_tienda_checkout.md` (F18.3).

---

## 2026-06-06 — 🔴 F18.2 (CRÍTICO) · condición de carrera en el designer → pérdida de datos

**Tipo:** bug crítico (frontend / designer).

### Síntoma
- En el designer los campos SEO salían vacíos aunque estaban guardados; al Guardar se sobreescribían con vacío (rodar perdió seo.titulo/desc/keywords).

### Causa
- `initNuevosBloques()` (puebla SEO/redes/fuentes) corría con `setTimeout(400)` fijo, sin esperar a `loadStoreData()` (async). Con Render frío o `/negocio` pesado (logo base64 de 976KB), la carga tardaba >400ms → campos con default vacío → guardado destructivo.

### Solución (`designer.js`, `designer.html?v=…og2`)
- `initNuevosBloques()` ahora tras `await loadStoreData()`+`loadNegocioPlan()`; el setTimeout pasa a fallback guardado (2s, flag `__nuevosBloquesInit`).
- Red de seguridad `window._configCargada`: `saveAllSettings()` aborta si la config no cargó (no sobreescribe con vacío).
- Cache-busting `?v=20260606-og2`.
- Pendiente relacionado: migrar `negocios.logo_url` base64 (976KB) a URL Cloudinary. Detalle en `memory/fixes_tienda_checkout.md` (F18.2).

---

## 2026-06-06 — ✨ F18 · elegir la imagen del preview compartido (OG) + arreglo base64

**Tipo:** feature/UX (frontend: designer + Cloudflare Worker).

### Pedido
- Poder seleccionar la imagen que sale al compartir el enlace (sobre todo el del resumen de pedido). En "rodar" tomaba el banner y no había dónde cambiarlo. Decisión: una sola imagen para todo (estándar OG).

### Solución (FRONT)
- Ya existía `config_tienda.seo.ogImage` (solo campo URL, y el Worker no lo usaba).
- **Designer**: "Imagen para enlaces compartidos (WhatsApp/Facebook)" ahora con **subida de imagen** (case `seoOgImage`) + preview, en sección SEO. Aclara que controla el preview de tienda/pedido.
- **Worker v1.24**: `pickOgImage()` descarta `data:` URIs (el logo de rodar está en base64 → inválido para OG). Prioridad del pedido: `seo.ogImage` → hero → splash → logo → fallback. Aplicado también a tienda y producto.

### Notas
- WhatsApp cachea previews. Detalle en `memory/fixes_tienda_checkout.md` (F18).

---

## 2026-06-06 — ✨ F17 · preview del resumen de pedido al compartir (OG / WhatsApp)

**Tipo:** feature (frontend / Cloudflare Worker).

### Objetivo
- Que el enlace `/pedido/<slug>/<codigo>` que el tendero envía al comprador muestre una tarjeta profesional con la marca de la tienda (antes: texto plano).

### Solución (`_worker.js` v1.23)
- La rama `/pedido/:tienda/:codigo` servía heyden.html a todos (sin OG). Ahora, si es bot, devuelve OG con `fetchNegocio(slug)`: título `Pedido <codigo> · <Tienda>`, descripción cálida + imagen de portada/hero (o logo) con fallback. Humanos siguen recibiendo heyden.html.

### Notas
- WhatsApp cachea previews → probar con pedido/enlace nuevo o debugger OG de Facebook. Detalle en `memory/fixes_tienda_checkout.md` (F17).

---

## 2026-06-06 — ✨ F16 · vista previa de producto al compartir (OpenGraph / WhatsApp)

**Tipo:** feature (backend + worker + frontend).

### Objetivo
- Que al compartir el link de un producto por WhatsApp salga **foto + nombre + precio** (antes vacío).

### Por qué fallaba
- El enlace usaba `#producto-<id>` (hash, no llega al servidor) y los bots no ejecutan JS. El Worker ya hacía OG de tienda, pero no de producto.

### Solución (3 capas)
- **Backend** (`catalogo_api.py`): endpoint público `GET /api/tienda/<slug>/producto/<id>/og` (solo activos/publicados). Test `test_producto_og_publico.py` → 7/0.
- **Worker** (`_worker.js` v1.22): `fetchProductoOg` + rama que, si la URL trae `?producto=<id>`, inyecta OG con la foto del producto (cae a OG de tienda si falla).
- **Frontend**: enlaces de compartir ahora usan `?producto=<id>` (rastreable); `checkUrlForProduct` abre el producto al llegar por query (compat con `#`).

### Notas
- WhatsApp cachea previews → probar con producto nuevo o el debugger de OG de Facebook. Verificación real solo en prod. Detalle en `memory/fixes_tienda_checkout.md` (F16).

---

## 2026-06-06 — 🐞 FIX producción F13 · columnas de la tabla notification (campanita)

**Tipo:** corrección de esquema (backend, clase F8).

### Problema
- Campanita vacía: las notificaciones automáticas (A50/A51: badge ganado, plan cambiado, recompensa de liga) podían fallar en silencio si la tabla `notification` de prod (vieja) no tenía las columnas nuevas (`titulo`, `negocio_id`, `prioridad`, etc.). `notificar_negocio` es a prueba de fallos → el INSERT inválido se perdía sin error.

### Solución
- Migración idempotente en `create_app()`: `ALTER TABLE notification ADD COLUMN IF NOT EXISTS` para negocio_id, sender_id, titulo, message(TEXT), type, prioridad, is_read, is_accepted, referencia_tipo/_id, action_url, extra_data, timestamp, fecha_lectura + índices `ix_notif_negocio` / `ix_notif_user_read`.
- Test `test_fix_notification_columns_f13.py` → **26/0**.
- Nota: no hay backfill de badges ganados antes del deploy de A50 (eso fue timing, no bug). De aquí en adelante las notificaciones llegan.
- Pendientes relacionados (en `memory/fixes_tienda_checkout.md`): F14 (miembro desde), F15 (franja en otras plantillas), badges clicable.

---

## 2026-06-06 — 🐞 FIX producción F12 · pantalla de carga de la tienda

**Tipo:** corrección de UX + branding (frontend) en la tienda pública y el Designer.

### Problema
- Al abrir una tienda se veían **3 pantallas de carga** (negra → splash "Mi Tienda/Bienvenido" → "Cargando tienda…"), con el spinner del splash **descuadrado a la izquierda** y un salto brusco.

### Causas
- `tienda/r.html` con fondo negro (flash). `#splashScreen` visible por defecto (splash genérico aunque `enabled=false`), apilado con `#loadingScreen`. `.splash-spinner` sin `margin:0 auto`. Splash con cierre fijo de 3s.

### Solución (FRONT, completo)
- **r.html:** fondo claro + logo de la tienda (pulso) en el loader; reenvía `__TUKO_LOGO/NAME/COLOR`.
- **index.html:** splash oculto por defecto; loader con logo desde el primer frame (script inline).
- **tienda.css:** spinner centrado + `.loading-logo`.
- **tienda.js:** splash usa el logo como respaldo y cierra **por disponibilidad** (mín ~800ms + tienda lista) en vez de 3s.
- **Designer:** aviso único + botón "Usar mi logo como bienvenida". Logo como default no destructivo.
- `node --check` OK en todos. Detalle en `memory/fixes_tienda_checkout.md` (F12).

---

## 2026-06-06 — 🐞 FIX producción F11 · detalle de pedido sin productos

**Tipo:** corrección (frontend) en Gestión de Pedidos online.

### Problema
- Al abrir un pedido (clic en la tarjeta), el modal mostraba "PRODUCTOS (0)" aunque la tarjeta decía "1 producto(s)". Los productos solo se veían al entrar a **Editar**.

### Causa
- `verDetalle` (`contabilidad/modulos/pedidos.html`) usaba el item de la **lista** (`pedidos.find`), y el endpoint de lista no trae el array `productos` (solo `num_productos`). Editar sí hacía `fetch(/pedidos/<id>)`, por eso funcionaba.

### Solución (FRONT)
- `verDetalle` ahora también hace `fetch(/pedidos/<id>)` y fusiona el detalle (`{...listItem, ...data.pedido}`) antes de renderizar → el modal muestra nombre/cantidad/precio. Mismo endpoint que ya usaba Editar. `node --check` OK. Detalle en `memory/fixes_tienda_checkout.md` (F11).

---

## 2026-06-06 — 🐞 FIX producción F10 · estados de pedido (salto directo)

**Tipo:** corrección de UX (frontend) en Gestión de Pedidos online.

### Problema
- El stepper de estados (Confirmado→Preparando→Enviado→En Oficina→Entregado) solo dejaba avanzar **un paso a la vez**. Si el pedido ya llegó pero no se marcaron los intermedios, tocaba ir uno por uno (re-buscando guía/nombre) hasta Entregado.

### Solución (FRONT, `contabilidad/modulos/pedidos.html`)
- Cualquier estado **futuro** del flujo es clickeable. Avance al siguiente = rápido; **salto** a uno más adelante = con **confirmación** que lista los intermedios que se dan por hechos; retroceso conserva confirmación. `cambiarEstadoConConfirm(id, estado, modo)` con modos avance/salto/retroceso (compat con `true`). `getEstadosBotones` del modal unificado a `FLUJO_ESTADOS` (incluye en_oficina) y con saltos. Nuevo estilo `.estep-jump`. El backend ya aceptaba cualquier estado (sin secuencia), así que es fix solo de front. `node --check` OK.
- Detalle en `memory/fixes_tienda_checkout.md` (F10). Backlog v2 de ideas guardado en `memory/roadmap_v2.md`.

---

## 2026-06-05 — Panel admin A51 · Web Push real · 🎉 ROADMAP COMPLETO (51/51)

**Sprint final.** Fase 7 EXTRA COMPLETA. **Avance 51/51 — todas las fases ✅.**

### Completado
- **A51 — Web Push real (notificaciones con la app cerrada).** Cierra el último pendiente del proyecto (lo que faltaba para que llegaran con la app cerrada).
  - **Backend:** servicio `api/utils/push_service.py` con helpers PUROS `construir_payload_push`, `_es_suscripcion_muerta` (404/410), `vapid_disponible` + `enviar_push_a_usuario` (envía con `pywebpush` si VAPID está configurado; elimina suscripciones muertas; a prueba de fallos → 0 envíos si falta infra). Tabla `push_subscriptions` (migración `create_app`). Endpoints `GET /api/notifications/push/vapid`, `POST .../push/subscribe` (**sesión**, no header forjable; upsert por endpoint), `POST .../push/unsubscribe`. Cableado en `notificar_negocio` → la campanita (A50) ahora también dispara push. `pywebpush==2.0.0` en `requirements.txt`.
  - **Frontend:** `notifications.js` se suscribe (SW ready + pushManager.subscribe con la clave VAPID + POST al backend) al conceder permiso. El service worker ya tenía `push`/`notificationclick`.
  - **Test:** `test_admin_webpush_a51.py` → **24/24**.
- **Activación en prod:** definir env vars `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT` en Render (generar con `vapid` o web-push). Sin ellas, degrada limpio a solo-campanita.

### 🏁 Cierre del roadmap del Panel de Administración
- **51/51 sprints.** Fases 0-7 completas (A1-A51). Objetivo cumplido: administrar toda la plataforma sin tocar código.
- F-fixes de producción atendidos en el camino: F6 (responsive vista producto), F7 (plan/trial schema drift), F8 (migraciones en prod), F9 (compresión de fotos).
- Backlog opcional pendiente: F3 (test e2e recibo), F5 (ícono PWA), edición de prompts de Dora, envío automático real del WhatsApp post-venta, adopción incremental del gestor de textos.

### Siguiente paso
- A definir por Carlos (verificación en producción, backlog opcional, o nuevas funcionalidades).

---

## 2026-06-05 — Panel admin A50 · Campanita automática (Fase 7 EXTRA)

**Sprint actual:** Fase 7 EXTRA (notificaciones). Avance **50/51**.

### Completado
- **A50 — Campanita automática en eventos del sistema.** Respuesta a la pregunta de Carlos (antes ni el cambio de plan ni ganar badge notificaban).
  - **Backend:** servicio `api/utils/notificaciones_service.py`: helper PURO `construir_notificacion(evento, ctx)` (plantillas plan_cambiado/badge_ganado/suscripcion_por_vencer/recompensa_liga) + `notificar_negocio(...)` que inserta en `notification`, resuelve el dueño y es **a prueba de fallos** (nunca rompe la operación). Cableado en: `_asignar_badge` (insignia ganada), `assign_plan_to_negocio` (cambio de plan), `otorgar_recompensas_liga` (premio de liga).
  - **Sin UI nueva:** la campanita 🔔 + SSE ya existentes muestran estas notificaciones; el toast del navegador salta si el usuario tiene la app abierta y con permiso.
- **Test:** `test_admin_notif_auto_a50.py` → **17/17**.

### Pendiente
- **A51 — Web Push real** (notificaciones con la app cerrada: VAPID + pywebpush + suscripción) → cierra el roadmap.

---

## 2026-06-05 — Panel admin A49 · Gestor central de textos ⭐ · 🎉 FASE 6 COMPLETA

**Sprint actual:** Panel de Administración. **Fase 6 COMPLETA (A41-A49).** Avance **49/51** (Fases 0-6 completas).

### Completado
- **A49 — Gestor central de textos/copys ⭐.** El mayor habilitador del objetivo "sin programador": editar textos visibles sin tocar código.
  - **Backend:** `TEXTOS_DEFAULT` (catálogo curado por categoría) + helpers PUROS `validar_textos`, `get_textos`, `get_texto(clave, fallback)`, `set_textos` en `config_plataforma.py` (override en `config_global`, clave `textos`). Endpoints `GET/PUT /api/admin/textos` (`requiere_permiso('configuracion')`, auditado) + **público** `GET /api/textos-publicos` (mapa clave→valor, base i18n, para que el frontend aplique overrides).
  - **Frontend:** sección "Textos / Copys" (Configuración): edición agrupada por categoría, buscador, marca ✎ editado, guardado por diff.
- **Test:** `test_admin_textos_a49.py` → **18/18**.
- **🎉 Cierre Fase 6:** pagos Wompi (A41), facturación (A42), reseñas (A43), Dora IA (A44), Habeas Data (A45), emails (A46), verticales (A47), integraciones (A48), textos (A49).

### Estado global
- **Fases 0-6 ✅ COMPLETAS (A1-A49) → 49/51.** Solo queda la **Fase 7 EXTRA** (notificaciones: A50 campanita automática, A51 web push), que Carlos pidió dejar al final.

### Siguiente paso
- **A50 — Campanita automática en eventos del sistema** (notificación in-app al cambiar plan, ganar badge, etc.).

---

## 2026-06-05 — Panel admin A48 · Integraciones y automatizaciones

**Sprint actual:** Panel de Administración. **Fase 6.** Avance **48/51**.

### Completado
- **A48 — Integraciones y automatizaciones.** Centro de estado de integraciones + automatización de WhatsApp post-venta.
  - **Backend:** helpers PUROS `estado_integraciones` (Resend/Groq por env, Cloudinary embebido siempre OK, Wompi según negocios activos) + `validar_integraciones_config` + `INTEGRACIONES_CONFIG_DEFAULT` en `api/utils/integraciones_service.py`. `get/set_integraciones_config` en config_global. Endpoints `GET /api/admin/integraciones` (estado + config + triggers + referencia import CSV) y `PUT .../integraciones/config` (`requiere_permiso('configuracion')`, auditado).
  - **Frontend:** sección "Integraciones" (Configuración): semáforo de cada integración, editor de WhatsApp post-venta (toggle/disparador/plantilla con variables) y nota del import CSV (módulo de Contabilidad).
- **Test:** `test_admin_integraciones_a48.py` → **20/20**.

### Pendiente (Fase 6)
- A49 gestor central de textos/copys → cierra Fase 6.

### Siguiente paso
- **A49 — Gestor central de textos/copys (sin programador) ⭐** — cierra Fase 6 y el grueso del roadmap.

---

## 2026-06-05 — Panel admin A47 · Verticales + overview de tienda avanzada

**Sprint actual:** Panel de Administración. **Fase 6.** Avance **47/51**.

### Completado
- **A47 — Verticales + tienda avanzada.** Visibilidad de plataforma que faltaba (Taller/Restaurante/MecaLink + cupones/carritos/reseñas).
  - **Backend:** helper PURO `etiqueta_vertical` + `VERTICALES_META` en `api/utils/verticales_service.py`. Endpoint `GET /api/admin/verticales/overview` (`requiere_permiso('negocios')`): distribución de negocios por `tipo_pagina` (excluye papelera) + cupones (total/activos/usos), carritos abandonados (abandonados/recuperados/valor_recuperable) y reseñas (total/aprobadas).
  - **Frontend:** sección "Verticales & tienda avanzada" (Plataforma): grid de verticales (con ícono/label) + tarjetas de cupones, carritos y reseñas.
- **Test:** `test_admin_verticales_a47.py` → **16/16**.

### Pendiente (Fase 6)
- A48 integraciones/automatizaciones · A49 gestor central de textos.

### Siguiente paso
- **A48 — Integraciones y automatizaciones** (WhatsApp post-venta, import CSV marketplace, dominios/SEO/worker).

---

## 2026-06-05 — Panel admin A46 · Gestor de plantillas de email (Resend)

**Sprint actual:** Panel de Administración. **Fase 6.** Avance **46/51**.

### Completado
- **A46 — Gestor de emails.** Antes los textos de los correos estaban en código; ahora editables desde el panel.
  - **Backend:** `EMAIL_PLANTILLAS_DEFAULT` (recuperar_password, bienvenida, confirmacion_pedido) + helpers PUROS `render_email` (sustituye `{{var}}`/`{{ var }}`, sin ejecutar código → seguro), `validar_plantilla_email`, `get/set_email_plantilla` en `config_plataforma.py` (override en `config_global`). **Cableo seguro en `forgot_password`**: usa la plantilla editada si existe, si no, fallback al `EMAIL_TEMPLATE` fijo. Endpoints `GET /api/admin/emails` (plantillas + deliverability de Resend), `PUT .../emails/<clave>` (validado+auditado), `POST .../emails/<clave>/test` (renderiza con variables de muestra y envía por Resend). `requiere_permiso('configuracion')`.
  - **Frontend:** sección "Emails" (Configuración): estado de Resend, selector de plantilla, editor de asunto/HTML con hint de variables, guardar y enviar prueba.
- **Test:** `test_admin_emails_a46.py` → **24/24**.

### Pendiente (Fase 6)
- A47 verticales + overview tienda · A48 integraciones · A49 gestor de textos.

### Siguiente paso
- **A47 — Admin de verticales + overview de tienda avanzada** (Taller/Restaurante/MecaLink + cupones/carritos/analytics).

---

## 2026-06-05 — Panel admin A45 · Habeas Data / privacidad (Ley 1581)

**Sprint actual:** Panel de Administración. **Fase 6.** Avance **45/51**.

### Completado
- **A45 — Habeas Data / privacidad.** Obligación legal en Colombia que no existía.
  - **Backend:** helpers PUROS `validar_tipo_solicitud` y `construir_export_usuario` (filtra `CAMPOS_SENSIBLES` → nunca exporta contraseñas/hashes/tokens) en `api/utils/privacidad_service.py`. Tabla `solicitudes_privacidad` (migración en `create_app`). Endpoints: `GET /api/admin/privacidad/usuario/<id>/export` (portabilidad JSON: usuario + consentimiento + negocios + reseñas, auditado), `GET/POST /privacidad/solicitudes` (registrar), `POST .../solicitudes/<id>/procesar` (**superadmin**: completar/rechazar; para eliminación = **derecho al olvido** vía baja lógica/papelera, NO purga; bloquea borrar admins activos; trazable con atendida_por/fecha). Registro de consentimiento desde `usuarios.acepto_terminos`.
  - **Frontend:** sección "Privacidad (Habeas Data)" (Configuración): exportar datos (descarga JSON), registrar solicitud y tabla de solicitudes con completar/rechazar. Badge de pendientes en el nav.
- **Test:** `test_admin_privacidad_a45.py` → **27/27**.

### Pendiente (Fase 6)
- A46 emails Resend · A47 verticales · A48 integraciones · A49 gestor de textos.

### Siguiente paso
- **A46 — Gestor de plantillas de email (Resend) + deliverability**.

---

## 2026-06-05 — Panel admin A44 · Administración de Dora IA

**Sprint actual:** Panel de Administración. **Fase 6.** Avance **44/51**.

### Completado
- **A44 — Admin de Dora IA (costos y abuso).** Antes Dora no tenía control admin (modelo hardcodeado, sin límites ni tracking → costo impredecible).
  - **Backend:** config IA en `config_global` (clave `ia`) + helpers PUROS `validar_ia_config`, `limite_ia_por_plan`, `puede_usar_ia` en `config_plataforma.py`. Tabla `ia_uso` (negocio_id, fecha, usos; migración en `create_app`). **Integración en `call_groq`** (choke point único de Dora): aplica **toggle global** + **límite diario por plan** antes de llamar a Groq, usa **modelo/max_tokens** de config, y registra el uso solo tras éxito. Todo a prueba de fallos: ante cualquier error de gobierno, deja pasar para no romper Dora. Endpoints `GET /api/admin/ia` (config + consumo hoy/30d + top consumidores) y `PUT .../ia/config` (**superadmin**, auditado).
  - **Frontend:** sección "IA (Dora)" (Plataforma): stat-cards de consumo + estado, toggle de Dora, modelo/tokens, límites/día por plan, tabla de top consumidores.
- **Test:** `test_admin_ia_a44.py` → **27/27**.

### Pendiente (Fase 6)
- A45 Habeas Data · A46 emails Resend · A47 verticales · A48 integraciones · A49 gestor de textos.

### Siguiente paso
- **A45 — Habeas Data / privacidad** (exportar datos de usuario, derecho al olvido, consentimientos — Ley 1581).

---

## 2026-06-05 — Panel admin A43 · Moderación global de reseñas

**Sprint actual:** Panel de Administración. **Fase 6.** Avance **43/51**.

### Completado
- **A43 — Moderación de reseñas a nivel plataforma** (complementa la moderación por-negocio existente).
  - **Backend:** helpers PUROS `normalizar_email` y `evaluar_resena_sospechosa` (heurística: no verificada, comentario mínimo, extremo 1/5★ sin texto, rating inválido) en `api/utils/resenas_service.py`. Tabla `resena_baneos` (email PK, migración en `create_app`). Endpoints `GET /api/admin/resenas` (filtros estado/rating/búsqueda, join negocio/producto, flags sospechosa + baneado), `POST .../resenas/<id>/moderar` (aprobar/ocultar), `GET/POST/DELETE .../resenas/baneos|banear` (banear oculta todas sus reseñas + bloquea futuras). Todos `requiere_permiso('negocios')`, auditados. **Cableo en `crear_resena`**: si el email está baneado, la reseña entra como NO aprobada (a prueba de fallos).
  - **Frontend:** sección "Reseñas" (Gestión): filtros, tabla con ★, 🚩 sospechosa, ✅ verificada, botones ocultar/aprobar + banear, y vista de baneados.
- **Test:** `test_admin_resenas_a43.py` → **25/25**.

### Pendiente (Fase 6)
- A44 admin Dora IA · A45 Habeas Data · A46 emails Resend · A47 verticales · A48 integraciones · A49 gestor de textos.

### Siguiente paso
- **A44 — Administración de Dora IA** (límites por plan, consumo/costo, prompts, abuso).

---

## 2026-06-05 — Panel admin A42 · Facturación / cobro de suscripciones

**Sprint actual:** Panel de Administración. **Fase 6.** Avance **42/51**.

### Completado
- **A42 — Facturación de suscripciones.** A34 asignaba planes pero no gestionaba el COBRO; ahora hay tablero de facturación + dunning.
  - **Backend:** helper PURO `clasificar_cobro(estado, dias, dias_alerta=7)` en `pagos_service.py` (buckets al_dia/por_vencer/en_gracia/vencida/cancelada/pausada + acción sugerida + `requiere_accion`). Endpoint `GET /api/admin/facturacion/resumen` (`requiere_permiso('pagos')`): conteo por estado usando `estado_actual` del modelo, **MRR estimado** (suma `precio_mensual` del plan de las activas), cobros (total + 30d desde `pagos_suscripcion`), y lista **dunning** ordenada (vencidas→gracia→por vencer) con nombre/plan/días/acción.
  - **Frontend:** sección "Facturación" (grupo Finanzas): stat-cards (MRR, activas, trial, gracia, vencidas, cobrado 30d), tabla de dunning con botón **Gestionar suscripción** (reusa el modal de A34) y botón **Enviar avisos** (reusa el cron de alertas existente). Badge de pendientes en el nav.
- **Test:** `test_admin_facturacion_a42.py` → **20/20**.

### Pendiente (Fase 6)
- A43 moderación reseñas · A44 admin Dora IA · A45 Habeas Data · A46 emails Resend · A47 verticales · A48 integraciones · A49 gestor de textos.

### Siguiente paso
- **A43 — Moderación de reseñas de productos** (vista global, detectar/ocultar reseñas abusivas/falsas).

---

## 2026-06-05 — Panel admin A41 · Centro de pagos (Wompi) · 💳 ARRANCA FASE 6

**Sprint actual:** Panel de Administración. **Fase 6 (Pagos/Legal/IA) iniciada (A41-A49).** Avance **41/51**.

### Completado
- **A41 — Centro de pagos (Wompi).** Antes el cobro real (pasarela) no tenía NINGUNA vista admin. Ahora sí.
  - **Backend:** helpers PUROS `evaluar_config_wompi(cfg)` (estado ok/incompleto/sin_configurar, ambiente, `webhook_ok` = tiene `events_key`, faltantes) y `mascara_clave` en `api/utils/pagos_service.py`. Endpoints `GET /api/admin/pagos/wompi` (resumen: total/activos/en_prod/**webhook_roto**/incompletos + lista por negocio + métricas de pago aprobados/pendientes/rechazados/monto) y `GET .../pagos/wompi/<negocio_id>` (config **enmascarada** + últimas 15 transacciones). `requiere_permiso('pagos')`. **Seguridad:** nunca devuelve integrity/events_key; solo presencia (`tiene_*`) y máscara del public_key.
  - **Punto clave:** detecta **webhook roto** = negocio activo sin `events_key` → el webhook (que exige firma desde A-SEC-2) rechaza todos los cobros. Alerta visible.
  - **Frontend:** nuevo grupo nav "Finanzas" → sección "Pagos (Wompi)": stat-cards, tabla con estado/ambiente/webhook/activo + alerta 🚩, modal de detalle con transacciones; badge de alertas en el nav.
- **Test:** `test_admin_pagos_a41.py` → **26/26**.

### Pendiente (Fase 6)
- A42 cobro de suscripciones (dunning) · A43 moderación reseñas · A44 admin Dora IA · A45 Habeas Data · A46 emails Resend · A47 verticales · A48 integraciones · A49 gestor de textos.

### Siguiente paso
- **A42 — Facturación y cobro de suscripciones TuKomercio** (estado de pago por negocio, vencimientos, dunning).

---

## 2026-06-05 — Panel admin A40 · Pulido final + docs · 🎉 FASE 5 COMPLETA

**Sprint actual:** Panel de Administración. **Fase 5 (Analítica/Salud/Cierre) COMPLETA (A36-A40).** Avance **40/51**.

### Completado
- **A40 — Pulido final + documentación.** Solo frontend + docs (sin cambios backend).
  - **Responsividad (bug real corregido):** el sidebar se ocultaba en móvil (<768px) **sin botón para abrirlo** → panel inservible en celular. Añadido **botón hamburguesa ☰ flotante** + **backdrop**, cierre del menú al elegir sección, `flex-wrap` en headers, tablas con scroll-x y fuente reducida.
  - **Ayuda contextual:** mapa `SECTION_HELP` (16 secciones) + línea de ayuda azul que se actualiza al cambiar de sección (y al cargar el dashboard).
  - **Docs:** nuevo `MANUAL_ADMIN.md` (guía paso a paso para el administrador) en el repo backend; `TuKomercio_Funcionalidades.md` **§25 reescrita** reflejando A1–A39, versión → **v2.20.0**.
- **Suite:** 1220/0 (sin tocar backend).
- **🎉 Cierre Fase 5:** reportes/CSV (A36), salud (A37), config global (A38), feature flags v2 (A39), pulido+docs (A40).

### Estado global
- Fases 0-5 ✅ (A1-A40, **40/51**). Pendiente: **Fase 6** (Pagos/Legal/IA, A41-A49) y **Fase 7 EXTRA** (notificaciones, A50-A51).

### Siguiente paso
- **A41 — arranca Fase 6** (Pagos Wompi avanzado / legal / Dora IA / emails / verticales).

---

## 2026-06-05 — Panel admin A39 · Feature flags v2 (rollout % + overrides)

**Sprint actual:** Panel de Administración. **Fase 5.** Avance **39/51**.

### Completado
- **A39 — Feature flags v2.** El sistema pasó de on/off global + plan a: **rollout gradual por %** y **overrides por negocio**.
  - **Backend:** columna `feature_flags.rollout_pct` (default 100, retrocompatible) + modelo `FeatureOverride` (tabla `feature_overrides`, UNIQUE negocio+feature) + helper PURO `en_rollout(negocio_id, feature_key, pct)` (bucket md5 determinista y monótono) en `feature_models.py`. **`check_negocio_feature` integrado:** override OFF→`override_off`; override ON→`override_on` (habilita aunque el plan no la tenga); si plan la incluye pero el negocio no entra en el rollout→`rollout_pending`. Todo a prueba de fallos (default 100 = sin cambio para lo existente). Migración en `create_app` (ALTER + CREATE, lección F8). Endpoints `PUT /api/admin/features/<id>/rollout`, `GET .../features/<key>/overrides`, `POST/DELETE .../features/override` (auditados).
  - **Frontend:** en cada fila de feature, input de **rollout %** + botón ✓; botón 👥 abre **modal de overrides por negocio** (agregar ON/OFF por ID, listar, quitar).
- **Test:** `test_admin_featureflags_a39.py` → **26/26**.

### Pendiente (Fase 5)
- A40 pulido final + documentación del panel → cierra Fase 5.

### Siguiente paso
- **A40 — Pulido final + docs** (responsividad del panel, ayuda contextual, manual admin, actualizar `TuKomercio_Funcionalidades.md` §25).

---

## 2026-06-05 — Panel admin A38 · Configuración global de la plataforma

**Sprint actual:** Panel de Administración. **Fase 5.** Avance **38/51**.

### Completado
- **A38 — Configuración global.** Toggles y textos editables sin tocar código.
  - **Backend:** nuevo modelo `ConfigGlobal` (tabla `config_global`) en `models/colombia_data/config_plataforma.py` — creada por `create_all` (tiene modelo, importado en `models/__init__.py`) **y** por migración en `create_app` (doble garantía, lección F8). `CONFIG_GLOBAL_DEFAULT` (modo_mantenimiento, mensaje, registro_abierto, mensaje_registro_cerrado, textos términos/privacidad/landing) + `validar/get/set_config_global` (parcial, a prueba de fallos). Endpoints `GET /api/admin/config-global` (`requiere_permiso('configuracion')`) y `PUT` (**superadmin**, auditado sin volcar textos largos).
  - **Cableo real:** endpoint público `GET /api/config-publica` (mantenimiento/registro) y `register_user` ahora **rechaza con 403** si `registro_abierto=false` (tolerante: si falla la lectura, no bloquea).
  - **Frontend:** sección/nav "Config. global": toggles (mantenimiento, registro) con sus mensajes + editores de términos, privacidad (Habeas Data) y hero de la landing.
- **Test:** `test_admin_config_global_a38.py` → **22/22**.

### Pendiente (Fase 5)
- A39 feature flags v2 · A40 pulido final + docs.

### Siguiente paso
- **A39 — Centro de feature flags v2** (rollout por %, por segmento, por negocio; histórico).

---

## 2026-06-05 — Panel admin A37 · Salud del sistema

**Sprint actual:** Panel de Administración. **Fase 5.** Avance **37/51**.

### Completado
- **A37 — Salud del sistema.** Panel de estado para diagnosticar la plataforma de un vistazo.
  - **Backend:** helper PURO `evaluar_salud(d)` + `UMBRAL_BUGS_ATENCION` en `api/utils/salud_service.py` (semáforo ok/atención/crítico: BD caída = crítico; bugs nuevos ≥ umbral = atención). Endpoint `GET /api/admin/salud` (`requiere_permiso('reportes')`): health de BD (`SELECT 1` + latencia ms), errores recientes (feedback `tipo_feedback='bug'` + conteos por estado), métricas de uso (pedidos 24h/7d, negocios/usuarios nuevos 7d, activos 7d vía last_login, productos 7d), acciones admin 24h. Tolerante: si la BD falla marca db_ok=False sin reventar.
  - **Frontend:** sección/nav "Salud del sistema" (grupo Configuración): semáforo de estado general + chips BD/bugs, stat-cards de uso, tabla de errores recientes con link a Reportes.
- **Test:** `test_admin_salud_a37.py` → **19/19**.

### Pendiente (Fase 5)
- A38 config global · A39 feature flags v2 · A40 pulido final + docs.

### Siguiente paso
- **A38 — Configuración global de la plataforma** (modo mantenimiento, registro abierto/cerrado, textos legales/landing).

---

## 2026-06-05 — Panel admin A36 · Centro de reportes exportables · 📊 ARRANCA FASE 5

**Sprint actual:** Panel de Administración. **Fase 5 (Analítica/Salud/Cierre) iniciada (A36-A40).** Avance **36/51**.

### Completado
- **A36 — Centro de reportes exportables.** Nueva sección "Analítica" de plataforma + export CSV.
  - **Backend:** helper PURO `a_csv(headers, filas)` + `_celda_csv` en `api/utils/reportes_service.py` (escape correcto de comas/comillas/saltos + BOM UTF-8 para Excel, CRLF). Endpoints `GET /api/admin/reportes/resumen` (totales, economía de TuKoins [emitidos/gastados/circulación/tx desde `tukoins_transacciones`], distribución por plan, crecimiento mensual de negocios/usuarios con `date_trunc`, top ciudades; excluye papelera) y `GET /api/admin/reportes/export?tipo=negocios|usuarios|tukoins|crecimiento` (auditado como `export`). Ambos `requiere_permiso('reportes')`.
  - **Frontend:** sección/nav "Analítica" (grupo General): stat-cards de totales, tarjetas de economía TuKoins, distribución por plan (barras), tabla de crecimiento, top ciudades, y botones de descarga CSV (Blob client-side).
- **Test:** `test_admin_reportes_a36.py` → **24/24**.
- **Nota:** PDF se omitió a propósito; el CSV (Excel/Sheets) cubre el caso y es más robusto.

### Pendiente (Fase 5)
- A37 salud del sistema · A38 config global · A39 feature flags v2 · A40 pulido final + docs.

### Siguiente paso
- **A37 — Salud del sistema (health, errores, métricas de uso)**.

---

## 2026-06-05 — Panel admin A35 · Modo soporte · 🎉 FASE 4 COMPLETA

**Sprint actual:** Panel de Administración. **Fase 4 (Negocios) COMPLETA (A29-A35).** Avance **35/51**.

### Completado
- **A35 — Modo soporte / "ver como el usuario".** Se descartó la impersonación real de sesión (inseguro); en su lugar, snapshot **read-only** + diagnóstico.
  - **Backend:** helper PURO `diagnosticar_negocio(snapshot)` en `api/utils/soporte_service.py` (detecta: en papelera, inactivo, sin logo, sin página, perfil oculto, sin productos, sin pedidos, suscripción vencida/pausada, trial; si nada → 'ok'). Endpoint `GET /api/admin/soporte/negocio/<id>` (`requiere_permiso('negocios')`, **solo lectura**, sin `login_user`, auditado con acción `soporte`). Devuelve negocio+dueño+suscripción+conteos+últimos 5 pedidos/productos+diagnóstico+link a la tienda pública. Acción `soporte` añadida a `ACCIONES_VALIDAS`.
  - **Frontend:** botón "Modo soporte" 🛟 por fila de negocio + modal con diagnóstico (✓/ℹ/⚠), métricas, últimos pedidos/productos y botón "Ver su tienda pública".
- **Test:** `test_admin_soporte_a35.py` → **20/20**.
- **🎉 Cierre Fase 4:** Ficha 360 (A29), papelera (A30), moderación videos/perfiles (A31), feed comunidad (A32), anuncios masivos (A33), planes avanzados (A34), soporte (A35).

### Pendiente
- Fase 5 (A36-A40 · Analítica), Fase 6 (A41-A49 · Pagos/Legal), Fase 7 EXTRA (A50-A51 · Notificaciones).

### Siguiente paso
- **A36 — arranca Fase 5 (Analítica/Salud/Cierre)**.

---

## 2026-06-05 — 🐞 FIX producción F9 · no se podían guardar fotos de producto

**Tipo:** corrección urgente (usuario nuevo bloqueado al cargar fotos, ~17 errores).

### Causa
- En `contabilidad/modulos/inventario.html` (módulo real de productos; `inventario.js` es legado y no se carga), `handleGaleriaUpload` **rechazaba** toda imagen > 5MB. Fotos de celular (3-8MB) → casi todas rechazadas = los ~17 errores.

### Solución (FRONT)
- Compresión en el cliente con canvas: helper `comprimirImagen` + `handleGaleriaUpload` async que comprime antes de añadir (8MB → ~300KB). Solo omite si tras comprimir sigue >5MB. `node --check` OK.
- Detalle en `memory/fixes_tienda_checkout.md` (F9).

---

## 2026-06-05 — Panel admin A34 · Gestión avanzada de planes

**Sprint actual:** Panel de Administración. **Fase 4.** Avance **34/51**.

### Completado
- **A34 — Gestión de planes avanzada.** Hasta ahora el panel solo dejaba editar las *features* de un plan; faltaba editar sus **datos** (precio, nombre, etc.). Ahora sí.
  - **Backend:** validador PURO `validar_plan_datos(payload)` en `feature_models.py` (parcial — solo valida/normaliza los campos enviados: nombre, descripción, precio_mensual/anual ≥0, color hex #RRGGBB, ícono, orden, activo). Endpoint `PUT /api/admin/planes/<id>` (`admin_required`, auditado con antes/después). Suscripciones (activar/extender/cancelar/pausar/trial) y pagos (listar/registrar) ya existían de v3.0.
  - **Frontend:** botón "Editar" ✏️ en cada tarjeta de plan + modal con precio mensual/anual, color picker, ícono, orden y checkbox "activo". La tarjeta ahora muestra precio anual y marca "(inactivo)".
- **Test:** `test_admin_planes_a34.py` → **19/19**.

### Pendiente (Fase 4)
- A35 soporte/impersonar (ver como el usuario, read-only, auditado) → cierra Fase 4.

### Siguiente paso
- **A35 — Soporte / impersonar**.

---

## 2026-06-05 — Panel admin A33 · Anuncios / notificaciones masivas

**Sprint actual:** Panel de Administración. **Fase 4.** Avance **33/49**.

### Completado
- **A33 — Anuncios masivos.** Enviar notificaciones in-app (campanita) a segmentos de usuarios.
  - **Backend:** servicio `api/utils/anuncios_service.py`: helper PURO `construir_filtros_segmento(filtros)` (ciudad ILIKE, plan_key, nivel_min vía join `negocio_gamificacion`; siempre excluye papelera y exige usuario_id) + `PLANTILLAS_ANUNCIO` (5 plantillas) + `contar_destinatarios` (preview) + `enviar_anuncio` (**un solo `INSERT ... SELECT`** sobre `notification`, sin N inserts). Endpoints `GET /anuncios/plantillas`, `POST /anuncios/preview`, `POST /anuncios/enviar` (exige `confirmar`+mensaje, auditado con conteo). Todos `requiere_permiso('usuarios')`.
  - **Frontend:** nueva sección/nav "Anuncios": filtros de segmento con **contador de destinatarios en vivo**, selector de plantilla, título/mensaje/prioridad y envío con confirmación.
- **Test:** `test_admin_anuncios_a33.py` → **25/25**.

### Pendiente (Fase 4)
- A34 planes/suscripciones avanzada · A35 soporte/impersonar.

### Siguiente paso
- **A34 — Gestión de planes y suscripciones avanzada**.

---

## 2026-06-05 — 🐞 FIX CRÍTICO F8 · migraciones de run.py no corrían en prod

**Tipo:** corrección urgente de producción (panel no cargaba negocios).

### Problema
- `/api/admin/negocios/planes` → 500 ("Error cargando negocios"). El filtro `n.eliminado` (A30) referenciaba una columna inexistente en prod.

### Causa raíz (grande)
- En producción el entrypoint NO es `run.py` (Procfile `gunicorn run:run` sin variable `run`; Render usa el app factory). El único bloque de migraciones que corre en prod está en `src/__init__.py::create_app()`. `db.create_all()` crea **tablas con modelo** (por eso `gamif_config`/`intentos_login` existían) pero **NO añade columnas a tablas existentes ni crea tablas sin modelo**. → Todas mis migraciones en `run.py` (A15/A19/A25/A28/A30/A32 + columnas de F7) **nunca se aplicaron en prod**. F7 tampoco había quedado.

### Solución
- Copiadas TODAS las sentencias `ALTER … ADD COLUMN IF NOT EXISTS` / `CREATE TABLE IF NOT EXISTS` a la lista `migraciones` de `create_app()` en `src/__init__.py` (idempotentes, commit individual). Se aplican al desplegar.
- Documentado en `CLAUDE.md` (regla: migraciones SIEMPRE en `create_app()`), `memory/fixes_tienda_checkout.md` (F8) y `memory/feedback_repos_structure`.

### Post-deploy
- Reasignar Deluxe al negocio afectado (F7) ya debe funcionar; el listado de negocios vuelve a cargar.

---

## 2026-06-05 — Panel admin A32 · Moderación del feed de comunidad

**Sprint actual:** Panel de Administración. **Fase 4.** Avance **32/49**.

### Completado
- **A32 — Moderación del feed de comunidad (S32).** Control de los logros destacados (insignias Oro+) que se muestran como prueba social.
  - **Backend:** `FEED_COMUNIDAD_DEFAULT` (nivel_minimo 3, limite 15) + `validar/get/set_feed_comunidad_config` en `config_gamificacion.py`. Columna `negocio_badges_obtenidos.oculto_feed` (migración `run.py`). El feed público `eventos_comunidad()` ahora lee **nivel y límite configurables** y **excluye `oculto_feed`** (fallback al DEFAULT). Endpoints `GET /api/admin/feed-comunidad` (incluye ocultos + estado), `POST .../feed-comunidad/<id>/ocultar` (oculta/muestra **sin revocar** la insignia), `PUT .../feed-comunidad/config`. Todos `requiere_permiso('gamificacion')` y auditados.
  - **Frontend:** tarjeta "🌟 Feed de comunidad" en la sección Videos/Feed: inputs de nivel mínimo + límite, y tabla de logros con botón ocultar/mostrar y badge de estado (visible/oculto/revocado).
- **Test:** `test_admin_feed_comunidad_a32.py` → **21/21**.

### Pendiente (Fase 4)
- A33 anuncios/notificaciones masivas · A34 planes/suscripciones avanzada · A35 soporte/impersonar.

### Siguiente paso
- **A33 — Anuncios y notificaciones masivas** (avisos a segmentos por ciudad/plan/nivel; plantillas).

---

## 2026-06-05 — Panel admin A31 · Moderación de videos/feed y perfiles de creador

**Sprint actual:** Panel de Administración. **Fase 4.** Avance **31/49**.

### Completado
- **A31 — Moderación de feed/videos + perfiles de creador.**
  - **Backend:** helper PURO `aplicar_accion_video(accion)` + `ACCIONES_MODERACION_VIDEO` en `negocio_video.py` (aprobar/rechazar/ocultar/mostrar/destacar/quitar_destacado → dict de cambios). Endpoints `GET /api/admin/videos?estado=&limit=` (join `nombre_negocio`, resumen por estado_moderacion + ocultos), `POST .../videos/<id>/moderar` (valida acción, 404, guarda `motivo_rechazo`, `fecha_moderacion`, auditado), `GET .../perfiles-creador?buscar=` (excluye papelera), `POST .../negocios/<id>/perfil-publico` (toggle `perfil_publico`, auditado). Todos `requiere_permiso('negocios')`.
  - **Decisión:** la moderación opera sobre `visible` (rechazar/ocultar → `visible=false`, sale del feed que ya filtra por `visible`). NO se cambió el filtro del feed público a exigir `estado_moderacion='aprobado'` para no ocultar el feed actual (la mayoría de videos están en 'pendiente' por defecto).
  - **Frontend:** nueva sección + nav "Videos / Feed" (con badge de pendientes), tabla con thumbnail/estado/visible/acciones, filtro por estado, resumen coloreado; y tabla de "Perfiles públicos de creador" con búsqueda y toggle mostrar/ocultar.
- **Test:** `test_admin_videos_a31.py` → **27/27**.

### Pendiente (Fase 4)
- A32 moderación feed comunidad · A33 anuncios/notificaciones masivas · A34 planes/suscripciones avanzada · A35 soporte/impersonar.

### Siguiente paso
- **A32 — Moderación del feed de comunidad** (logros destacados S32, ocultar abusos).

---

## 2026-06-05 — Panel admin A30 · Soft-delete + papelera

**Sprint actual:** Panel de Administración. **Fase 4.** Avance **30/49**.

### Completado
- **A30 — Soft-delete + papelera (negocios y usuarios).** Reemplaza el borrado en cascada irreversible por baja lógica + restauración; el hard-delete queda como "purga" solo desde la papelera.
  - **Esquema:** columnas `eliminado`/`eliminado_en`/`eliminado_por` en `negocios` y `usuarios` (migración `run.py`, `ADD COLUMN IF NOT EXISTS`).
  - **Truco anti-scope:** soft-delete de negocio pone también `activo=false` → ya queda oculto en todas las vistas que filtran por `activo` (storefront, listados) sin tocar decenas de queries. Soft-delete de usuario pone `active=false` → el login ya rechaza `not active`. El flag `eliminado` distingue "papelera" de "desactivado/lista negra".
  - **Endpoints:** `POST .../negocios/<id>/papelera` + `/restaurar` (`requiere_permiso('negocios')`); `POST .../usuarios/<id>/papelera` + `/restaurar` (`superadmin`, bloquea administradores); `GET /api/admin/papelera`. Listados (`list_usuarios`, `list_negocios_with_plans`) excluyen `eliminado`. Todo auditado (`eliminar`/`restaurar`).
  - **Frontend:** botón "Enviar a papelera" 📦 por fila + botón/modal "Papelera" en la sección Negocios (restaurar y purgar definitivamente con confirmación).
- **Test:** `test_admin_papelera_a30.py` → **24/24**.

### Pendiente (Fase 4)
- A31 moderación feed/videos + perfiles creador · A32 moderación feed comunidad · A33 anuncios/notificaciones masivas · A34 planes/suscripciones avanzada · A35 soporte/impersonar.

### Siguiente paso
- **A31 — Moderación de feed/videos y perfiles de creador**.

---

## 2026-06-05 — Panel admin A29 · Ficha 360° del negocio · 🏪 ARRANCA FASE 4

**Sprint actual:** Panel de Administración. **Fase 4 (Negocios) iniciada (A29-A35).** Avance **29/49**.

### Completado
- **A29 — Ficha 360° del negocio.** Vista agregada de todo un negocio en un modal.
  - **Backend:** endpoint `GET /api/admin/negocios/<id>/ficha360` (`requiere_permiso('negocios')`). Agrega: datos del negocio (columnas correctas `id_negocio`/`nombre_negocio`), dueño (usuarios), suscripción (try/except, resiste el schema drift de F7), gamificación (nivel/XP/TuKoins/prestigio/racha/insignias), pedidos (total/entregados/ventas_total), productos y videos (por `estado_moderacion`). Conteos vía `_scalar_admin` (tolerante). 404 si el negocio no existe; cada bloque a prueba de fallos.
  - **Frontend:** modal "Ficha 360°" + botón por fila (icono clipboard) en la tabla de Negocios; render con chips por sección (estado/plan, dueño, suscripción, gamificación, actividad).
- **Test:** `test_admin_ficha360_a29.py` → **20/20**.

### Pendiente (Fase 4)
- A30 soft-delete + papelera · A31 moderación feed/videos + perfiles creador · A32 moderación feed comunidad · A33 anuncios/notificaciones masivas · A34 planes/suscripciones avanzada · A35 soporte/impersonar.

### Problemas
- Ninguno.

### Siguiente paso
- **A30 — Soft-delete + papelera (usuarios y negocios)**.

---

## 2026-06-05 — Panel admin A28 · Challenges 2.0 · 🎉 FASE 3 COMPLETA

**Sprint actual:** Panel de Administración. **Fase 3 (Eventos/Retos/Competencia) COMPLETA (A22-A28).** Avance **28/49**.

### Completado
- **A28 — Challenges 2.0 (integración con gamificación).** El concurso por video ahora da XP+TuKoins.
  - **Backend:** `CHALLENGE_REWARDS_DEFAULT` (participar 30 XP/15 TK, ganador 300 XP/150 TK) + helpers PUROS `validar_challenge_rewards` + `get/set_challenge_rewards` en `config_gamificacion.py`. Servicio `api/utils/challenge_gamif_service.py`: `premiar_participacion_aprobada` (al aprobar) y `finalizar_y_premiar` (al cerrar, ganador = más votos entre aprobadas). **Idempotente** vía flags `challenge_participaciones.gamif_otorgado` y `challenges.gamif_premiado` (migración en `run.py`). `update_participacion_estado` dispara el premio al aprobar **sin romper la moderación** (try/except).
  - **Endpoints:** `POST /api/admin/challenges/<id>/finalizar` y `GET/PUT .../challenges/recompensas-config` (`requiere_permiso('challenges')`, auditados).
  - **Frontend:** en la sección Challenges, tarjeta "🎮 Recompensas de gamificación" (4 campos) + botón "Finalizar y premiar" 🏆 por challenge (oculto si ya finalizado).
- **Test:** `test_admin_challenges_a28.py` → **25/25**.
- **🎉 Cierre de Fase 3:** eventos (A22), retos (A23), ligas + moderación (A24), recompensas de liga (A25), duelos (A26), referidos (A27) y challenges (A28) — toda la competencia/gamificación social administrable sin código.
- **Hallazgo (no bloqueante):** el listado de participaciones (`list_participaciones`) hace `JOIN negocios n ON n.id = cp.negocio_id` con `n.nombre`/`n.logo_url`, pero la tabla usa `id_negocio`/`nombre_negocio` → el nombre del negocio probablemente sale null ahí. No tocado en A28 (fuera de alcance); candidato a fix aparte.

### Pendiente
- Fase 4 (A29-A35), Fase 5 (A36-A40), Fase 6 (A41-A49).

### Siguiente paso
- **A29 — arranca Fase 4 (Negocios)**.

---

## 2026-06-05 — 🐞 FIX producción F7 · plan no se activa (schema drift suscripciones)

**Tipo:** corrección urgente de producción (no es sprint del roadmap).

### Problema
- Negocio con plan Deluxe asignado **atascado en plan básico** → solo permite 1 producto; al usuario le decía "tu plan no sirve para usar esa función"; y al activar el trial salía `UndefinedColumn: suscripciones_negocio.alertas_enviadas does not exist`.

### Causa raíz (una sola)
- **Schema drift:** el modelo `SuscripcionNegocio` declara `alertas_enviadas` (y `creado_por`/`modificado_por`/`notas`) que NO existen en la tabla de producción. Cualquier `SuscripcionNegocio.query...first()` revienta → `update_suscripcion_negocio` (admin_features_api) se cae ANTES del `UPDATE negocios SET plan_key=...` → el negocio nunca pasa a Deluxe → `check_negocio_feature` (lee `negocios.plan_key`) aplica límites de básico.

### Solución
- **`run.py`:** auto-migración `ALTER TABLE suscripciones_negocio ADD COLUMN IF NOT EXISTS` para `alertas_enviadas JSON`, `creado_por VARCHAR(50)`, `modificado_por VARCHAR(50)`, `notas TEXT`. Patrón estándar del proyecto. Suite verde (sin regresión).
- **Post-deploy (manual):** reasignar Deluxe al negocio 37 desde el panel (el primer intento no quedó persistido).

### Detalle en
- `memory/fixes_tienda_checkout.md` → F7.

---

## 2026-06-05 — Panel admin A27 · Gestión de referidos

**Sprint actual:** Panel de Administración. **Fase 3.** Avance **27/49**.

### Completado
- **A27 — Gestión de referidos.** Administración del sistema de referidos (S29) desde el panel.
  - **Backend:** `REFERIDOS_CONFIG_DEFAULT` (xp 50 / tukoins 30 / umbral_fraude 10 / ratio_min 0.2) + helpers PUROS `validar_referidos_config` y `marcar_referidores_sospechosos` (marca referidores con `total ≥ umbral` y `convertidos/total < ratio_min` → muchos referidos casi sin conversión = posibles cuentas falsas) + `get/set_referidos_config` en `config_gamificacion.py`. **`procesar_conversion_referido()` ahora lee la config efectiva** (recompensas editables sin tocar código; fallback a las constantes S29).
  - **Endpoints:** `GET /api/admin/gamificacion/referidos` (stats globales de conversión + top referidores con nombre/correo y flag 🚩 + referidos recientes + config) y `PUT .../referidos/config` (auditado). Ambos `requiere_permiso('gamificacion')`.
  - **Frontend:** tarjeta "🔗 Gestión de referidos": chips de stats (total/convertidos/tasa/recompensados/sospechosos), form de config (XP/TuKoins/umbral/ratio), tabla de top referidores (resalta sospechosos) y `<details>` con referidos recientes. Responsive (scroll-x), `escapeHtml`.
- **Test:** `test_admin_referidos_a27.py` → **28/28**.

### Pendiente (Fase 3)
- A28 challenges 2.0 (integrar challenges con gamificación) → cierra la Fase 3.

### Problemas
- Ninguno.

### Siguiente paso
- **A28 — Challenges 2.0**: integrar el sistema de challenges con la gamificación. Cierra Fase 3.

---

## 2026-06-05 — Panel admin A26 · Moderación de duelos

**Sprint actual:** Panel de Administración. **Fase 3.** Avance **26/49**.

### Completado
- **A26 — Moderación de duelos.** Visibilidad y control de los duelos 1v1 (S31).
  - **Backend:** nuevo estado `cancelado` + helper PURO `puede_cancelar_duelo(estado)` (solo `pendiente`/`activo`) y `ESTADOS_CANCELABLES` en `duelo.py`. Endpoints `GET /api/admin/gamificacion/duelos?estado=&limit=` (join de nombres de retador/retado + marcador + resumen por estado en toda la tabla) y `POST .../duelos/<id>/cancelar` (valida cancelabilidad, auditado como acción `rechazar` sobre entidad `duelo` con motivo). Ambos `requiere_permiso('gamificacion')`.
  - **Frontend:** tarjeta "⚔️ Moderación de duelos": filtro por estado, chips de resumen coloreados, tabla con marcador (retador-retado), 👑 ganador, badge de estado y botón Cancelar (solo si cancelable, con prompt de motivo). Responsive (scroll-x), `escapeHtml`.
- **Test:** `test_admin_duelos_a26.py` → **20/20**.

### Pendiente (Fase 3)
- A27 gestión de referidos · A28 challenges 2.0.

### Problemas
- Ninguno.

### Siguiente paso
- **A27 — Gestión de referidos**: ver árbol de referidos, conversiones, detectar fraude, ajustar recompensas (cubre captura `?ref=` pendiente de S29).

---

## 2026-06-05 — Panel admin A25 · Recompensas automáticas de liga (cron + UI)

**Sprint actual:** Panel de Administración. **Fase 3.** Avance **25/49**.

### Completado
- **A25 — Recompensas automáticas de liga.** Premio al **top-N del mes anterior** (XP + TuKoins por puesto, configurables), pensado para correr al cierre de cada mes (manual desde el panel o vía cron externo).
  - **Idempotencia:** nueva tabla `liga_recompensas` con `UNIQUE (periodo, liga, negocio_id)` + `ON CONFLICT DO NOTHING` y chequeo previo → ejecutarlo varias veces el mismo mes NO duplica premios. Migración auto en `run.py`.
  - **Backend:** `RECOMPENSAS_LIGA_DEFAULT` (top-3: 500/300/150 XP, 200/120/60 TK) + helpers PUROS `validar_recompensas_liga`, `recompensa_por_posicion`, `construir_plan_recompensas` (los **vetados de A24 NO ocupan podio**) + `get/set_recompensas_liga` en `config_gamificacion.py`. Servicio `api/utils/liga_recompensas_service.py`: `calcular_` (dry-run), `otorgar_` (aplica con `agregar_xp`/`agregar_tukoins` + log), `historial_`.
  - **Endpoints:** `GET .../ligas/recompensas` (config+preview+historial), `PUT .../recompensas/config`, `POST .../recompensas/simular` (`requiere_permiso`), `POST .../recompensas/ejecutar` (**`@superadmin_required` + `confirmar:true`**, auditado con conteo; sirve también de endpoint de cron mensual con API key admin — patrón "cron manual" ya usado en `admin_features_api`).
  - **Frontend:** dentro de la tarjeta de Ligas, bloque "🏅 Recompensas automáticas": editor de premios por puesto, **simular (dry-run)** → habilita "Ejecutar ahora" (gate), e historial. Responsive, `escapeHtml`.
- **Test:** `test_admin_recompensas_liga_a25.py` → **34/34**.

### Pendiente (Fase 3)
- A26 moderación de duelos · A27 gestión de referidos · A28 challenges 2.0.

### Problemas
- Ninguno nuevo.

### Siguiente paso
- **A26 — Moderación de duelos**: ver duelos activos/históricos, cancelar abusivos, ver marcadores.

---

## 2026-06-05 — Panel admin A24 · Moderación de ligas

**Sprint actual:** Panel de Administración. **Fase 3.** Avance **24/49**.

### Completado
- **A24 — Moderación de ligas.** Las ligas se calculan al vuelo (ranking por pedidos entregados/mes, filtrable por ciudad/categoría); no hay entidad persistida. Se añadió control de moderación:
  - **Backend:** helpers PUROS `validar_ligas_config(payload)` y `detectar_anomalias(filas, umbral)` (z-score = (puntaje−media)/desv; marca puntajes atípicamente altos = posible fraude; requiere n≥3 y desv>0) + `get/set_ligas_config()` y `get/set_negocios_excluidos_ligas()` en `config_gamificacion.py` (gamif_config `ligas_config` y `ligas_excluidos`). La liga **pública** (`ligas()`) ahora **excluye** a los negocios vetados (`NOT IN`, IDs int inline, a prueba de fallos).
  - **Endpoints:** `GET /api/admin/gamificacion/ligas` (ranking + stats + anomalías marcadas + excluidos), `PUT .../ligas/config` (min_participantes 1-100, umbral_anomalia 1.0-6.0), `POST .../ligas/moderar` (`excluir`/`readmitir`). Todos `requiere_permiso('gamificacion')` y auditados. Se añadieron `excluir`/`readmitir` a `ACCIONES_VALIDAS`.
  - **Frontend:** tarjeta "🏟️ Moderación de ligas": filtros ciudad/categoría (con debounce), chips de stats (participantes, segmentada, ventas, promedio, anomalías), tabla con 🚩 z-score y botón vetar/readmitir, y form de config. Responsive (tabla con scroll-x), `escapeHtml`.
- **Test:** `test_admin_ligas_a24.py` → **29/29**.
- **Nota matemática:** con un único outlier, el z-score máximo ≈ √(n−1); por eso las anomalías solo se detectan en ligas con suficientes participantes (correcto: importan en ligas grandes).

### Pendiente (Fase 3)
- A25 recompensas automáticas de liga (cron + UI) · A26 moderación de duelos · A27 gestión de referidos · A28 challenges 2.0.

### Problemas
- Test inicial usaba 5 participantes con 1 outlier → no detectable (z máx ≈2.0 < umbral 3). Corregido a datos realistas (20+1).
- `text()` no expande tuplas en `IN`; los IDs (ya validados int) se insertan inline de forma segura.

### Siguiente paso
- **A25 — Recompensas automáticas de liga (cron + UI)**: job mensual que premia al top-3 de cada liga + pantalla para revisar/forzar la ejecución.

---

## 2026-06-05 — Panel admin A23 · Editor de retos mensuales

**Sprint actual:** Panel de Administración. **Fase 3 (Eventos/Retos/Competencia).** Avance **23/49**.

### Completado
- **A23 — Editor de retos mensuales:** el pool `RETOS_MENSUALES` (Rey de las Ventas, El Más Productivo, Rey del Catálogo) pasa de constante a **BD editable** + **programación por mes**.
  - **Backend:** helpers PUROS `seleccionar_reto(pool, programacion, hoy)`, `validar_retos(payload)` y `validar_programacion_retos(payload, codigos)` + `get/set_retos_mensuales()` y `get/set_programacion_retos()` en `config_gamificacion.py`. La **métrica se valida** contra `METRICAS_RETO` = las soportadas por `_ranking_por_metrica` (`ventas_mes`, `productos_mes`, `productos_activos`) → un reto con métrica inventada se rechaza (no rompe el ranking). La **programación** (`{YYYY-MM: codigo}`) pisa la rotación automática solo si el código existe en el pool. `_reto_del_mes()` lee pool+programación y **cae a la rotación sobre el DEFAULT si la BD falla**.
  - **Endpoints:** `GET/PUT /api/admin/gamificacion/retos` (`requiere_permiso('gamificacion')`, auditados). El GET devuelve pool, default, métricas, programación y el reto **actual**.
  - **Frontend:** tarjeta "🏆 Retos mensuales" en la sección Gamificación: filas editables (ícono/nombre/métrica/descripción) + bloque "📅 Programación por mes" (input `month` + selector de reto). Responsive, `escapeHtml` en el render.
- **Test:** `test_admin_retos_a23.py` → **28/28**.

### Pendiente (Fase 3)
- A24 moderación de ligas · A25 recompensas de liga (cron) · A26 moderación de duelos · A27 gestión de referidos · A28 challenges 2.0.

### Problemas
- Ninguno. Import perezoso (`_retos_default()`) para evitar circular entre `config_gamificacion` y `gamificacion_api`.

### Siguiente paso
- **A24 — Moderación de ligas** (ver ligas por ciudad/categoría, anomalías, segmentación, top-3).

---

## 2026-06-05 — Panel admin A22 · 🛍️ ARRANCA FASE 3 (Eventos)

**Sprint actual:** Panel de Administración. **Fase 3 (Eventos, Retos y Competencia) iniciada (A22-A28).** Avance **22/49**.

### Completado
- **A22 — Gestor de eventos especiales (XP×):** se llevó `EVENTOS_ESPECIALES` (Semana del Tendero ×3, Aniversario ×2, Diciembre Mágico ×2) de constante en código a **BD editable** con el patrón "constante→BD con fallback".
  - **Backend:** helpers PUROS `evento_activo_en(lista, fecha)` y `validar_eventos(payload)` + `get/set_eventos_especiales()` en `config_gamificacion.py` (override en `gamif_config`, clave `eventos_especiales`). `evento_especial()` ahora lee la lista efectiva y **cae al DEFAULT del módulo si la BD no está** (operación a prueba de fallos; los tests sin app-context siguen verdes). Validación: mes 1-12, día 1-31, `dia_ini ≤ dia_fin`, `xp_mult` 1-10, código slug único.
  - **Endpoints:** `GET/PUT /api/admin/gamificacion/eventos` con `@requiere_permiso('gamificacion')`, auditados (`registrar_auditoria('editar','gamif_eventos', …, {antes, despues, total})`). El GET además devuelve el evento **activo hoy**.
  - **Frontend:** tarjeta "🎉 Eventos especiales (XP×)" en la sección Gamificación del panel: filas editables (ícono/nombre/mes/día ini/día fin/XP×), añadir/eliminar, guardar, e indicador del evento activo. Responsive (grid). `escapeHtml` en todo el render.
- **Test:** `test_admin_eventos_a22.py` → **28/28**. Suite completa **809/0**.

### Pendiente (Fase 3)
- A23 editor de retos mensuales · A24 moderación de ligas · A25 recompensas de liga (cron) · A26 moderación de duelos · A27 gestión de referidos · A28 challenges 2.0.

### Problemas
- Ninguno. El acoplamiento `config_gamificacion ↔ negocio_gamificacion` se resolvió con import perezoso (`_eventos_default()`) para evitar import circular.

### Siguiente paso
- **A23 — Editor de retos mensuales** (CRUD de `RETOS_MENSUALES`: métrica objetivo, recompensa, copy; programar el del mes).

---

## 2026-06-04 — Panel admin A21 · 🎉 FASE 2 COMPLETA

**Sprint actual:** Panel de Administración. **Fase 2 (Insignias) COMPLETA (A15-A21).** Avance **21/49**.

### ✅ Completado
- **A21 — Preview en vivo del diseño:** chip en el modal de insignia que refleja ícono/color/nombre/tier mientras se edita; el color pasó a `<input type="color">` (siempre hex válido). Solo frontend → **suite 781/0**. Commit: front `5df6434`.
- **🎉 Cierre de la Fase 2:** el admin gestiona las insignias SIN código → CRUD (A15), editor de criterios + cobertura (A16), otorgar/revocar (A17), coherencia por tier (A18), temporada/vigencia (A19), progreso/otorgamientos (A20), preview en vivo (A21).

### ⏳ Pendiente
- **Fase 3 — Eventos, Retos y Competencia (A22-A28):** gestor de eventos especiales (XP x), retos mensuales, ligas, recompensas de liga (cron), duelos, referidos, challenges 2.0.

### 👉 Siguiente paso sugerido
Abrir la **Fase 3 con A22 — Gestor de eventos especiales** (mover `EVENTOS_ESPECIALES` a BD: CRUD de eventos por fecha con multiplicador de XP).

---

## 2026-06-04 — Panel admin A20 (progreso/otorgamientos)

**Sprint actual:** Panel de Administración, Fase 2 (Insignias). Avance **20/49**.

### ✅ Completado
- **A20 — Vista de progreso/otorgamientos:** `GET /insignias/distribucion` (por tier) + `GET /insignias/<id>/estadisticas` (total otorgados, últimos en obtenerla, **ranking de cercanía** de negocios sin ella por % al criterio; solo `>=` numérico no secreto; acotado; sin escribir). Frontend: botón 📊 → modal (total + recientes + barras de cercanía) + distribución por tier en la cabecera. `test_admin_progreso_a20.py` 18/18 → **suite 781/0**. Commits: back `6408c8e`, front `75861ce`.

### ⏳ Pendiente
- Fase 2: **A21** (preview en vivo del diseño del badge) → cierra la Fase 2.

### 👉 Siguiente paso sugerido
**A21 — Preview en vivo del diseño** (mostrar cómo se verá la insignia con su ícono/color/tier mientras se edita) y con eso se cierra la Fase 2.

---

## 2026-06-04 — Panel admin A19 (insignias de temporada)

**Sprint actual:** Panel de Administración, Fase 2 (Insignias). Avance **19/49**.

### ✅ Completado
- **A19 — Insignias de temporada/evento:** columnas `vigencia_inicio/vigencia_fin` por insignia (null=siempre) + migración. `badge_vigente()` puro; el servicio (`verificar_badges`/`simular_badges`) no otorga fuera de la ventana → cualquier insignia se puede programar por fechas SIN código (generaliza el hardcode de `temporadas_activas`). Frontend: campos de fecha en el modal + indicador 🗓️ en la lista. `test_admin_temporada_a19.py` 19/19 → **suite 763/0**. Commits: back `6046799`, front `deda213`.

### ⏳ Pendiente
- Fase 2: A20 (vista de progreso/otorgamientos por insignia), A21 (preview en vivo del diseño). Con eso se cierra la Fase 2.

### 👉 Siguiente paso sugerido
**A20 — Vista de progreso/otorgamientos** (por insignia: cuántos la tienen, distribución por tier, ranking de cercanía).

---

## 2026-06-04 — Panel admin A18 (coherencia de tier)

**Sprint actual:** Panel de Administración, Fase 2 (Insignias). Avance **18/49**.

### ✅ Completado
- **A18 — Validador de coherencia (CURVA_DIFICULTAD):** la coherencia real no existía (la constante era solo tier→nombre). `evaluar_coherencia_tier()` puro avisa si, dentro de una métrica, la dificultad rompe la monotonicidad por tier (>=/> creciente; <=/< decreciente). `POST /insignias/coherencia`. Frontend: la vista previa muestra ✓/⚠️ y al guardar pide confirmación si hay avisos (no bloquea). `test_admin_coherencia_a18.py` 15/15 → **suite 744/0**. Commits: back `7395917`, front `9bd968f`.

### ⏳ Pendiente
- Fase 2: A19 (insignias por temporada/evento programadas), A20 (vista de progreso/otorgamientos por insignia), A21 (preview en vivo del diseño).

### 👉 Siguiente paso sugerido
**A19 — Insignias de temporada/evento** (activar insignias por ventana de fecha, calendario).

---

## 2026-06-04 — Panel admin A17 (otorgar/revocar insignias)

**Sprint actual:** Panel de Administración, Fase 2 (Insignias). Avance **17/49**.

### ✅ Completado
- **A17 — Otorgar / revocar insignias manualmente:** `POST /insignias/<id>/otorgar` (idempotente, reactiva revocadas, valida negocio, auditado) y `POST /insignias/<id>/revocar` (`@superadmin_required`, motivo obligatorio, soft-delete, auditado). Reusa `NegocioBadgeObtenido`. Frontend: botón 🎖️ + modal por insignia. `test_admin_otorgar_a17.py` 16/16 → **suite 729/0**. Commits: back `0f97c2f`, front `3df898e`.

### ⏳ Pendiente
- Fase 2: A18 (validador CURVA_DIFICULTAD), A19 (insignias por temporada), A20 (vista de progreso/otorgamientos), A21 (preview en vivo del diseño).

### 👉 Siguiente paso sugerido
**A18 — Validador de coherencia (CURVA_DIFICULTAD):** avisar si un criterio rompe la monotonicidad de dificultad por tier antes de guardar.

---

## 2026-06-04 — Panel admin A16 (editor visual de criterios)

**Sprint actual:** Panel de Administración, Fase 2 (Insignias). Avance **16/49**.

### ✅ Completado
- **A16 — Editor visual de criterios:** `METRICAS_CRITERIO` (~28 métricas key→label, todas verificadas contra `BadgeVerificationService`). Endpoints `GET /insignias/metricas` y `POST /insignias/criterio/preview` (cuenta cuántos negocios cumplirían un criterio, acotado, sin escribir). En el modal de insignia, el criterio pasó de input libre a **selector de métricas** + botón "Vista previa de cobertura". `test_admin_criterios_a16.py` 16/16 → **suite 713/0**. Commits: back `8f4cdf4`, front `8b26569`.

### ⏳ Pendiente
- Fase 2: A17 (otorgar/revocar manual), A18 (validador CURVA_DIFICULTAD), A19 (insignias por temporada), A20 (vista de progreso/otorgamientos), A21 (preview en vivo del diseño).

### 👉 Siguiente paso sugerido
**A17 — Otorgar / revocar insignias manualmente** (dar o quitar un badge a un negocio, auditado).

---

## 2026-06-04 — ✅ Verificación de flujos del panel + deploy (post A-SEC-2)

**Tarea:** confirmar que el frontend manda `credentials:'include'` a los endpoints ahora protegidos. Deploy a producción.

### 🔎 Hallazgo
- Tras A-SEC-2, varios `fetch` de los módulos del tendero **no enviaban la cookie de sesión** (antes pasaban por el header `X-User-ID`, ya ignorado): `pedidos.html` (15/16 sin credentials), `crm`, `cupones`, `carritos`, `analytics`, `wompi`, `venta`, `dropshipping`, parte de `inventario.js`. Sin esto, esos paneles habrían dado 401 tras el deploy.

### ✅ Corregido
- **Wrapper de `window.fetch`** inyectado en `<head>` de cada módulo del tendero (cargan como **iframe** → ejecuta en cada doc) que añade `credentials:'include'` SOLO a llamadas al API propio (onrender.com / `/api/`), respeta credenciales explícitas y deja intactas las de terceros (Cloudinary). Idempotente. 11 módulos.
- Admin (`admin.html` 65/65) y `wizard.js` ya enviaban credentials → sin cambios.
- Verificado: `/producto/<id>/vista` y `/productos/publicos/<id>` siguen **públicos** (compradores sin sesión) → tienda pública intacta.
- Validado JS (`node --check`) en los 11 módulos.

### 🧪 Prueba mental de los 3 flujos críticos → OK
1. **Tendero ve sus pedidos:** iframe pedidos → wrapper añade cookie → guard valida sesión + propiedad de negocio → ve solo los suyos.
2. **Tendero edita un producto:** iframe inventario → `require_auth` con sesión → producto scopeado por `usuario_id` → no puede tocar ajenos.
3. **Comprador magic link:** heyden → `/pedidos/buscar?codigo=` (público allowlist) + catálogo público → sin sesión, ve solo SU pedido por el código.

### 🚀 Deploy
- Push a `main` en ambos repos → Render (backend) + Cloudflare Pages (frontend) auto-deploy. Commits: back A-SEC-2 `5bc73ef`, front `5421624`.

### 👉 Siguiente paso sugerido
Tras validación manual de Carlos → retomar **A16** (editor visual de criterios).

---

## 2026-06-04 — 🔐 A-SEC-2 · Tenant isolation / IDOR (dominios de pagos y datos)

**Sprint:** auditoría IDOR + fixes en pedidos, checkout, wompi, cupones, crm, carritos, reseñas, analytics, catálogo, negocio, página, qr. Suite **697/0**.

### 🔎 Hallazgos (qué estaba vulnerable)
- **pedidos_api (18/18 endpoints):** sin `@login_required` ni validación de propiedad. Cualquiera con un `pedido_id` (enumerable) podía ver/editar/cancelar pedidos ajenos, **marcarlos como pagados**, registrar guías, crear devoluciones. Identidad vía `X-User-ID` (header forjable).
- **crm_api (4/4):** exposición de PII (nombre, teléfono, correo, historial de compras) de cualquier negocio sin auth.
- **catalogo_api (TODO el módulo):** `get_authorized_user_id()` **priorizaba el header `X-User-ID` sobre la sesión** → suplantación total: con cualquier sesión, `X-User-ID: <víctima>` daba acceso a sus productos/inventario.
- **cupones / carritos / reseñas / analytics:** endpoints de panel (`/negocio/<id>/...`) sin validar dueño → editar cupones, moderar/eliminar reseñas, ver carritos/analytics de otros.
- **wompi config (GET/PUT):** leer/editar llaves Wompi de cualquier negocio sin auth.
- **wompi webhook (crítico):** la firma solo se validaba *si* había `events_key` y header → **sin esos, marcaba el pedido como pagado igual**. Sin validación de monto (replay/parcial).

### ✅ Corregido
- **Helper central** `api/utils/seguridad.py`: `usuario_sesion_id()` (solo sesión), `negocio_es_de_usuario`, `pedido_es_de_usuario`, y `crear_guard_tenant()` → un **`before_request` por blueprint** que exige sesión y valida propiedad de `negocio_id`/`pedido_id`, con **allowlist explícita de rutas públicas**.
- Guards cableados en **pedidos, wompi, cupones, crm, carritos, reseñas, analytics** → IDOR cerrado en bloque (usuario A → recurso de negocio B = **403**; sin sesión = **401**).
- **catalogo:** `get_authorized_user_id()` ahora **solo usa la sesión** (header ignorado). `pedidos.get_user_id()` sin fallback a header.
- **pedidos:** búsqueda por teléfono exige dueño (la pública magic-link es solo por `?codigo=`); `recibir_devolucion` valida usuario→negocio→devolución.
- **wompi webhook:** firma **obligatoria** (rechaza 401 si no hay `events_key`/checksum), valida **monto == total del pedido** (rechaza 400 si no), e **idempotente** (no re-marca pagado).
- Recursos hijos (cupón/reseña/carrito) ya estaban scopeados por `negocio_id` (verificado).
- **Públicos legítimos marcados** y verificados (solo exponen lo necesario): checkout, magic-link por código, validar cupón, guardar/recuperar carrito, reseña pública (crear/leer), visita/trust, wompi config-pub/session/verify/webhook, micrositio por slug, QR (ya validaban dueño).
- Test `test_seguridad_asec2.py`: **29/29**. Commit: back `5bc73ef`.

### ⏳ Pendiente / notas
- **Verificar en staging** que los paneles del tendero (pedidos, contabilidad, etc.) envían la cookie de sesión (`credentials:'include'`); ahora los endpoints exigen sesión real. Si algún fetch del front mandaba solo `X-User-ID` sin credenciales, hay que añadirle `credentials:'include'`.
- `checkout_api` es público (comprador): validar que el `negocio_id` exista/activo (mejora menor, no IDOR).
- Considerar transacción/lock atómico en el webhook para TOCTOU extremo (hoy mitigado con idempotencia + monto).

### 👉 Siguiente paso sugerido
Retomar la **Fase 2 del panel con A16** (editor visual de criterios), ya con la base de seguridad sólida.

---

## 2026-06-04 — 🔐 A-SEC-1 · Sprint de seguridad transversal

**Sprint:** auditoría + fixes de seguridad (no feature). Suite **668/0**.

### 🔎 Hallazgos (qué estaba vulnerable)
1. **CSRF:** sesión por cookie `SameSite=None` sin ninguna validación de origen en requests mutantes → un sitio malicioso podía forzar POST/PUT/DELETE con la cookie del usuario.
2. **IDOR (grave):** `gamificacion_api._get_nid()` devolvía el `negocio_id` del parámetro **sin validar propiedad** → cualquier usuario logueado operaba sobre la gamificación de otro negocio con `?negocio_id=`. Afectaba TODOS los endpoints de gamificación (prestigio, misiones, onboarding, etc.).
3. **XSS (stored):** la tienda pública (`tienda.js`) inyectaba `nombre`/`categoría`/`alt` de productos y testimonios **sin escapar** en `innerHTML` → un tendero podía poner `<img onerror=...>` en el nombre de un producto y ejecutar script en el navegador de cada comprador. El CRUD de insignias no validaba color/ícono.
4. **Fuerza bruta:** el contador de intentos de login estaba en la **cookie de sesión** → el atacante la ignora y nunca se bloquea (ineficaz). Sin límite en password-reset.
5. **Bug latente:** `admin_api.ALLOWED_ORIGINS` no incluía `tukomercio.co` (CORS del admin habría fallado en producción).

### ✅ Corregido
1. **CSRF:** guardia global `before_request` en `create_app` que valida `Origin` (con fallback a `Referer`) contra `Config.CORS_ORIGINS` en todo método mutante; exime webhook de Wompi y health. → request con Origin ajeno = **403**.
2. **IDOR:** `_get_nid` ahora exige `_negocio_es_mio()` (propiedad del negocio); cross-tenant → None → 404. Cierra todos los endpoints de gamificación de una vez.
3. **XSS:** `tienda.js` escapa producto (nombre/categoría/alt) y testimonios (nombre/texto). Backend: `validar_badge` exige color hex/rgba e ícono seguros (helpers `color_hex_valido`/`icono_valido`/`texto_limpio` en `api/utils/seguridad.py`).
4. **Fuerza bruta:** rate limit **server-side por IP+email** (tabla `intentos_login`, `evaluar_bloqueo` puro) en login y password-reset; bloqueo 5 fallos / 15 min con backoff; lockout **auditado en `admin_audit_log` con IP**.
5. Whitelist de admin alineada con `tukomercio.co`/`www`.
- Test `test_seguridad_asec1.py`: **35/35**. Commits: back `886253e`, front `0ff412d`.

### ⏳ Pendiente / notas
- IDOR: queda **auditar el resto de dominios** que reciben `negocio_id` en ruta (pedidos, catálogo, wompi, cupones, crm, carritos) — varios ya validan por ruta/login pero conviene una pasada dedicada (A-SEC-2).
- Rate limit: store en BD es cross-worker; si se migra a Redis, mejor aún.
- Recomendado: probar manualmente el flujo de login/bloqueo en staging tras el deploy.

### 👉 Siguiente paso sugerido
Continuar la Fase 2 con **A16 — Editor visual de criterios** (lo pausamos por el sprint de seguridad), o hacer **A-SEC-2** (auditoría IDOR del resto de dominios).

---

## 2026-06-04 — Panel admin A15 · arranca FASE 2 (Insignias)

**Sprint actual:** Panel de Administración, Fase 2 (Insignias). Avance **15/49**.

### ✅ Completado
- **A15 — CRUD de insignias:** catálogo (`negocio_badges`) editable desde el panel.
  - **Bug resuelto:** el seeder corría con `actualizar_visual=True` y pisaba los badges en cada arranque → nueva columna `editado_admin`; el seeder ahora respeta lo editado por el admin (migración `ADD COLUMN IF NOT EXISTS`).
  - `validar_badge()` puro + endpoints GET/POST/PUT (editar marca `editado_admin`) y DELETE (`@superadmin_required`, solo si `total_otorgados==0`). Nueva sección "Insignias" en el sidebar con tabla + modal crear/editar.
  - `test_admin_insignias_a15.py` 27/27 → **suite 633/0**. Commits: back `3cf2960`, front `d78e69b`.

### ⏳ Pendiente
- Fase 2: A16 (editor visual de criterios + preview de cuántos cumplirían), A17 (otorgar/revocar manual), A18 (validador CURVA_DIFICULTAD), A19 (insignias por temporada), A20 (vista de progreso/otorgamientos), A21 (preview en vivo del diseño).
- F3 (auditoría recibo) y F5 (ícono PWA) en backlog.

### 🐞 Problemas encontrados / decisiones
- Sin la columna `editado_admin`, cualquier edición de badge se revertiría al reiniciar Render. Esa fue la pieza clave para que A15 sea real ("sin programador").
- El código del badge se bloquea en el modal al editar (es la clave única / criterio del catálogo).

### 👉 Siguiente paso sugerido
**A16 — Editor visual de criterios** (elegir `criterio_tipo` de la lista de métricas disponibles + preview "cuántos negocios cumplirían").

---

## 2026-06-04 — Panel admin A12 · 🎉 FASE 1 COMPLETA

**Sprint actual:** Panel de Administración. **Fase 1 (Gamificación/Economía) COMPLETA (A6-A14).** Avance **14/49**.

### ✅ Completado
- **A12 — Parámetros de sugerencias/comparativas:** `SUGERENCIAS_DEFAULT` + config en `gamif_config` (umbral_casi, umbral_avance, racha_minima, max_sugerencias, badges_considerar, destacado_top_pct). `generar_sugerencias()` toma `cfg` (compat con `limite`, S35 verde); `comparativas` añade flag `destacado`. Endpoints `GET/PUT /api/admin/gamificacion/sugerencias-config` (auditado) + card en el panel. `test_admin_sugerencias_a12.py` 19/19 → **suite 606/0**. Commits: back `8638e20`, front `56df74d`.
- **🎉 Cierre de la Fase 1:** el admin ya controla SIN código toda la economía/gamificación → XP por evento (A6), misiones (A7), tienda de TuKoins (A8), economía+bono (A9), ficha por negocio (A10), rachas (A11), sugerencias/comparativas (A12), simulador (A13) y recálculo masivo (A14).

### ⏳ Pendiente
- **Fase 2 — Control de Insignias (A15-A21):** CRUD de badges, editor de criterios, otorgar/revocar, etc.
- F3 (auditoría recibo) y F5 (ícono PWA) en backlog.

### 🐞 Problemas encontrados / decisiones
- `generar_sugerencias` mantuvo el parámetro `limite` para no romper el test S35; `cfg` es opcional con fallback a `SUGERENCIAS_DEFAULT`.

### 👉 Siguiente paso sugerido
Abrir la **Fase 2 con A15 — CRUD de insignias** (mover `BADGES_INICIALES` a edición desde el panel, con el patrón ya probado).

---

## 2026-06-04 — Panel admin A14 (recálculo masivo)

**Sprint actual:** Panel de Administración, Fase 1. Avance **13/49** (Fase 1: 8/9; falta A12).

### ✅ Completado
- **A14 — Recálculo masivo (niveles/insignias)** con las 2 condiciones exigidas:
  1. **Dry-run obligatorio:** `POST /gamificacion/recalcular/preview` muestra cuántos negocios cambiarían + muestra, sin escribir; el botón "Aplicar" en el panel queda **deshabilitado** hasta ejecutar la vista previa (y solo si hay cambios). `BadgeVerificationService.simular_badges()` = dry-run de insignias.
  2. **Aplicar = superadmin + auditado:** `POST /gamificacion/recalcular/aplicar` con `@superadmin_required`, exige `confirmar=true`, y **audita con el conteo de registros modificados**.
  - Tope `RECALC_CAP=2000` reportado (sin cap silencioso). `test_admin_recalculo_a14.py` 16/16 → **suite 587/0**. Commits: back `7776bbc`, front `819aba3`.

### ⏳ Pendiente
- **A12 — Parámetros de sugerencias/comparativas** (único que falta para cerrar la Fase 1).
- Fase 2 (Insignias, A15-A21) en adelante.
- F3 (auditoría recibo) y F5 (ícono PWA) en backlog.

### 🐞 Problemas encontrados / decisiones
- El servicio de insignias no tenía dry-run; se añadió `simular_badges()` (evalúa criterios sin `_asignar_badge` ni commit) para poder mostrar la vista previa sin efectos.
- Corrección de seguimiento: marqué la Fase 1 como completa por error; **A12 sigue pendiente** → Fase 1 = 8/9.

### 👉 Siguiente paso sugerido
Cerrar la Fase 1 con **A12 — Parámetros de sugerencias/comparativas**, y luego abrir la **Fase 2 (Insignias)**.

---

## 2026-06-04 — Panel admin A13 (simulador)

**Sprint actual:** Panel de Administración, Fase 1 (Gamificación/Economía). Avance **12/49**.

### ✅ Completado
- **A13 — Simulador / modo prueba:** helpers puros `nivel_por_xp` + `simular_evento` (replican la lógica del motor sin tocar BD) + `POST /api/admin/gamificacion/simular` (dry-run, sin commit; parte del XP real de un negocio o un XP inicial; resuelve evento especial, bono y misiones efectivas). Card "🧪 Simulador" en el panel con desglose y subida de nivel. `'simular'` añadido a `ACCIONES_VALIDAS`. `test_admin_simulador_a13.py` 21/21 → **suite 571/0**. Commits: back `6e6e801`, front `a034501`.
- Sirve para **validar en vivo** los cambios de A6 (XP), A9 (bono) y A11 (rachas) antes de que afecten a los negocios.

### ⏳ Pendiente
- Fase 1: A12 (parámetros de sugerencias/comparativas), A14 (recálculo masivo de niveles/insignias) → cierra la Fase 1.
- F3 (auditoría end-to-end del recibo) y F5 (ícono PWA) en backlog.

### 🐞 Problemas encontrados / decisiones
- El simulador NO reutiliza los hooks reales (que hacen commit); replica su lógica en una función pura para garantizar cero efectos secundarios. Test verifica que el endpoint no contiene `commit`.

### 👉 Siguiente paso sugerido
**A14 — Recálculo masivo** (recalcular niveles/insignias de todos tras cambios de criterio; con dry-run y barra de progreso) para cerrar la Fase 1, o A12 (bajo riesgo).

---

## 2026-06-04 — Panel admin A11 + backlog F5

**Sprint actual:** Panel de Administración, Fase 1 (Gamificación/Economía).

### ✅ Completado
- **A11 — Reglas de rachas configurables:** umbral de récord editable (reemplaza `>= 3` hardcodeado en hooks de login-usuario y actividad-negocio) + bono opcional de TuKoins al alcanzar el umbral (default 0 = sin cambio). Endpoints `GET/PUT /api/admin/gamificacion/rachas` (auditado) + card en el panel. `test_admin_rachas_a11.py` 23/23 → **suite 550/0**. Commits: back `45bba30`, front `932917a`.
- **F5 (backlog)** registrado en `fixes_tienda_checkout.md`: ícono PWA estirado ("huevito"); causa probable manifest no cuadrado / falta variante maskable. Prioridad baja, NO trabajar aún.

### ⏳ Pendiente
- Fase 1: A12 (parámetros de sugerencias/comparativas), A13 (simulador), A14 (recálculo masivo).
- F3 (auditoría end-to-end del recibo) y F5 (ícono PWA) en cola.

### 🐞 Problemas encontrados / decisiones
- Bono por récord acotado a otorgarse **solo al alcanzar el umbral exacto** (una vez por racha) para evitar farmeo diario. Default 0 → comportamiento sin cambios y tests previos verdes vía fallback.

### 👉 Siguiente paso sugerido
Continuar con **A12 — Parámetros de sugerencias/comparativas** (bajo riesgo) o A13 (simulador, más visible).

---

## 2026-06-04 — Fixes de tienda/checkout (F1, F2, F4) · de cara al cliente

**Sprint actual:** bugs de producción de `fixes_tienda_checkout.md` (prioridad sobre A11).

### ✅ Completado
- **F1 — Branding multitenant del recibo** (`heyden.html`): color de marca dinámico (`color_tema` → `--brand`/`--brand-dark`), eliminados los 20 usos del rojo de Rodar hardcodeado y los defaults `RODAR`/`rodar`; logo dinámico; saludo personalizado con el nombre **cargado de la API** (no de la URL).
- **F2 — Fuente única de verdad del envío**: el pedido guardado manda. checkout persiste `modo_entrega` + `envio_a_convenir` en `datos_envio`; regla única `etiquetaEnvio()` en recibo/total/WhatsApp; wording "Por confirmar con el vendedor". Elimina el "$10.000 vs a confirmar".
- **F4 — Enlace del recibo**: dominio `tukomercio.co`; **bug del prefijo** `c=-2026-0043` corregido (`Pedido._prefijo_codigo()`, nunca vacío); **ruta limpia** `tukomercio.co/pedido/{tienda}/{codigo}` (`_worker.js` v1.21); **sin nombre del comprador en la URL** (Ley 1581); compatibilidad con enlaces viejos.
- Tests: backend `test_fix_codigo_pedido_f4.py` 20/20 → **suite 527/0**. Lógica de front (color/envío/ruta/PII) verificada con Node (12/12). JS validado (`node --check`).
- Commits: backend `ab6b165`, frontend `0912875`.

### ⏳ Pendiente
- **F3** (auditoría end-to-end del recibo): la consistencia ya está garantizada por F1+F2; falta el test de regresión end-to-end y aplicar `etiquetaEnvio` también en el panel de pedidos del tendero.
- Retomar el roadmap del panel admin en **A11**.

### 🐞 Problemas encontrados / decisiones
- Causa raíz del prefijo vacío: `slug[:3].upper()` con slug `''` → `-2026-0043`. Fix robusto centralizado en el modelo.
- El backend (`checkout_api`) ya usaba `tukomercio.co`; el problema de dominio estaba en el **frontend** (`pedidos.html`, `checkout.js` usaban `tuko.pages.dev`).
- Los flags de envío no persistían vía `DireccionComprador.to_dict_pedido()`; se inyectan directo en `datos_envio` (JSONB) tras crear el pedido.
- Default CSS `--brand` se dejó en el rojo actual para no introducir regresión si el JS falla; el color real del negocio lo sobreescribe.

### 👉 Siguiente paso sugerido
Cerrar **F3** (test end-to-end + regla de envío en panel de pedidos) o retomar **A11**. A definir con Carlos.

---

## 2026-06-04 — Organización de documentación

**Sprint actual:** tarea transversal de documentación (no consume sprint del roadmap A*).

### ✅ Completado
- **README profesional en ambos repos** (antes eran stubs de 24 bytes "# TRAYECTORIA_Python_mvc"):
  - Backend `README.md`: qué es, stack, instalar/correr local, tests, estructura, despliegue Render, enlaces a CLAUDE/BITACORA/API/CHANGELOG.
  - Frontend `README.md`: vanilla JS, Cloudflare Pages, ruteo del `_worker.js`, correr local, validar JS, convenciones.
- **`docs/API.md`** (nuevo): referencia de ~30 endpoints clave por dominio (auth, negocio/catálogo, tiendas/pedidos/pagos, gamificación, admin), generada leyendo los blueprints reales y sus prefijos.
- **`CHANGELOG.md`** (nuevo): inicia en **v2.19.0** con resumen de lo grande ya construido + regla de actualizar en cada versión.
- **`memory/project_tukomercio.md`**: reducido a nota breve que apunta a `CLAUDE.md` como **fuente única de verdad técnica** (evita divergencia).
- `INVENTARIO_DOCS.md` (creado en la tarea previa) sigue vigente.

### ⏳ Pendiente
- Retomar el roadmap del panel admin en **A11** (Fase 1, 5/9).
- Bugs de tienda/checkout **F1–F3** en cola.
- `docs/API.md` es no-exhaustivo: ampliar con parámetros/respuestas cuando haga falta.

### 🐞 Problemas encontrados
- Los README existían pero eran stubs vacíos. El repo frontend tiene su git root en `proyecto_sena/TRAYECTORIA_Python_mvc/` (no en `public/`).
- `requirements.txt` en UTF-16 (afecta cómo se lee, no la instalación).

### 👉 Siguiente paso sugerido
Continuar con **A11 — Reglas de rachas configurables** (mismo patrón `gamif_config`).

---

## 2026-06-03 — Panel de Administración · Fase 1 (Gamificación/Economía)

**Sprint actual:** Roadmap del Panel de Administración (`admin_panel_roadmap.md`). Objetivo global:
poder administrar TODO (sobre todo los 40 sprints de gamificación) **sin tocar código**.
Avance: **10/49** sprints (Fase 0 completa; Fase 1 en 5/9).

### ✅ Completado
- **Fase 0 — Cimientos (A1–A5):**
  - A1: shell modular del panel (ya existía; verificado).
  - A2: **log de auditoría** (`admin_audit_log`, helper `registrar_auditoria`, sección "Auditoría"). 15 tests.
  - A3: **permisos granulares por módulo** (`MODULOS_PERMISOS`, `requiere_permiso`, editor 🔑). 19 tests.
  - A4: **dashboard de KPIs reales** (`/api/admin/metrics`). 9 tests.
  - A5: **buscador global** (usuarios/negocios/admins). 12 tests.
- **Fase 1 — Gamificación/Economía (A6–A10):**
  - A6: **editor de XP por evento** (patrón "constante → BD con fallback", tabla `gamif_config`). 22 tests.
  - A7: **editor de misiones** (editar/activar pools diaria/semanal/mensual). 24 tests.
  - A8: **editor de la tienda de TuKoins** (CRUD de `tienda_items`). 22 tests.
  - A9: **economía de TuKoins** (circulación, top holders, ajuste manual, bono por fecha configurable). 19 tests.
  - A10: **ficha de gamificación por negocio** (ver/corregir XP, nivel, prestigio, rachas, TuKoins; auditado). 19 tests.
- Suite de tests: **507 pasando, 0 fallando**.
- Documentos creados hoy: `CLAUDE.md` y `BITACORA.md` (este).

### ⏳ Pendiente
- **Fase 1 restante:** A11 (reglas de rachas configurables), A12 (parámetros de sugerencias/comparativas), A13 (simulador/modo prueba), A14 (recálculo masivo de niveles/insignias).
- **Fases 2–6** del panel (insignias, eventos/retos/competencia, negocios/usuarios/comunidad, analítica, pagos/legal/IA): 0 iniciadas.
- **Bugs de tienda/checkout (F1–F3)** en cola (`fixes_tienda_checkout.md`):
  - F1: el resumen de pedido (`heyden.html`) no aplica el color de marca (rojo de Rodar hardcodeado) ni siempre el logo.
  - F2: inconsistencia del valor de envío ($10.000 vs "a confirmar con el asesor").
  - F3: auditoría end-to-end del recibo.

### 🐞 Problemas encontrados / decisiones
- La auditoría inicial describió `admin.html` como panel de leads de 1205 líneas: **incorrecto** — el panel real (4413 líneas) ya era modular. No requirió reescritura.
- `requirements.txt` está en **UTF-16** (se ve con espacios al hacer `cat`/`head`).
- En Windows, los tests necesitan `PYTHONUTF8=1` para no romper con emojis; Git avisa LF→CRLF (no es error).
- Decisión anti-bloqueo (A3): no se reemplazaron los decoradores existentes; `requiere_permiso` se adopta solo en endpoints nuevos para no dejar fuera a admins con `permisos` vacíos.
- Compatibilidad (A9): al hacer configurable el bono de TuKoins, `bono_tukoins()` ahora lee `gamif_config` con **fallback**, así los tests previos (S36) siguen verdes sin la tabla.

### 👉 Siguiente paso sugerido
Continuar con **A11 — Reglas de rachas configurables** (umbral de récord y recompensas de racha → `gamif_config`, mismo patrón de A6/A7). Alternativa de alto valor visible: **A13 — Simulador/modo prueba** para validar en vivo todo lo construido en la Fase 1.

---

<!-- Plantilla para nuevas entradas (copiar y rellenar al terminar cada tarea):

## AAAA-MM-DD — <Módulo/Fase> · <Sprint>

**Sprint actual:** <id y nombre>

### ✅ Completado
- ...

### ⏳ Pendiente
- ...

### 🐞 Problemas encontrados
- ...

### 👉 Siguiente paso sugerido
- ...
-->
