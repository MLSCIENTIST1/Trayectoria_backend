import os
import json
import requests
from flask import Blueprint, jsonify, request
from flask_login import current_user

dora_bp = Blueprint('dora', __name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

def get_groq_key():
    return os.environ.get("GROQ_API_KEY", "")


# ── Auth flexible: header X-User-ID (móvil) o sesión Flask (PC) ──────────────
def get_request_user_id():
    """
    Retorna usuario_id como int, o None si no hay sesión válida.
    Prioridad: header X-User-ID → sesión Flask-Login.
    """
    uid = request.headers.get('X-User-ID', '').strip()
    if uid and uid not in ('0', ''):
        try:
            return int(uid)
        except (ValueError, TypeError):
            pass
    # Fallback: cookie de sesión Flask (funciona en PC)
    try:
        if current_user and current_user.is_authenticated:
            return int(current_user.id_usuario)
    except Exception:
        pass
    return None


def require_dora_auth():
    """Devuelve respuesta 401 si no hay ningún método de autenticación válido."""
    if get_request_user_id() is None:
        return jsonify({"error": "No autorizado. Inicia sesión."}), 401
    return None


def _resolve_negocio_id(negocio_id_param):
    """Obtiene negocio_id del parámetro o del primer negocio del usuario autenticado."""
    if negocio_id_param:
        return int(negocio_id_param)
    try:
        user_id = get_request_user_id()
        if not user_id:
            return None
        from src.models.colombia_data.negocio import Negocio
        negocio = Negocio.query.filter_by(usuario_id=user_id).first()
        return negocio.id_negocio if negocio else None
    except Exception:
        return None


def get_negocio_context(negocio_id):
    """Consulta la BD y devuelve contexto real del negocio para inyectar en el prompt."""
    nid = _resolve_negocio_id(negocio_id)
    if not nid:
        return ""
    try:
        from src.models.colombia_data.contabilidad.operaciones_y_catalogo import (
            ProductoCatalogo, TransaccionOperativa, AlertaOperativa
        )
        from datetime import datetime, timedelta

        productos = (
            ProductoCatalogo.query
            .filter_by(negocio_id=nid, activo=True)
            .order_by(ProductoCatalogo.total_ventas.desc())
            .limit(15)
            .all()
        )
        productos_list = [
            f"- {p.nombre} | precio: ${float(p.precio):,.0f} | stock: {p.stock} | cat: {p.categoria}"
            for p in productos
        ]

        hace_30_dias = datetime.utcnow() - timedelta(days=30)
        transacciones = (
            TransaccionOperativa.query
            .filter(
                TransaccionOperativa.negocio_id == nid,
                TransaccionOperativa.fecha >= hace_30_dias
            )
            .order_by(TransaccionOperativa.fecha.desc())
            .limit(10)
            .all()
        )
        trans_list = [
            f"- {t.tipo} | {t.concepto} | ${float(t.monto):,.0f} | {t.fecha.strftime('%d/%m/%Y %H:%M') if t.fecha else '-'}"
            for t in transacciones
        ]

        alertas = (
            AlertaOperativa.query
            .filter_by(negocio_id=nid, completada=False)
            .limit(5)
            .all()
        )
        alertas_list = [f"- [{a.prioridad}] {a.tarea}" for a in alertas]

        partes = []
        if productos_list:
            partes.append("CATÁLOGO DE PRODUCTOS (activos, ordenados por ventas):\n" + "\n".join(productos_list))
        if trans_list:
            partes.append("ÚLTIMAS TRANSACCIONES (30 días):\n" + "\n".join(trans_list))
        if alertas_list:
            partes.append("ALERTAS ACTIVAS:\n" + "\n".join(alertas_list))

        return "\n\n".join(partes)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ""


def build_system_prompt(negocio_nombre=None, negocio_tipo=None, user_nombre=None, negocio_context=""):
    nombre_tienda = negocio_nombre or "tu tienda"
    tipo = negocio_tipo or "tienda"
    nombre_usuario = user_nombre or "tendero"

    context_block = f"\n\nDATA REAL DE {nombre_tienda.upper()}:\n{negocio_context}" if negocio_context else ""

    return f"""Eres Dora IA, asistente inteligente de TuKomercio — plataforma de e-commerce y gestión para tenderos y emprendedores colombianos.
Tu misión es ayudar a {nombre_usuario}, dueño de "{nombre_tienda}" ({tipo}), a crecer su negocio.{context_block}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GUÍA COMPLETA DE TuKomercio — úsala SIEMPRE que pregunten cómo hacer algo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NAVEGACIÓN (menú lateral izquierdo):
• PRINCIPAL: Mi Trayectoria · Buscar para mi negocio · Feed Tukeros · Challenge
• MI NEGOCIO: Mis Negocios · Mis Sucursales · Catálogo · Centro Financiero
• OPERACIONES: Bancos y Pagos · Servicios · Publicar
• HERRAMIENTAS: Mi Página Web · Mi Portafolio
• Búsqueda rápida: Ctrl+K o la lupa en el encabezado

──────────────────────────────────────────
MÓDULO: DISEÑADOR DE TIENDA ("Mi Página Web")
──────────────────────────────────────────
Dónde: Menú → HERRAMIENTAS → "Mi Página Web"
Para qué: personalizar el aspecto visual de tu tienda pública.

LOGO:
• Se sube en la sección "Logo de la Tienda" del diseñador
• Soporta PNG, JPG y GIF animado (máx 2 MB)
• Con el slider ajustas el tamaño del logo (32 px a 80 px)
• Puedes mostrar u ocultar el nombre del negocio junto al logo con un checkbox
• TIP: si tienes un logo en GIF animado, súbelo igual — la tienda lo muestra en movimiento

BANNER SUPERIOR:
• Activa/desactiva el banner con un toggle
• Puedes cargar hasta 3 imágenes para el slider del banner (GIF soportado)

COLORES Y TIPOGRAFÍA:
• Elige el color principal de la tienda, color de texto y color de fondo
• Selecciona la fuente (tipografía) entre varias opciones

TARJETA DE PRODUCTO (cómo se ve cada producto en la tienda):
• Puedes activar o desactivar badges (etiquetas) que aparecen en las fotos de producto:
  - 🏷️ Descuento, 🆕 Nuevo, ⚠️ Última unidad, ❌ Agotado, ⭐ Top Rated, 🔥 Popular,
  - ✨ Destacado, 🚚 Envío gratis, 📦 Pre-orden, 💎 Edición limitada, ⚡ Flash Sale,
  - 🎁 Combo, 🛡️ Garantía, 🌿 Eco-friendly
• Puedes mostrar precio original tachado, ahorro en pesos, porcentaje de descuento
• Puedes mostrar estrellas de rating, conteo de reseñas, stock disponible
• Los badges manuales (por ejemplo "Nuevo" en un producto específico) se asignan desde Inventario PRO

ACTIVAR TIENDA PÚBLICA:
• Botón "Publicar tienda" → la tienda queda en: tuko.pages.dev/tienda/?slug=tu-negocio

──────────────────────────────────────────
MÓDULO: INVENTARIO PRO
──────────────────────────────────────────
Dónde: Menú → MI NEGOCIO → "Catálogo" → sección Inventario PRO
Para qué: gestionar todos los productos de tu tienda.

AGREGAR PRODUCTO PROPIO:
1. Botón "➕ Nuevo Producto"
2. Llena: Nombre, Descripción, SKU (código interno), Código de barras (EAN/UPC)
3. Categoría, Costo de compra, Precio de venta, Stock inicial
4. Sube la foto del producto
5. Guarda → el producto aparece automáticamente en tu tienda pública

DROPSHIPPING (productos de proveedores):
• En la tarjeta de cada producto hay un toggle "Dropshipping"
• Al activarlo, el producto se marca como de dropshipping (color ámbar)
• Significa que lo despacha el proveedor, no tú directamente
• Los productos de dropshipping también aparecen en tu tienda pública normalmente

DORA ESCANEA TU INVENTARIO:
• Botón "🔍 Escanear productos" → Dora analiza hasta 60 productos y detecta los que pueden estar en la categoría equivocada
• Dora sugiere la categoría correcta y puedes aceptar el cambio con un clic

──────────────────────────────────────────
MÓDULO: DROPSHIPPING (importar catálogo de proveedores)
──────────────────────────────────────────
Dónde: Menú → MI NEGOCIO → "Catálogo" → pestaña Dropshipping
Para qué: agregar masivamente productos de proveedores a tu catálogo.

POR CSV (sin integración API):
1. Selecciona el proveedor en la lista
2. Define tu margen de ganancia (%)
3. Sube el archivo CSV que te dio el proveedor
4. Clic en "Importar" → los productos se cargan a tu inventario con el margen aplicado

POR API (proveedores con integración directa):
1. Selecciona el proveedor
2. Ingresa tu API Key del proveedor
3. Clic en "Sincronizar" → trae el catálogo completo actualizado
• Nota: si no tienes API Key, usa la importación por CSV

──────────────────────────────────────────
MÓDULO: PUNTO DE VENTA (Ventas presenciales)
──────────────────────────────────────────
Dónde: Menú → MI NEGOCIO → "Centro Financiero" → pestaña "Ventas"
Para qué: registrar ventas físicas en el local (cobro en caja).

CÓMO HACER UNA VENTA:
1. Busca el producto por nombre o categoría en el panel izquierdo
2. Haz clic en el producto para agregarlo al carrito (panel derecho)
3. Ajusta la cantidad con los botones + y −
4. Registra el nombre del cliente (opcional)
5. Selecciona método de pago: efectivo, transferencia, etc.
6. Botón "Confirmar venta" → queda registrada en contabilidad y descuenta el stock
• En celular: el carrito se abre con el botón flotante inferior

──────────────────────────────────────────
MÓDULO: PEDIDOS ONLINE
──────────────────────────────────────────
Dónde: Menú → MI NEGOCIO → "Centro Financiero" → pestaña "Pedidos"
Para qué: gestionar los pedidos que llegan desde tu tienda web.

ESTADOS DEL PEDIDO (stepper visual en cada tarjeta):
• Pendiente → Confirmado → Preparando → Enviado → Entregado
• Haz clic en el siguiente paso del stepper para avanzar el estado
• Si avanzaste por error, puedes hacer clic en un paso anterior — te pide confirmación antes de retroceder

GUÍA DE ENVÍO:
• En el detalle del pedido puedes ingresar número de guía y transportadora
• Cuando el estado es "Enviado", el cliente puede rastrear el pedido en: tuko.pages.dev/heyden.html

NOTIFICACIONES WHATSAPP AL CLIENTE:
• Cada tarjeta de pedido tiene botones de WhatsApp según el estado:
  - ✅ Confirmado → "Tu pedido fue confirmado, lo estaremos alistando..."
  - 📦 Preparando → "Estamos alistando tu pedido..."
  - 🚚 Enviado → "Tu pedido va en camino, tu guía es: [número]"
  - 🏢 En oficina → "Tu pedido está en la oficina de [transportadora], pasa a recogerlo"
  - ↩️ Devuelto → "Tu pedido fue devuelto, ¿deseas que lo reenviemos?"
• El botón genera un enlace wa.me con el mensaje pre-llenado — solo haces clic

PROSPECTOS (clientes que dicen "llámame después"):
• Pestaña "Prospectos" en el módulo de Pedidos
• Agrega un cliente con: nombre, teléfono, producto de interés y fecha de recordatorio
• El sistema te alerta cuando se vence la fecha (tarjeta roja = vencido, amarilla = hoy, azul = futuro)
• Banner rojo sticky aparece automáticamente cuando tienes prospectos vencidos
• Botón WA directo para enviarle mensaje al prospecto
• NO afecta la contabilidad — es solo un recordatorio personal

──────────────────────────────────────────
VISTA: CONFIRMACIÓN DE PEDIDO (página del cliente)
──────────────────────────────────────────
Qué es: página pública que se envía al cliente por WhatsApp con el resumen de su pedido.
URL: tuko.pages.dev/heyden.html?c=[código-pedido]&s=[slug-negocio]
El enlace se genera automáticamente al confirmar un pedido en el módulo de Pedidos.

Qué ve el cliente en esa página:
• Logo y nombre del negocio con badge del estado actual (Enviado, Confirmado, etc.)
• Número de pedido, fecha
• Datos del destinatario: nombre, teléfono, cédula
• Dirección de entrega con botón "Ver en Mapa"
• Detalle del producto comprado y precio
• Método de pago (efectivo, transferencia, etc.)
• Transportadora y número de guía
• Nombre y teléfono del asesor
• Total a pagar
• Botón "Ver más productos en nuestra tienda" → va a la tienda online del negocio
• Si tiene guía: sección de rastreo con enlace directo a Interrapidísimo o Coordinadora
• Productos sugeridos de la misma tienda (cross-sell automático)
• Sección inferior con anuncios de TuKomercio, MecaLink y Soluciones Digitales

Cómo comparte el vendedor este enlace:
→ En el módulo de Pedidos, botón "🚚 Enviado con guía" → genera el wa.me con el enlace incluido
→ El cliente solo hace clic en el link y ve toda la info de su pedido

──────────────────────────────────────────
MÓDULO: GASTOS
──────────────────────────────────────────
Dónde: Centro Financiero → pestaña "Gastos"
Para qué: registrar todos los gastos del negocio.
• Registra: concepto, monto, fecha, categoría (Inventario, Arriendo, Servicios Públicos, etc.)
• Dora puede ayudarte a clasificar un gasto — usa el botón "Clasificar gasto" en mi barra de herramientas

──────────────────────────────────────────
MÓDULO: REPORTES FINANCIEROS
──────────────────────────────────────────
Dónde: Centro Financiero → pestaña "Reportes"
Para qué: ver el resumen de ingresos, gastos y rentabilidad.
• Filtra por fechas y ve el consolidado del negocio
• Útil para saber cuánto ganaste en el mes

──────────────────────────────────────────
MÓDULO: PERFIL DEL NEGOCIO
──────────────────────────────────────────
Dónde: Menú → MI NEGOCIO → tu negocio → "Ver perfil"
Para qué: página pública del negocio con reseñas, videos y contacto.
• Los clientes pueden ver reseñas y calificaciones
• Puedes subir videos de tus productos
• Botones de contacto: WhatsApp, ver tienda, redes sociales

──────────────────────────────────────────
MÓDULO: GAMIFICACIÓN
──────────────────────────────────────────
Dónde: Menú → "Mi Trayectoria" / Challenge
Para qué: ganar puntos y subir de nivel como tendero en TuKomercio.
• Completa retos y desafíos para ganar insignias
• El ranking te posiciona frente a otros tukeros

──────────────────────────────────────────
LO QUE TuKomercio NO TIENE (para no confundir al usuario)
──────────────────────────────────────────
• NO hay pasarela de pago integrada — los pagos se coordinan directamente con el cliente (efectivo, transferencia, contraentrega)
• NO hay múltiples monedas ni tasas de cambio
• NO hay "temas prediseñados" para elegir — el diseño se personaliza libremente en Mi Página Web
• NO hay botón de tienda en la esquina superior derecha de la app

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REGLAS DE RESPUESTA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Habla en español colombiano, informal pero profesional (tutéalo al usuario)
• Cuando expliques pasos, usa lista numerada y sé específico con nombres de botones/secciones
• Máximo 5 oraciones por respuesta salvo que estés explicando pasos detallados
• Emojis: máximo 2 por respuesta
• Si preguntan cómo hacer algo → usa SOLO los pasos reales de arriba, NUNCA inventes botones
• Si preguntan por productos, ventas o stock → usa la DATA REAL del negocio
• Si no sabes algo con certeza → di "no tengo esa info exacta, revisa en [módulo]"
• Si el usuario parece perdido → sugiere primero la búsqueda con Ctrl+K

MIS HERRAMIENTAS (botones en mi barra inferior):
• ✏️ Describir producto → genera descripción atractiva para un producto
• 🌟 Campaña completa → crea banner + WhatsApp + Instagram + precio promo + consejo táctico
• 📣 Crear aviso → texto para banner, WhatsApp, Instagram o redes sociales
• 💰 Sugerir precio → calcula precio de venta basado en costo y categoría
• 🧾 Clasificar gasto → dice en qué categoría contable va un gasto"""


def call_groq(messages, system_prompt):
    key = get_groq_key()
    if not key:
        return None, "GROQ_API_KEY no configurada en el servidor"

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "max_tokens": 512,
        "temperature": 0.7,
    }
    try:
        resp = requests.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
            timeout=20
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"], None
    except requests.exceptions.Timeout:
        return None, "La IA tardó demasiado. Intenta de nuevo."
    except requests.exceptions.HTTPError as e:
        try:
            detail = resp.json().get('error', {}).get('message', '')
        except Exception:
            detail = ''
        if resp.status_code == 429:
            return None, "Límite de uso alcanzado. Intenta en unos segundos."
        return None, f"Error de Groq {resp.status_code}: {detail}"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, str(e)


