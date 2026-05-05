import os
import json
import requests
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

dora_bp = Blueprint('dora', __name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

def get_groq_key():
    return os.environ.get("GROQ_API_KEY", "")

def build_system_prompt(negocio_nombre=None, negocio_tipo=None, user_nombre=None):
    nombre_tienda = negocio_nombre or "tu tienda"
    tipo = negocio_tipo or "tienda"
    nombre_usuario = user_nombre or "tendero"

    return f"""Eres Dora IA, la asistente inteligente de TuKomercio — la plataforma de e-commerce para tenderos colombianos.

Tu misión es ayudar a {nombre_usuario}, dueño de {nombre_tienda} ({tipo}), a hacer crecer su negocio.

CONOCES PERFECTAMENTE TuKomercio:
- Designer: personalizador visual de la tienda (tipografía, colores, banners, redes sociales, testimonios, galería)
- Inventario: gestión de productos, stock y precios
- Ventas: registro de ventas y pedidos
- Contabilidad: ingresos, gastos, reportes financieros
- Búsqueda Global (Ctrl+K): para encontrar cualquier módulo o app

ESTILO DE RESPUESTA:
- Habla en español colombiano, informal pero profesional
- Sé concisa: máximo 3-4 oraciones por respuesta a menos que expliques algo complejo
- Usa emojis con moderación (1-2 por respuesta)
- Si el usuario pregunta cómo hacer algo en TuKomercio, da pasos concretos
- Si pregunta sobre su negocio (ventas, precios, clientes), da consejos prácticos para tenderos colombianos
- Si te preguntan algo que no sabes, admítelo y sugiere la mejor alternativa

CAPACIDADES ESPECIALES QUE PUEDES HACER:
- Generar descripciones de productos para el catálogo
- Analizar e interpretar cifras de ventas
- Clasificar gastos en categorías contables
- Crear textos de promociones y banners
- Sugerir estrategias de precios para el mercado colombiano
- Ayudar a configurar la tienda en el Designer
- Responder preguntas sobre el negocio y el mercado local

Recuerda: eres parte de TuKomercio, no eres ChatGPT ni otro asistente genérico. Eres Dora IA."""


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
@login_required
def chat():
    data = request.get_json() or {}
    messages = data.get('messages', [])
    negocio_nombre = data.get('negocio_nombre')
    negocio_tipo = data.get('negocio_tipo')

    if not messages:
        return jsonify({"error": "No hay mensajes"}), 400

    system_prompt = build_system_prompt(
        negocio_nombre=negocio_nombre,
        negocio_tipo=negocio_tipo,
        user_nombre=getattr(current_user, 'nombre', None)
    )

    reply, error = call_groq(messages, system_prompt)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"reply": reply})


@dora_bp.route('/ia/describir-producto', methods=['POST'])
@login_required
def describir_producto():
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
@login_required
def generar_promo():
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
@login_required
def clasificar_gasto():
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
@login_required
def analizar_ventas():
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
@login_required
def sugerir_precio():
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
@login_required
def generar_campana():
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
@login_required
def contexto_modulo():
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

Responde de forma directa, práctica y en español colombiano. Máximo 3 oraciones. Sin introducción innecesaria."""

    reply, error = call_groq([{"role": "user", "content": pregunta}], system)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"reply": reply})
