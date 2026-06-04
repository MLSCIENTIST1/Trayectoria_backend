# API — Referencia de endpoints principales

> Referencia **no exhaustiva** de los endpoints más importantes, generada leyendo los blueprints reales
> (`src/api/**`). Base del API en producción: `https://trayectoria-backend.onrender.com`.
> Auth por **cookie de sesión** (Flask-Login) → el frontend llama con `credentials: 'include'`.
> Última actualización: 2026-06-04.

Notas de prefijos: el grueso del API cuelga de `/api`; el panel admin de `/api/admin`; auth de `/api/auth`.

---

## 🔐 Auth — `src/api/auth/`
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/login` | Inicia sesión (crea cookie de sesión). |
| POST | `/api/auth/logout` | Cierra sesión. |
| GET | `/api/auth/session/verify` | Verifica si la sesión actual es válida. |
| GET | `/api/auth/user/profile` | Perfil del usuario autenticado. |
| POST | `/api/auth/forgot-password` | Envía email de recuperación (Resend). |
| GET | `/api/auth/verify-reset-token/<token>` | Valida el token de restablecimiento. |
| POST | `/api/auth/reset-password` | Establece nueva contraseña. |

## 🏪 Negocio y catálogo — `src/api/negocio/`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/negocio/slug/<slug>` | Datos públicos del negocio por slug (nombre, `color_tema`, `logo_url`, badges). |
| GET | `/api/productos/publicos/<negocio_id>` | Catálogo público de productos de un negocio. |
| POST | `/api/catalogo/producto/guardar` | Crea/edita un producto del catálogo. |
| PUT/PATCH | `/api/producto/actualizar/<id_producto>` | Actualiza un producto. |
| POST | `/api/producto/<id_producto>/stock` | Ajusta stock (registra movimiento). |
| GET | `/api/inventario/estadisticas` | KPIs de inventario del negocio. |
| GET/POST | `/api/categorias` | Lista / crea categorías de producto. |

## 🛒 Tiendas — checkout, pedidos, pagos — `src/api/tiendas/`
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/tiendas/<slug>/checkout` | Crea un pedido desde la tienda pública. |
| GET | `/api/pedidos/negocio/<negocio_id>` | Lista pedidos de un negocio. |
| GET | `/api/pedidos/<pedido_id>` | Detalle de un pedido. |
| PUT/PATCH | `/api/pedidos/<pedido_id>/estado` | Cambia el estado del pedido. |
| POST | `/api/pedidos/<pedido_id>/cancelar` | Cancela un pedido (con motivo). |
| POST | `/api/pedidos/manual` | Registra una venta/pedido manual. |
| GET | `/api/pedidos/buscar?codigo=` | Busca un pedido por código (lo usa `heyden.html`). |
| POST | `/api/pedidos/<pedido_id>/devolucion` | Registra una devolución. |
| POST/GET | `/api/negocio/<negocio_id>/cupones` | Crea / lista cupones de descuento. |
| POST | `/api/cupones/validar` | Valida un cupón en el carrito. |
| GET | `/api/negocio/<negocio_id>/crm/compradores` | CRM: lista de compradores del negocio. |
| POST/GET | `/api/negocio/<negocio_id>/carrito/guardar` · `/carritos` | Carritos abandonados (guardar / listar). |
| POST/GET | `/api/resenas/<negocio_id>/productos/<producto_id>` | Reseñas de producto (dejar / listar). |
| GET/PUT | `/api/negocio/<negocio_id>/wompi/config` | Config de la pasarela Wompi del negocio. |
| POST | `/api/wompi/webhook` | Webhook de confirmación de pago de Wompi. |

## 🎮 Gamificación — `src/api/gamificacion/`
| Método | Ruta | Descripción |
|---|---|---|
| GET/POST | `/api/gamificacion/dashboard` | Dashboard de gamificación del negocio (nivel, XP, rachas, misiones, TuKoins). |
| POST | `/api/gamificacion/misiones/completar` | Marca una misión como completada. |
| GET | `/api/gamificacion/leaderboard` · `/ligas` | Ranking global / ligas por ciudad y categoría. |
| GET | `/api/gamificacion/reto-mes` | Reto mensual vigente. |
| GET | `/api/gamificacion/tienda` · POST `/tienda/comprar` | Catálogo de ítems TuKoins / canjear. |
| GET | `/api/gamificacion/bono-hoy` · `/evento-activo` | Bono de TuKoins del día / evento especial (XP x). |
| POST | `/api/gamificacion/prestigio` | Prestigiar (reinicia XP por una estrella). |
| POST | `/api/gamificacion/onboarding-completado` | Recompensa al terminar el onboarding. |
| GET | `/api/gamificacion/proximos-badges` · `/sugerencias` | Insignias cercanas / sugerencias. |
| GET | `/api/creador/<usuario_id>` | Perfil público del creador. |
| GET | `/api/widget/badges/<slug>` | Widget embebible de insignias del negocio. |

## 🛠️ Admin (superadmin) — `src/api/admin_api.py` (prefijo `/api/admin`)
Protegido por `@admin_required` / `@superadmin_required` / `@requiere_permiso('<modulo>')`.

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/admin/check` | ¿El usuario actual es admin? (lo usa el navbar). |
| GET | `/api/admin/metrics` | KPIs de plataforma (usuarios, negocios, ventas, XP, TuKoins, insignias…). |
| GET | `/api/admin/search?q=` | Buscador global (usuarios / negocios / admins). |
| GET | `/api/admin/auditoria` | Log de auditoría de acciones admin (filtros + paginación). |
| GET/PUT | `/api/admin/permisos/modulos` · `/<id>/permisos` | Catálogo de módulos / asignar permisos a un admin. |
| GET | `/api/admin/usuarios` · DELETE `/usuarios/<id>` | Listar/buscar usuarios / eliminar. |
| GET/POST | `/api/admin/challenges` (+ `/participaciones`) | CRUD de challenges + moderación. |
| GET/POST | `/api/admin/features` · `/planes` | Feature flags / planes de suscripción. |
| GET/PUT | `/api/admin/gamificacion/config` · `/xp-eventos` | Ver / editar XP por evento (config editable). |
| GET/PUT | `/api/admin/gamificacion/misiones` | Editar / activar misiones. |
| GET/PUT/POST | `/api/admin/gamificacion/tienda` (+ `/<id>`) | CRUD de ítems de la tienda de TuKoins. |
| GET/POST/PUT | `/api/admin/gamificacion/economia` · `/economia/ajuste` · `/bono` | Economía: circulación, ajuste manual, bono por fecha. |
| GET/POST | `/api/admin/gamificacion/negocio/<id>` (+ `/ajuste`) | Ficha de gamificación por negocio (ver/corregir). |

---

> Esta referencia se irá ampliando. Para el detalle de parámetros y respuestas, leer el blueprint
> correspondiente en `src/api/`. Regla del proyecto: **no inventar endpoints** — verificar aquí o en el código.