@dora_bp.route('/ia/chat', methods=['POST'])
def chat():
    auth_err = require_dora_auth()
    if auth_err: return auth_err

    data = request.get_json() or {}
    messages = data.get('messages', [])
    negocio_nombre = data.get('negocio_nombre')
    negocio_tipo = data.get('negocio_tipo')
    negocio_id = data.get('negocio_id')

    if not messages:
        return jsonify({"error": "No hay mensajes"}), 400

    negocio_context = get_negocio_context(negocio_id)

    # Obtener nombre del usuario (sesión Flask o lookup por header)
    user_nombre = None
    try:
        if current_user and current_user.is_authenticated:
            user_nombre = getattr(current_user, 'nombre', None)
        else:
            uid = get_request_user_id()
            if uid:
                from src.models.colombia_data.usuario import Usuario
                u = Usuario.query.get(uid)
                user_nombre = u.nombre if u else None
    except Exception:
        pass

    system_prompt = build_system_prompt(
        negocio_nombre=negocio_nombre,
        negocio_tipo=negocio_tipo,
        user_nombre=user_nombre,
        negocio_context=negocio_context
    )

    reply, error = call_groq(messages, system_prompt)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"reply": reply})


@dora_bp.route('/ia/describir-producto', methods=['POST'])
def describir_producto():
    auth_err = require_dora_auth()
    if auth_err: return auth_err
    data = request.get_json() or {}
    nombre = data.get('nombre', '')
    precio = data.get('precio', '')
    categoria = data.get('categoria', '')
    detalles = data.get('detalles', '')

    if not nombre:
        return jsonify({"error": "Nombre del producto requerido"}), 400

    prompt = f"Escribe una descripción de producto atractiva y concisa (máximo 80 palabras) para una tienda colombiana. Producto: {nombre}. Precio: {precio}. Categoría: {categoria}. Detalles adicionales: {detalles}. La descripción debe ser en español, persuasiva, y enfocada en el beneficio para el cliente."

    system = "Eres un experto en marketing para tiendas colombianas. Generas descripciones de productos cortas, persuasivas y en español colombiano. Devuelve SOLO el texto de la descripción, sin comillas ni encabezados."

    reply, error = call_groq([{"role": "user", "content": prompt}], system)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"descripcion": reply})


