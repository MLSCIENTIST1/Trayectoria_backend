import logging
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_cors import cross_origin

# Importaciones ajustadas a tu estructura de carpetas
from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.colombia_data import Colombia 
from src.models.database import db

# Configuración de logs para ver errores en Render
logger = logging.getLogger(__name__)

negocio_api_bp = Blueprint('negocio_api_bp', __name__)

@negocio_api_bp.route('/ciudades', methods=['GET'])
@cross_origin()
def get_ciudades():
    """Retorna ciudades para el autocompletado"""
    try:
        termino = request.args.get('q', '').strip()
        
        query = Colombia.query.with_entities(Colombia.ciudad_id, Colombia.ciudad_nombre)
        
        if termino:
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        ciudades_db = query.limit(20).all()
        
        # IMPORTANTE: El frontend espera "id" y "nombre"
        resultado = [
            {"id": c.ciudad_id, "nombre": c.ciudad_nombre} 
            for c in ciudades_db
        ]
        return jsonify(resultado), 200
    except Exception as e:
        logger.error(f"❌ Error en get_ciudades: {str(e)}")
        return jsonify({"error": "Error al obtener ciudades"}), 500

@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin()
@login_required
def registrar_negocio():
    # Manejo explícito de OPTIONS para evitar el 404 del log inicial
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    data = request.get_json()
    logger.info(f"📩 Datos recibidos: {data}")

    try:
        # Validar que venga el ciudad_id
        if not data.get('ciudad_id'):
            return jsonify({"error": "Debe seleccionar una ciudad válida de la lista"}), 400

        nuevo_negocio = Negocio(
            nombre_negocio=data.get('nombre_negocio'), # Según tu modelo: nombre_negocio
            categoria=data.get('tipoNegocio'),        # Según tu modelo: categoria
            descripcion=data.get('descripcion'),
            direccion=data.get('direccion'),
            ciudad_id=int(data.get('ciudad_id')),
            telefono=data.get('telefono'),
            # Si tu modelo Negocio no tiene estos campos aún, ignóralos o agrégalos
            usuario_id=current_user.id_usuario        # Según tu modelo: usuario_id
        )
        
        db.session.add(nuevo_negocio)
        db.session.commit()
        
        logger.info("✅ Negocio guardado exitosamente en la DB")
        return jsonify({"message": "Negocio registrado con éxito"}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error al registrar: {str(e)}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500