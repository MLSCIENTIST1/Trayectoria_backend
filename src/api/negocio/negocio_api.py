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

# Nombre único para el Blueprint para evitar colisiones
negocio_api_bp = Blueprint('negocio_api_bp', __name__)

print("\n🚀 [SISTEMA] Módulo negocio_api.py cargado exitosamente.")

@negocio_api_bp.before_request
def debug_incoming_request():
    """Log de interceptación: Si el 404 persiste y esto no sale, el error es el ruteo central."""
    print(f"📡 [DEBUG BLUEPRINT] Petición entrante: {request.method} {request.path}")

@negocio_api_bp.route('/ciudades', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_ciudades():
    """Retorna ciudades para el autocompletado con logs profundos"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    print("\n--- [LOG INICIO: GET /api/ciudades] ---")
    try:
        # 1. Inspección de parámetros
        termino = request.args.get('q', '').strip()
        print(f"🔍 BUSQUEDA: Término recibido = '{termino}'")
        
        # 2. Diagnóstico de Salud de la DB
        print("🛠️ DB CHECK: Verificando tabla 'colombia'...")
        try:
            # Intento de conteo rápido para verificar existencia de tabla
            total_filas = db.session.query(Colombia).count()
            print(f"📊 DB OK: Tabla encontrada. Total registros disponibles: {total_filas}")
        except Exception as db_err:
            print(f"❌ DB ERROR CRÍTICO: No se pudo acceder a la tabla 'colombia'.")
            print(f"Detalle técnico: {str(db_err)}")
            return jsonify({"error": "Tabla no encontrada", "details": str(db_err)}), 500

        # 3. Ejecución de la lógica de negocio
        print(f"🧪 QUERY: Ejecutando filtro ILIKE para '{termino}'")
        query = Colombia.query.with_entities(Colombia.ciudad_id, Colombia.ciudad_nombre)
        
        if termino:
            # Filtrar por nombre ignorando mayúsculas/minúsculas
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        ciudades_db = query.limit(15).all()
        print(f"✅ QUERY EXITOSA: Se encontraron {len(ciudades_db)} coincidencias.")

        # 4. Respuesta
        resultado = [
            {"id": c.ciudad_id, "nombre": c.ciudad_nombre} 
            for c in ciudades_db
        ]
        
        if not resultado:
            print("⚠️ AVISO: La lista de resultados está vacía.")
        else:
            print(f"📦 DATA: Enviando {len(resultado)} ciudades al frontend.")

        print("--- [LOG FIN: GET /api/ciudades] ---\n")
        return jsonify(resultado), 200

    except Exception as e:
        print(f"🔥 ERROR FATAL en /ciudades: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Fallo interno", "details": str(e)}), 500

@negocio_api_bp.route('/registrar_negocio', methods=['POST', 'OPTIONS'])
@cross_origin()
@login_required
def registrar_negocio():
    """Registra un nuevo negocio vinculado al usuario logueado"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    print("\n--- [LOG INICIO: POST /api/registrar_negocio] ---")
    
    try:
        data = request.get_json()
        print(f"📥 PAYLOAD: {data}")
        
        if not current_user.is_authenticated:
            print("🚫 AUTH: Usuario no autenticado intentando registrar.")
            return jsonify({"error": "Sesión requerida"}), 401
            
        print(f"👤 USUARIO: ID {current_user.id_usuario} ({current_user.email})")

        # 1. Validación de campos obligatorios
        if not data or not data.get('ciudad_id') or not data.get('nombre_negocio'):
            print("❌ VALIDACIÓN: Faltan campos requeridos (nombre o ciudad_id)")
            return jsonify({"error": "Nombre y ciudad son obligatorios"}), 400

        # 2. Creación del objeto
        print("💾 DB: Mapeando datos al modelo Negocio...")
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
        
        print(f"✨ ÉXITO: Negocio guardado con ID {nuevo_negocio.id}")
        print("--- [LOG FIN: POST COMPLETADO] ---\n")
        
        return jsonify({
            "status": "success",
            "message": "Negocio registrado correctamente",
            "negocio_id": nuevo_negocio.id
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"🔥 ERROR FATAL en /registrar_negocio: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Error al guardar registro", "details": str(e)}), 500