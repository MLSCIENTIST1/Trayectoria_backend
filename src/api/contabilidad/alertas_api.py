from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required, current_user
from src.models.database import db
from src.models.colombia_data.contabilidad.operaciones import AlertaOperativa
from datetime import datetime
import traceback

alertas_api_bp = Blueprint('alertas_service', __name__)

def get_auth_user_id():
    """Helper para extraer ID de usuario desde Header o Sesión"""
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
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "No autorizado"}), 401

    try:
        # Traemos todas las alertas del negocio visibles para este usuario
        alertas = AlertaOperativa.query.filter_by(
            negocio_id=negocio_id,
            usuario_id=user_id
        ).order_by(AlertaOperativa.completada.asc(), AlertaOperativa.fecha_programada.asc()).all()
        
        # Serialización manual por si el modelo no tiene to_dict actualizado
        data_list = []
        for a in alertas:
            data_list.append({
                "id_alerta": a.id_alerta,
                "tarea": a.tarea,
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
        print(f"Error GET Alertas: {traceback.format_exc()}")
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
        
        # Procesar fecha desde el frontend (ISO 8601)
        fecha_str = data.get('fecha')
        fecha_obj = datetime.fromisoformat(fecha_str.replace('Z', '+00:00')) if fecha_str else datetime.utcnow()

        nueva_alerta = AlertaOperativa(
            negocio_id=int(data.get('negocio_id')),
            usuario_id=user_id,
            tarea=data.get('tarea'),
            fecha_programada=fecha_obj,
            prioridad=data.get('prioridad', 'MEDIA').upper()
        )
        
        db.session.add(nueva_alerta)
        db.session.commit()
        return jsonify({"success": True, "message": "Alerta programada correctamente"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error POST Alerta: {traceback.format_exc()}")
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
        alerta = AlertaOperativa.query.filter_by(
            id_alerta=id_alerta, 
            usuario_id=user_id
        ).first()
        
        if not alerta:
            return jsonify({"success": False, "message": "Alerta no encontrada"}), 404
        
        if request.method == 'PATCH':
            alerta.completada = not alerta.completada
            msg = "Estado actualizado"
        else:
            db.session.delete(alerta)
            msg = "Alerta eliminada"
            
        db.session.commit()
        return jsonify({"success": True, "message": msg}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500