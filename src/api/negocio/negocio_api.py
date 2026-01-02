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
        nuevo_negocio = Negocio(
            nombre_negocio=data.get('nombre_negocio'),
            categoria=data.get('tipo_negocio') or data.get('tipoNegocio'), 
            descripcion=data.get('descripcion'),
            direccion=data.get('direccion'),
            ciudad_id=int(data.get('ciudad_id')) if data.get('ciudad_id') else None,
            telefono=data.get('telefono'),
            usuario_id=current_user.id_usuario 
        )
        db.session.add(nuevo_negocio)
        db.session.commit()
        
        # Acceso seguro al ID recién creado
        negocio_id = getattr(nuevo_negocio, 'id_negocio', getattr(nuevo_negocio, 'id', None))
        return jsonify({"status": "success", "id": negocio_id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"🔥 ERROR en /registrar_negocio: {str(e)}")
        return jsonify({"error": "No se pudo guardar", "details": str(e)}), 500

# --- 3. OBTENER MIS NEGOCIOS (CORREGIDO) ---
@negocio_api_bp.route('/mis_negocios', methods=['GET'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_mis_negocios():
    try:
        negocios = Negocio.query.filter_by(usuario_id=current_user.id_usuario).all()
        
        resultado = []
        for n in negocios:
            # Esta línea corrige el error de "id_negocio" inexistente
            # Busca 'id_negocio', si no existe busca 'id'
            safe_id = getattr(n, 'id_negocio', getattr(n, 'id', None))
            
            resultado.append({
                "id": safe_id, 
                "nombre_negocio": n.nombre_negocio
            })
            
        return jsonify(resultado), 200
    except Exception as e:
        logger.error(f"🔥 ERROR en /mis_negocios: {str(e)}")
        return jsonify({"error": "Error al obtener negocios"}), 500

# --- 4. REGISTRAR SUCURSAL ---
@negocio_api_bp.route('/registrar_sucursal', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
@login_required
def registrar_sucursal():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        data = request.get_json()
        negocio_id = data.get('negocio_id')

        # Verificación dinámica de propiedad para evitar el mismo error de ID
        negocios_usuario = Negocio.query.filter_by(usuario_id=current_user.id_usuario).all()
        ids_propios = [getattr(n, 'id_negocio', getattr(n, 'id', None)) for n in negocios_usuario]

        if int(negocio_id) not in ids_propios:
            return jsonify({"error": "No autorizado para este negocio"}), 403

        nueva_sucursal = Sucursal(
            nombre_sucursal=data.get('nombre_sucursal'),
            direccion=data.get('direccion'),
            telefono=data.get('telefono'),
            ciudad=data.get('ciudad'),
            departamento=data.get('departamento'),
            codigo_postal=data.get('codigo_postal'),
            activo=data.get('activo', True),
            es_principal=data.get('es_principal', False),
            cajeros=data.get('cajeros', []),           
            administradores=data.get('administradores', []), 
            negocio_id=negocio_id
        )

        db.session.add(nueva_sucursal)
        db.session.commit()

        suc_id = getattr(nueva_sucursal, 'id_sucursal', getattr(nueva_sucursal, 'id', None))
        return jsonify({"status": "success", "id": suc_id}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"🔥 ERROR en /registrar_sucursal: {str(e)}")
        return jsonify({"error": "Error interno", "details": str(e)}), 500

# --- 5. OBTENER SUCURSALES POR NEGOCIO ---
@negocio_api_bp.route('/negocios/<int:negocio_id>/sucursales', methods=['GET'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_sucursales(negocio_id):
    try:
        # Validación de propiedad segura
        negocio_check = Negocio.query.filter_by(usuario_id=current_user.id_usuario).all()
        ids_propios = [getattr(n, 'id_negocio', getattr(n, 'id', None)) for n in negocio_check]
        
        if negocio_id not in ids_propios:
            return jsonify({"error": "Acceso denegado"}), 403

        sucursales = Sucursal.query.filter_by(negocio_id=negocio_id).all()
        return jsonify([s.to_dict() for s in sucursales]), 200
    except Exception as e:
        logger.error(f"🔥 ERROR en obtener_sucursales: {str(e)}")
        return jsonify({"error": "Error al obtener sucursales"}), 500