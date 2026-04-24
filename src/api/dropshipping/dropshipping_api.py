# ============================================
# dropshipping_api.py - v1.0
# Integración multi-proveedor para TuKomercio
# Soporta: CSV/JSON manual + API Mastershop + API Dropi
# ============================================

import json
import csv
import io
import logging
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.database import db
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import ProductoCatalogo

logger = logging.getLogger(__name__)

dropshipping_bp = Blueprint('dropshipping_bp', __name__)

# ============================================
# CONFIGURACIÓN DE PROVEEDORES
# ============================================

PROVEEDORES = {
    'mastershop': {
        'nombre': 'Mastershop',
        'api_url': 'https://app.mastershop.com/api',  # Actualizar cuando tengas credenciales
        'api_key': None,  # Pendiente
        'activo': False   # Se activa cuando tengas API key
    },
    'dropi': {
        'nombre': 'Dropi',
        'api_url': 'https://app.dropi.co/api',  # Actualizar cuando tengas credenciales
        'api_key': None,  # Pendiente
        'activo': False   # Se activa cuando tengas API key
    }
}

# ============================================
# ADAPTADORES POR PROVEEDOR
# Traducen el formato de cada proveedor
# al formato de ProductoCatalogo de TuKomercio
# ============================================

def adaptar_mastershop(producto_raw):
    """Traduce producto de Mastershop al formato TuKomercio"""
    return {
        'nombre': producto_raw.get('nombre') or producto_raw.get('name') or producto_raw.get('Nombre_del_Producto*') or '',
        'descripcion': producto_raw.get('descripcion') or producto_raw.get('description') or producto_raw.get('Descripción*') or '',
        'precio': float(str(producto_raw.get('precio') or producto_raw.get('price') or producto_raw.get('Precio*') or 0).replace(',', '').replace('.', '') or 0),
        'costo': float(str(producto_raw.get('costo') or producto_raw.get('cost') or 0).replace(',', '').replace('.', '') or 0),
        'stock': int(producto_raw.get('stock') or producto_raw.get('cantidad') or 99),
        'categoria': producto_raw.get('categoria') or producto_raw.get('category') or producto_raw.get('Categoría*') or 'General',
        'imagen_url': producto_raw.get('imagen_url') or producto_raw.get('image') or '',
        'imagenes': [],
        'referencia_sku': producto_raw.get('sku') or producto_raw.get('SKU') or 'SIN_SKU',
        'proveedor': 'mastershop',
        'proveedor_id': producto_raw.get('proveedor_id') or '',
    }

def adaptar_dropi(producto_raw):
    """Traduce producto de Dropi al formato TuKomercio"""
    return {
        'nombre': producto_raw.get('product_name') or producto_raw.get('nombre') or '',
        'descripcion': producto_raw.get('description') or producto_raw.get('descripcion') or '',
        'precio': float(producto_raw.get('suggested_price') or producto_raw.get('precio') or 0),
        'costo': float(producto_raw.get('dropshipper_price') or producto_raw.get('costo') or 0),
        'stock': int(producto_raw.get('stock') or 99),
        'categoria': producto_raw.get('category') or producto_raw.get('categoria') or 'General',
        'imagen_url': producto_raw.get('main_image') or producto_raw.get('imagen_url') or '',
        'imagenes': producto_raw.get('images') or [],
        'referencia_sku': producto_raw.get('product_id') or producto_raw.get('sku') or 'SIN_SKU',
        'proveedor': 'dropi',
        'proveedor_id': str(producto_raw.get('product_id') or ''),
    }

def adaptar_csv_generico(fila):
    """Traduce una fila de CSV genérico al formato TuKomercio"""
    return {
        'nombre': fila.get('nombre') or fila.get('name') or fila.get('producto') or '',
        'descripcion': fila.get('descripcion') or fila.get('description') or '',
        'precio': float(fila.get('precio') or fila.get('price') or 0),
        'costo': float(fila.get('costo') or fila.get('cost') or 0),
        'stock': int(fila.get('stock') or fila.get('cantidad') or 99),
        'categoria': fila.get('categoria') or fila.get('category') or 'General',
        'imagen_url': fila.get('imagen_url') or fila.get('image') or fila.get('imagen') or '',
        'imagenes': [],
        'referencia_sku': fila.get('sku') or fila.get('referencia') or 'SIN_SKU',
        'proveedor': fila.get('proveedor') or 'manual',
        'proveedor_id': fila.get('id') or fila.get('proveedor_id') or '',
    }

ADAPTADORES = {
    'mastershop': adaptar_mastershop,
    'dropi': adaptar_dropi,
    'manual': adaptar_csv_generico,
}

