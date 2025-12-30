import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from src.models.database import db
from src.models.usuarios import Usuario  

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para el autocompletado de servicios
search_service_autocomplete_bp = Blueprint('search_service_autocomplete_bp', __name__)

@search_service_autocomplete_bp.route('/search_service_autocomplete', methods=['GET'])
@login_required
def obtener_nombre_servicios():
    """
    Endpoint para buscar servicios de forma dinámica (autocompletado).
    """
    logger.debug('Blueprint cargado exitosamente.')

    # Obtener el término ingresado por el usuario
    termino = request.args.get('q', '').strip()

    # Validar si el término está vacío
    if not termino:
        logger.warning("No se proporcionó un término de búsqueda.")
        return jsonify([])

    try:
        # Realizar la consulta filtrando servicios cuyo nombre coincida parcialmente
        servicios = Servicio.query.filter(
            Servicio.nombre_servicio.ilike(f"%{termino}%")
        ).limit(10).all()  # Limitar a 10 resultados

        # Extraer solo los nombres de los servicios para el autocompletado
        resultados = [servicio.nombre_servicio for servicio in servicios]

        # Registrar los resultados en los logs para depuración
        logger.debug(f"Término buscado: {termino}")
        logger.debug(f"Servicios encontrados: {resultados}")

        return jsonify(resultados)

    except SQLAlchemyError as e:
        # Manejar errores de base de datos y registrar en los logs
        logger.error(f"Error al buscar servicios en la base de datos: {e}")
        return jsonify({"error": "Error al buscar servicios"}), 500

    except Exception as e:
        # Manejar errores generales y registrar en los logs
        logger.error(f"Error inesperado al buscar servicios: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
