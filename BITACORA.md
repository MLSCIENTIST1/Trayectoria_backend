# BITÁCORA DE SPRINTS — TuKomercio

> Registro cronológico del trabajo. Se actualiza **al terminar cada tarea**.
> Estructura por entrada: Fecha · Sprint actual · Completado · Pendiente · Problemas · Siguiente paso.
> Roadmaps detallados: `memory/admin_panel_roadmap.md`, `memory/gamification_roadmap.md`, `memory/fixes_tienda_checkout.md`.

> 📌 **Nota de alcance:** el "sistema de reportes de error" **ya existe** en el código
> (sección *Reportes* del panel admin + `src/api/feedback_api.py` + tabla de reportes). El **sprint
> en curso real** es el **Panel de Administración** (roadmap A1–A49), que entre otras cosas integra
> y amplía la administración de esos reportes.

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
