"""
BizFlow Studio - Scores API
Endpoints para obtener y gestionar scores de usuarios
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from src.models.database import db
from src.models.trayectoria.user_score import UserScore
from src.models.trayectoria.user_score_history import UserScoreHistory
import logging

logger = logging.getLogger(__name__)

scores_bp = Blueprint('scores_api', __name__)


# ==================== GET SCORES ====================

@scores_bp.route('/api/users/<int:user_id>/scores', methods=['GET'])
@login_required
def get_user_scores(user_id):
    """
    Obtiene los scores del usuario
    GET /api/users/123/scores
    
    Returns:
        {
            "contratante": { "valor": 87, "tendencia": 3, "cambio": "up" },
            "contratado": { "valor": 92, "tendencia": 2, "cambio": "up" },
            "global": { "valor": 89, "tendencia": 2, "cambio": "up" }
        }
    """
    try:
        # Verificar que el usuario pueda acceder (es el mismo o tiene permisos)
        if current_user.id_usuario != user_id:
            # Aquí podrías agregar lógica para verificar si el perfil es público
            pass
        
        # Buscar o crear score
        user_score = UserScore.query.filter_by(usuario_id=user_id).first()
        
        if not user_score:
            # Si no existe, calcularlo
            user_score = UserScore.calcular_score_usuario(user_id)
            
            if not user_score:
                # Si aún no hay datos, devolver scores en 0
                return jsonify({
                    "contratante": {"valor": 0, "tendencia": 0, "cambio": "stable"},
                    "contratado": {"valor": 0, "tendencia": 0, "cambio": "stable"},
                    "global": {"valor": 0, "tendencia": 0, "cambio": "stable"}
                }), 200
        
        return jsonify(user_score.serialize()["scores"]), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo scores del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo scores"}), 500


# ==================== GET SCORE HISTORY ====================

@scores_bp.route('/api/users/<int:user_id>/scores/history', methods=['GET'])
@login_required
def get_score_history(user_id):
    """
    Obtiene el historial de scores para gráficos
    GET /api/users/123/scores/history?period=6m&type=global
    
    Query params:
        - period: '6m', '1y', 'all' (default: '6m')
        - type: 'contratante', 'contratado', 'global' (default: 'global')
    
    Returns:
        {
            "labels": ["Ago", "Sep", "Oct", "Nov", "Dic", "Ene"],
            "data": [82, 85, 84, 88, 90, 92]
        }
    """
    try:
        period = request.args.get('period', '6m')
        tipo_score = request.args.get('type', 'global')
        
        # Validar parámetros
        if period not in ['6m', '1y', 'all']:
            period = '6m'
        
        if tipo_score not in ['contratante', 'contratado', 'global']:
            tipo_score = 'global'
        
        # Obtener historial
        historial = UserScoreHistory.obtener_historial(user_id, tipo_score, period)
        
        return jsonify(historial), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo historial de scores del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo historial"}), 500


# ==================== GET PERCENTILE ====================

@scores_bp.route('/api/users/<int:user_id>/percentile', methods=['GET'])
@login_required
def get_user_percentile(user_id):
    """
    Obtiene el percentil del usuario y comparación con el mercado
    GET /api/users/123/percentile
    
    Returns:
        {
            "percentile": 92,
            "rank": "Top 8%",
            "comparison": {
                "tiempo_respuesta": {"valor": "2x más rápido", "tipo": "better"},
                "tasa_exito": {"valor": "+15% arriba", "tipo": "better"},
                ...
            }
        }
    """
    try:
        user_score = UserScore.query.filter_by(usuario_id=user_id).first()
        
        if not user_score:
            return jsonify({
                "percentile": 0,
                "rank": "Sin datos",
                "comparison": {}
            }), 200
        
        # Calcular percentil si no existe
        if not user_score.percentil:
            # Aquí calcularías el percentil comparando con otros usuarios
            # Por ahora, valor de ejemplo basado en el score global
            if user_score.score_global >= 90:
                user_score.percentil = 92
            elif user_score.score_global >= 80:
                user_score.percentil = 75
            elif user_score.score_global >= 70:
                user_score.percentil = 50
            else:
                user_score.percentil = 25
            
            db.session.commit()
        
        # Calcular ranking
        rank_text = f"Top {100 - int(user_score.percentil)}%"
        
        # Comparación con el mercado (placeholder - implementar lógica real)
        comparison = {
            "tiempo_respuesta": {"valor": "2x más rápido", "tipo": "better"},
            "tasa_exito": {"valor": "+15% arriba", "tipo": "better"},
            "precio_promedio": {"valor": "En el rango", "tipo": "same"},
            "recontratacion": {"valor": "+23% arriba", "tipo": "better"}
        }
        
        return jsonify({
            "percentile": round(user_score.percentil, 1),
            "rank": rank_text,
            "comparison": comparison
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo percentil del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo percentil"}), 500


# ==================== RECALCULAR SCORES ====================

@scores_bp.route('/api/users/<int:user_id>/scores/recalculate', methods=['POST'])
@login_required
def recalculate_scores(user_id):
    """
    Fuerza el recálculo de scores del usuario
    POST /api/users/123/scores/recalculate
    
    Útil para:
    - Después de recibir nuevas calificaciones
    - Actualización manual por admin
    - Debugging
    """
    try:
        # Verificar permisos (solo el usuario o admin)
        if current_user.id_usuario != user_id:
            # Aquí verificarías si es admin
            return jsonify({"error": "No autorizado"}), 403
        
        # Recalcular score
        user_score = UserScore.calcular_score_usuario(user_id)
        
        if not user_score:
            return jsonify({"error": "No se pudo calcular el score"}), 500
        
        # Registrar en historial
        UserScoreHistory.registrar_cambio(
            user_id,
            'global',
            user_score.score_global,
            'recalculo_manual'
        )
        
        return jsonify({
            "message": "Score recalculado exitosamente",
            "scores": user_score.serialize()["scores"]
        }), 200
        
    except Exception as e:
        logger.error(f"Error recalculando scores del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error recalculando scores"}), 500


# ==================== GET MARKET COMPARISON ====================

@scores_bp.route('/api/users/<int:user_id>/market-comparison', methods=['GET'])
@login_required
def get_market_comparison(user_id):
    """
    Obtiene comparación detallada con el mercado
    GET /api/users/123/market-comparison
    
    Returns:
        Estadísticas comparativas con otros usuarios similares
    """
    try:
        # Placeholder - implementar lógica real de comparación
        comparison_data = {
            "categoria": "Desarrollo Full Stack",
            "comparaciones": [
                {
                    "metrica": "Tiempo de Respuesta",
                    "valor_usuario": "15 min",
                    "valor_mercado": "45 min",
                    "diferencia": "66% más rápido",
                    "tipo": "better"
                },
                {
                    "metrica": "Rating Promedio",
                    "valor_usuario": 4.8,
                    "valor_mercado": 4.3,
                    "diferencia": "+0.5 puntos",
                    "tipo": "better"
                },
                {
                    "metrica": "Precio por Hora",
                    "valor_usuario": "$45",
                    "valor_mercado": "$40-50",
                    "diferencia": "En rango",
                    "tipo": "same"
                }
            ]
        }
        
        return jsonify(comparison_data), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo comparación de mercado del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo comparación"}), 500