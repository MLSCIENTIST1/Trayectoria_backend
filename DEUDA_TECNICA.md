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
