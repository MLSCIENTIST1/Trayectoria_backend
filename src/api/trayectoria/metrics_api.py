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
BizFlow Studio - Metrics API
Endpoints para obtener y gestionar métricas de usuarios
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from src.models.database import db
from src.models.trayectoria.user_metric import UserMetric
import logging

logger = logging.getLogger(__name__)

metrics_bp = Blueprint('metrics_api', __name__)


# ==================== GET ALL METRICS ====================

@metrics_bp.route('/api/users/<int:user_id>/metrics', methods=['GET'])
@login_required
def get_user_metrics(user_id):
    """
    Obtiene todas las métricas del usuario
    GET /api/users/123/metrics
    
    Query params:
        - include_system: true/false (default: false) - Incluir métricas del sistema
    
    Returns:
        [
            {
                "id": "proyectos_completados",
                "nombre": "Proyectos Completados",
                "valor": "95",
                "cambio": "+8 este mes",
                "tipo_cambio": "positive",
                "icono": "briefcase-fill",
                "color": "#10b981",
                "visible": true,
                "sistema": false,
                "categoria": "volumen"
            },
            ...
        ]
    """
    try:
        # Verificar acceso
        if current_user.id_usuario != user_id:
            # Si no es el usuario, solo mostrar métricas públicas
            metricas = UserMetric.query.filter_by(
                usuario_id=user_id,
                is_public=True
            ).order_by(UserMetric.orden).all()
        else:
            # Si es el usuario, mostrar todas (o solo no-sistema según parámetro)
            include_system = request.args.get('include_system', 'false').lower() == 'true'
            
            if include_system:
                metricas = UserMetric.query.filter_by(usuario_id=user_id).order_by(UserMetric.orden).all()
            else:
                metricas = UserMetric.query.filter_by(
                    usuario_id=user_id,
                    is_system=False
                ).order_by(UserMetric.orden).all()
        
        # Si no hay métricas, inicializarlas
        if not metricas:
            UserMetric.inicializar_metricas_usuario(user_id)
            metricas = UserMetric.query.filter_by(usuario_id=user_id).order_by(UserMetric.orden).all()
        
        return jsonify([metrica.serialize() for metrica in metricas]), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo métricas"}), 500


# ==================== GET METRICS BY CATEGORY ====================

@metrics_bp.route('/api/users/<int:user_id>/metrics/<string:category>', methods=['GET'])
@login_required
def get_metrics_by_category(user_id, category):
    """
    Obtiene métricas de una categoría específica
    GET /api/users/123/metrics/volumen
    
    Categorías: 'volumen', 'velocidad', 'calidad', 'fidelidad', 'riesgo', 'rendimiento', 'cumplimiento'
    """
    try:
        # Verificar acceso
        is_owner = current_user.id_usuario == user_id
        
        query = UserMetric.query.filter_by(
            usuario_id=user_id,
            categoria=category
        )
        
        # Si no es el dueño, solo métricas públicas
        if not is_owner:
            query = query.filter_by(is_public=True)
        
        metricas = query.order_by(UserMetric.orden).all()
        
        return jsonify([metrica.serialize() for metrica in metricas]), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de categoría {category} del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo métricas"}), 500


# ==================== UPDATE METRIC ====================

@metrics_bp.route('/api/users/<int:user_id>/metrics/<string:metric_key>', methods=['PUT'])
@login_required
def update_metric(user_id, metric_key):
    """
    Actualiza una métrica del usuario
    PUT /api/users/123/metrics/proyectos_completados
    
    Body:
        {
            "valor": 100,
            "cambio_texto": "+5 este mes",
            "tipo_cambio": "positive"
        }
    
    Solo para el usuario o admin
    """
    try:
        # Verificar permisos
        if current_user.id_usuario != user_id:
            # Aquí verificarías si es admin
            return jsonify({"error": "No autorizado"}), 403
        
        data = request.get_json()
        nuevo_valor = data.get('valor')
        cambio_texto = data.get('cambio_texto')
        tipo_cambio = data.get('tipo_cambio')
        
        if nuevo_valor is None:
            return jsonify({"error": "Valor requerido"}), 400
        
        # Actualizar métrica
        metrica = UserMetric.actualizar_metrica(
            user_id,
            metric_key,
            nuevo_valor,
            cambio_texto=cambio_texto,
            tipo_cambio=tipo_cambio
        )
        
        if not metrica:
            return jsonify({"error": "Métrica no encontrada"}), 404
        
        return jsonify({
            "message": "Métrica actualizada",
            "metric": metrica.serialize()
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando métrica {metric_key} del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error actualizando métrica"}), 500


# ==================== TOGGLE METRIC VISIBILITY ====================

@metrics_bp.route('/api/users/<int:user_id>/metrics/<string:metric_key>/visibility', methods=['PATCH'])
@login_required
def toggle_metric_visibility(user_id, metric_key):
    """
    Cambia la visibilidad pública de una métrica
    PATCH /api/users/123/metrics/proyectos_completados/visibility
    
    Body:
        {
            "is_public": true/false
        }
    """
    try:
        # Verificar que sea el usuario correcto
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        data = request.get_json()
        is_public = data.get('is_public', True)
        
        # Buscar la métrica
        metrica = UserMetric.query.filter_by(
            usuario_id=user_id,
            metric_key=metric_key
        ).first()
        
        if not metrica:
            return jsonify({"error": "Métrica no encontrada"}), 404
        
        # No permitir cambiar visibilidad de métricas del sistema
        if metrica.is_system:
            return jsonify({"error": "No se puede cambiar visibilidad de métricas del sistema"}), 400
        
        # Actualizar visibilidad
        metrica.is_public = is_public
        db.session.commit()
        
        logger.info(f"Visibilidad de métrica {metric_key} actualizada para usuario {user_id}: {is_public}")
        
        return jsonify({
            "message": "Visibilidad actualizada",
            "is_public": is_public
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando visibilidad de métrica {metric_key} del usuario {user_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error actualizando visibilidad"}), 500


# ==================== RECALCULATE METRICS ====================

@metrics_bp.route('/api/users/<int:user_id>/metrics/recalculate', methods=['POST'])
@login_required
def recalculate_metrics(user_id):
    """
    Recalcula todas las métricas del usuario desde sus calificaciones y servicios
    POST /api/users/123/metrics/recalculate
    """
    try:
        # Verificar permisos
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        # Recalcular métricas
        UserMetric.calcular_metricas_desde_calificaciones(user_id)
        
        # Obtener métricas actualizadas
        metricas = UserMetric.query.filter_by(usuario_id=user_id).order_by(UserMetric.orden).all()
        
        return jsonify({
            "message"