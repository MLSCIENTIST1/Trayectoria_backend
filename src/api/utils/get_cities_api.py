from src.models.database import db
from src.models.usuarios import Usuario
# CORRECCIÓN: El archivo se llama colombia_data y la clase Colombia
from src.models.colombia_data import Colombia  
import logging
import sys
from flask import Blueprint, jsonify, request
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

# --- CONFIGURACIÓN DE LOGS PARA RENDER ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Blueprint
get_cities_bp = Blueprint('get_cities_bp', __name__)

@get_cities_bp.route('/ciudades', methods=['GET'])
def obtener_nombre_ciudades():
    """
    API para buscar ciudades por nombre o ID. 
    Ajustada para usar 'ciudad_id' como llave primaria según colombia_data.py
    """
    logger.info("========================================")
    logger.info("🚀 SOLICITUD RECIBIDA: /api/ciudades")
    
    # 1. Obtener parámetros de la URL
    termino = request.args.get('q', '').strip()
    id_param = request.args.get('id', '').strip()
    
    logger.debug(f"📥 Query Params -> q: '{termino}', id: '{id_param}'")

    try:
        # --- CASO A: Búsqueda por ID específico ---
        if id_param:
            if not id_param.isdigit():
                return jsonify({"error": "El ID debe ser un número"}), 400

            # CORRECCIÓN: Tu modelo usa ciudad_id, no id
            ciudad = Colombia.query.filter_by(ciudad_id=int(id_param)).first()
            if ciudad:
                logger.info(f"✅ Ciudad encontrada: {ciudad.ciudad_nombre}")
                return jsonify({"id": ciudad.ciudad_id, "nombre": ciudad.ciudad_nombre}), 200
            else:
                return jsonify({"error": "Ciudad no encontrada"}), 404

        # --- CASO B: Búsqueda por Nombre o Carga Inicial ---
        query = Colombia.query
        if termino:
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        # Ordenamos y limitamos resultados
        ciudades = query.order_by(Colombia.ciudad_nombre.asc()).limit(50).all()
        
        # CORRECCIÓN: Mapeo usando ciudad_id y ciudad_nombre
        resultados = [
            {
                "id": c.ciudad_id, 
                "nombre": c.ciudad_nombre
            } for c in ciudades
        ]
        
        logger.info(f"📊 Ciudades recuperadas: {len(resultados)}")
        return jsonify(resultados), 200

    except SQLAlchemyError as e:
        logger.error(f"❌ ERROR SQLALCHEMY: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error en la base de datos"}), 500

    except Exception as e:
        logger.error(f"❌ ERROR INESPERADO: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500