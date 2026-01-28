"""
BizFlow Studio - API de Generación de QR
Generación on-the-fly de códigos QR para negocios y páginas

VERSIÓN 1.1
- QR de negocio (perfil público)
- QR de página (tienda/landing) - futuro
- Perfil público del negocio
- 🔄 URL actualizada para perfil público
"""

import logging
import io
import base64
import re
from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
from flask_login import current_user
from src.models.database import db
from src.models.colombia_data.negocio import Negocio

# QR Code
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("⚠️ qrcode no instalado. Instalar con: pip install qrcode[pil]")

# Logger
logger = logging.getLogger(__name__)

# Blueprint
qr_generator_bp = Blueprint('qr_generator_bp', __name__)

# ==========================================
# CONFIGURACIÓN
# ==========================================
QR_BASE_URL = "https://tuko.pages.dev"  # ✅ URL actualizada


def get_perfil_publico_url(slug):
    """Genera la URL del perfil público para el QR."""
    return f"{QR_BASE_URL}/negocio/negocio_perfil.html?slug={slug}"


# ==========================================
# HELPERS
# ==========================================

def get_current_user_id():
    """Obtiene el ID del usuario autenticado."""
    # 1. JWT primero
    try:
        from src.auth_jwt import get_user_id_from_jwt
        jwt_user_id = get_user_id_from_jwt()
        if jwt_user_id:
            return jwt_user_id
    except:
        pass
    
    # 2. Header X-User-ID
    header_id = request.headers.get('X-User-ID')
    if header_id and header_id.isdigit():
        return int(header_id)
    
    # 3. Flask-Login
    if current_user.is_authenticated:
        return getattr(current_user, 'id_usuario', None)
    
    return None


def generar_qr_imagen(data, size=10, border=2):
    """
    Genera una imagen QR en memoria.
    
    Args:
        data (str): Datos a codificar (URL)
        size (int): Tamaño del QR (box_size)
        border (int): Borde blanco alrededor
        
    Returns:
        BytesIO: Imagen PNG en memoria
    """
    if not QR_AVAILABLE:
        raise Exception("Librería qrcode no disponible")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer


# ==========================================
# HEALTH CHECK
# ==========================================

@qr_generator_bp.route('/api/qr/health', methods=['GET'])
def qr_health():
    """Health check del módulo QR."""
    return jsonify({
        "status": "online",
        "module": "qr_generator",
        "version": "1.1.0",
        "qr_available": QR_AVAILABLE,
        "base_url": QR_BASE_URL
    }), 200


# ==========================================
# QR DEL NEGOCIO
# ==========================================

