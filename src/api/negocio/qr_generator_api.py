# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗██╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗  ██████╗██╗ ██████╗ 
# ╚══██╔══╝██║   ██║██║ ██╔╝██╔═══██╗████╗ ████║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗
#    ██║   ██║   ██║█████╔╝ ██║   ██║██╔████╔██║█████╗  ██████╔╝██║     ██║██║   ██║
#    ██║   ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║   ██║
#    ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║╚██████╔╝
#    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝ 
# ═══════════════════════════════════════════════════════════════════════════════
#
# TUKOMERCIO - Plataforma de Comercio Electrónico, Gamificación y Gestión Empresarial
# Anteriormente conocido como: Trayectoria / BizFlow Studio
#
# ═══════════════════════════════════════════════════════════════════════════════
# AVISO DE PROPIEDAD INTELECTUAL Y DERECHOS DE AUTOR
# ═══════════════════════════════════════════════════════════════════════════════
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#
# TITULAR DE DERECHOS:
#   Nombre:     Carlos Eduardo Huérfano Bermúdez
#   C.C.:       1.064.986.917 (Cereté, Córdoba, Colombia)
#   Contacto:   carlos-5100@hotmail.com | +57 322 818 8375
#   Ubicación:  Bogotá D.C., Colombia
#
# INFORMACIÓN DEL PROYECTO:
#   Nombre:     TuKomercio
#   Inicio:     Julio 24, 2024
#   Repositorio: github.com/routeres (routeres@gmail.com)
#
# ═══════════════════════════════════════════════════════════════════════════════
# TÉRMINOS DE USO Y RESTRICCIONES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este código fuente es CONFIDENCIAL y constituye un SECRETO COMERCIAL.
#
# QUEDA ESTRICTAMENTE PROHIBIDO sin autorización ESCRITA del titular:
#
#   1. Copiar, reproducir o duplicar este código, total o parcialmente
#   2. Modificar, adaptar o crear obras derivadas
#   3. Distribuir, publicar, sublicenciar o transferir a terceros
#   4. Usar para desarrollo de productos competidores
#   5. Realizar ingeniería inversa, descompilar o desensamblar
#   6. Remover o alterar este aviso de propiedad intelectual
#
# El acceso a este código NO otorga ninguna licencia implícita o explícita.
#
# ═══════════════════════════════════════════════════════════════════════════════
# PROTECCIÓN LEGAL
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este software está protegido por:
#
#   • Ley 23 de 1982 - Derechos de Autor (Colombia)
#   • Ley 1915 de 2018 - Modernización Derechos de Autor (Colombia)
#   • Decisión Andina 351 de 1993 - Régimen Común sobre Derecho de Autor
#   • Convenio de Berna para la Protección de Obras Literarias y Artísticas
#   • Tratado OMPI sobre Derecho de Autor (WCT)
#   • Acuerdo ADPIC/TRIPS - Organización Mundial del Comercio
#
# SANCIONES POR INFRACCIÓN:
#   • Civiles: Indemnización por daños y perjuicios (Art. 57, Ley 23/1982)
#   • Penales: Prisión de 4 a 8 años y multa (Art. 271, Código Penal Colombiano)
#
# ═══════════════════════════════════════════════════════════════════════════════
# JURISDICCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
#
# Cualquier disputa será resuelta exclusivamente por los tribunales de
# Bogotá D.C., Colombia, bajo las leyes de la República de Colombia.
#
# ═══════════════════════════════════════════════════════════════════════════════
#
# Para solicitar autorización de uso: carlos-5100@hotmail.com
#
# ═══════════════════════════════════════════════════════════════════════════════



