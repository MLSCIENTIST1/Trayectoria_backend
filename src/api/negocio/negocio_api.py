import logging
import sys
import traceback
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_cors import cross_origin

# Importaciones de modelos
from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.colombia_data import Colombia 
from src.models.colombia_data.sucursales import Sucursal # Sincronizado con tu nuevo archivo
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

# --- 2. REGISTRAR NEGOCIO ---
@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required 
def registrar_negocio():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        data = request.get_json()
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

# --- 3. OBTENER MIS NEGOCIOS (Para Selectores) ---
@negocio_api_bp.route('/mis_negocios', methods=['GET'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_mis_negocios():
    try:
        negocios = Negocio.query.filter_by(usuario_id=current_user.id_usuario).all()
        resultado = [{"id": getattr(n, 'id_negocio', n.id), "nombre_negocio": n.nombre_negocio} for n in negocios]
        return jsonify(resultado), 200
    except Exception as e:
        logger.error(f"🔥 ERROR en /mis_negocios: {str(e)}")
        return jsonify({"error": "Error al obtener negocios"}), 500

# --- 4. REGISTRAR SUCURSAL (NUEVA RUTA) ---
@negocio_api_bp.route('/registrar_sucursal', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def registrar_sucursal():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        data = request.get_json()
        logger.info(f"🏢 Intentando registrar sucursal para negocio ID: {data.get('negocio_id')}")

        # Validamos que el negocio pertenezca al usuario antes de dejarle crear una sucursal
        negocio = Negocio.query.filter_by(id_negocio=data.get('negocio_id'), usuario_id=current_user.id_usuario).first()
        if not negocio:
            return jsonify({"error": "No tienes permiso para agregar sucursales a este negocio"}), 403

        nueva_sucursal = Sucursal(
            nombre_sucursal=data.get('nombre_sucursal'),
            direccion=data.get('direccion'),
            telefono=data.get('telefono'),
            es_principal=data.get('es_principal', False),
            negocio_id=data.get('negocio_id')
        )

        db.session.add(nueva_sucursal)
        db.session.commit()

        logger.info(f"✨ Sucursal '{nueva_sucursal.nombre_sucursal}' creada con éxito.")
        return jsonify({"status": "success", "id": nueva_sucursal.id_sucursal}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"🔥 ERROR en /registrar_sucursal: {str(e)}")
        return jsonify({"error": "No se pudo registrar la sucursal", "details": str(e)}), 500

# --- 5. OBTENER SUCURSALES POR NEGOCIO ---
@negocio_api_bp.route('/negocios/<int:negocio_id>/sucursales', methods=['GET'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_sucursales(negocio_id):
    try:
        # Seguridad: Solo ver sucursales de negocios propios
        negocio = Negocio.query.filter_by(id_negocio=negocio_id, usuario_id=current_user.id_usuario).first()
        if not negocio:
            return jsonify({"error": "Acceso denegado"}), 403

        sucursales = Sucursal.query.filter_by(negocio_id=negocio_id).all()
        resultado = [{"id": s.id_sucursal, "nombre_sucursal": s.nombre_sucursal} for s in sucursales]
        return jsonify(resultado), 200
    except Exception as e:
        logger.error(f"🔥 ERROR en sucursales: {str(e)}")
        return jsonify({"error": "Error al obtener sucursales"}), 500