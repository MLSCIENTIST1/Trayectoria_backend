# TuKomercio — Backend

Backend del SaaS de e-commerce **TuKomercio** (antes *Trayectoria / BizFlow Studio*): una plataforma
multi-tenant para que negocios colombianos (tenderos, microempresas) creen su tienda online, gestionen
catálogo/pedidos/contabilidad y participen en un sistema completo de **gamificación**.

> © 2024–2026 Carlos Eduardo Huérfano Bermúdez. Código **confidencial** (ver cabecera de copyright en los archivos).

---

## 🧱 Stack

- **Python 3.13** · **Flask 3.1** (app factory en `src/__init__.py`)
- **Flask-SQLAlchemy / SQLAlchemy 2.0** + **psycopg2** → **PostgreSQL (Neon)**
- **Flask-Login** + sesiones server-side (Flask-Session sobre SQLAlchemy) — **no JWT**
- **flask-cors** (con `supports_credentials`), **Flask-Migrate** (Alembic)
- **gunicorn** en producción (`Procfile: web: gunicorn run:run`)
- Integraciones: **Cloudinary** / **Firebase Storage** (imágenes), **Wompi** (pagos), **Resend** (emails)

El **frontend** es un repo aparte (vanilla JS en Cloudflare Pages). Ver la sección de arquitectura en [`CLAUDE.md`](CLAUDE.md).

---

## 🚀 Instalar y correr localmente

```bash
# 1. Clonar y entrar
git clone <repo-backend> && cd "trayectoria 30 dic"

# 2. Entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Dependencias
pip install -r requirements.txt   # nota: el archivo está en UTF-16

# 4. Variables de entorno (mínimo)
#    DATABASE_URL = postgresql://...   (Neon)
#    + claves de Cloudinary / Firebase / Wompi / Resend para funcionalidad completa
#    Se pueden poner en un archivo .env

# 5. Arrancar (desarrollo)
python run.py                 # levanta Flask en 0.0.0.0:<PORT> (debug)
```

Al arrancar, `run.py` ejecuta **auto-reparaciones de esquema** (`CREATE TABLE / ADD COLUMN IF NOT EXISTS`)
y **seeders idempotentes** (catálogo de insignias, ítems de tienda). No requiere paso manual de migración para esos cambios.

### Tests
Scripts standalone en `src/tests_apis/` (no pytest). Cada uno imprime `RESULTADO: N pasaron, M fallaron`:
```bash
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 venv/Scripts/python.exe src/tests_apis/test_X.py
```

---

## 📂 Estructura (resumen)

```
src/
├── __init__.py        # create_app(), Config, CORS, registro de blueprints (safe_register)
├── api/               # Endpoints por dominio: auth, tiendas, negocio, gamificacion, admin, ia, ...
├── models/            # Modelos SQLAlchemy (negocio, gamificación, administrador, auditoría, ...)
└── tests_apis/        # Tests
run.py                 # Entrypoint + auto-migraciones de arranque
```

Referencia de endpoints: [`docs/API.md`](docs/API.md).

---

## ☁️ Despliegue

- **Backend → Render.** Render ejecuta el `Procfile` (`gunicorn run:run`). `DATABASE_URL` y demás secretos se configuran como variables de entorno del servicio. Push a `main` despliega.
- **Frontend → Cloudflare Pages** (repo aparte): publica `public/`; el ruteo de dominio lo hace `public/_worker.js`. Dominio: `tukomercio.co` (`tuko.pages.dev`).

---

## 📚 Documentación del proyecto

| Documento | Contenido |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | **Fuente única de verdad técnica**: qué es, stack, arquitectura de 2 repos, convenciones, auth. |
| [`BITACORA.md`](BITACORA.md) | Bitácora de sprints (se actualiza al terminar cada tarea). |
| [`docs/API.md`](docs/API.md) | Referencia de los endpoints principales por dominio. |
| [`CHANGELOG.md`](CHANGELOG.md) | Historial de versiones. |
| [`INVENTARIO_DOCS.md`](INVENTARIO_DOCS.md) | Inventario de toda la documentación (memoria + plan SENA). |

---

## 🤝 Flujo de trabajo

`rama feature → implementar (back + front) → tests verdes → commit → merge a main → push (ambos repos) → actualizar roadmap + BITACORA.md`.
Mensajes de commit en español. Consultar `CLAUDE.md` antes de cambios importantes.
