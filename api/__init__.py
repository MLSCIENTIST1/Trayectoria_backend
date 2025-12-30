from flask import Blueprint

# Crear el Blueprint principal
api_bp = Blueprint('api', __name__)

# Importar los Blueprints encontrados
from .__init__ import api_bp

# Registrar los Blueprints en el principal
api_bp.register_blueprint(api_bp)
