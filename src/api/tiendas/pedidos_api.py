"""
TUKOMERCIO - Pedidos API v1.0
Gestión de pedidos para el dueño del negocio
Ubicación: src/api/tiendas/pedidos_api.py
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from sqlalchemy import func
from src.models.database import db
from src.models.compradores.pedido import Pedido, PedidoHistorial

logger = logging.getLogger(__name__)

pedidos_api_bp = Blueprint('pedidos_api_bp', __name__, url_prefix='/api')


# ==========================================
# HELPER: Obtener User ID
# ==========================================
def get_user_id():
    """Obtiene el user_id del header o sesión."""
    try:
        from flask_login import current_user
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            return current_user.id_usuario
    except:
        pass
    return request.headers.get('X-User-ID', type=int)


# ==========================================
# LISTAR PEDIDOS DE UN NEGOCIO
# ==========================================
@pedidos_api_bp.route('/pedidos/negocio/<int:negocio_id>', methods=['GET'])
@cross_origin()
def listar_pedidos(negocio_id):
    """
    Lista todos los pedidos de un negocio.
    
    GET /api/pedidos/negocio/{id}
    GET /api/pedidos/negocio/{id}?estado=pendiente
    GET /api/pedidos/negocio/{id}?limit=50&offset=0
    """
    try:
        # Parámetros de filtro
        estado = request.args.get('estado')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        orden = request.args.get('orden', 'desc')  # asc o desc
        
        # Query base
        query = Pedido.query.filter_by(negocio_id=negocio_id)
        
        # Filtrar por estado
        if estado and estado != 'todos':
            query = query.filter_by(estado=estado)
        
        # Ordenar
        if orden == 'asc':
            query = query.order_by(Pedido.fecha_pedido.asc())
        else:
            query = query.order_by(Pedido.fecha_pedido.desc())
        
        # Paginación
        total = query.count()
        pedidos = query.offset(offset).limit(limit).all()
        
        return jsonify({
            "success": True,
            "pedidos": [p.to_dict_lista() for p in pedidos],
            "total": total,
            "limit": limit,
            "offset": offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando pedidos: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# OBTENER DETALLE DE UN PEDIDO
# ==========================================
@pedidos_api_bp.route('/pedidos/<int:pedido_id>', methods=['GET'])
@cross_origin()
def obtener_pedido(pedido_id):
    """
    Obtiene el detalle completo de un pedido.
    
    GET /api/pedidos/{id}
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404
        
        return jsonify({
            "success": True,
            "pedido": pedido.to_dict(include_historial=True)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo pedido: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# CAMBIAR ESTADO DE UN PEDIDO
# ==========================================
@pedidos_api_bp.route('/pedidos/<int:pedido_id>/estado', methods=['PUT', 'PATCH'])
@cross_origin()
def cambiar_estado_pedido(pedido_id):
    """
    Cambia el estado de un pedido.
    
    PUT /api/pedidos/{id}/estado
    Body: { "estado": "enviado", "comentario": "Enviado con Servientrega" }
    """
    try:
        user_id = get_user_id()
        data = request.get_json() or {}
        
        nuevo_estado = data.get('estado')
        comentario = data.get('comentario')
        
        if not nuevo_estado:
            return jsonify({"success": False, "error": "Estado requerido"}), 400
        
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404
        
        # Validar estado
        if nuevo_estado not in Pedido.ESTADOS:
            return jsonify({
                "success": False, 
                "error": f"Estado inválido. Válidos: {list(Pedido.ESTADOS.keys())}"
            }), 400
        
        # Cambiar estado
        estado_anterior = pedido.estado
        pedido.cambiar_estado(nuevo_estado, usuario_id=user_id, comentario=comentario)
        
        db.session.commit()
        
        logger.info(f"Pedido {pedido.codigo_pedido}: {estado_anterior} → {nuevo_estado}")
        
        return jsonify({
            "success": True,
            "message": f"Estado actualizado a: {nuevo_estado}",
            "pedido": {
                "id": pedido.id_pedido,
                "codigo": pedido.codigo_pedido,
                "estado_anterior": estado_anterior,
                "estado": pedido.estado,
                "estado_info": pedido.estado_info
            }
        }), 200
        
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cambiando estado: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# CANCELAR PEDIDO
# ==========================================
@pedidos_api_bp.route('/pedidos/<int:pedido_id>/cancelar', methods=['POST'])
@cross_origin()
def cancelar_pedido(pedido_id):
    """
    Cancela un pedido.
    
    POST /api/pedidos/{id}/cancelar
    Body: { "motivo": "Cliente solicitó cancelación" }
    """
    try:
        user_id = get_user_id()
        data = request.get_json() or {}
        motivo = data.get('motivo', 'Cancelado por el negocio')
        
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404
        
        if not pedido.puede_cancelar:
            return jsonify({
                "success": False, 
                "error": f"No se puede cancelar un pedido en estado: {pedido.estado}"
            }), 400
        
        pedido.cancelar(motivo=motivo, usuario_id=user_id)
        db.session.commit()
        
        logger.info(f"Pedido {pedido.codigo_pedido} cancelado: {motivo}")
        
        return jsonify({
            "success": True,
            "message": "Pedido cancelado",
            "pedido": {
                "id": pedido.id_pedido,
                "codigo": pedido.codigo_pedido,
                "estado": pedido.estado,
                "motivo_cancelacion": motivo
            }
        }), 200
        
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cancelando pedido: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# MARCAR COMO PAGADO
# ==========================================
@pedidos_api_bp.route('/pedidos/<int:pedido_id>/pago', methods=['POST'])
@cross_origin()
def marcar_pagado(pedido_id):
    """
    Marca un pedido como pagado.
    
    POST /api/pedidos/{id}/pago
    Body: { "referencia": "TXN-123456" }
    """
    try:
        data = request.get_json() or {}
        referencia = data.get('referencia')
        
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404
        
        pedido.marcar_pagado(referencia=referencia)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Pago registrado",
            "pedido": {
                "id": pedido.id_pedido,
                "estado_pago": pedido.estado_pago,
                "referencia_pago": pedido.referencia_pago
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error marcando pago: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# AGREGAR NOTA INTERNA
# ==========================================
@pedidos_api_bp.route('/pedidos/<int:pedido_id>/notas', methods=['POST'])
@cross_origin()
def agregar_nota(pedido_id):
    """
    Agrega una nota interna al pedido.
    
    POST /api/pedidos/{id}/notas
    Body: { "nota": "Cliente solicitó entrega después de las 6pm" }
    """
    try:
        data = request.get_json() or {}
        nota = data.get('nota')
        
        if not nota:
            return jsonify({"success": False, "error": "Nota requerida"}), 400
        
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404
        
        # Concatenar nota si ya existe
        if pedido.notas_vendedor:
            pedido.notas_vendedor += f"\n[{datetime.now().strftime('%d/%m %H:%M')}] {nota}"
        else:
            pedido.notas_vendedor = f"[{datetime.now().strftime('%d/%m %H:%M')}] {nota}"
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Nota agregada",
            "notas": pedido.notas_vendedor
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error agregando nota: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ESTADÍSTICAS DE PEDIDOS
# ==========================================
@pedidos_api_bp.route('/pedidos/negocio/<int:negocio_id>/stats', methods=['GET'])
@cross_origin()
def estadisticas_pedidos(negocio_id):
    """
    Obtiene estadísticas de pedidos del negocio.
    
    GET /api/pedidos/negocio/{id}/stats
    """
    try:
        # Contar por estado
        stats_estado = db.session.query(
            Pedido.estado,
            func.count(Pedido.id_pedido).label('cantidad'),
            func.sum(Pedido.total).label('total')
        ).filter_by(
            negocio_id=negocio_id
        ).group_by(
            Pedido.estado
        ).all()
        
        por_estado = {}
        total_pedidos = 0
        total_ventas = 0
        
        for estado, cantidad, total in stats_estado:
            por_estado[estado] = {
                'cantidad': cantidad,
                'total': float(total or 0)
            }
            total_pedidos += cantidad
            if estado not in ['cancelado', 'devuelto']:
                total_ventas += float(total or 0)
        
        # Pedidos de hoy
        hoy = datetime.now().date()
        pedidos_hoy = Pedido.query.filter(
            Pedido.negocio_id == negocio_id,
            func.date(Pedido.fecha_pedido) == hoy
        ).count()
        
        # Ventas de hoy (solo confirmados/entregados)
        ventas_hoy = db.session.query(
            func.sum(Pedido.total)
        ).filter(
            Pedido.negocio_id == negocio_id,
            func.date(Pedido.fecha_pedido) == hoy,
            Pedido.estado.in_(['confirmado', 'preparando', 'enviado', 'entregado'])
        ).scalar() or 0
        
        return jsonify({
            "success": True,
            "stats": {
                "total_pedidos": total_pedidos,
                "total_ventas": total_ventas,
                "por_estado": por_estado,
                "hoy": {
                    "pedidos": pedidos_hoy,
                    "ventas": float(ventas_hoy)
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error en estadísticas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# HISTORIAL DE UN PEDIDO
# ==========================================
@pedidos_api_bp.route('/pedidos/<int:pedido_id>/historial', methods=['GET'])
@cross_origin()
def historial_pedido(pedido_id):
    """
    Obtiene el historial de cambios de un pedido.
    
    GET /api/pedidos/{id}/historial
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404
        
        historial = PedidoHistorial.query.filter_by(
            pedido_id=pedido_id
        ).order_by(
            PedidoHistorial.fecha.desc()
        ).all()
        
        return jsonify({
            "success": True,
            "historial": [h.to_dict() for h in historial]
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# BUSCAR PEDIDO POR CÓDIGO
# ==========================================
@pedidos_api_bp.route('/pedidos/buscar', methods=['GET'])
@cross_origin()
def buscar_pedido():
    """
    Busca un pedido por código o teléfono del cliente.
    
    GET /api/pedidos/buscar?codigo=PED-2024-0001
    GET /api/pedidos/buscar?telefono=3001234567&negocio_id=4
    """
    try:
        codigo = request.args.get('codigo')
        telefono = request.args.get('telefono')
        negocio_id = request.args.get('negocio_id', type=int)
        
        if codigo:
            pedido = Pedido.query.filter_by(codigo_pedido=codigo).first()
            if pedido:
                return jsonify({
                    "success": True,
                    "pedido": pedido.to_dict()
                }), 200
            else:
                return jsonify({"success": False, "error": "Pedido no encontrado"}), 404
        
        if telefono:
            query = Pedido.query.filter(
                Pedido.datos_comprador['telefono'].astext == telefono
            )
            if negocio_id:
                query = query.filter_by(negocio_id=negocio_id)
            
            pedidos = query.order_by(Pedido.fecha_pedido.desc()).limit(10).all()
            
            return jsonify({
                "success": True,
                "pedidos": [p.to_dict_lista() for p in pedidos],
                "total": len(pedidos)
            }), 200
        
        return jsonify({"success": False, "error": "Proporciona código o teléfono"}), 400
        
    except Exception as e:
        logger.error(f"Error buscando pedido: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# HEALTH CHECK
# ==========================================
@pedidos_api_bp.route('/pedidos/health', methods=['GET'])
def pedidos_health():
    return jsonify({
        "status": "online",
        "module": "pedidos_api",
        "version": "1.0.0"
    }), 200