# 🛠️ Manual del Administrador — Panel TuKomercio

> Guía práctica del Panel de Administración (`/admin/panel/admin.html`).
> Objetivo del panel: **administrar toda la plataforma sin tocar código.**
> Última actualización: 2026-06-05 (sprints A1–A39 completados).

---

## 1. Acceso y roles

- El panel se abre en `tukomercio.co/admin/panel/` y exige **sesión de administrador**.
- Roles (tabla `administradores`):
  - **superadmin** — acceso total, incluido lo más sensible (config global, recompensas, purga).
  - **admin** — acceso según sus **permisos por módulo**.
  - **moderator** — pensado para moderación (videos, reportes, ligas/duelos).
- Los permisos se asignan en **Configuración → Administradores**. Un `superadmin` siempre pasa todas las validaciones.

> Toda acción que modifica datos queda registrada en **Auditoría** (quién, qué, cuándo).

---

## 2. Navegación

Menú lateral por grupos. En **móvil** usa el botón ☰ (arriba a la izquierda) para abrir/cerrar el menú.
Cada sección muestra una **línea de ayuda** azul con su propósito.

| Grupo | Secciones |
|---|---|
| General | Dashboard · Analítica |
| Gestión | Challenges · Participaciones · Reportes (errores) |
| Plataforma | Feature Flags · Planes · Negocios |
| Usuarios | Cuentas · Anuncios |
| Gamificación | Gamificación · Insignias · Videos/Feed |
| Configuración | Administradores · Auditoría · Salud del sistema · Config. global |

---

## 3. Tareas frecuentes (paso a paso)

### Cambiar el plan de un negocio
**Negocios** → fila del negocio → botón **cambiar plan** (o **Gestionar suscripción** para activar/extender/cancelar y registrar pagos).

### Diagnosticar a un usuario que reporta un problema
**Negocios** → botón **Modo soporte** 🛟: muestra estado, plan, últimos pedidos/productos, **diagnóstico automático** (sin logo, sin productos, suscripción vencida, etc.) y un link a su tienda pública. *Es de solo lectura.*

### Ver todo de un negocio
**Negocios** → botón **Ficha 360°** 📋: datos, dueño, suscripción, gamificación, pedidos, productos y videos.

### Enviar un aviso a varios usuarios
**Anuncios** → define el segmento (ciudad / plan / nivel), revisa el **contador de destinatarios**, elige una plantilla o escribe el mensaje, y **Enviar**. Llega a la campanita 🔔 de cada usuario.

### Moderar contenido
- **Videos/Feed**: aprobar/rechazar/ocultar/destacar videos; mostrar/ocultar perfiles de creador; controlar los logros del feed de comunidad.
- **Challenges → Participaciones**: aprobar/rechazar videos de challenge.
- **Gamificación → (ligas/duelos)**: vetar negocios de ligas, cancelar duelos abusivos, revisar referidos sospechosos.

### Borrar sin perder datos (papelera)
**Negocios** → **Enviar a papelera** 📦 (baja lógica reversible). En **Papelera** puedes **Restaurar** o **Eliminar definitivamente** (purga, irreversible, solo superadmin).

### Premiar a los mejores
- **Gamificación → Ligas → Recompensas**: simula (dry-run obligatorio) y luego ejecuta el premio al top-N del mes anterior (idempotente).
- **Challenges**: botón 🏆 **Finalizar y premiar** otorga XP/TuKoins al ganador.

### Lanzar una función gradualmente
**Feature Flags** → ajusta el **rollout %** (p. ej. 10% de negocios) y guarda. Para forzar a un negocio puntual, usa **Overrides por negocio** (👥) ON/OFF.

### Cerrar el registro o activar mantenimiento
**Config. global** (solo superadmin) → toggles de **modo mantenimiento** y **registro abierto/cerrado** (este último el backend lo respeta de inmediato). Aquí también se editan los textos legales (términos, privacidad/Habeas Data) y el hero de la landing.

### Exportar datos
**Analítica** → botones **Exportar CSV** (negocios, usuarios, TuKoins, crecimiento). El CSV abre directo en Excel/Sheets (con acentos correctos).

### Revisar la salud de la plataforma
**Salud del sistema** → semáforo general, estado de la BD (latencia), errores recientes y métricas de uso (24h/7d).

---

## 4. Configurar la gamificación (sin código)

En **Gamificación** todo es editable y se aplica sin redeploy (patrón "constante → BD con fallback"):
XP por evento, misiones, economía/tienda de TuKoins, rachas, **eventos especiales (XP×)**, **retos mensuales** (con programación por mes), **sugerencias**, simulador y recálculo masivo.
En **Insignias**: crear/editar (con preview en vivo), criterios, otorgar/revocar, coherencia por tier, temporadas y estadísticas.

---

## 5. Notas de seguridad

- Las acciones más sensibles exigen **superadmin** (config global, recompensas de liga, purga de papelera).
- El sistema valida **aislamiento por tenant** (un negocio no ve datos de otro) y **CSRF/headers**.
- Nunca se "suplanta" la sesión de un usuario: el **Modo soporte** es de solo lectura.

---

## 6. ¿Algo no carga?

1. Revisa **Salud del sistema** (¿BD OK?).
2. Si una sección no carga, recarga con Ctrl+F5 (puede ser caché).
3. Errores recurrentes quedan en **Reportes**; los técnicos, en los logs de Render.
4. Cualquier cambio de esquema nuevo se aplica solo al desplegar (auto-migraciones en `create_app`).
