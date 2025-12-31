from src.models.database import db
from src.models.usuarios import Usuario
from src.models.colombia import Colombia  # Asegúrate de que este modelo exista y sea correcto
import logging
import sys
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

# --- CONFIGURACIÓN DE LOGS PARA RENDER ---
# Configuramos el logger para que emita a la salida estándar (visible en consola de Render)
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
# @login_required  # Descomenta una vez confirmes que la conexión funciona sin seguridad
def obtener_nombre_ciudades():
    """
    API para buscar ciudades por nombre o ID. 
    Soporta carga inicial (sin parámetros) y búsqueda filtrada.
    """
    logger.info("========================================")
    logger.info("🚀 SOLICITUD RECIBIDA: /api/ciudades")
    
    # 1. Obtener parámetros de la URL
    termino = request.args.get('q', '').strip()
    id_ciudad = request.args.get('id', '').strip()
    
    logger.debug(f"📥 Query Params -> q: '{termino}', id: '{id_ciudad}'")
    logger.debug(f"👤 Usuario Autenticado: {current_user.is_authenticated}")

    try:
        # --- CASO A: Búsqueda por ID específico ---
        if id_ciudad:
            logger.debug(f"🔍 Filtrando por ID: {id_ciudad}")
            if not id_ciudad.isdigit():
                logger.warning(f"❌ ID inválido (no numérico): {id_ciudad}")
                return jsonify({"error": "El ID debe ser un número"}), 400

            ciudad = Colombia.query.get(id_ciudad) # Uso de .get() para búsqueda directa por PK
            if ciudad:
                logger.info(f"✅ Ciudad encontrada por ID: {ciudad.ciudad_nombre}")
                return jsonify({"id": ciudad.id, "nombre": ciudad.ciudad_nombre}), 200
            else:
                logger.warning(f"⚠️ No se encontró ciudad con ID: {id_ciudad}")
                return jsonify({"error": "Ciudad no encontrada"}), 404

        # --- CASO B: Búsqueda por Nombre o Carga Inicial ---
        logger.debug(f"🔍 Consultando lista de ciudades (Filtro: '{termino}')")
        
        query = Colombia.query
        if termino:
            # Búsqueda parcial (LIKE) insensible a mayúsculas
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        # Ordenamos alfabéticamente y limitamos para no saturar el frontend
        ciudades = query.order_by(Colombia.ciudad_nombre.asc()).limit(50).all()
        
        # IMPORTANTE: El JS espera 'id' y 'nombre'
        resultados = [{"id": c.id, "nombre": c.ciudad_nombre} for c in ciudades]
        
        logger.info(f"📊 Ciudades recuperadas: {len(resultados)}")
        
        # Log para verificar el formato de salida
        if resultados:
            logger.debug(f"📝 Ejemplo del primer resultado: {resultados[0]}")

        return jsonify(resultados), 200

    except SQLAlchemyError as e:
        logger.error(f"❌ ERROR SQLALCHEMY: {str(e)}")
        db.session.rollback() # Limpiar la sesión tras el error
        return jsonify({"error": "Error en la base de datos", "details": str(e)}), 500

    except Exception as e:
        logger.error(f"❌ ERROR INESPERADO: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500