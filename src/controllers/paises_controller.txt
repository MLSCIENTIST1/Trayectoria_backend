from flask import Blueprint, jsonify, request
from src.models.colombia_data.colombia_data import Colombia  # Importa tu modelo de ciudades

paises_bp = Blueprint('paises', __name__)

@paises_bp.route('/api/ciudades', methods=['GET'])
def obtener_ciudades():
    pais = request.args.get('pais', '').strip()
    termino = request.args.get('q', '').strip()

    if not pais or not termino:  # Asegura que ambos parámetros estén presentes
        return jsonify([])

    # Lógica específica para Colombia
    if pais == "Colombia":
        ciudades = Colombia.query.filter(Colombia.ciudad_nombre.ilike(f'{termino}%')).limit(20).all()
        resultados = [ciudad.ciudad_nombre for ciudad in ciudades]
        return jsonify(resultados)

    # Para otros países (inhabilitado por ahora)
    # elif pais == "México":
    #     # Implementar lógica futura para México
    #     return jsonify(["Ciudad de México", "Guadalajara", "Monterrey"])  # Ejemplo temporal
    # elif pais == "Brasil":
    #     # Implementar lógica futura para Brasil
    #     pass

    # Si el país no está soportado, devuelve una lista vacía
    return jsonify([])