# ============================================
# HELPER: GUARDAR PRODUCTO EN BD
# ============================================

def guardar_producto_dropshipping(producto_adaptado, negocio_id, usuario_id, markup=1.0):
    """
    Guarda un producto adaptado en la BD de TuKomercio.
    markup: multiplicador de precio (ej: 1.3 = 30% de margen sobre el precio del proveedor)
    """
    precio_final = round(producto_adaptado['precio'] * markup)

    # Verificar si ya existe por SKU + proveedor para no duplicar
    sku_unico = f"DS_{producto_adaptado['proveedor']}_{producto_adaptado['referencia_sku']}"

    existente = ProductoCatalogo.query.filter_by(
        negocio_id=negocio_id,
        referencia_sku=sku_unico
    ).first()

    if existente:
        # Actualizar precio y stock si ya existe
        existente.precio = precio_final
        existente.stock = producto_adaptado['stock']
        existente.fecha_actualizacion = datetime.utcnow()
        return existente, 'actualizado'

    # Crear nuevo
    imagenes = producto_adaptado.get('imagenes', [])
    if isinstance(imagenes, str):
        try:
            imagenes = json.loads(imagenes)
        except:
            imagenes = []

    nuevo = ProductoCatalogo(
        nombre=producto_adaptado['nombre'],
        precio=precio_final,
        negocio_id=negocio_id,
        usuario_id=usuario_id,
        descripcion=producto_adaptado.get('descripcion', ''),
        costo=producto_adaptado.get('costo', 0),
        stock=producto_adaptado.get('stock', 99),
        categoria=producto_adaptado.get('categoria', 'General'),
        referencia_sku=sku_unico,
        imagen_url=producto_adaptado.get('imagen_url', ''),
        imagenes=json.dumps(imagenes),
        activo=True,
        estado_publicacion=True,
    )
    db.session.add(nuevo)
    return nuevo, 'creado'


# ============================================
# ENDPOINT 1: IMPORTAR CSV/JSON MANUAL
# Funciona con Mastershop, Dropi o cualquier proveedor
# ============================================

@dropshipping_bp.route('/dropshipping/importar', methods=['POST', 'OPTIONS'])

@cross_origin(supports_credentials=True)
def importar_dropshipping():
    """
    POST /api/dropshipping/importar

    Importa productos desde CSV o JSON de cualquier proveedor.

    FormData o JSON:
    - proveedor: 'mastershop' | 'dropi' | 'manual'
    - negocio_id: ID del negocio (default: 4 para RODAR)
    - markup: multiplicador de precio (default: 1.0)
    - archivo: archivo CSV (opcional)
    - productos: array JSON (opcional si no hay archivo)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        # Leer parámetros
        is_form = 'multipart/form-data' in (request.content_type or '')
        data = request.form.to_dict() if is_form else (request.get_json(silent=True) or {})

        proveedor = data.get('proveedor', 'manual').lower()
        negocio_id = int(data.get('negocio_id', 4))  # Default RODAR
        usuario_id = int(data.get('usuario_id', 1))
        markup = float(data.get('markup', 1.0))

        adaptador = ADAPTADORES.get(proveedor, adaptar_csv_generico)
        productos_raw = []

        # ── Leer desde archivo CSV ──
        if 'archivo' in request.files:
            archivo = request.files['archivo']
            contenido = archivo.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(contenido))
            productos_raw = list(reader)
            logger.info(f"📄 CSV recibido: {len(productos_raw)} filas | Proveedor: {proveedor}")

        # ── Leer desde JSON ──
        elif 'productos' in data:
            productos_raw = json.loads(data['productos']) if isinstance(data['productos'], str) else data['productos']

        elif not is_form:
            body = request.get_json(silent=True) or {}
            productos_raw = body.get('productos', [])

        if not productos_raw:
            return jsonify({"success": False, "message": "No se recibieron productos"}), 400

        # ── Procesar e importar ──
        creados = 0
        actualizados = 0
        errores = []

        for idx, raw in enumerate(productos_raw):
            try:
                adaptado = adaptador(raw)

                if not adaptado['nombre']:
                    errores.append({"fila": idx + 1, "error": "Nombre vacío"})
                    continue

                producto, accion = guardar_producto_dropshipping(
                    adaptado, negocio_id, usuario_id, markup
                )

                if accion == 'creado':
                    creados += 1
                else:
                    actualizados += 1

            except Exception as e:
                errores.append({"fila": idx + 1, "error": str(e)})

        db.session.commit()

        logger.info(f"✅ Dropshipping importado | Creados: {creados} | Actualizados: {actualizados} | Errores: {len(errores)}")

        return jsonify({
            "success": True,
            "message": f"{creados} productos creados, {actualizados} actualizados",
            "creados": creados,
            "actualizados": actualizados,
            "errores": len(errores),
            "detalle_errores": errores[:10]
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error importar dropshipping: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# ENDPOINT 2: CONECTAR API PROVEEDOR
# Se activa cuando tengas credenciales de Mastershop/Dropi
# ============================================

@dropshipping_bp.route('/dropshipping/conectar/<proveedor>', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def conectar_proveedor(proveedor):
    """
    POST /api/dropshipping/conectar/{proveedor}

    Guarda las credenciales de API de un proveedor.
    Body: { "api_key": "...", "api_secret": "..." }
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    if proveedor not in PROVEEDORES:
        return jsonify({"success": False, "message": f"Proveedor '{proveedor}' no soportado"}), 400

    data = request.get_json(silent=True) or {}
    api_key = data.get('api_key', '').strip()

    if not api_key:
        return jsonify({"success": False, "message": "api_key es requerida"}), 400

    PROVEEDORES[proveedor]['api_key'] = api_key
    PROVEEDORES[proveedor]['activo'] = True

    return jsonify({
        "success": True,
        "message": f"Proveedor {PROVEEDORES[proveedor]['nombre']} conectado",
        "proveedor": proveedor
    }), 200


