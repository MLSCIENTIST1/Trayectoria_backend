# CLAUDE.md — Contexto del proyecto TuKomercio

> Documento de contexto para asistentes de IA y nuevos desarrolladores.
> Generado a partir del código real del repositorio. Mantener actualizado.

---

## 1. ¿Qué es TuKomercio?

**TuKomercio** (antes "Trayectoria" / "BizFlow Studio") es una **plataforma SaaS de e-commerce multi-tenant** para negocios colombianos (principalmente tenderos/microempresas). Un usuario puede tener uno o varios **negocios**; cada negocio tiene su micrositio/tienda online pública, catálogo, pedidos, contabilidad, y un sistema de **gamificación** completo (XP, niveles, TuKoins, misiones, insignias, ligas, eventos).

- **Estado:** MVP en producción.
- **Dueño / titular de derechos:** Carlos Eduardo Huérfano Bermúdez. El código es **confidencial** (ver cabecera de copyright en los archivos).
- **Mercado:** +500k tiendas de barrio en Colombia, <5% digitalizadas.

---

## 2. Stack tecnológico (verificado en `requirements.txt` y `src/__init__.py`)

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.13 |
| Framework | **Flask 3.1.2** (app factory `create_app()` en `src/__init__.py`) |
| ORM | **Flask-SQLAlchemy 3.1.1** / SQLAlchemy 2.0.45 |
| Migraciones | Flask-Migrate 4.1 (Alembic) + auto-reparaciones en `run.py` |
| DB driver | **psycopg2-binary 2.9.11** |
| Base de datos | **PostgreSQL en Neon** |
| Auth | **Flask-Login 0.6.3** + sesiones server-side (Flask-Session sobre SQLAlchemy). **NO usa JWT.** |
| Sesión/cookies | `bizflow_session`, `SameSite=None`, `Secure=True`, `HttpOnly=True` |
| CORS | flask-cors 6.0.2 (con `supports_credentials=True`) |
| Servidor prod | **gunicorn** (`Procfile`: `web: gunicorn run:run`) |
| Hosting backend | **Render** (`trayectoria-backend.onrender.com`) |
| Hosting frontend | **Cloudflare Pages** (`tuko.pages.dev` → dominio `tukomercio.co`) |
| Imágenes | Cloudinary 1.44 + Firebase Cloud Storage |
| Otros | qrcode[pil], Pillow, Flask-Mail, requests, **Resend** (emails transaccionales) |

`DATABASE_URL` viene por variable de entorno; `src/__init__.py` normaliza `postgres://` → `postgresql://`.

---

## 3. Arquitectura de dos repositorios ⚠️ CRÍTICO

El proyecto vive en **dos repos físicamente separados** (NUNCA mezclar archivos entre ellos):

