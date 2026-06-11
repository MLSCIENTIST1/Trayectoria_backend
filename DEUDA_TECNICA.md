# 🧰 Deuda técnica — TuKomercio

> Pendientes técnicos conocidos. Cada entrada: qué falta, por qué, y cómo se conecta.

---

## Pasarela de pago de PLANES (Wompi) — pendiente

**Estado:** el cobro de la mensualidad de plan es **100% manual** (un admin registra el
pago en `pagos_suscripcion` vía `POST /api/admin/negocios/<id>/pagos`). No hay pasarela
automática para suscripciones (Wompi hoy solo cobra productos de la tienda, no planes).

**Qué falta:** integrar la pasarela para cobrar planes (link de pago / checkout de plan +
webhook de confirmación + recurrencia).

**Cómo conectar (sin reescribir nada):** ya existe el **punto de enganche único**
`on_pago_confirmado(negocio_id, es_primer_pago, origen)` en
`src/api/gamificacion/gamificacion_hooks.py`. Hoy lo llama el registro manual del pago
(`origen='manual'`). Cuando se integre Wompi, el **webhook debe llamar a esa misma
función** con `origen='wompi'` y `es_primer_pago` calculado igual (primer pago completado
del negocio). Toda la lógica de referidos (nivel 2) cuelga de ahí → se vuelve automática
sin tocar referidos.

**⚠️ Importante:** la cuenta de Wompi debe ser de **TuKomercio SAS** (la empresa), **no
personal**.

**Relacionado:** Sprint Referidos "Comparte y gana" (CHANGELOG 2.23.0); roadmap v2 #2
(pagos colombianos: Nequi/Daviplata/QR).

---

## Split View — fases diferidas (CHANGELOG 2.24.0)

La Vista Dividida entregó Fase 0 (protección móvil), Fase 1 (motor) y parte de Fase 3/4. Quedan:

**Fase 2 — Split contextual (master-detail):** en vistas de lista (Pedidos, Inventario, CRM), al
seleccionar un ítem abrir un panel de DETALLE al lado (cerrado por defecto, se abre al seleccionar,
colapsable). Modo COMPARAR (2 ítems lado a lado). Requiere integrar en cada módulo de lista un evento que
el shell escuche para abrir el panel de detalle. En móvil debe comportarse como hoy (navegación normal /
bottom-sheet), nunca paneles lado a lado.

**Fase 3 — Barra de actividad en vivo:** dentro del panel "Mi tienda (vista previa)", una barra inferior
expandible con últimas visitas/pedidos (estilo consola de Firebase) + sync suave cross-panel (si el panel A
registra una venta, refrescar el panel B vía evento global ligero; sin websockets nuevos). El panel preview
y su refrescar ya existen; falta la barra de actividad y el bus de eventos.

**Badge "Multitasker" real:** hoy la 1ª vez se da una celebración LOCAL (confetti + toast, idempotente por
localStorage). Falta crear el badge en el catálogo de gamificación y un disparo idempotente (evento/endpoint
con CSRF) para otorgarlo de verdad y que cuente en el perfil. Hook sugerido: primer uso del split.

**Arquitectura lista:** `window.SplitView` ya registra un slot `'asistente'` (panel lateral para futuro chat
IA) — solo el hueco; implementar la IA es trabajo aparte.