# ============================================
# ENDPOINT 3: SINCRONIZAR DESDE API
# Se usa cuando el proveedor tiene API activa
# ============================================

@dropshipping_bp.route('/dropshipping/sincronizar/<proveedor>', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def sincronizar_proveedor(proveedor):
    """
    POST /api/dropshipping/sincronizar/{proveedor}

    Jala productos directo de la API del proveedor.
    Requiere que el proveedor esté conectado con API key.
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    if proveedor not in PROVEEDORES:
        return jsonify({"success": False, "message": f"Proveedor '{proveedor}' no soportado"}), 400

    config = PROVEEDORES[proveedor]

    if not config['activo'] or not config['api_key']:
        return jsonify({
            "success": False,
            "message": f"Proveedor '{proveedor}' no tiene API configurada. Usa /dropshipping/importar con CSV por ahora."
        }), 400

    try:
        data = request.get_json(silent=True) or {}
        negocio_id = int(data.get('negocio_id', 4))
        usuario_id = int(data.get('usuario_id', 1))
        markup = float(data.get('markup', 1.0))
        pagina = int(data.get('pagina', 1))
        limite = int(data.get('limite', 50))

        # ── Llamar API del proveedor ──
        headers = {'Authorization': f'Bearer {config["api_key"]}', 'Content-Type': 'application/json'}

        if proveedor == 'mastershop':
            url = f"{config['api_url']}/products?page={pagina}&limit={limite}"
        elif proveedor == 'dropi':
            url = f"{config['api_url']}/products?page={pagina}&per_page={limite}"
        else:
            url = f"{config['api_url']}/products"

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "message": f"Error API {proveedor}: {response.status_code}"
            }), 400

        response_data = response.json()

        # Extraer lista de productos según el proveedor
        if proveedor == 'mastershop':
            productos_raw = response_data.get('data') or response_data.get('products') or []
        elif proveedor == 'dropi':
            productos_raw = response_data.get('products') or response_data.get('data') or []
        else:
            productos_raw = response_data if isinstance(response_data, list) else []

        adaptador = ADAPTADORES[proveedor]
        creados = 0
        actualizados = 0
        errores = []

        for raw in productos_raw:
            try:
                adaptado = adaptador(raw)
                if not adaptado['nombre']:
                    continue
                _, accion = guardar_producto_dropshipping(adaptado, negocio_id, usuario_id, markup)
                if accion == 'creado':
                    creados += 1
                else:
                    actualizados += 1
            except Exception as e:
                errores.append(str(e))

        db.session.commit()

        return jsonify({
            "success": True,
            "proveedor": proveedor,
            "creados": creados,
            "actualizados": actualizados,
            "errores": len(errores),
            "total_recibidos": len(productos_raw)
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error sincronizar {proveedor}: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ============================================
# ENDPOINT 4: ESTADO DE PROVEEDORES
# ============================================

@dropshipping_bp.route('/dropshipping/estado', methods=['GET'])
@cross_origin(supports_credentials=True)
def estado_proveedores():
    """GET /api/dropshipping/estado"""
    return jsonify({
        "success": True,
        "proveedores": {
            k: {
                "nombre": v['nombre'],
                "activo": v['activo'],
                "tiene_api": bool(v['api_key'])
            }
            for k, v in PROVEEDORES.items()
        }
    }), 200