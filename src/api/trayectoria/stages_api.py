"""
BizFlow Studio - Stages API
Endpoints para las 4 etapas de la trayectoria (E1-E4)
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from src.models.database import db
from src.models.trayectoria.user_stage_score import UserStageScore
import logging

logger = logging.getLogger(__name__)

stages_bp = Blueprint('stages_api', __name__)


# ==================== GET STAGES ====================

@stages_bp.route('/api/users/<int:user_id>/stages', methods=['GET'])
@login_required
def get_user_stages(user_id):
    """
    Obtiene las 4 etapas del usuario
    GET /api/users/123/stages
    
    Returns:
        [
            {
                "id": "e1",
                "numero": 1,
                "nombre": "Primer Contacto",
                "color": "#3b82f6",
                "score": 4.9,
                "visible": true,
                "metricas": [...]
            },
            ...
        ]
    """
    try:
        # Verificar acceso (usuario mismo o perfil público)
        if current_user.id_usuario != user_id:
            # Aquí podrías verificar si el perfil es público
            pass
        
        # Buscar etapas
        stages = UserStageScore.query.filter_by(usuario_id=user_id).order_by(UserStageScore.stage_number).all()
        
        # Si no existen, inicializarlas
        if not stages:
            UserStageScore.inicializar_etapas_usuario(user_id)
            stages = UserStageScore.query.filter_by(usuario_id=user_id).order_by(UserStageScore.stage_number).all()
        
        # Filtrar etapas privadas si no es el usuario
        if current_user.id_usuario != user_id:
            stages = [s for s in stages if s.is_public]
        
        return jsonify([stage.serialize() for stage in stages]), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo etapas del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo etapas"}), 500


# ==================== UPDATE STAGE VISIBILITY ====================

@stages_bp.route('/api/users/<int:user_id>/stages/<string:stage_id>/visibility', methods=['PATCH'])
@login_required
def update_stage_visibility(user_id, stage_id):
    """
    Actualiza la visibilidad de una etapa
    PATCH /api/users/123/stages/e1/visibility
    
    Body:
        {
            "is_public": true/false
        }
    
    Returns:
        {
            "message": "Visibilidad actualizada",
            "is_public": true
        }
    """
    try:
        # Verificar que sea el usuario correcto
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        # Validar stage_id
        if stage_id not in ['e1', 'e2', 'e3', 'e4']:
            return jsonify({"error": "Stage ID inválido"}), 400
        
        data = request.get_json()
        is_public = data.get('is_public', True)
        
        # Buscar la etapa
        stage = UserStageScore.query.filter_by(
            usuario_id=user_id,
            stage_id=stage_id
        ).first()
        
        if not stage:
            return jsonify({"error": "Etapa no encontrada"}), 404
        
        # Actualizar visibilidad
        stage.is_public = is_public
        db.session.commit()
        
        logger.info(f"Visibilidad de etapa {stage_id} actualizada para usuario {user_id}: {is_public}")
        
        return jsonify({
            "message": "Visibilidad actualizada",
            "is_public": is_public
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando visibilidad de etapa {stage_id} del usuario {user_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error actualizando visibilidad"}), 500


# ==================== UPDATE STAGE METRICS ====================

@stages_bp.route('/api/users/<int:user_id>/stages/<string:stage_id>/metrics', methods=['PUT'])
@login_required
def update_stage_metrics(user_id, stage_id):
    """
    Actualiza las métricas de una etapa
    PUT /api/users/123/stages/e1/metrics
    
    Body:
        {
            "metrics": [
                {"label": "Velocidad", "icono": "lightning-charge", "valor": "15 min"},
                {"label": "Profesionalismo", "icono": "chat-heart", "valor": "4.9"}
            ]
        }
    """
    try:
        # Verificar que sea el usuario correcto o admin
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        # Validar stage_id
        if stage_id not in ['e1', 'e2', 'e3', 'e4']:
            return jsonify({"error": "Stage ID inválido"}), 400
        
        data = request.get_json()
        metrics = data.get('metrics', [])
        
        # Buscar la etapa
        stage = UserStageScore.query.filter_by(
            usuario_id=user_id,
            stage_id=stage_id
        ).first()
        
        if not stage:
            return jsonify({"error": "Etapa no encontrada"}), 404
        
        # Actualizar métricas
        stage.metrics = metrics
        db.session.commit()
        
        logger.info(f"Métricas de etapa {stage_id} actualizadas para usuario {user_id}")
        
        return jsonify({
            "message": "Métricas actualizadas",
            "stage": stage.serialize()
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando métricas de etapa {stage_id} del usuario {user_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error actualizando métricas"}), 500


# ==================== RECALCULATE STAGE SCORES ====================

@stages_bp.route('/api/users/<int:user_id>/stages/recalculate', methods=['POST'])
@login_required
def recalculate_stage_scores(user_id):
    """
    Recalcula los scores de las 4 etapas basándose en calificaciones
    POST /api/users/123/stages/recalculate
    """
    try:
        # Verificar que sea el usuario correcto o admin
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        # Recalcular scores
        UserStageScore.calcular_scores_etapas(user_id)
        
        # Obtener etapas actualizadas
        stages = UserStageScore.query.filter_by(usuario_id=user_id).order_by(UserStageScore.stage_number).all()
        
        return jsonify({
            "message": "Scores de etapas recalculados",
            "stages": [stage.serialize() for stage in stages]
        }), 200
        
    except Exception as e:
        logger.error(f"Error recalculando etapas del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error recalculando etapas"}), 500


# ==================== GET SINGLE STAGE ====================

@stages_bp.route('/api/users/<int:user_id>/stages/<string:stage_id>', methods=['GET'])
@login_required
def get_single_stage(user_id, stage_id):
    """
    Obtiene una etapa específica
    GET /api/users/123/stages/e1
    """
    try:
        # Validar stage_id
        if stage_id not in ['e1', 'e2', 'e3', 'e4']:
            return jsonify({"error": "Stage ID inválido"}), 400
        
        # Buscar la etapa
        stage = UserStageScore.query.filter_by(
            usuario_id=user_id,
            stage_id=stage_id
        ).first()
        
        if not stage:
            return jsonify({"error": "Etapa no encontrada"}), 404
        
        # Verificar si es pública o es el usuario
        if not stage.is_public and current_user.id_usuario != user_id:
            return jsonify({"error": "Etapa privada"}), 403
        
        return jsonify(stage.serialize()), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo etapa {stage_id} del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo etapa"}), 500


# ==================== UPDATE STAGE SCORE ====================

@stages_bp.route('/api/users/<int:user_id>/stages/<string:stage_id>/score', methods=['PATCH'])
@login_required
def update_stage_score(user_id, stage_id):
    """
    Actualiza manualmente el score de una etapa
    PATCH /api/users/123/stages/e1/score
    
    Body:
        {
            "score": 4.7
        }
    
    Solo para admins o casos especiales
    """
    try:
        # Verificar que sea el usuario correcto o admin
        if current_user.id_usuario != user_id:
            # Aquí verificarías si es admin
            return jsonify({"error": "No autorizado"}), 403
        
        # Validar stage_id
        if stage_id not in ['e1', 'e2', 'e3', 'e4']:
            return jsonify({"error": "Stage ID inválido"}), 400
        
        data = request.get_json()
        new_score = data.get('score')
        
        if new_score is None or not (0 <= new_score <= 5):
            return jsonify({"error": "Score inválido (debe estar entre 0 y 5)"}), 400
        
        # Buscar la etapa
        stage = UserStageScore.query.filter_by(
            usuario_id=user_id,
            stage_id=stage_id
        ).first()
        
        if not stage:
            return jsonify({"error": "Etapa no encontrada"}), 404
        
        # Actualizar score
        stage.score = new_score
        db.session.commit()
        
        logger.info(f"Score de etapa {stage_id} actualizado manualmente para usuario {user_id}: {new_score}")
        
        return jsonify({
            "message": "Score actualizado",
            "stage": stage.serialize()
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando score de etapa {stage_id} del usuario {user_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error actualizando score"}), 500