"""
BizFlow Studio - API de Trayectoria
Endpoints para scores, badges, métricas y portfolio de usuarios
"""

from src.api.trayectoria.scores_api import scores_bp
from src.api.trayectoria.stages_api import stages_bp
from src.api.trayectoria.badges_api import badges_bp
from src.api.trayectoria.metrics_api import metrics_bp
from src.api.trayectoria.portfolio_api import portfolio_bp

__all__ = [
    'scores_bp',
    'stages_bp',
    'badges_bp',
    'metrics_bp',
    'portfolio_bp'
]