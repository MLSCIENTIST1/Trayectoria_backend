from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required, current_user
from src.models.database import db
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import AlertaOperativa
from datetime import datetime
import traceback

alertas_api_bp = Blueprint('alertas_service', __name__)

def get_auth_user_id():
    """
    Helper centralizado para obtener la identidad del usuario.
    Busca primero en el Header personalizado (X-User-ID) para el POS,
    y luego en la sesión activa de Flask-Login.
    """
    user_id = request.headers.get('X-User-ID')
    if user_id and user_id.isdigit():
        return int(user_id)
    if current_user.is_authenticated:
        return current_user.id_usuario
    return None

# 1. OBTENER ALERTAS DEL NEGOCIO
@alertas_api_bp.route('/control/alertas/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_alertas(negocio_id):
    # Manejo de Pre-flight para CORS
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Identidad no válida o falta X-User-ID"}), 401

    try:
        # Filtrado por negocio_id y usuario_id para asegurar privacidad de datos
        alertas = AlertaOperativa.query.filter_by(
            negocio_id=negocio_id,
            usuario_id=user_id
        ).order_by(AlertaOperativa.completada.asc(), AlertaOperativa.fecha_programada.asc()).all()
        
        # Serialización robusta
        data_list = []
        for a in alertas:
            data_list.append({
                "id_alerta": a.id_alerta,
                "tarea": a.tarea, # Correcto: usamos 'tarea' del modelo
                "fecha_programada": a.fecha_programada.isoformat() if a.fecha_programada else None,
                "prioridad": a.prioridad,
                "completada": a.completada,
                "fecha_creacion": a.fecha_creacion.isoformat() if a.fecha_creacion else None
            })

        return jsonify({
            "success": True,
            "data": data_list
        }), 200
    except Exception as e:
        print(f"❌ Error GET Alertas: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500

# 2. GUARDAR NUEVA ALERTA
@alertas_api_bp.route('/control/alertas/guardar', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def guardar_alerta():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        data = request.get_json()
        
        # Procesar fecha: soporta ISO string desde JS o genera UTC actual
        fecha_str = data.get('fecha')
        if fecha_str:
            # Limpieza básica para compatibilidad de zona horaria
            fecha_obj = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        else:
            fecha_obj = datetime.utcnow()

        nueva_alerta = AlertaOperativa(
            negocio_id=int(data.get('negocio_id')),
            usuario_id=user_id,
            tarea=data.get('tarea'), # Aseguramos uso de 'tarea'
            fecha_programada=fecha_obj,
            prioridad=data.get('prioridad', 'MEDIA').upper()
        )
        
        db.session.add(nueva_alerta)
        db.session.commit()
        return jsonify({"success": True, "message": "Alerta programada correctamente"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error POST Alerta: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500

# 3. MARCAR COMO COMPLETADA / ELIMINAR
@alertas_api_bp.route('/control/alertas/check/<int:id_alerta>', methods=['PATCH', 'DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def gestionar_alerta(id_alerta):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        # Verificamos que la alerta pertenezca al usuario antes de modificarla
        alerta = AlertaOperativa.query.filter_by(
            id_alerta=id_alerta, 
            usuario_id=user_id
        ).first()
        
        if not alerta:
            return jsonify({"success": False, "message": "Alerta no encontrada o acceso denegado"}), 404
        
        if request.method == 'PATCH':
            alerta.completada = not alerta.completada
            msg = "Estado de tarea actualizado"
        else:
            db.session.delete(alerta)
            msg = "Alerta eliminada definitivamente"
            
        db.session.commit()
        return jsonify({"success": True, "message": msg}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500