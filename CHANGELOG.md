# Changelog — TuKomercio

Todas las versiones notables del proyecto. Formato inspirado en [Keep a Changelog](https://keepachangelog.com/es/).

> **Regla:** actualizar este archivo en **cada versión nueva**. Añadir una entrada `## [vX.Y.Z] — AAAA-MM-DD`
> arriba del todo con secciones *Añadido / Cambiado / Arreglado / Eliminado* según aplique. La versión también
> se refleja en el endpoint `/api/health` del backend.

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