@dora_bp.route('/ia/generar-promo', methods=['POST'])
def generar_promo():
    auth_err = require_dora_auth()
    if auth_err: return auth_err
    data = request.get_json() or {}
    contexto = data.get('contexto', '')
    tipo = data.get('tipo', 'banner')

    if not contexto:
        return jsonify({"error": "Contexto requerido"}), 400

    prompt = f"Genera un texto corto y llamativo para {tipo} de una tienda colombiana. Contexto: {contexto}. El texto debe ser en español, máximo 15 palabras, impactante y con un call-to-action claro. Devuelve SOLO el texto del aviso."

    system = "Eres un experto en publicidad para tiendas colombianas. Creas textos de avisos y banners cortos, impactantes y en español. Solo devuelves el texto del aviso, sin explicaciones."

    reply, error = call_groq([{"role": "user", "content": prompt}], system)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"texto": reply})


@dora_bp.route('/ia/clasificar-gasto', methods=['POST'])
def clasificar_gasto():
    auth_err = require_dora_auth()
    if auth_err: return auth_err
    data = request.get_json() or {}
    descripcion = data.get('descripcion', '')

    if not descripcion:
        return jsonify({"error": "Descripción del gasto requerida"}), 400

    prompt = f"""Clasifica este gasto de negocio en una sola categoría contable colombiana.
Gasto: "{descripcion}"
Categorías posibles: Inventario/Mercancía, Servicios Públicos, Arriendo, Transporte/Domicilios, Marketing/Publicidad, Nómina/Personal, Equipos/Tecnología, Impuestos, Empaques/Materiales, Otros.
Responde SOLO con: {{categoría}} | {{razón breve en máximo 10 palabras}}"""

    system = "Eres un contador especializado en pequeños negocios colombianos. Clasificas gastos en categorías contables de forma precisa y concisa."

    reply, error = call_groq([{"role": "user", "content": prompt}], system)
    if error:
        return jsonify({"error": error}), 500

    parts = reply.strip().split("|", 1)
    categoria = parts[0].strip() if parts else reply
    razon = parts[1].strip() if len(parts) > 1 else ""

    return jsonify({"categoria": categoria, "razon": razon, "raw": reply})


