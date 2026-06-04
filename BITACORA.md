# BITÁCORA DE SPRINTS — TuKomercio

> Registro cronológico del trabajo. Se actualiza **al terminar cada tarea**.
> Estructura por entrada: Fecha · Sprint actual · Completado · Pendiente · Problemas · Siguiente paso.
> Roadmaps detallados: `memory/admin_panel_roadmap.md`, `memory/gamification_roadmap.md`, `memory/fixes_tienda_checkout.md`.

> 📌 **Nota de alcance:** el "sistema de reportes de error" **ya existe** en el código
> (sección *Reportes* del panel admin + `src/api/feedback_api.py` + tabla de reportes). El **sprint
> en curso real** es el **Panel de Administración** (roadmap A1–A49), que entre otras cosas integra
> y amplía la administración de esos reportes.

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