| Repo | Ruta local | Remoto | Despliegue |
|---|---|---|---|
| **Backend** (este) | `C:\Users\carlo\Desktop\trayectoria 30 dic\` | `MLSCIENTIST1/cloude_first_repositorie_bizflow-backend_render` | Render |
| **Frontend** | `C:\Users\carlo\Desktop\proyecto_sena\TRAYECTORIA_Python_mvc\public\` | `MLSCIENTIST1/cloude_first_repositorie_bizflow-frontend` | Cloudflare Pages |

Ambos repos trabajan en la rama **`main`**. Casi todo cambio funcional toca **ambos** (endpoint en back + UI en front) → se commitea y pushea a `main` en los dos.

---

## 4. Estructura de carpetas (backend)

```
trayectoria 30 dic/
├── run.py                      # Entrypoint. Importa create_app(); al arranque corre
│                               # auto-reparaciones de esquema (ver §6). gunicorn usa run:run
├── Procfile                    # web: gunicorn run:run
├── requirements.txt            # (codificado en UTF-16)
├── migrations/                 # Alembic
├── src/
│   ├── __init__.py             # create_app(), Config, CORS, registro de blueprints (safe_register)
│   ├── api/                    # Endpoints, organizados por dominio
│   │   ├── __init__.py         # register_api(app): registra todos los blueprints
│   │   ├── admin_api.py        # Panel superadmin (admins, challenges, usuarios, stats, auditoría,
│   │   │                       #   permisos, métricas, búsqueda, config de gamificación)
│   │   ├── admin_features_api.py   # Feature flags + planes
│   │   ├── admin/leads_admin_api.py # Leads/campaña + plantillas
│   │   ├── auth/               # auth_system.py (login), password_reset_api.py
│   │   ├── gamificacion/       # gamificacion_api.py + gamificacion_hooks.py (motor de eventos)
│   │   ├── tiendas/            # checkout_api, pedidos_api, wompi_api, cupones_api, crm_api,
│   │   │                       #   carritos_api, resenas_api, analytics_api
│   │   ├── negocio/            # catalogo_api, negocio_completo_api, pagina_api, qr_generator_api
│   │   ├── notifications/      # campanita, SSE, chat, push
│   │   ├── ia/dora_api.py      # Asistente IA "Dora"
│   │   ├── taller/ restaurante/ mecalink/   # verticales
│   │   └── utils/              # badge_verification_service.py, metricas_service.py, etc.
│   ├── models/
│   │   ├── __init__.py         # importa y exporta todos los modelos
│   │   ├── administrador.py    # tabla administradores (roles + permisos JSONB)
│   │   ├── admin_audit.py      # tabla admin_audit_log (auditoría del panel)
│   │   ├── colombia_data/
│   │   │   ├── negocio.py, negocio_perfil_config.py
│   │   │   ├── contabilidad/   # wompi_config.py, etc.
│   │   │   └── ratings/        # gamificación: negocio_gamificacion.py, negocio_badge.py,
│   │   │                       #   config_gamificacion.py (gamif_config), duelo.py, referido.py …
│   │   └── ...
│   └── tests_apis/             # Tests (scripts standalone, ver §7)
```

> El frontend (otro repo) sirve `public/` estático; el panel admin es `public/admin/panel/admin.html`
> (single-page, sidebar modular). El ruteo de dominio lo hace `public/_worker.js` (Cloudflare Worker).

---

## 5. Autenticación y panel de administración

- **Usuarios:** Flask-Login con cookie de sesión (no JWT). El front manda credenciales con `credentials: 'include'` y headers `X-User-ID` / `X-Business-ID`.
- **Admin/superadmin:** tabla `administradores` (`email`, `rol` ∈ {superadmin, admin, moderator}, `permisos` JSONB, `activo`). Decoradores en `admin_api.py`:
  - `@admin_required` — debe ser admin activo.
  - `@superadmin_required` — solo superadmin.
  - `@requiere_permiso('<modulo>')` — admin con ese permiso (superadmin pasa siempre). Catálogo en `MODULOS_PERMISOS`.
- Toda acción mutante del panel se registra con `registrar_auditoria(accion, entidad, entidad_id, detalle)` (tabla `admin_audit_log`), con **conexión propia y commit aislado** (nunca rompe el endpoint).

---

## 6. Convenciones de código (observadas en el repo)

1. **Blueprints por dominio** con `url_prefix` (el grueso bajo `/api/...`, el admin bajo `/api/admin`). Registro centralizado vía `safe_register(...)` en `src/api/__init__.py` (tolerante: si un módulo falla, no tumba la app).
2. **Idioma:** nombres, comentarios y mensajes en **español**; `snake_case` en Python, `camelCase` en JS.
3. **A prueba de fallos en gamificación:** los hooks (`gamificacion_hooks.py`) corren en `try/except` con commit propio y rollback aislado — si la gamificación falla, la operación principal (venta, etc.) **no se ve afectada**.
4. **Patrón "constante → BD con fallback" (`gamif_config`):** valores configurables (XP por evento, misiones, bono de TuKoins…) tienen un DEFAULT en código y un override en la tabla `gamif_config`; helpers puros (`merge_*`, `validar_*`) + getters que leen BD y **caen al DEFAULT si falla**. Permite editar desde el panel sin redeploy.
5. **Auto-reparación de esquema en `run.py`:** al arranque se ejecutan `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` y `CREATE TABLE IF NOT EXISTS` para columnas/tablas nuevas (en vez de depender solo de migraciones). Patrón a seguir al añadir campos.
6. **Seeders idempotentes:** catálogos (badges, ítems de tienda) se siembran al arranque sin duplicar (`seed_badges_catalogo`, `seed_tienda_items`).
7. **DB:** la mayoría del código nuevo usa `db.session` (SQLAlchemy); `admin_api.py` usa además `psycopg2` crudo (`get_db_connection()` + `RealDictCursor`) para consultas puntuales.
8. **CORS:** orígenes en whitelist + `supports_credentials=True`. Al añadir endpoints admin, respetar `build_cors_response()` / preflight existentes.
9. **No inventar endpoints:** verificar siempre en `src/api/` antes de llamar/crear uno.
10. **Cabecera de copyright** en archivos clave (propiedad de Carlos E. Huérfano). No removerla.

### Reglas del frontend (otro repo)
- **Vanilla JS, sin frameworks** (no React/Vue). Modales se muestran con clase `.active`/`.show`.
- **Responsive obligatorio** (320px → tablet → escritorio).
- **Estética premium, no caricaturesca** (referencia Linear/Stripe/Vercel; sin confeti estridente ni sonidos).
- Validar JS con `node --check` antes de commitear.

---

## 7. Tests

- Viven en `src/tests_apis/` como **scripts standalone** (no pytest). Cada uno imprime al final `RESULTADO: N pasaron, M fallaron` y retorna exit code.
- Estrategia: **helpers puros testeables** + SQLite en memoria para lo que toca BD
  (`db._engine_options = {}` para limpiar opts de pool de Postgres; crear solo las tablas necesarias por los modelos con JSONB).
- Ejecutar (Windows, consola UTF-8 para emojis):
  ```
  PYTHONUTF8=1 PYTHONIOENCODING=utf-8 venv/Scripts/python.exe src/tests_apis/test_X.py
  ```
- Suite actual: 500+ tests pasando.

---

## 8. Roadmaps y documentación

- **`TuKomercio_Funcionalidades.md`** (en el escritorio): inventario completo de funcionalidades (v2.19.0, 27 secciones). Actualizar al añadir features.
- Roadmaps de seguimiento (memoria de Claude, `C:\Users\carlo\.claude\projects\C--Users-carlo-Desktop\memory\`):
  - `gamification_roadmap.md` — 40 sprints de gamificación (S1–S40) ✅ completos.
  - `admin_panel_roadmap.md` — 49 sprints del panel de admin (A1–A49), en curso.
  - `fixes_tienda_checkout.md` — bugs de tienda/checkout (F1–F3).
- **`BITACORA.md`** (este repo): bitácora de sprints; se actualiza al terminar cada tarea.

---

## 9. Flujo de trabajo por sprint (estándar del proyecto)

```
rama feature → implementar (back + front) → test (suite verde) →
commit → merge a main → push (ambos repos) → actualizar roadmap + BITACORA.md
```
Mensajes de commit en español, descriptivos. No saltarse hooks ni firmas.
