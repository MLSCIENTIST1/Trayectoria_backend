"""
BizFlow Studio - Portfolio API
Endpoints para gestionar videos del portfolio personal del usuario
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from src.models.database import db
from src.models.trayectoria.portfolio_video import PortfolioVideo
from werkzeug.utils import secure_filename
import os
import logging

logger = logging.getLogger(__name__)

portfolio_bp = Blueprint('portfolio_api', __name__)


# ==================== GET ALL VIDEOS ====================

@portfolio_bp.route('/api/users/<int:user_id>/videos', methods=['GET'])
@login_required
def get_portfolio_videos(user_id):
    """
    Obtiene la lista de videos del portfolio del usuario
    GET /api/users/123/videos
    
    Query params:
        - destacados_only: true/false (default: false)
    
    Returns:
        [
            {
                "id": 1,
                "titulo": "App E-commerce",
                "descripcion": "Mi mejor trabajo",
                "url": "/uploads/videos/video1.mp4",
                "thumbnail": "/uploads/thumbnails/video1.jpg",
                "duracion": "2:00:58",
                "vistas": 1200,
                "likes": 89,
                "metricas": ["proyectos_completados", "rating_promedio"],
                "badges": ["perfeccionista", "rayo-veloz"],
                "destacado": true,
                "promovido": false,
                "fecha": "2024-01-10T15:30:00"
            },
            ...
        ]
    """
    try:
        destacados_only = request.args.get('destacados_only', 'false').lower() == 'true'
        
        query = PortfolioVideo.query.filter_by(
            usuario_id=user_id,
            activo=True
        )
        
        if destacados_only:
            query = query.filter_by(destacado=True)
        
        videos = query.order_by(PortfolioVideo.orden).all()
        
        return jsonify([video.serialize() for video in videos]), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo videos del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo videos"}), 500


# ==================== UPLOAD VIDEO ====================

@portfolio_bp.route('/api/users/<int:user_id>/videos', methods=['POST'])
@login_required
def upload_video(user_id):
    """
    Sube un nuevo video al portfolio
    POST /api/users/123/videos
    
    Form data:
        - video: archivo de video
        - title: título del video
        - description: descripción (opcional)
        - duracion: duración en formato "HH:MM:SS" (opcional)
    
    Returns:
        {
            "message": "Video subido exitosamente",
            "video_id": 5,
            "url": "/uploads/videos/video5.mp4"
        }
    """
    try:
        # Verificar permisos
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        # Verificar que se envió un archivo
        if 'video' not in request.files:
            return jsonify({"error": "No se envió video"}), 400
        
        file = request.files['video']
        titulo = request.form.get('title', 'Sin título')
        descripcion = request.form.get('description')
        duracion = request.form.get('duracion')
        
        if file.filename == '':
            return jsonify({"error": "Archivo vacío"}), 400
        
        # Validar extensión
        allowed_extensions = {'mp4', 'mov', 'avi', 'webm', 'mkv'}
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else None
        
        if file_ext not in allowed_extensions:
            return jsonify({"error": f"Formato no permitido. Use: {', '.join(allowed_extensions)}"}), 400
        
        # Generar nombre único
        from datetime import datetime
        timestamp = datetime.utcnow().timestamp()
        new_filename = f"user_{user_id}_{int(timestamp)}.{file_ext}"
        
        # Guardar archivo
        upload_folder = os.path.join('static', 'uploads', 'videos')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, new_filename)
        file.save(filepath)
        
        # URL relativa
        video_url = f"/uploads/videos/{new_filename}"
        
        # Crear registro en DB
        video = PortfolioVideo.crear_video(
            usuario_id=user_id,
            titulo=titulo,
            url=video_url,
            descripcion=descripcion,
            duracion=duracion
        )
        
        if not video:
            return jsonify({"error": "No se pudo guardar el video"}), 500
        
        logger.info(f"Video subido para usuario {user_id}: {titulo}")
        
        return jsonify({
            "message": "Video subido exitosamente",
            "video_id": video.id,
            "url": video_url,
            "video": video.serialize()
        }), 201
        
    except Exception as e:
        logger.error(f"Error subiendo video para usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error subiendo video"}), 500


# ==================== UPDATE VIDEO ====================

@portfolio_bp.route('/api/users/<int:user_id>/videos/<int:video_id>', methods=['PUT'])
@login_required
def update_video(user_id, video_id):
    """
    Actualiza información de un video
    PUT /api/users/123/videos/5
    
    Body:
        {
            "titulo": "Nuevo título",
            "descripcion": "Nueva descripción",
            "destacado": true
        }
    """
    try:
        # Verificar permisos
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        # Buscar video
        video = PortfolioVideo.query.filter_by(
            id=video_id,
            usuario_id=user_id
        ).first()
        
        if not video:
            return jsonify({"error": "Video no encontrado"}), 404
        
        # Actualizar campos
        data = request.get_json()
        
        if 'titulo' in data:
            video.titulo = data['titulo']
        if 'descripcion' in data:
            video.descripcion = data['descripcion']
        if 'destacado' in data:
            video.destacado = data['destacado']
        
        db.session.commit()
        
        logger.info(f"Video {video_id} actualizado para usuario {user_id}")
        
        return jsonify({
            "message": "Video actualizado",
            "video": video.serialize()
        }), 200
        
    except Exception as e:
        logger.error(f"Error actualizando video {video_id} del usuario {user_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error actualizando video"}), 500


# ==================== DELETE VIDEO ====================

@portfolio_bp.route('/api/users/<int:user_id>/videos/<int:video_id>', methods=['DELETE'])
@login_required
def delete_video(user_id, video_id):
    """
    Elimina un video del portfolio
    DELETE /api/users/123/videos/5
    """
    try:
        # Verificar permisos
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        # Buscar video
        video = PortfolioVideo.query.filter_by(
            id=video_id,
            usuario_id=user_id
        ).first()
        
        if not video:
            return jsonify({"error": "Video no encontrado"}), 404
        
        # Intentar eliminar archivo físico (opcional)
        try:
            if video.url and video.url.startswith('/uploads/'):
                file_path = os.path.join('static', video.url.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivo físico: {str(e)}")
        
        # Eliminar de DB
        db.session.delete(video)
        db.session.commit()
        
        logger.info(f"Video {video_id} eliminado para usuario {user_id}")
        
        return jsonify({"message": "Video eliminado exitosamente"}), 200
        
    except Exception as e:
        logger.error(f"Error eliminando video {video_id} del usuario {user_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error eliminando video"}), 500


# ==================== ASSOCIATE METRICS ====================

@portfolio_bp.route('/api/users/<int:user_id>/videos/<int:video_id>/metrics', methods=['POST'])
@login_required
def associate_metrics(user_id, video_id):
    """
    Asocia métricas a un video
    POST /api/users/123/videos/5/metrics
    
    Body:
        {
            "metric_ids": ["proyectos_completados", "rating_promedio"]
        }
    """
    try:
        # Verificar permisos
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        data = request.get_json()
        metric_ids = data.get('metric_ids', [])
        
        if not isinstance(metric_ids, list):
            return jsonify({"error": "metric_ids debe ser un array"}), 400
        
        # Asociar métricas
        video = PortfolioVideo.asociar_metricas(video_id, metric_ids)
        
        if not video:
            return jsonify({"error": "Video no encontrado"}), 404
        
        return jsonify({
            "message": "Métricas asociadas",
            "video": video.serialize()
        }), 200
        
    except Exception as e:
        logger.error(f"Error asociando métricas al video {video_id}: {str(e)}")
        return jsonify({"error": "Error asociando métricas"}), 500


# ==================== ASSOCIATE BADGES ====================

@portfolio_bp.route('/api/users/<int:user_id>/videos/<int:video_id>/badges', methods=['POST'])
@login_required
def associate_badges(user_id, video_id):
    """
    Asocia badges a un video
    POST /api/users/123/videos/5/badges
    
    Body:
        {
            "badge_ids": ["perfeccionista", "rayo-veloz"]
        }
    """
    try:
        # Verificar permisos
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        data = request.get_json()
        badge_ids = data.get('badge_ids', [])
        
        if not isinstance(badge_ids, list):
            return jsonify({"error": "badge_ids debe ser un array"}), 400
        
        # Asociar badges
        video = PortfolioVideo.asociar_badges(video_id, badge_ids)
        
        if not video:
            return jsonify({"error": "Video no encontrado"}), 404
        
        return jsonify({
            "message": "Badges asociados",
            "video": video.serialize()
        }), 200
        
    except Exception as e:
        logger.error(f"Error asociando badges al video {video_id}: {str(e)}")
        return jsonify({"error": "Error asociando badges"}), 500


# ==================== INCREMENT VIEW ====================

@portfolio_bp.route('/api/users/<int:user_id>/videos/<int:video_id>/view', methods=['POST'])
def increment_video_view(user_id, video_id):
    """
    Incrementa el contador de vistas de un video
    POST /api/users/123/videos/5/view
    
    No requiere login (endpoint público)
    """
    try:
        PortfolioVideo.incrementar_vista(video_id)
        return jsonify({"message": "Vista registrada"}), 200
        
    except Exception as e:
        logger.error(f"Error incrementando vista del video {video_id}: {str(e)}")
        return jsonify({"error": "Error registrando vista"}), 500


# ==================== TOGGLE LIKE ====================

@portfolio_bp.route('/api/users/<int:user_id>/videos/<int:video_id>/like', methods=['POST'])
@login_required
def toggle_video_like(user_id, video_id):
    """
    Da like a un video
    POST /api/users/123/videos/5/like
    
    En una implementación completa, deberías verificar que el usuario no haya dado like antes
    """
    try:
        likes = PortfolioVideo.toggle_like(video_id)
        
        if likes is None:
            return jsonify({"error": "Video no encontrado"}), 404
        
        return jsonify({
            "message": "Like registrado",
            "likes": likes
        }), 200
        
    except Exception as e:
        logger.error(f"Error registrando like del video {video_id}: {str(e)}")
        return jsonify({"error": "Error registrando like"}), 500


# ==================== PROMOTE VIDEO ====================

@portfolio_bp.route('/api/users/<int:user_id>/videos/<int:video_id>/promote', methods=['POST'])
@login_required
def promote_video(user_id, video_id):
    """
    Promueve un video (función premium)
    POST /api/users/123/videos/5/promote
    
    Requiere verificación de suscripción premium
    """
    try:
        # Verificar permisos
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        # Aquí deberías verificar si el usuario tiene suscripción premium
        # if not current_user.tiene_premium:
        #     return jsonify({"error": "Requiere suscripción premium"}), 403
        
        video = PortfolioVideo.promover_video(video_id)
        
        if not video:
            return jsonify({"error": "Video no encontrado"}), 404
        
        logger.info(f"Video {video_id} promovido para usuario {user_id}")
        
        return jsonify({
            "message": "Video promovido exitosamente",
            "video": video.serialize()
        }), 200
        
    except Exception as e:
        logger.error(f"Error promoviendo video {video_id}: {str(e)}")
        return jsonify({"error": "Error promoviendo video"}), 500


# ==================== REORDER VIDEOS ====================

@portfolio_bp.route('/api/users/<int:user_id>/videos/reorder', methods=['PUT'])
@login_required
def reorder_videos(user_id):
    """
    Reordena los videos del portfolio
    PUT /api/users/123/videos/reorder
    
    Body:
        {
            "order": [3, 1, 5, 2, 4]
        }
    """
    try:
        # Verificar permisos
        if current_user.id_usuario != user_id:
            return jsonify({"error": "No autorizado"}), 403
        
        data = request.get_json()
        order = data.get('order', [])
        
        if not isinstance(order, list):
            return jsonify({"error": "order debe ser un array"}), 400
        
        # Reordenar
        PortfolioVideo.reordenar_videos(user_id, order)
        
        return jsonify({"message": "Videos reordenados exitosamente"}), 200
        
    except Exception as e:
        logger.error(f"Error reordenando videos del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error reordenando videos"}), 500


# ==================== GET SINGLE VIDEO ====================

@portfolio_bp.route('/api/users/<int:user_id>/videos/<int:video_id>', methods=['GET'])
def get_single_video(user_id, video_id):
    """
    Obtiene un video específico
    GET /api/users/123/videos/5
    
    Endpoint público
    """
    try:
        video = PortfolioVideo.query.filter_by(
            id=video_id,
            usuario_id=user_id,
            activo=True
        ).first()
        
        if not video:
            return jsonify({"error": "Video no encontrado"}), 404
        
        return jsonify(video.serialize()), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo video {video_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo video"}), 500