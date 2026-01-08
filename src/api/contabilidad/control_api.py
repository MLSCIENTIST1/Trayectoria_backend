from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_login import login_required, current_user
from src.models.database import db
from src.models.colombia_data.contabilidad.operaciones import TransaccionOperativa, AlertaOperativa
from src.models.colombia_data.catalogo.catalogo import ProductoCatalogo
from datetime import datetime
import traceback

control_api_bp = Blueprint('control_operativo', __name__)



@control_api_bp.route('/control/reporte/<int:negocio_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def obtener_reporte(negocio_id):
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
        
    try:
        # 1. Consultamos las transacciones del negocio ordenadas por fecha
        operaciones = TransaccionOperativa.query.filter_by(negocio_id=negocio_id)\
            .order_by(TransaccionOperativa.fecha.desc()).all()
        
        # 2. Construimos la respuesta mapeando al formato del Frontend
        resultado = []
        for op in operaciones:
            data = op.to_dict()
            resultado.append({
                "fecha": data["fecha"],
                "concepto": data["concepto"] or "Sin concepto",
                "categoria": data["categoria"] or "General",
                "monto": data["monto"],
                "tipo": data["tipo"],
                "metodo_pago": data["metodo"]
            })
        
        return jsonify({
            "success": True,
            "operaciones": resultado
        }), 200

    except Exception as e:
        print("❌ Error crítico en obtener_reporte:")
        print(traceback.format_exc())
        return jsonify({
            "success": False, 
            "message": "Error interno del servidor",
            "error_detail": str(e)
        }), 500