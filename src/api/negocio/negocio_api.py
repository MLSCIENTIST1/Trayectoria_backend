import logging
import sys
import traceback
from flask import Blueprint, jsonify, request, make_response
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
@cross_origin(supports_credentials=True) # Reforzamos credentials aquí también
def get_ciudades():
    """Retorna ciudades para el autocompletado"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        termino = request.args.get('q', '').strip()
        
        # Lógica de filtrado optimizada
        query = Colombia.query.with_entities(Colombia.ciudad_id, Colombia.ciudad_nombre)
        if termino:
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        ciudades_db = query.limit(15).all()
        resultado = [{"id": c.ciudad_id, "nombre": c.ciudad_nombre} for c in ciudades_db]
        
        return jsonify(resultado), 200

    except Exception as e:
        logger.error(f"🔥 ERROR en /ciudades: {str(e)}")
        return jsonify({"error": "Fallo en la consulta", "details": str(e)}), 500

@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True) # VITAL para que el 401 no bloquee el navegador
@login_required 
def registrar_negocio():
    """Registra un nuevo negocio vinculado al usuario logueado"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    logger.info("--- [LOG INICIO: POST /api/registrar_negocio] ---")
    
    try:
        data = request.get_json()
        
        # Log de seguridad para verificar quién intenta registrar
        logger.info(f"👤 Intento de registro por: {current_user.correo} (ID: {current_user.id_usuario})")

        # 1. Validación de campos obligatorios (Sincronizado con nombres del Frontend)
        nombre_negocio = data.get('nombre_negocio')
        ciudad_id = data.get('ciudad_id')

        if not nombre_negocio or not ciudad_id:
            logger.warning(f"❌ VALIDACIÓN FALLIDA: Datos incompletos. Recibido: {data}")
            return jsonify({"error": "El nombre del negocio y la ciudad son obligatorios"}), 400

        # 2. Creación del objeto
        nuevo_negocio = Negocio(
            nombre_negocio=nombre_negocio,
            categoria=data.get('tipoNegocio'), 
            descripcion=data.get('descripcion'),
            direccion=data.get('direccion'),
            ciudad_id=int(ciudad_id),
            telefono=data.get('telefono'),
            usuario_id=current_user.id_usuario 
        )
        
        # 3. Persistencia
        db.session.add(nuevo_negocio)
        db.session.commit()
        
        # Obtener el ID generado (id_negocio o id según tu modelo)
        negocio_id = getattr(nuevo_negocio, 'id_negocio', getattr(nuevo_negocio, 'id', 'N/A'))
        
        logger.info(f"✨ ÉXITO: Negocio '{nombre_negocio}' guardado con ID {negocio_id}")
        
        return jsonify({
            "status": "success",
            "message": "Negocio registrado correctamente",
            "id": negocio_id
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"🔥 ERROR FATAL en /registrar_negocio: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "No se pudo guardar el negocio", "details": str(e)}), 500