@dora_bp.route('/ia/analizar-ventas', methods=['POST'])
def analizar_ventas():
    auth_err = require_dora_auth()
    if auth_err: return auth_err
    data = request.get_json() or {}
    ventas_data = data.get('ventas', {})

    if not ventas_data:
        return jsonify({"error": "Datos de ventas requeridos"}), 400

    prompt = f"""Analiza estas cifras de ventas de una tienda colombiana y da 2-3 insights accionables:
{json.dumps(ventas_data, ensure_ascii=False)}
Sé conciso, práctico y en español colombiano. Incluye una recomendación específica para mejorar."""

    system = "Eres un analista de negocios especializado en tiendas y emprendimientos colombianos. Interpretas cifras de ventas y das recomendaciones prácticas y accionables."

    reply, error = call_groq([{"role": "user", "content": prompt}], system)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"analisis": reply})


@dora_bp.route('/ia/sugerir-precio', methods=['POST'])
def sugerir_precio():
    auth_err = require_dora_auth()
    if auth_err: return auth_err
    data = request.get_json() or {}
    nombre = data.get('nombre', '')
    costo = data.get('costo', '')
    categoria = data.get('categoria', '')
    negocio_tipo = data.get('negocio_tipo', 'tienda')

    if not nombre:
        return jsonify({"error": "Nombre del producto requerido"}), 400

    costo_txt = f" El costo de compra es ${costo}." if costo else ""
    categoria_txt = f" Categoría: {categoria}." if categoria else ""

    prompt = f"""Para una {negocio_tipo} colombiana que vende "{nombre}"{categoria_txt}{costo_txt}
Sugiere un precio de venta competitivo para el mercado colombiano.
Responde en este formato exacto (3 líneas):
PRECIO_SUGERIDO: $X.XXX
RANGO: $X.XXX - $Y.YYY
RAZON: [máximo 15 palabras explicando el precio]"""

    system = "Eres un experto en precios para el mercado retail colombiano — tiendas de barrio, minimercados y emprendimientos. Conoces precios de productos cotidianos en Colombia 2025."

    reply, error = call_groq([{"role": "user", "content": prompt}], system)
    if error:
        return jsonify({"error": error}), 500

    lines = reply.strip().split('\n')
    precio = rango = razon = ''
    for line in lines:
        if line.startswith('PRECIO_SUGERIDO:'):
            precio = line.replace('PRECIO_SUGERIDO:', '').strip()
        elif line.startswith('RANGO:'):
            rango = line.replace('RANGO:', '').strip()
        elif line.startswith('RAZON:'):
            razon = line.replace('RAZON:', '').strip()

    return jsonify({"precio_sugerido": precio, "rango": rango, "razon": razon, "raw": reply})


