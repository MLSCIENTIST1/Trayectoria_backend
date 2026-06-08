# Changelog — TuKomercio

Todas las versiones notables del proyecto. Formato inspirado en [Keep a Changelog](https://keepachangelog.com/es/).

> **Regla:** actualizar este archivo en **cada versión nueva**. Añadir una entrada `## [vX.Y.Z] — AAAA-MM-DD`
> arriba del todo con secciones *Añadido / Cambiado / Arreglado / Eliminado* según aplique. La versión también
> se refleja en el endpoint `/api/health` del backend.

---

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
