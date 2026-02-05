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
BizFlow Studio - Badges API
Endpoints para obtener badges/logros de usuarios
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from src.models.database import db
from src.models.trayectoria.badge import Badge
from src.models.trayectoria.user_badge import UserBadge
import logging

logger = logging.getLogger(__name__)

badges_bp = Blueprint('badges_api', __name__)


# ==================== GET USER BADGES ====================

@badges_bp.route('/api/users/<int:user_id>/badges', methods=['GET'])
@login_required
def get_user_badges(user_id):
    """
    Obtiene todos los badges del usuario (desbloqueados y bloqueados)
    GET /api/users/123/badges
    
    Returns:
        [
            {
                "id": "primera-estrella",
                "nombre": "Primera Estrella",
                "descripcion": "Primera calificación 5⭐",
                "emoji": "🏆",
                "color": "#fbbf24",
                "rgb": "251,191,36",
                "desbloqueado": true,
                "fecha_desbloqueo": "2024-01-10T15:30:00",
                "mostrar_en_perfil": true
            },
            ...
        ]
    """
    try:
        # Verificar acceso
        if current_user.id_usuario != user_id:
            # Aquí podrías verificar si el perfil es público
            pass
        
        # Buscar badges del usuario con información del badge
        user_badges = db.session.query(UserBadge, Badge).join(
            Badge, UserBadge.badge_id == Badge.id
        ).filter(
            UserBadge.usuario_id == user_id,
            Badge.activo == True
        ).order_by(Badge.orden).all()
        
        # Si no tiene badges, inicializarlos
        if not user_badges:
            UserBadge.inicializar_badges_usuario(user_id)
            user_badges = db.session.query(UserBadge, Badge).join(
                Badge, UserBadge.badge_id == Badge.id
            ).filter(
                UserBadge.usuario_id == user_id,
                Badge.activo == True
            ).order_by(Badge.orden).all()
        
        # Serializar
        badges_data = []
        for user_badge, badge in user_badges:
            badge_info = badge.serialize()
            badge_info['desbloqueado'] = user_badge.desbloqueado
            badge_info['fecha_desbloqueo'] = user_badge.fecha_desbloqueo.isoformat() if user_badge.fecha_desbloqueo else None
            badge_info['mostrar_en_perfil'] = user_badge.mostrar_en_perfil
            badges_data.append(badge_info)
        
        return jsonify(badges_data), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo badges del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo badges"}), 500


# ==================== GET BADGE PROGRESS ====================

@badges_bp.route('/api/users/<int:user_id>/badges/progress', methods=['GET'])
@login_required
def get_badge_progress(user_id):
    """
    Obtiene el progreso de badges del usuario
    GET /api/users/123/badges/progress
    
    Returns:
        {
            "desbloqueados": 12,
            "total": 20,
            "porcentaje": 60
        }
    """
    try:
        progreso = UserBadge.obtener_progreso_badges(user_id)
        return jsonify(progreso), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo progreso de badges del usuario {user_id}: {str(e)}")
        return jsonify({"error": "Error obteniendo progreso"}), 500


# ==================== UNLOCK BADGE (MANUAL) ====================

@badges_bp.route('/api/users/<int:user_id>/badges/<string:badge_id>/unlock', methods=['POST'])
@login_required
def unlock_badge_manual(user_id, badge_id):
    """
    Desbloquea manualmente un badge para un usuario
    POST /api/users/123/badges/primera-estrella/unlock
    
    Body (opcional):
        {
            "motivo": "Alcanzó primera calificación 5 estrellas",
            "valor_alcanzado": 1
        }
    
    Solo para admins o sistema automatizado
    """
    try:
        # Verificar permisos (solo admin o sistema)
        if current_user.id_usuario != user_id:
            # Aquí verificarías si es admin
            return jsonify({"error": "No autorizado"}), 403
        
        data = request.get_json() or {}
        motivo = data.get('motivo')
        valor_alcanzado = data.get('valor_alcanzado')
        
        # Desbloquear badge
        user_badge = UserBadge.desbloquear_badge(
            user_id,
            badge_id,
            motivo=motivo,
            valor_alcanzado=valor_alcanzado
        )
        
        if not user_badge:
            return jsonify({"error": "No se pudo desbloquear el badge"}), 500
        
        return jsonify({
            "message": "Badge desbloqueado exitosamente",
            "badge": user_badge.serialize()
        }), 200
        
    except Exception as e:
        logger.error(f"Error desbloqueando badge {badge_id} para usuario {user_id}: {str(e)}")