@dora_bp.route('/ia/generar-campana', methods=['POST'])
def generar_campana():
    auth_err = require_dora_auth()
    if auth_err: return auth_err
    data = request.get_json() or {}
    producto = data.get('producto', '')
    objetivo = data.get('objetivo', 'vender más')
    publico = data.get('publico', 'clientes habituales')
    precio_actual = data.get('precio_actual', '')

    if not producto:
        return jsonify({"error": "Producto requerido"}), 400

    precio_txt = f" El precio actual es ${precio_actual}." if precio_actual else ""
    prompt = f"""Crea un paquete de marketing completo para una tienda colombiana.
Producto/oferta: {producto}
Objetivo: {objetivo}
Público: {publico}{precio_txt}

Responde en este formato exacto (sin texto adicional):
BANNER: [texto del banner, máx 12 palabras, impactante]
WHATSAPP: [mensaje de WhatsApp informal y llamativo, máx 3 líneas con emojis]
INSTAGRAM: [caption para Instagram, máx 2 líneas + 3 hashtags]
PRECIO_PROMO: [precio o % de descuento sugerido para esta campaña]
CONSEJO: [un consejo táctico de 10 palabras para maximizar esta campaña]"""

    system = "Eres un experto en marketing digital para pequeños negocios y tiendas colombianas. Hablas en español colombiano informal. Creas contenido auténtico que realmente funciona para tenderos."

    reply, error = call_groq([{"role": "user", "content": prompt}], system)
    if error:
        return jsonify({"error": error}), 500

    result = {"banner": "", "whatsapp": "", "instagram": "", "precio_promo": "", "consejo": "", "raw": reply}
    for line in reply.strip().split('\n'):
        if line.startswith('BANNER:'):
            result["banner"] = line.replace('BANNER:', '').strip()
        elif line.startswith('WHATSAPP:'):
            result["whatsapp"] = line.replace('WHATSAPP:', '').strip()
        elif line.startswith('INSTAGRAM:'):
            result["instagram"] = line.replace('INSTAGRAM:', '').strip()
        elif line.startswith('PRECIO_PROMO:'):
            result["precio_promo"] = line.replace('PRECIO_PROMO:', '').strip()
        elif line.startswith('CONSEJO:'):
            result["consejo"] = line.replace('CONSEJO:', '').strip()

    return jsonify(result)


