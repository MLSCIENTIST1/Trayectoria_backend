from src.models.database import db
from src.models.usuarios import Usuario
from src.models.colombia import Colombia  # <-- Asegúrate de importar tu modelo
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

# Configuración del Logger para ver todo en los logs de Render
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Blueprint
get_cities_bp = Blueprint('get_cities_bp', __name__)

@get_cities_bp.route('/ciudades', methods=['GET']) # <-- Cambiado a GET y ruta coherente con JS
# @login_required # <-- Sugerencia: Comenta esto temporalmente para probar si el error es de sesión
def obtener_nombre_ciudades():
    """
    API para buscar ciudades por nombre o ID.
    """
    logger.info("========================================")
    logger.info("🚀 INICIO DE SOLICITUD: obtener_nombre_ciudades")
    
    # Depuración de parámetros recibidos
    termino = request.args.get('q', '').strip()
    id_ciudad = request.args.get('id', '').strip()
    
    logger.debug(f"📥 Parámetros recibidos -> q (término): '{termino}', id: '{id_ciudad}'")

    try:
        # 1. Búsqueda por ID
        if id_ciudad:
            logger.debug(f"🔍 Buscando ciudad por ID: {id_ciudad}")
            if not id_ciudad.isdigit():
                logger.warning(f"❌ ID no numérico: {id_ciudad}")
                return jsonify({"error": "El ID debe ser un número"}), 400

            ciudad = Colombia.query.filter_by(id=id_ciudad).first()
            if ciudad:
                logger.info(f"✅ Ciudad encontrada: {ciudad.ciudad_nombre}")
                return jsonify({"id": ciudad.id, "ciudad_nombre": ciudad.ciudad_nombre}), 200
            else:
                logger.warning(f"⚠️ No se encontró ciudad con ID: {id_ciudad}")
                return jsonify({"error": "Ciudad no encontrada"}), 404

        # 2. Búsqueda por nombre (Término vacío trae algunas por defecto si q está vacío)
        logger.debug(f"🔍 Buscando ciudades que coincidan con: '{termino}'")
        
        # Si no hay término, traemos las primeras 20 para llenar el select inicial
        query = Colombia.query
        if termino:
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        ciudades = query.limit(20).all()
        
        # Mapeo de resultados para que el JS reciba un objeto claro
        resultados = [{"id": c.id, "nombre": c.ciudad_nombre} for c in ciudades]
        
        logger.info(f"📊 Ciudades encontradas en DB: {len(resultados)}")
        return jsonify(resultados), 200

    except SQLAlchemyError as e:
        logger.error(f"❌ Error de SQLAlchemy: {str(e)}")
        return jsonify({"error": "Error al consultar la base de datos", "details": str(e)}), 500

    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500