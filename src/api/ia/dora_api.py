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

def _resolve_negocio_id(negocio_id_param):
    """Obtiene negocio_id del parámetro o del primer negocio del usuario autenticado."""
    if negocio_id_param:
        return int(negocio_id_param)
    try:
        from src.models.colombia_data.negocio import Negocio
        negocio = Negocio.query.filter_by(usuario_id=current_user.id_usuario).first()
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

    return f"""Eres Dora IA, la asistente inteligente de TuKomercio — la plataforma de e-commerce para tenderos colombianos.

Tu misión es ayudar a {nombre_usuario}, dueño de {nombre_tienda} ({tipo}), a hacer crecer su negocio.{context_block}

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
- Si preguntan por un producto específico, precio, stock o venta: usa SIEMPRE la data real de arriba
- Si te preguntan algo que no está en la data real, dilo claramente y sugiere dónde encontrarlo

CAPACIDADES ESPECIALES:
- Generar descripciones de productos para el catálogo
- Analizar e interpretar cifras de ventas
- Clasificar gastos en categorías contables
- Crear textos de promociones y banners
- Sugerir estrategias de precios para el mercado colombiano

Recuerda: eres parte de TuKomercio. Tienes acceso a la data real del negocio — úsala."""


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
    negocio_id = data.get('negocio_id')

    if not messages:
        return jsonify({"error": "No hay mensajes"}), 400

    negocio_context = get_negocio_context(negocio_id)

    system_prompt = build_system_prompt(
        negocio_nombre=negocio_nombre,
        negocio_tipo=negocio_tipo,
        user_nombre=getattr(current_user, 'nombre', None),
        negocio_context=negocio_context
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


@dora_bp.route('/ia/buscar-producto', methods=['POST'])
@login_required
def buscar_producto():
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
@login_required
def auditar_categorias():
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
@login_required
def corregir_categoria():
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
@login_required
def actualizar_stock():
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
