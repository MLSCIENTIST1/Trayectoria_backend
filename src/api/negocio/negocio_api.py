import logging
import sys
import traceback
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_cors import cross_origin

# Importaciones ajustadas
from src.models.colombia_data.negocio import Negocio
from src.models.colombia_data.colombia_data import Colombia 
from src.models.database import db

# Configuración de logs extrema para Render
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime) - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

negocio_api_bp = Blueprint('negocio_api_bp', __name__)

@negocio_api_bp.before_request
def debug_before_request():
    """Este log aparecerá CUALQUIER vez que se intente tocar una ruta de este Blueprint"""
    print(f"\n📡 [BLUEPRINT NEGOCIO] Intento de acceso a: {request.path} [{request.method}]")

@negocio_api_bp.route('/ciudades', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_ciudades():
    """Retorna ciudades para el autocompletado con logs profundos"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    print("--- [LOG INICIO: GET /ciudades] ---")
    try:
        # 1. Inspección de la Request
        termino = request.args.get('q', '').strip()
        print(f"DEBUG: Headers recibidos: {dict(request.headers)}")
        print(f"DEBUG: Parámetro de búsqueda 'q': '{termino}'")
        
        # 2. Diagnóstico de la Base de Datos
        print("DEBUG: Verificando conexión a tabla 'colombia'...")
        try:
            total_db = db.session.query(Colombia).count()
            print(f"✅ DB STATUS: La tabla 'colombia' es accesible. Total registros: {total_db}")
        except Exception as e_db:
            print(f"❌ DB ERROR: No se puede leer la tabla 'colombia'. ¿Existe la tabla?")
            print(f"DETALLE ERROR DB: {str(e_db)}")
            return jsonify({"error": "Error de acceso a DB", "details": str(e_db)}), 500

        # 3. Ejecución de la Query
        print(f"DEBUG: Ejecutando Query con filtro ILIKE '%{termino}%'...")
        query = Colombia.query.with_entities(Colombia.ciudad_id, Colombia.ciudad_nombre)
        
        if termino:
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        ciudades_db = query.limit(20).all()
        print(f"✅ QUERY EXITOSA: Se recuperaron {len(ciudades_db)} filas de la DB.")

        # 4. Formateo y Respuesta
        resultado = [
            {"id": c.ciudad_id, "nombre": c.ciudad_nombre} 
            for c in ciudades_db
        ]
        
        # Imprimimos los 2 primeros resultados para ver si el formato es correcto
        if resultado:
            print(f"DEBUG: Ejemplo de datos encontrados: {resultado[:2]}")
        else:
            print("⚠️ ADVERTENCIA: La query no devolvió ningún resultado para ese término.")

        print("--- [LOG FIN: SOLICITUD PROCESADA] ---\n")
        return jsonify(resultado), 200

    except Exception as e:
        print(f"❌ ERROR CRÍTICO en get_ciudades: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500

@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin()
@login_required
def registrar_negocio():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    print("\n--- [LOG INICIO: POST /registrar_negocio] ---")
    
    try:
        data = request.get_json()
        print(f"DEBUG: Payload recibido: {data}")
        print(f"DEBUG: Usuario autenticado: {current_user.id_usuario if current_user else 'ANÓNIMO'}")

        # 1. Validaciones
        if not data:
            print("❌ ERROR: Request Body vacío")
            return jsonify({"error": "No se enviaron datos"}), 400
            
        if not data.get('ciudad_id'):
            print("❌ ERROR: El campo 'ciudad_id' es obligatorio")
            return jsonify({"error": "Falta ciudad_id"}), 400

        # 2. Creación del Registro
        print("DEBUG: Mapeando datos al modelo Negocio...")
        nuevo_negocio = Negocio(
            nombre_negocio=data.get('nombre_negocio'),
            categoria=data.get('tipoNegocio'), 
            descripcion=data.get('descripcion'),
            direccion=data.get('direccion'),
            ciudad_id=int(data.get('ciudad_id')),
            telefono=data.get('telefono'),
            usuario_id=current_user.id_usuario 
        )
        
        # 3. Commit
        db.session.add(nuevo_negocio)
        db.session.commit()
        
        print(f"✅ REGISTRO EXITOSO: Negocio ID {nuevo_negocio.id} guardado.")
        print("--- [LOG FIN: POST FINALIZADO] ---\n")
        
        return jsonify({"message": "Negocio registrado", "id": nuevo_negocio.id}), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR EN POST: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Error interno: {str(e)}"}), 500