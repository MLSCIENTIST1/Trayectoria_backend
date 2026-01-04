import logging
import sys
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_cors import cross_origin

# Importaciones de modelos
from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.colombia_data import Colombia 
from src.models.colombia_data.sucursales import Sucursal 
from src.models.database import db

# --- CONFIGURACIÓN DE LOGS ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

negocio_api_bp = Blueprint('negocio_api_bp', __name__)

# --- 1. CIUDADES ---
@negocio_api_bp.route('/ciudades', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_ciudades():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        termino = request.args.get('q', '').strip()
        logger.debug(f"🔍 Buscando ciudades: '{termino}'")
        
        query = Colombia.query.with_entities(Colombia.ciudad_id, Colombia.ciudad_nombre)
        if termino:
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        ciudades_db = query.limit(20).all()
        resultado = [{"id": c.ciudad_id, "nombre": c.ciudad_nombre} for c in ciudades_db]
        return jsonify(resultado), 200
    except Exception as e:
        logger.error(f"🔥 ERROR en /ciudades: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- 2. CONFIGURACIÓN DE PÁGINA (NUEVO) ---
@negocio_api_bp.route('/configuracion-pagina/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_configuracion_pagina(negocio_id):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        # Validamos que el negocio pertenezca al usuario
        negocio = Negocio.query.filter_by(id_negocio=negocio_id, usuario_id=current_user.id_usuario).first()
        if not negocio:
            return jsonify({"success": False, "error": "Negocio no encontrado"}), 404
        
        return jsonify({
            "success": True,
            "has_page": getattr(negocio, 'tiene_pagina', False),
            "slug": getattr(negocio, 'slug', None),
            "plantilla_id": getattr(negocio, 'plantilla_id', None)
        }), 200
    except Exception as e:
        logger.error(f"🔥 ERROR en /configuracion-pagina: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@negocio_api_bp.route('/publicar-pagina', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def publicar_pagina():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        data = request.get_json()
        negocio_id = data.get('id_negocio')
        plantilla_id = data.get('plantilla_id')

        negocio = Negocio.query.filter_by(id_negocio=negocio_id, usuario_id=current_user.id_usuario).first()
        if not negocio:
            return jsonify({"success": False, "error": "No autorizado"}), 403

        # Actualizamos datos de publicación
        negocio.tiene_pagina = True
        negocio.plantilla_id = plantilla_id
        
        # Generar slug simple si no tiene uno
        if not getattr(negocio, 'slug', None):
            negocio.slug = negocio.nombre_negocio.lower().replace(" ", "-")

        db.session.commit()
        return jsonify({"success": True, "slug": negocio.slug}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# --- 3. REGISTRAR NEGOCIO ---
@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required 
def registrar_negocio():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        data = request.get_json()
        logger.info(f"📩 Registro negocio: {data.get('nombre_negocio')}")
        nuevo_negocio = Negocio(
            nombre_negocio=data.get('nombre_negocio'),
            categoria=data.get('tipo_negocio') or data.get('categoria'), 
            descripcion=data.get('descripcion'),
            direccion=data.get('direccion'),
            ciudad_id=int(data.get('ciudad_id')) if data.get('ciudad_id') else None,
            telefono=data.get('telefono'),
            usuario_id=current_user.id_usuario 
        )
        db.session.add(nuevo_negocio)
        db.session.commit()
        return jsonify({"status": "success", "id": nuevo_negocio.id_negocio}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"🔥 ERROR en /registrar_negocio: {str(e)}")
        return jsonify({"error": "No se pudo guardar", "details": str(e)}), 500

# --- 4. OBTENER MIS NEGOCIOS ---
@negocio_api_bp.route('/mis_negocios', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_mis_negocios():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        logger.debug(f"👤 Buscando negocios para usuario ID: {current_user.id_usuario}")
        negocios = Negocio.query.filter_by(usuario_id=current_user.id_usuario).all()
        resultado = [n.serialize() for n in negocios]
        logger.info(f"📋 Enviando {len(resultado)} negocios.")
        return jsonify(resultado), 200
    except Exception as e:
        logger.error(f"🔥 ERROR en /mis_negocios: {str(e)}")
        return jsonify({"error": "Error al obtener negocios"}), 500

# --- 5. REGISTRAR SUCURSAL ---
@negocio_api_bp.route('/registrar_sucursal', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def registrar_sucursal():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        data = request.get_json()
        negocio_id = data.get('negocio_id')
        if not negocio_id:
            return jsonify({"error": "ID de negocio requerido"}), 400

        negocio = Negocio.query.filter_by(id_negocio=negocio_id, usuario_id=current_user.id_usuario).first()
        if not negocio:
            return jsonify({"error": "No autorizado"}), 403

        nueva_sucursal = Sucursal(
            nombre_sucursal=data.get('nombre_sucursal'),
            direccion=data.get('direccion'),
            telefono=data.get('telefono'),
            ciudad=data.get('ciudadSucursal') or data.get('ciudad'),
            departamento=data.get('departamento'),
            codigo_postal=data.get('codigo_postal'),
            activo=data.get('activo', True),
            es_principal=data.get('es_principal', False),
            negocio_id=int(negocio_id)
        )
        db.session.add(nueva_sucursal)
        db.session.commit()
        return jsonify({"status": "success", "id": nueva_sucursal.id_sucursal}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error interno", "details": str(e)}), 500

# --- 6. OBTENER SUCURSALES ---
@negocio_api_bp.route('/negocios/<int:negocio_id>/sucursales', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_sucursales(negocio_id):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        negocio = Negocio.query.filter_by(id_negocio=negocio_id, usuario_id=current_user.id_usuario).first()
        if not negocio:
            return jsonify({"error": "Acceso denegado"}), 403
        sucursales = Sucursal.query.filter_by(negocio_id=negocio_id).all()
        return jsonify([s.to_dict() for s in sucursales]), 200
    except Exception as e:
        logger.error(f"🔥 ERROR en obtener_sucursales: {str(e)}")
        return jsonify({"error": "Error al obtener sucursales"}), 500