# ═══════════════════════════════════════════════════════════════════════════════
# ███████╗██╗   ██╗██╗  ██╗ ██████╗ ███╗   ███╗███████╗██████╗  ██████╗██╗ ██████╗ 
# ╚══██╔══╝██║   ██║██║ ██╔╝██╔═══██╗████╗ ████║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗
#    ██║   ██║   ██║█████╔╝ ██║   ██║██╔████╔██║█████╗  ██████╔╝██║     ██║██║   ██║
#    ██║   ██║   ██║██╔═██╗ ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║   ██║
#    ██║   ╚██████╔╝██║  ██╗╚██████╔╝██║ ╚═╝ ██║███████╗██║  ██║╚██████╗██║╚██████╔╝
#    ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝ ╚═════╝ 
# ═══════════════════════════════════════════════════════════════════════════════
#
# TUKOMERCIO - Plataforma de Comercio Electrónico, Gamificación y Gestión Empresarial
# Anteriormente conocido como: Trayectoria / BizFlow Studio
#
# ═══════════════════════════════════════════════════════════════════════════════
# AVISO DE PROPIEDAD INTELECTUAL Y DERECHOS DE AUTOR
# ═══════════════════════════════════════════════════════════════════════════════
#
# © 2024-2026 Carlos Eduardo Huérfano Bermúdez. Todos los derechos reservados.
#
# TITULAR DE DERECHOS:
#   Nombre:     Carlos Eduardo Huérfano Bermúdez
#   C.C.:       1.064.986.917 (Cereté, Córdoba, Colombia)
#   Contacto:   carlos-5100@hotmail.com | +57 322 818 8375
#   Ubicación:  Bogotá D.C., Colombia
#
# INFORMACIÓN DEL PROYECTO:
#   Nombre:     TuKomercio
#   Inicio:     Julio 24, 2024
#   Repositorio: github.com/routeres (routeres@gmail.com)
#
# ═══════════════════════════════════════════════════════════════════════════════
# TÉRMINOS DE USO Y RESTRICCIONES
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este código fuente es CONFIDENCIAL y constituye un SECRETO COMERCIAL.
#
# QUEDA ESTRICTAMENTE PROHIBIDO sin autorización ESCRITA del titular:
#
#   1. Copiar, reproducir o duplicar este código, total o parcialmente
#   2. Modificar, adaptar o crear obras derivadas
#   3. Distribuir, publicar, sublicenciar o transferir a terceros
#   4. Usar para desarrollo de productos competidores
#   5. Realizar ingeniería inversa, descompilar o desensamblar
#   6. Remover o alterar este aviso de propiedad intelectual
#
# El acceso a este código NO otorga ninguna licencia implícita o explícita.
#
# ═══════════════════════════════════════════════════════════════════════════════
# PROTECCIÓN LEGAL
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este software está protegido por:
#
#   • Ley 23 de 1982 - Derechos de Autor (Colombia)
#   • Ley 1915 de 2018 - Modernización Derechos de Autor (Colombia)
#   • Decisión Andina 351 de 1993 - Régimen Común sobre Derecho de Autor
#   • Convenio de Berna para la Protección de Obras Literarias y Artísticas
#   • Tratado OMPI sobre Derecho de Autor (WCT)
#   • Acuerdo ADPIC/TRIPS - Organización Mundial del Comercio
#
# SANCIONES POR INFRACCIÓN:
#   • Civiles: Indemnización por daños y perjuicios (Art. 57, Ley 23/1982)
#   • Penales: Prisión de 4 a 8 años y multa (Art. 271, Código Penal Colombiano)
#
# ═══════════════════════════════════════════════════════════════════════════════
# JURISDICCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
#
# Cualquier disputa será resuelta exclusivamente por los tribunales de
# Bogotá D.C., Colombia, bajo las leyes de la República de Colombia.
#
# ═══════════════════════════════════════════════════════════════════════════════
#
# Para solicitar autorización de uso: carlos-5100@hotmail.com
#
# ═══════════════════════════════════════════════════════════════════════════════



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