# BITÁCORA DE SPRINTS — TuKomercio

> Registro cronológico del trabajo. Se actualiza **al terminar cada tarea**.
> Estructura por entrada: Fecha · Sprint actual · Completado · Pendiente · Problemas · Siguiente paso.
> Roadmaps detallados: `memory/admin_panel_roadmap.md`, `memory/gamification_roadmap.md`, `memory/fixes_tienda_checkout.md`.

> 📌 **Nota de alcance:** el "sistema de reportes de error" **ya existe** en el código
> (sección *Reportes* del panel admin + `src/api/feedback_api.py` + tabla de reportes). El **sprint
> en curso real** es el **Panel de Administración** (roadmap A1–A49), que entre otras cosas integra
> y amplía la administración de esos reportes.

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