"""
BizFlow Studio - API de Generación de QR
Generación on-the-fly de códigos QR para negocios y páginas

VERSIÓN 2.0
- QR de negocio (perfil público)
- 🆕 QR de página (tienda)
- Perfil público del negocio
- Soporte para diferentes tipos de página
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
QR_BASE_URL = "https://tuko.pages.dev"

# URLs por tipo de página
PAGE_URLS = {
    'tienda': lambda slug: f"{QR_BASE_URL}/tienda/?slug={slug}",
    'ecommerce': lambda slug: f"{QR_BASE_URL}/tienda/?slug={slug}",
    'landing': lambda slug: f"{QR_BASE_URL}/sitio/{slug}",  # Próximamente
    'catalogo': lambda slug: f"{QR_BASE_URL}/catalogo/{slug}",  # Próximamente
    'portfolio': lambda slug: f"{QR_BASE_URL}/portfolio/{slug}",  # Próximamente
    'restaurant': lambda slug: f"{QR_BASE_URL}/menu/{slug}",  # Próximamente
}


def get_perfil_publico_url(slug):
    """Genera la URL del perfil público para el QR."""
    return f"{QR_BASE_URL}/negocio/negocio_perfil.html?slug={slug}"


def get_pagina_url(slug, tipo_pagina):
    """
    Genera la URL de la página según su tipo.
    
    Args:
        slug (str): Slug del negocio
        tipo_pagina (str): Tipo de página (tienda, landing, etc.)
        
    Returns:
        str: URL de la página
    """
    # Normalizar tipo
    tipo = (tipo_pagina or 'tienda').lower()
    
    # Obtener función generadora de URL
    url_generator = PAGE_URLS.get(tipo, PAGE_URLS['tienda'])
    
    return url_generator(slug)


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


def generar_qr_imagen(data, size=10, border=2, fill_color="black", back_color="white"):
    """
    Genera una imagen QR en memoria.
    
    Args:
        data (str): Datos a codificar (URL)
        size (int): Tamaño del QR (box_size)
        border (int): Borde blanco alrededor
        fill_color (str): Color del QR
        back_color (str): Color de fondo
        
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
    
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    
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
        "version": "2.0.0",
        "qr_available": QR_AVAILABLE,
        "base_url": QR_BASE_URL,
        "supported_pages": list(PAGE_URLS.keys())
    }), 200


# ==========================================
# QR DEL NEGOCIO (Perfil Público)
# ==========================================