@dora_bp.route('/ia/contexto-modulo', methods=['POST'])
def contexto_modulo():
    auth_err = require_dora_auth()
    if auth_err: return auth_err
    data = request.get_json() or {}
    modulo = data.get('modulo', 'general')
    pregunta = data.get('pregunta', '')
    contexto_datos = data.get('datos', {})
    negocio_nombre = data.get('negocio_nombre')
    negocio_tipo = data.get('negocio_tipo')

    if not pregunta:
        return jsonify({"error": "Pregunta requerida"}), 400

    modulo_contextos = {
        'inventario': "El usuario está en el módulo de Inventario de TuKomercio, gestionando sus productos.",
        'ventas': "El usuario está en el módulo de Ventas (POS) de TuKomercio, procesando una venta.",
        'gastos': "El usuario está en el módulo de Gastos de TuKomercio, registrando y clasificando gastos.",
        'reportes': "El usuario está viendo sus Reportes Financieros en TuKomercio.",
        'alertas': "El usuario está en el módulo de Alertas y Tareas de TuKomercio.",
        'dashboard': "El usuario está viendo su Dashboard financiero en TuKomercio.",
        'compras': "El usuario está en el módulo de Compras a Proveedores de TuKomercio.",
        'pedidos': "El usuario está gestionando Pedidos de clientes en TuKomercio.",
    }

    ctx_modulo = modulo_contextos.get(modulo, "El usuario está usando TuKomercio.")
    nombre_tienda = negocio_nombre or "su tienda"

    datos_str = ""
    if contexto_datos:
        datos_str = f"\n\nDATOS DEL CONTEXTO ACTUAL:\n{json.dumps(contexto_datos, ensure_ascii=False, indent=2)}"

    system = f"""Eres Dora IA, asistente inteligente de TuKomercio para tenderos colombianos.

{ctx_modulo}
La tienda se llama: {nombre_tienda} (tipo: {negocio_tipo or 'tienda'}).{datos_str}

NAVEGACIÓN REAL DE TuKomercio (menú lateral):
• MI NEGOCIO: Mis Negocios · Mis Sucursales · Catálogo · Centro Financiero
• HERRAMIENTAS: Mi Página Web · Mi Portafolio
• OPERACIONES: Bancos y Pagos · Servicios · Publicar

FLUJOS PRINCIPALES:
• Crear/editar tienda online → "Mi Página Web" (logo, colores, descripción, activar tienda pública)
• Agregar productos → "Catálogo" (nombre, precio, stock, imagen, categoría)
• Enlace de la tienda → tuko.pages.dev/tienda/?slug=nombre-negocio
• Registrar venta física → "Centro Financiero" → POS (Punto de Venta)
• Ver pedidos online → "Pedidos Online" en el Centro Financiero
• Gastos e ingresos → "Centro Financiero"
• Búsqueda rápida → Ctrl+K

LO QUE TuKomercio NO TIENE: tasas de cambio, temas prediseñados, pago integrado con pasarela, botón de tienda en esquina superior derecha.

REGLA CRÍTICA: Si no sabes con certeza cómo funciona algo en TuKomercio, di "no tengo esa información exacta, revisa en [módulo]". NUNCA inventes pasos o botones que no existen.

Responde directo, práctico, en español colombiano. Máximo 4 oraciones."""

    reply, error = call_groq([{"role": "user", "content": pregunta}], system)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"reply": reply})


