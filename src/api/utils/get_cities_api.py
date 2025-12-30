from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para obtener ciudades
get_cities_bp = Blueprint('get_cities_bp', __name__)

@get_cities_bp.route('/get_cities', methods=['POST'])
@login_required
def obtener_nombre_ciudades():
    """
    API para buscar ciudades por nombre o ID.
    """
    logger.info("Procesando solicitud POST para obtener ciudades.")

    termino = request.args.get('q', '').strip()
    id_ciudad = request.args.get('id', '').strip()

    try:
        # Búsqueda por ID
        if id_ciudad:
            if not id_ciudad.isdigit():
                logger.warning("El ID proporcionado no es un número.")
                return jsonify({"error": "El ID debe ser un número"}), 400

            ciudad = Colombia.query.filter_by(id=id_ciudad).first()
            if ciudad:
                logger.info(f"Ciudad encontrada: ID {ciudad.id}, Nombre {ciudad.ciudad_nombre}.")
                return jsonify({"id": ciudad.id, "ciudad_nombre": ciudad.ciudad_nombre}), 200
            else:
                logger.warning("Ciudad no encontrada para el ID proporcionado.")
                return jsonify({"error": "Ciudad no encontrada"}), 404

        # Búsqueda por nombre
        if termino:
            logger.debug(f"Buscando ciudades con el término: {termino}")
            ciudades = Colombia.query.filter(
                Colombia.ciudad_nombre.ilike(f"%{termino}%")
            ).limit(10).all()

            resultados = [ciudad.ciudad_nombre for ciudad in ciudades]
            logger.info(f"Ciudades encontradas: {resultados}")
            return jsonify(resultados), 200

        # Sin parámetros válidos
        logger.warning("Solicitud inválida: falta un término o ID para la búsqueda.")
        return jsonify({"error": "Se requiere un término o ID"}), 400

    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos: {e}")
        return jsonify({"error": "Error al consultar la base de datos"}), 500

    except Exception as e:
        logger.exception("Error interno del servidor.")
        return jsonify({"error": "Error interno del servidor"}), 500
