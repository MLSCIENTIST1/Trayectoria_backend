from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required, current_user
from src.models.database import db
from src.models.colombia_data.contabilidad.operaciones import AlertaOperativa

alertas_api_bp = Blueprint('alertas_service', __name__)

# 1. OBTENER ALERTAS DEL NEGOCIO
@alertas_api_bp.route('/control/alertas/<int:negocio_id>', methods=['GET'])
@cross_origin(supports_credentials=True)
@login_required
def obtener_alertas(negocio_id):
    try:
        # Traemos alertas no completadas primero
        alertas = AlertaOperativa.query.filter_by(
            negocio_id=negocio_id,
            usuario_id=current_user.id_usuario
        ).order_by(AlertaOperativa.completada.asc(), AlertaOperativa.fecha_programada.asc()).all()
        
        return jsonify({
            "success": True,
            "data": [a.to_dict() for a in alertas]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# 2. GUARDAR NUEVA ALERTA
@alertas_api_bp.route('/control/alertas/guardar', methods=['POST'])
@cross_origin(supports_credentials=True)
@login_required
def guardar_alerta():
    try:
        data = request.get_json()
        nueva_alerta = AlertaOperativa(
            negocio_id=int(data.get('negocio_id')),
            usuario_id=current_user.id_usuario,
            tarea=data.get('tarea'),
            fecha_programada=data.get('fecha'), # ISO format desde JS
            prioridad=data.get('prioridad', 'MEDIA')
        )
        db.session.add(nueva_alerta)
        db.session.commit()
        return jsonify({"success": True, "message": "Alerta programada"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# 3. MARCAR COMO COMPLETADA / ELIMINAR
@alertas_api_bp.route('/control/alertas/check/<int:id_alerta>', methods=['PATCH', 'DELETE'])
@cross_origin(supports_credentials=True)
@login_required
def gestionar_alerta(id_alerta):
    try:
        alerta = AlertaOperativa.query.filter_by(
            id_alerta=id_alerta, 
            usuario_id=current_user.id_usuario
        ).first()
        
        if not alerta:
            return jsonify({"success": False, "message": "Alerta no encontrada"}), 404
        
        if request.method == 'PATCH':
            alerta.completada = not alerta.completada
        else:
            db.session.delete(alerta)
            
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500