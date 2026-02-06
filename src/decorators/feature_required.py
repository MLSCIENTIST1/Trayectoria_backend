# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO - Decorador: @feature_required
# ═══════════════════════════════════════════════════════════════════════════════
#
# INSTRUCCIONES:
# 1. Coloca este archivo en: src/decorators/feature_required.py
# 2. Importa en cualquier archivo de rutas donde lo necesites
#
# USO:
#   from src.decorators.feature_required import feature_required
#
#   @app.route('/api/cartera')
#   @login_required           # ← primero verificas que esté logueado
#   @feature_required('cartera')  # ← luego verificas que tenga acceso a la feature
#   def get_cartera():
#       limite = g.feature_limite  # None si es ilimitado, o un número
#       ...
# ═══════════════════════════════════════════════════════════════════════════════

from functools import wraps
from flask import jsonify, g, request
from src.models.feature_models import check_negocio_feature

import logging
logger = logging.getLogger(__name__)


def feature_required(feature_key):
    """
    Decorador que protege un endpoint verificando:
    
    1. ¿La feature está ACTIVA globalmente? (admin no la apagó)
    2. ¿El PLAN del negocio incluye esta feature?
    
    Si pasa ambas verificaciones, agrega a `g`:
        - g.feature_limite:  int o None (el límite para esta feature)
        - g.feature_config:  dict con config extra
    
    Si NO pasa, retorna 403 con información del error.
    
    Parámetros:
        feature_key (str): El key de la feature a verificar. Ej: 'cartera', 'store_designer'
    
    Ejemplo:
        @app.route('/api/cartera/resumen')
        @login_required
        @feature_required('cartera')
        def cartera_resumen():
            # Si llegamos aquí, el negocio tiene acceso a 'cartera'
            return jsonify({'data': '...'})
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # ─────────────────────────────────────────
            # Obtener el negocio_id del contexto
            # ─────────────────────────────────────────
            # Intenta obtener de varias fuentes (ajusta según tu auth)
            negocio_id = None
            
            # Opción 1: Viene en g (tu login_required lo pone ahí)
            if hasattr(g, 'negocio_id'):
                negocio_id = g.negocio_id
            elif hasattr(g, 'current_negocio_id'):
                negocio_id = g.current_negocio_id
            elif hasattr(g, 'current_negocio') and g.current_negocio:
                negocio_id = getattr(g.current_negocio, 'id_negocio', None)
            
            # Opción 2: Viene como parámetro en la URL
            if not negocio_id:
                negocio_id = kwargs.get('negocio_id') or kwargs.get('id_negocio')
            
            # Opción 3: Viene en el header o query param
            if not negocio_id:
                negocio_id = request.headers.get('X-Negocio-Id') or request.args.get('negocio_id')
            
            if not negocio_id:
                logger.warning(f"feature_required('{feature_key}'): No se pudo determinar negocio_id")
                return jsonify({
                    'error': 'negocio_required',
                    'message': 'Se requiere un negocio para verificar permisos'
                }), 400
            
            # ─────────────────────────────────────────
            # Verificar acceso a la feature
            # ─────────────────────────────────────────
            result = check_negocio_feature(int(negocio_id), feature_key)
            
            if not result['allowed']:
                reason = result.get('reason', 'unknown')
                
                if reason == 'feature_disabled_global':
                    logger.info(f"Feature '{feature_key}' deshabilitada globalmente")
                    return jsonify({
                        'error': 'feature_disabled',
                        'message': 'Esta funcionalidad no está disponible actualmente',
                        'feature': feature_key
                    }), 403
                
                elif reason == 'plan_upgrade_required':
                    logger.info(f"Negocio {negocio_id} (plan: {result.get('current_plan')}) "
                              f"intentó acceder a '{feature_key}' - upgrade requerido")
                    return jsonify({
                        'error': 'plan_upgrade_required',
                        'message': 'Tu plan actual no incluye esta funcionalidad',
                        'feature': feature_key,
                        'current_plan': result.get('current_plan')
                    }), 403
                
                else:
                    return jsonify({
                        'error': reason,
                        'message': 'No tienes acceso a esta funcionalidad',
                        'feature': feature_key
                    }), 403
            
            # ─────────────────────────────────────────
            # Feature permitida: pasar datos al endpoint
            # ─────────────────────────────────────────
            g.feature_limite = result.get('limite')
            g.feature_config = result.get('config', {})
            g.feature_plan = result.get('current_plan')
            
            return f(*args, **kwargs)
        
        return wrapper
    return decorator