@qr_generator_bp.route('/api/negocio/<int:negocio_id>/qr', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_qr_negocio(negocio_id):
    """
    Genera y devuelve el QR del negocio.
    
    Query params:
        - format: 'png' (default) | 'base64' | 'json'
        - size: tamaño del QR (default: 10)
        
    Returns:
        - PNG image (default)
        - Base64 string
        - JSON con datos del QR
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    if not QR_AVAILABLE:
        return jsonify({"success": False, "error": "QR no disponible en el servidor"}), 503
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        if not negocio.slug:
            return jsonify({"success": False, "error": "El negocio no tiene slug configurado"}), 400
        
        # ✅ URL del perfil público (formato correcto)
        qr_data = get_perfil_publico_url(negocio.slug)
        
        # Actualizar qr_negocio_data si cambió
        if getattr(negocio, 'qr_negocio_data', None) != qr_data:
            negocio.qr_negocio_data = qr_data
            db.session.commit()
        
        # Parámetros
        formato = request.args.get('format', 'png').lower()
        size = int(request.args.get('size', 10))
        size = max(5, min(20, size))  # Limitar entre 5 y 20
        
        # Generar QR
        qr_buffer = generar_qr_imagen(qr_data, size=size)
        
        if formato == 'png':
            return send_file(
                qr_buffer,
                mimetype='image/png',
                as_attachment=False,
                download_name=f"qr-{negocio.slug}.png"
            )
        
        elif formato == 'base64':
            qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')
            return jsonify({
                "success": True,
                "data": {
                    "base64": f"data:image/png;base64,{qr_base64}",
                    "qr_data": qr_data,
                    "negocio_id": negocio_id,
                    "slug": negocio.slug,
                    "nombre": negocio.nombre_negocio
                }
            }), 200
        
        else:  # json
            return jsonify({
                "success": True,
                "data": {
                    "qr_data": qr_data,
                    "qr_url": f"/api/negocio/{negocio_id}/qr?format=png",
                    "qr_download_url": f"/api/negocio/{negocio_id}/qr/download",
                    "negocio_id": negocio_id,
                    "nombre": negocio.nombre_negocio,
                    "slug": negocio.slug
                }
            }), 200
        
    except Exception as e:
        logger.error(f"❌ Error generando QR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@qr_generator_bp.route('/api/negocio/<int:negocio_id>/qr/download', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def descargar_qr_negocio(negocio_id):
    """
    Descarga el QR como archivo PNG de alta calidad para impresión.
    
    Query params:
        - size: tamaño del QR (default: 15, para mejor calidad)
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    if not QR_AVAILABLE:
        return jsonify({"success": False, "error": "QR no disponible"}), 503
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        negocio = Negocio.query.filter_by(
            id_negocio=negocio_id,
            usuario_id=user_id
        ).first()
        
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        if not negocio.slug:
            return jsonify({"success": False, "error": "Sin slug configurado"}), 400
        
        # ✅ URL del perfil público (formato correcto)
        qr_data = get_perfil_publico_url(negocio.slug)
        
        size = int(request.args.get('size', 15))
        size = max(10, min(25, size))
        
        qr_buffer = generar_qr_imagen(qr_data, size=size, border=4)
        
        # Nombre limpio para el archivo
        nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '_', negocio.nombre_negocio)
        
        return send_file(
            qr_buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=f"QR_{nombre_limpio}.png"
        )
        
    except Exception as e:
        logger.error(f"❌ Error descargando QR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# PERFIL PÚBLICO DEL NEGOCIO (donde apunta el QR)
# ==========================================

@qr_generator_bp.route('/api/n/<string:slug>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def perfil_publico_negocio(slug):
    """
    Perfil público del negocio - Endpoint donde apunta el QR.
    NO requiere autenticación.
    
    Retorna información pública del negocio:
    - Nombre, descripción, categoría
    - Logo, WhatsApp
    - Links a sus páginas (tienda, landing, etc.)
    - Info para calificar
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        negocio = Negocio.query.filter_by(
            slug=slug,
            activo=True
        ).first()
        
        if not negocio:
            return jsonify({
                "success": False, 
                "error": "Negocio no encontrado"
            }), 404
        
        # Verificar si el perfil es público
        if not getattr(negocio, 'perfil_publico', True):
            return jsonify({
                "success": False, 
                "error": "Este perfil no está disponible públicamente"
            }), 403
        
        # WhatsApp link
        whatsapp_link = None
        if negocio.whatsapp:
            numero = ''.join(filter(str.isdigit, negocio.whatsapp))
            if len(numero) == 10:
                numero = f"57{numero}"
            whatsapp_link = f"https://wa.me/{numero}"
        
        # Construir respuesta pública
        data = {
            "id_negocio": negocio.id_negocio,
            "nombre": negocio.nombre_negocio,
            "descripcion": negocio.descripcion,
            "categoria": negocio.categoria,
            "logo_url": negocio.logo_url,
            "color_tema": negocio.color_tema,
            
            # Contacto
            "telefono": negocio.telefono,
            "whatsapp": negocio.whatsapp,
            "whatsapp_link": whatsapp_link,
            "direccion": negocio.direccion,
            
            # Ciudad
            "ciudad": negocio.ciudad.ciudad_nombre if negocio.ciudad else None,
            
            # Páginas disponibles
            "tiene_pagina": negocio.tiene_pagina,
            "tipo_pagina": negocio.tipo_pagina,
            "slug": negocio.slug,
            
            # URLs de páginas
            "urls": {
                "tienda": f"/tienda/{negocio.slug}" if negocio.tiene_pagina and negocio.tipo_pagina == 'tienda' else None,
                "catalogo": f"/catalogo/{negocio.slug}" if negocio.tiene_pagina and negocio.tipo_pagina == 'catalogo' else None,
                "landing": f"/sitio/{negocio.slug}" if negocio.tiene_pagina else None,
                "calificar": f"/calificar/{negocio.slug}",
                "perfil_publico": get_perfil_publico_url(negocio.slug)
            },
            
            # Para calificaciones (futuro)
            "puede_calificar": True
        }
        
        return jsonify({"success": True, "data": data}), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo perfil público: {e}")
        return jsonify({"success": False, "error": "Error interno"}), 500


# ==========================================
# QR GENÉRICO (para URLs personalizadas)
# ==========================================

@qr_generator_bp.route('/api/qr/generate', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def generar_qr_generico():
    """
    Genera un QR para cualquier URL/dato.
    Requiere autenticación.
    
    Body:
        - data: string a codificar (requerido)
        - size: tamaño (opcional, default: 10)
        - format: 'png' | 'base64' (opcional, default: 'base64')
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    if not QR_AVAILABLE:
        return jsonify({"success": False, "error": "QR no disponible"}), 503
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        body = request.get_json()
        if not body or not body.get('data'):
            return jsonify({"success": False, "error": "Se requiere 'data' en el body"}), 400
        
        qr_data = body['data']
        size = int(body.get('size', 10))
        size = max(5, min(20, size))
        formato = body.get('format', 'base64').lower()
        
        qr_buffer = generar_qr_imagen(qr_data, size=size)
        
        if formato == 'png':
            return send_file(
                qr_buffer,
                mimetype='image/png',
                as_attachment=False,
                download_name="qr-generated.png"
            )
        else:
            qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')
            return jsonify({
                "success": True,
                "data": {
                    "base64": f"data:image/png;base64,{qr_base64}",
                    "qr_data": qr_data
                }
            }), 200
        
    except Exception as e:
        logger.error(f"❌ Error generando QR genérico: {e}")
        return jsonify({"success": False, "error": str(e)}), 500