@qr_generator_bp.route('/api/negocio/<int:negocio_id>/qr', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_qr_negocio(negocio_id):
    """
    Genera y devuelve el QR del negocio (perfil público).
    
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
        
        # URL del perfil público
        qr_data = get_perfil_publico_url(negocio.slug)
        
        # Actualizar qr_negocio_data si cambió
        if getattr(negocio, 'qr_negocio_data', None) != qr_data:
            negocio.qr_negocio_data = qr_data
            db.session.commit()
        
        # Parámetros
        formato = request.args.get('format', 'png').lower()
        size = int(request.args.get('size', 10))
        size = max(5, min(20, size))
        
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
                    "qr_type": "negocio",
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
                    "qr_type": "negocio",
                    "qr_url": f"/api/negocio/{negocio_id}/qr?format=png",
                    "qr_download_url": f"/api/negocio/{negocio_id}/qr/download",
                    "negocio_id": negocio_id,
                    "nombre": negocio.nombre_negocio,
                    "slug": negocio.slug
                }
            }), 200
        
    except Exception as e:
        logger.error(f"❌ Error generando QR de negocio: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@qr_generator_bp.route('/api/negocio/<int:negocio_id>/qr/download', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def descargar_qr_negocio(negocio_id):
    """
    Descarga el QR del negocio como archivo PNG de alta calidad.
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
        
        qr_data = get_perfil_publico_url(negocio.slug)
        
        size = int(request.args.get('size', 15))
        size = max(10, min(25, size))
        
        qr_buffer = generar_qr_imagen(qr_data, size=size, border=4)
        
        nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '_', negocio.nombre_negocio)
        
        return send_file(
            qr_buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=f"QR_Negocio_{nombre_limpio}.png"
        )
        
    except Exception as e:
        logger.error(f"❌ Error descargando QR de negocio: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# 🆕 QR DE PÁGINA (Tienda, Landing, etc.)
# ==========================================

@qr_generator_bp.route('/api/negocio/<int:negocio_id>/pagina/qr', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_qr_pagina(negocio_id):
    """
    Genera y devuelve el QR de la página del negocio (tienda, landing, etc.).
    
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
        
        if not negocio.tiene_pagina:
            return jsonify({"success": False, "error": "El negocio no tiene página activa"}), 400
        
        # Obtener tipo de página
        tipo_pagina = negocio.tipo_pagina or 'tienda'
        
        # Generar URL según tipo de página
        qr_data = get_pagina_url(negocio.slug, tipo_pagina)
        
        # Parámetros
        formato = request.args.get('format', 'png').lower()
        size = int(request.args.get('size', 10))
        size = max(5, min(20, size))
        
        # Generar QR
        qr_buffer = generar_qr_imagen(qr_data, size=size)
        
        if formato == 'png':
            return send_file(
                qr_buffer,
                mimetype='image/png',
                as_attachment=False,
                download_name=f"qr-pagina-{negocio.slug}.png"
            )
        
        elif formato == 'base64':
            qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')
            return jsonify({
                "success": True,
                "data": {
                    "base64": f"data:image/png;base64,{qr_base64}",
                    "qr_data": qr_data,
                    "qr_type": "pagina",
                    "tipo_pagina": tipo_pagina,
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
                    "qr_type": "pagina",
                    "tipo_pagina": tipo_pagina,
                    "qr_url": f"/api/negocio/{negocio_id}/pagina/qr?format=png",
                    "qr_download_url": f"/api/negocio/{negocio_id}/pagina/qr/download",
                    "negocio_id": negocio_id,
                    "nombre": negocio.nombre_negocio,
                    "slug": negocio.slug
                }
            }), 200
        
    except Exception as e:
        logger.error(f"❌ Error generando QR de página: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@qr_generator_bp.route('/api/negocio/<int:negocio_id>/pagina/qr/download', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def descargar_qr_pagina(negocio_id):
    """
    Descarga el QR de la página como archivo PNG de alta calidad para impresión.
    
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
        
        if not negocio.tiene_pagina:
            return jsonify({"success": False, "error": "Sin página activa"}), 400
        
        # Obtener tipo y URL
        tipo_pagina = negocio.tipo_pagina or 'tienda'
        qr_data = get_pagina_url(negocio.slug, tipo_pagina)
        
        size = int(request.args.get('size', 15))
        size = max(10, min(25, size))
        
        qr_buffer = generar_qr_imagen(qr_data, size=size, border=4)
        
        # Nombre del archivo según tipo
        tipo_label = {
            'tienda': 'Tienda',
            'ecommerce': 'Tienda',
            'landing': 'Landing',
            'catalogo': 'Catalogo',
            'portfolio': 'Portfolio',
            'restaurant': 'Menu'
        }.get(tipo_pagina, 'Pagina')
        
        nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '_', negocio.nombre_negocio)
        
        return send_file(
            qr_buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name=f"QR_{tipo_label}_{nombre_limpio}.png"
        )
        
    except Exception as e:
        logger.error(f"❌ Error descargando QR de página: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# 🆕 QR COMBINADO (Ambos QRs)
# ==========================================

@qr_generator_bp.route('/api/negocio/<int:negocio_id>/qr/all', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_todos_qr(negocio_id):
    """
    Obtiene información de todos los QRs disponibles para un negocio.
    
    Returns:
        JSON con:
        - QR de negocio (perfil público)
        - QR de página (si tiene página activa)
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
        
        response_data = {
            "negocio_id": negocio_id,
            "nombre": negocio.nombre_negocio,
            "slug": negocio.slug,
            "qrs": []
        }
        
        # QR de Negocio (siempre disponible)
        qr_negocio_url = get_perfil_publico_url(negocio.slug)
        qr_negocio_buffer = generar_qr_imagen(qr_negocio_url, size=10)
        qr_negocio_base64 = base64.b64encode(qr_negocio_buffer.getvalue()).decode('utf-8')
        
        response_data["qrs"].append({
            "type": "negocio",
            "label": "Perfil del Negocio",
            "description": "QR para ver el perfil público y reputación",
            "icon": "bi-building",
            "url": qr_negocio_url,
            "base64": f"data:image/png;base64,{qr_negocio_base64}",
            "download_url": f"/api/negocio/{negocio_id}/qr/download",
            "available": True
        })
        
        # QR de Página (solo si tiene página activa)
        if negocio.tiene_pagina:
            tipo_pagina = negocio.tipo_pagina or 'tienda'
            qr_pagina_url = get_pagina_url(negocio.slug, tipo_pagina)
            qr_pagina_buffer = generar_qr_imagen(qr_pagina_url, size=10)
            qr_pagina_base64 = base64.b64encode(qr_pagina_buffer.getvalue()).decode('utf-8')
            
            tipo_labels = {
                'tienda': ('Tienda Online', 'QR para acceder directamente a tu tienda', 'bi-cart3'),
                'ecommerce': ('Tienda Online', 'QR para acceder directamente a tu tienda', 'bi-cart3'),
                'landing': ('Landing Page', 'QR para tu página de presentación', 'bi-window'),
                'catalogo': ('Catálogo', 'QR para ver tu catálogo de productos', 'bi-grid'),
                'portfolio': ('Portafolio', 'QR para mostrar tus trabajos', 'bi-briefcase'),
                'restaurant': ('Menú Digital', 'QR para ver el menú del restaurante', 'bi-cup-hot'),
            }
            
            label, desc, icon = tipo_labels.get(tipo_pagina, ('Página', 'QR de tu página web', 'bi-globe'))
            
            response_data["qrs"].append({
                "type": "pagina",
                "tipo_pagina": tipo_pagina,
                "label": label,
                "description": desc,
                "icon": icon,
                "url": qr_pagina_url,
                "base64": f"data:image/png;base64,{qr_pagina_base64}",
                "download_url": f"/api/negocio/{negocio_id}/pagina/qr/download",
                "available": True
            })
        else:
            # Página no activa - mostrar como próximamente
            response_data["qrs"].append({
                "type": "pagina",
                "tipo_pagina": None,
                "label": "Página Web",
                "description": "Crea tu página para obtener este QR",
                "icon": "bi-globe",
                "url": None,
                "base64": None,
                "download_url": None,
                "available": False
            })
        
        return jsonify({"success": True, "data": response_data}), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo QRs: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# PERFIL PÚBLICO DEL NEGOCIO
# ==========================================

@qr_generator_bp.route('/api/n/<string:slug>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def perfil_publico_negocio(slug):
    """
    Perfil público del negocio - Endpoint donde apunta el QR.
    NO requiere autenticación.
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
        
        data = {
            "id_negocio": negocio.id_negocio,
            "nombre": negocio.nombre_negocio,
            "descripcion": negocio.descripcion,
            "categoria": negocio.categoria,
            "logo_url": negocio.logo_url,
            "color_tema": negocio.color_tema,
            
            "telefono": negocio.telefono,
            "whatsapp": negocio.whatsapp,
            "whatsapp_link": whatsapp_link,
            "direccion": negocio.direccion,
            
            "ciudad": negocio.ciudad.ciudad_nombre if negocio.ciudad else None,
            
            "tiene_pagina": negocio.tiene_pagina,
            "tipo_pagina": negocio.tipo_pagina,
            "slug": negocio.slug,
            
            "urls": {
                "tienda": get_pagina_url(negocio.slug, 'tienda') if negocio.tiene_pagina and negocio.tipo_pagina in ['tienda', 'ecommerce'] else None,
                "perfil_publico": get_perfil_publico_url(negocio.slug)
            },
            
            "puede_calificar": True
        }
        
        return jsonify({"success": True, "data": data}), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo perfil público: {e}")
        return jsonify({"success": False, "error": "Error interno"}), 500


# ==========================================
# QR GENÉRICO
# ==========================================

@qr_generator_bp.route('/api/qr/generate', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def generar_qr_generico():
    """
    Genera un QR para cualquier URL/dato.
    Requiere autenticación.
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