@dora_bp.route('/ia/buscar-producto', methods=['POST'])
def buscar_producto():
    auth_err = require_dora_auth()
    if auth_err: return auth_err
    """Busca un producto por nombre (fuzzy) en el catálogo del negocio."""
    data = request.get_json() or {}
    nombre_busqueda = data.get('nombre', '').strip()
    negocio_id = data.get('negocio_id')

    if not nombre_busqueda:
        return jsonify({"error": "Nombre requerido"}), 400

    nid = _resolve_negocio_id(negocio_id)
    if not nid:
        return jsonify({"error": "Negocio no encontrado"}), 404

    try:
        from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo

        # Búsqueda insensible a mayúsculas con ILIKE
        productos = (
            ProductoCatalogo.query
            .filter(
                ProductoCatalogo.negocio_id == nid,
                ProductoCatalogo.activo == True,
                ProductoCatalogo.nombre.ilike(f'%{nombre_busqueda}%')
            )
            .limit(5)
            .all()
        )

        if not productos:
            return jsonify({"productos": [], "mensaje": f"No encontré ningún producto con '{nombre_busqueda}'"})

        return jsonify({
            "productos": [
                {
                    "id": p.id_producto,
                    "nombre": p.nombre,
                    "precio": float(p.precio),
                    "stock": p.stock,
                    "categoria": p.categoria,
                    "stock_minimo": p.stock_minimo
                }
                for p in productos
            ]
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@dora_bp.route('/ia/auditar-categorias', methods=['POST'])
def auditar_categorias():
    auth_err = require_dora_auth()
    if auth_err: return auth_err
    """
    Dora analiza los productos del negocio y detecta los que parecen
    estar en la categoría equivocada. Devuelve una lista de sugerencias.
    """
    data = request.get_json() or {}
    negocio_id = data.get('negocio_id')

    nid = _resolve_negocio_id(negocio_id)
    if not nid:
        return jsonify({"error": "Negocio no encontrado"}), 404

    try:
        from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo
        import random

        # Cargar todos los productos activos del negocio
        todos = (
            ProductoCatalogo.query
            .filter_by(negocio_id=nid, activo=True)
            .with_entities(
                ProductoCatalogo.id_producto,
                ProductoCatalogo.nombre,
                ProductoCatalogo.categoria,
            )
            .all()
        )

        if not todos:
            return jsonify({"sugerencias": [], "total_analizados": 0,
                            "mensaje": "No hay productos para analizar."})

        # Muestreo diverso: hasta 5 por categoría, máximo 60 total
        por_categoria = {}
        for p in todos:
            cat = p.categoria or "Sin categoría"
            por_categoria.setdefault(cat, []).append(p)

        muestra = []
        for productos_cat in por_categoria.values():
            random.shuffle(productos_cat)
            muestra.extend(productos_cat[:5])

        random.shuffle(muestra)
        muestra = muestra[:60]

        # Construir lista para el prompt
        lineas = "\n".join(
            f'{i+1}. ID={p.id_producto} | "{p.nombre}" | Categoría: "{p.categoria or "Sin categoría"}"'
            for i, p in enumerate(muestra)
        )

        prompt = f"""Analiza esta lista de productos de una tienda colombiana y detecta SOLO los que claramente están en la categoría equivocada o en una categoría genérica que podría ser más específica.

PRODUCTOS:
{lineas}

Responde ÚNICAMENTE con un array JSON (sin texto adicional, sin markdown, sin explicaciones fuera del JSON).
Si no hay productos mal categorizados, responde con un array vacío: []

Formato requerido:
[
  {{
    "producto_id": 123,
    "nombre": "nombre del producto",
    "categoria_actual": "categoría actual",
    "categoria_sugerida": "categoría más apropiada",
    "razon": "razón breve en máximo 12 palabras"
  }}
]

Solo incluye productos donde estés MUY SEGURO de que la categoría es incorrecta. Sé conservador."""

        system = ("Eres un experto en clasificación de productos para tiendas colombianas. "
                  "Tu tarea es detectar productos mal categorizados. "
                  "Responde SOLO con JSON válido, sin markdown ni texto adicional.")

        key = get_groq_key()
        if not key:
            return jsonify({"error": "GROQ_API_KEY no configurada"}), 500

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024,
            "temperature": 0.3,
        }
        resp = requests.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip()

        # Limpiar posibles code fences de markdown
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        try:
            sugerencias = json.loads(raw)
            if not isinstance(sugerencias, list):
                sugerencias = []
        except json.JSONDecodeError:
            # Intentar extraer el array JSON si viene mezclado con texto
            import re as _re
            match = _re.search(r'\[.*\]', raw, _re.DOTALL)
            sugerencias = json.loads(match.group(0)) if match else []

        return jsonify({
            "sugerencias": sugerencias,
            "total_analizados": len(muestra),
            "total_productos": len(todos),
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@dora_bp.route('/ia/corregir-categoria', methods=['POST'])
def corregir_categoria():
    auth_err = require_dora_auth()
    if auth_err: return auth_err
    """Actualiza la categoría de un producto según la sugerencia de Dora."""
    data = request.get_json() or {}
    producto_id = data.get('producto_id')
    nueva_categoria = data.get('nueva_categoria', '').strip()
    negocio_id = data.get('negocio_id')

    if not producto_id or not nueva_categoria:
        return jsonify({"error": "producto_id y nueva_categoria son requeridos"}), 400

    nid = _resolve_negocio_id(negocio_id)
    if not nid:
        return jsonify({"error": "Negocio no encontrado"}), 404

    try:
        from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo
        from src.models.database import db

        producto = ProductoCatalogo.query.filter_by(
            id_producto=int(producto_id),
            negocio_id=nid
        ).first()

        if not producto:
            return jsonify({"error": "Producto no encontrado o no pertenece a tu negocio"}), 404

        categoria_anterior = producto.categoria
        producto.categoria = nueva_categoria
        db.session.commit()

        return jsonify({
            "ok": True,
            "producto": producto.nombre,
            "categoria_anterior": categoria_anterior,
            "categoria_nueva": nueva_categoria
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@dora_bp.route('/ia/actualizar-stock', methods=['POST'])
def actualizar_stock():
    auth_err = require_dora_auth()
    if auth_err: return auth_err
    """Actualiza el stock de un producto. Requiere confirmación previa del usuario."""
    data = request.get_json() or {}
    producto_id = data.get('producto_id')
    nuevo_stock = data.get('nuevo_stock')
    negocio_id = data.get('negocio_id')

    if producto_id is None or nuevo_stock is None:
        return jsonify({"error": "producto_id y nuevo_stock son requeridos"}), 400

    nid = _resolve_negocio_id(negocio_id)
    if not nid:
        return jsonify({"error": "Negocio no encontrado"}), 404

    try:
        from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo
        from src.models.database import db

        producto = ProductoCatalogo.query.filter_by(
            id_producto=int(producto_id),
            negocio_id=nid
        ).first()

        if not producto:
            return jsonify({"error": "Producto no encontrado o no pertenece a tu negocio"}), 404

        stock_anterior = producto.stock
        producto.stock = int(nuevo_stock)
        db.session.commit()

        return jsonify({
            "ok": True,
            "producto": producto.nombre,
            "stock_anterior": stock_anterior,
            "stock_nuevo": producto.stock
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
