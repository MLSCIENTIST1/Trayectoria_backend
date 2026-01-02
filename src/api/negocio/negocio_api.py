import logging
import sys
import traceback
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_cors import cross_origin

# Importaciones de modelos
from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.colombia_data import Colombia 
from src.models.database import db

# --- CONFIGURACIÓN DE LOGS PARA RENDER ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
if not logger.handlers:
    logger.addHandler(handler)

# Nombre único para el Blueprint
negocio_api_bp = Blueprint('negocio_api_bp', __name__)

@negocio_api_bp.before_request
def debug_incoming_request():
    """Intercepta cada petición para debug en consola de Render"""
    logger.debug(f"📡 [DEBUG BLUEPRINT] Petición entrante: {request.method} {request.path}")

@negocio_api_bp.route('/ciudades', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_ciudades():
    """Retorna ciudades para el autocompletado"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    logger.info("--- [LOG INICIO: GET /api/ciudades] ---")
    try:
        # 1. Obtención de parámetros
        termino = request.args.get('q', '').strip()
        logger.debug(f"🔍 BUSQUEDA: Término recibido = '{termino}'")
        
        # 2. Diagnóstico de Salud de la DB (Mapeadores)
        # Si esto falla aquí, el problema es una relación rota en models/
        total_filas = db.session.query(Colombia).count()
        logger.debug(f"📊 DB STATUS: Tabla 'colombia' accesible. Registros: {total_filas}")

        # 3. Lógica de filtrado
        query = Colombia.query.with_entities(Colombia.ciudad_id, Colombia.ciudad_nombre)
        
        if termino:
            # ilike para búsqueda insensible a mayúsculas en Postgres
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        ciudades_db = query.limit(15).all()
        
        # 4. Construcción de respuesta
        resultado = [
            {"id": c.ciudad_id, "nombre": c.ciudad_nombre} 
            for c in ciudades_db
        ]
        
        logger.info(f"✅ ÉXITO: Enviando {len(resultado)} ciudades.")
        return jsonify(resultado), 200

    except Exception as e:
        logger.error(f"🔥 ERROR en /ciudades: {str(e)}")
        # Imprime el rastro completo en los logs de Render
        traceback.print_exc()
        return jsonify({"error": "Fallo en la consulta de ciudades", "details": str(e)}), 500

@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin()
@login_required # Redirigirá a 'api.init_sesion_bp.ingreso' si falla
def registrar_negocio():
    """Registra un nuevo negocio vinculado al usuario logueado"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    logger.info("--- [LOG INICIO: POST /api/registrar_negocio] ---")
    
    try:
        data = request.get_json()
        
        # Flask-Login ya verifica esto con @login_required, 
        # pero añadimos un log para mayor claridad
        logger.debug(f"👤 USUARIO: ID {current_user.id_usuario} ({current_user.correo})")

        # 1. Validación de campos obligatorios
        if not data or not data.get('ciudad_id') or not data.get('nombre_negocio'):
            logger.warning("❌ VALIDACIÓN FALLIDA: Datos incompletos.")
            return jsonify({"error": "Nombre y ciudad son obligatorios"}), 400

        # 2. Creación del objeto (Sincronizado con el modelo Negocio)
        nuevo_negocio = Negocio(
            nombre_negocio=data.get('nombre_negocio'),
            categoria=data.get('tipoNegocio'), 
            descripcion=data.get('descripcion'),
            direccion=data.get('direccion'),
            ciudad_id=int(data.get('ciudad_id')),
            telefono=data.get('telefono'),
            usuario_id=current_user.id_usuario # Usando id_usuario corregido
        )
        
        # 3. Persistencia
        db.session.add(nuevo_negocio)
        db.session.commit()
        
        logger.info(f"✨ ÉXITO: Negocio guardado con ID {nuevo_negocio.id_negocio if hasattr(nuevo_negocio, 'id_negocio') else nuevo_negocio.id}")
        
        return jsonify({
            "status": "success",
            "message": "Negocio registrado correctamente"
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"🔥 ERROR en /registrar_negocio: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Error al procesar el registro", "details": str(e)}), 500