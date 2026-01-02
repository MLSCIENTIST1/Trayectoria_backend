import logging
import sys
import traceback
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_cors import cross_origin

# Importaciones de modelos
from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.colombia_data import Colombia 
# NOTA: Asegúrate de que este sea el nombre correcto de tu modelo de Sucursal
from src.models.colombia_data.sucursal import Sucursal 
from src.models.database import db

# --- CONFIGURACIÓN DE LOGS ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
if not logger.handlers:
    logger.addHandler(handler)

negocio_api_bp = Blueprint('negocio_api_bp', __name__)

@negocio_api_bp.before_request
def debug_incoming_request():
    logger.debug(f"📡 [DEBUG BLUEPRINT] Petición entrante: {request.method} {request.path}")

# --- 1. CIUDADES (Autocompletado) ---
@negocio_api_bp.route('/ciudades', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_ciudades():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        termino = request.args.get('q', '').strip()
        query = Colombia.query.with_entities(Colombia.ciudad_id, Colombia.ciudad_nombre)
        if termino:
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        ciudades_db = query.limit(15).all()
        resultado = [{"id": c.ciudad_id, "nombre": c.ciudad_nombre} for c in ciudades_db]
        return jsonify(resultado), 200
    except Exception as e:
        logger.error(f"🔥 ERROR en /ciudades: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- 2. REGISTRAR NEGOCIO (POST) ---
@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required 
def registrar_negocio():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        data = request.get_json()
        logger.info(f"👤 Registro por: {current_user.correo} (ID: {current_user.id_usuario})")

        nombre_negocio = data.get('nombre_negocio')
        ciudad_id = data.get('ciudad_id')

        if not nombre_negocio or not ciudad_id:
            return jsonify({"error": "Datos incompletos"}), 400

        nuevo_negocio = Negocio(
            nombre_negocio=nombre_negocio,
            categoria=data.get('tipo_negocio') or data.get('tipoNegocio'), 
            descripcion=data.get('descripcion'),
            direccion=data.get('direccion'),
            ciudad_id=int(ciudad_id),
            telefono=data.get('telefono'),
            usuario_id=current_user.id_usuario 
        )
        
        db.session.add(nuevo_negocio)
        db.session.commit()
        
        negocio_id = getattr(nuevo_negocio, 'id_negocio', getattr(nuevo_negocio, 'id', 'N/A'))
        return jsonify({"status": "success", "id": negocio_id}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"🔥 ERROR en /registrar_negocio: {str(e)}")
        return jsonify({"error": "No se pudo guardar", "details": str(e)}), 500

# --- 3. OBTENER MIS NEGOCIOS (Para el Selector) ---
@negocio_api_bp.route('/mis_negocios', methods=['GET'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_mis_negocios():
    """Retorna los negocios pertenecientes al usuario logueado"""
    try:
        logger.info(f"📋 Consultando negocios para usuario: {current_user.id_usuario}")
        # Filtramos negocios por el ID del usuario actual
        negocios = Negocio.query.filter_by(usuario_id=current_user.id_usuario).all()
        
        resultado = []
        for n in negocios:
            resultado.append({
                "id": getattr(n, 'id_negocio', n.id), # Maneja si tu columna es 'id' o 'id_negocio'
                "nombre_negocio": n.nombre_negocio
            })
        
        return jsonify(resultado), 200
    except Exception as e:
        logger.error(f"🔥 ERROR en /mis_negocios: {str(e)}")
        return jsonify({"error": "Error al obtener negocios"}), 500

# --- 4. OBTENER SUCURSALES POR NEGOCIO ---
@negocio_api_bp.route('/negocios/<int:negocio_id>/sucursales', methods=['GET'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_sucursales(negocio_id):
    """Retorna las sucursales de un negocio específico"""
    try:
        # Verificación de seguridad: El negocio debe pertenecer al usuario logueado
        negocio = Negocio.query.filter_by(id_negocio=negocio_id, usuario_id=current_user.id_usuario).first()
        
        if not negocio:
            return jsonify({"error": "Negocio no encontrado o acceso denegado"}), 403

        sucursales = Sucursal.query.filter_by(negocio_id=negocio_id).all()
        
        resultado = []
        for s in sucursales:
            resultado.append({
                "id": getattr(s, 'id_sucursal', s.id),
                "nombre_sucursal": s.nombre_sucursal
            })
            
        return jsonify(resultado), 200
    except Exception as e:
        logger.error(f"🔥 ERROR en sucursales: {str(e)}")
        return jsonify({"error": "Error al obtener sucursales"}), 500