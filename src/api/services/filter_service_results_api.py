from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import or_

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para resultados de filtro de servicio
filter_service_results_bp = Blueprint('filter_service_results_bp', __name__)

@filter_service_results_bp.route('/filter_service_results', methods=['POST'])
@login_required
def resultado_filtro_servicio():
    """
    API para filtrar servicios con base en la ciudad y la labor.
    Devuelve los servicios encontrados y los detalles del usuario asociado en formato JSON.
    """
    logger.info(f"Procesando solicitud POST para filtrar servicios del usuario {current_user.id_usuario}.")

    try:
        # Obtener parámetros de la solicitud
        ciudad = request.args.get('city')
        labor = request.args.get('job')

        logger.debug(f"Parámetros de búsqueda - Ciudad: {ciudad}, Labor: {labor}")

        # Construir consulta con filtros dinámicos
        query_servicios = Servicio.query
        condiciones = []

        if ciudad:
            condiciones.append(Servicio.categoria.ilike(f"%{ciudad}%"))
        if labor:
            condiciones.append(Servicio.nombre_servicio.ilike(f"%{labor}%"))

        if condiciones:
            query_servicios = query_servicios.filter(or_(*condiciones))

        servicios = query_servicios.all()

        # Validar si no hay resultados
        if not servicios:
            logger.info("No se encontraron servicios para los criterios proporcionados.")
            return jsonify({"mensaje": "No se encontraron servicios para los criterios proporcionados"}), 404

        # Construir resultados a devolver
        resultados = [
            {
                "servicio_id": servicio.id_servicio,
                "nombre_servicio": servicio.nombre_servicio,
                "descripcion": servicio.descripcion,
                "categoria": servicio.categoria,
                "precio": servicio.precio,
                "service_active": servicio.service_active,
                "datos_usuario": {
                    "usuario_id": servicio.id_usuario,
                    "nombre": Usuario.query.get(servicio.id_usuario).nombre,
                    "apellidos": Usuario.query.get(servicio.id_usuario).apellidos,
                    "correo": Usuario.query.get(servicio.id_usuario).correo,
                    "celular": Usuario.query.get(servicio.id_usuario).celular,
                    "ciudad": Usuario.query.get(servicio.id_usuario).ciudad,
                    "labor": Usuario.query.get(servicio.id_usuario).labor,
                    "calificaciones": [
                        {
                            "calificacion1": c.calificacion_recived_contratado1,
                            "calificacion2": c.calificacion_recived_contratado2,
                            "calificacion3": c.calificacion_recived_contratado3
                        }
                        for c in ServiceRatings.query.filter_by(servicio_id=servicio.id_servicio).all()
                    ]
                }
            }
            for servicio in servicios
        ]

        logger.info(f"Servicios encontrados y procesados con éxito. Total: {len(servicios)}")
        return jsonify({"resultados": resultados}), 200

    except Exception as e:
        logger.exception(f"Error al realizar la consulta: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
