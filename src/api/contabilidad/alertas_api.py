"""
BizFlow Studio - API de Alertas
Usa modelo AlertaOperativa
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.database import db
from src.models.colombia_data.contabilidad.operaciones_y_catalogo import AlertaOperativa
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

alertas_api_bp = Blueprint('alertas_api_bp', __name__)


@alertas_api_bp.route('/control/alertas/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_alertas(negocio_id):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        alertas = AlertaOperativa.query.filter_by(negocio_id=negocio_id)\
            .order_by(AlertaOperativa.completada.asc(), AlertaOperativa.fecha_programada.asc())\
            .all()
        
        return jsonify({"success": True, "data": [a.to_dict() for a in alertas]}), 200
    except Exception as e:
        logger.error(f"Error obteniendo alertas: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@alertas_api_bp.route('/control/alertas', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def crear_alerta():
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        data = request.get_json() or {}
        
        fecha_programada = datetime.utcnow()
        if data.get('fecha_programada'):
            try:
                fecha_programada = datetime.fromisoformat(data['fecha_programada'].replace('Z', '+00:00'))
            except:
                fecha_programada = datetime.strptime(data['fecha_programada'], '%Y-%m-%dT%H:%M')
        
        nueva = AlertaOperativa(
            negocio_id=int(data['negocio_id']),
            usuario_id=int(data.get('usuario_id', 0)),
            tarea=data['tarea'],
            tipo=data.get('categoria', 'GENERAL'),
            prioridad=data.get('prioridad', 'MEDIA').upper(),
            fecha_programada=fecha_programada
        )
        
        db.session.add(nueva)
        db.session.commit()
        
        return jsonify({"success": True, "data": nueva.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@alertas_api_bp.route('/control/alertas/<int:id_alerta>', methods=['PUT', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def actualizar_alerta(id_alerta):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        alerta = AlertaOperativa.query.get(id_alerta)
        if not alerta:
            return jsonify({"success": False, "message": "No encontrada"}), 404
        
        data = request.get_json() or {}
        
        if 'completada' in data:
            if data['completada']:
                alerta.marcar_completada()
            else:
                alerta.completada = False
                alerta.fecha_completada = None
        
        if 'tarea' in data:
            alerta.tarea = data['tarea']
        if 'prioridad' in data:
            alerta.prioridad = data['prioridad'].upper()
        
        db.session.commit()
        return jsonify({"success": True, "data": alerta.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@alertas_api_bp.route('/control/alertas/<int:id_alerta>', methods=['DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def eliminar_alerta(id_alerta):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    
    try:
        alerta = AlertaOperativa.query.get(id_alerta)
        if not alerta:
            return jsonify({"success": False, "message": "No encontrada"}), 404
        
        db.session.delete(alerta)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500