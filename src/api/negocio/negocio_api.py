import logging
import sys
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_cors import cross_origin

# Importaciones ajustadas
from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.colombia_data import Colombia 
from src.models.database import db

# Configuración de logs para Render (Salida forzada a stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

negocio_api_bp = Blueprint('negocio_api_bp', __name__)

@negocio_api_bp.route('/ciudades', methods=['GET'])
@cross_origin()
def get_ciudades():
    """Retorna ciudades para el autocompletado con logs profundos"""
    print("\n--- [LOG INICIO: GET /api/ciudades] ---")
    try:
        # 1. Verificar parámetros
        termino = request.args.get('q', '').strip()
        print(f"DEBUG: Buscando ciudades con término: '{termino}'")
        
        # 2. Verificar estado de la tabla Colombia
        try:
            total_ciudades = Colombia.query.count()
            print(f"DEBUG: Conexión DB OK. Registros totales en tabla 'colombia': {total_ciudades}")
        except Exception as db_err:
            print(f"❌ ERROR DB: La tabla 'colombia' no parece existir o no es accesible: {str(db_err)}")
            return jsonify({"error": "Error de base de datos", "details": str(db_err)}), 500

        # 3. Construir query
        query = Colombia.query.with_entities(Colombia.ciudad_id, Colombia.ciudad_nombre)
        
        if termino:
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        ciudades_db = query.limit(20).all()
        print(f"DEBUG: Resultados encontrados para '{termino}': {len(ciudades_db)}")

        # 4. Formatear resultados
        resultado = [
            {"id": c.ciudad_id, "nombre": c.ciudad_nombre} 
            for c in ciudades_db
        ]
        
        print(f"DEBUG: JSON de salida: {resultado[:3]}... (truncado)")
        print("--- [LOG FIN: EXITOSO] ---\n")
        return jsonify(resultado), 200

    except Exception as e:
        print(f"❌ ERROR CRÍTICO en get_ciudades: {str(e)}")
        return jsonify({"error": "Error interno", "details": str(e)}), 500

@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin()
@login_required
def registrar_negocio():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    print("\n--- [LOG INICIO: POST /api/registrar_negocio] ---")
    data = request.get_json()
    print(f"DEBUG: Datos recibidos del frontend: {data}")

    try:
        # 1. Validaciones básicas
        if not data:
            print("❌ ERROR: No se recibieron datos (JSON vacío)")
            return jsonify({"error": "No se enviaron datos"}), 400
            
        if not data.get('ciudad_id'):
            print("❌ ERROR: ciudad_id ausente en el JSON")
            return jsonify({"error": "Debe seleccionar una ciudad válida"}), 400

        # 2. Crear instancia del modelo
        print(f"DEBUG: Intentando guardar negocio para usuario ID: {current_user.id_usuario}")
        nuevo_negocio = Negocio(
            nombre_negocio=data.get('nombre_negocio'),
            categoria=data.get('tipoNegocio'), 
            descripcion=data.get('descripcion'),
            direccion=data.get('direccion'),
            ciudad_id=int(data.get('ciudad_id')),
            telefono=data.get('telefono'),
            usuario_id=current_user.id_usuario 
        )
        
        # 3. Persistencia
        db.session.add(nuevo_negocio)
        db.session.commit()
        
        print(f"✅ ÉXITO: Negocio '{nuevo_negocio.nombre_negocio}' creado con ID: {nuevo_negocio.id}")
        print("--- [LOG FIN: REGISTRO COMPLETADO] ---\n")
        
        return jsonify({"message": "Negocio registrado con éxito", "id": nuevo_negocio.id}), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR AL REGISTRAR NEGOCIO: {str(e)}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500