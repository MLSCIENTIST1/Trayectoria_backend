# ═══════════════════════════════════════════════════════════════════════════════
# TUKOMERCIO — API de Reseñas de Productos v1.0
# ═══════════════════════════════════════════════════════════════════════════════
#
# Endpoints públicos (sin auth):
#   POST   /api/resenas/<negocio_id>/productos/<producto_id>   ← el comprador deja reseña
#   GET    /api/resenas/<negocio_id>/productos/<producto_id>   ← tienda pública pide reseñas
#   GET    /api/resenas/<negocio_id>/resumen                   ← rating general del negocio
#
# Endpoints del tendero (requieren X-Business-ID o sesión):
#   GET    /api/negocio/<negocio_id>/resenas                   ← lista para moderar
#   PUT    /api/negocio/<negocio_id>/resenas/<id>/moderar      ← aprobar / rechazar
#   DELETE /api/negocio/<negocio_id>/resenas/<id>              ← eliminar
#
# ═══════════════════════════════════════════════════════════════════════════════

import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from sqlalchemy import func

from src.models.database import db
from src.models import Negocio, ProductoCatalogo, ProductoReview

logger = logging.getLogger(__name__)

resenas_bp = Blueprint('resenas', __name__)

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _recalcular_rating(producto_id: int, negocio_id: int):
    """Recalcula rating_promedio y total_reviews en ProductoCatalogo."""
    resultado = db.session.query(
        func.avg(ProductoReview.rating).label('promedio'),
        func.count(ProductoReview.id).label('total')
    ).filter(
        ProductoReview.producto_id == producto_id,
        ProductoReview.negocio_id == negocio_id,
        ProductoReview.aprobado == True
    ).first()

    producto = ProductoCatalogo.query.get(producto_id)
    if producto:
        producto.rating_promedio = round(float(resultado.promedio or 0), 1)
        producto.total_reviews = resultado.total or 0


def _get_negocio_or_404(negocio_id):
    negocio = Negocio.query.get(negocio_id)
    if not negocio:
        return None, jsonify({'success': False, 'error': 'Negocio no encontrado'}), 404
    return negocio, None, None


# ─────────────────────────────────────────────────────────────
# POST — Crear reseña (público, el comprador)
# ─────────────────────────────────────────────────────────────

@resenas_bp.route('/resenas/<int:negocio_id>/productos/<int:producto_id>', methods=['POST', 'OPTIONS'])
@cross_origin()
def crear_resena(negocio_id, producto_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        data = request.get_json(force=True, silent=True) or {}

        rating = data.get('rating')
        if not rating or not isinstance(rating, int) or not (1 <= rating <= 5):
            return jsonify({'success': False, 'error': 'rating debe ser entero entre 1 y 5'}), 400

        nombre = (data.get('nombre') or '').strip()[:100] or 'Anónimo'
        email  = (data.get('email') or '').strip()[:150]
        titulo = (data.get('titulo') or '').strip()[:150]
        comentario = (data.get('comentario') or '').strip()

        # Verificar que el producto pertenece al negocio
        producto = ProductoCatalogo.query.filter_by(
            id_producto=producto_id, negocio_id=negocio_id
        ).first()
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404

        # Si viene pedido_id, marcar como verificado (compra comprobada)
        pedido_id = data.get('pedido_id')
        verificado = False
        if pedido_id:
            from src.models import Pedido
            pedido = Pedido.query.filter_by(
                id_pedido=pedido_id, negocio_id=negocio_id, estado='entregado'
            ).first()
            verificado = pedido is not None

        # Evitar spam: máx 1 reseña por email por producto
        if email:
            existente = ProductoReview.query.filter_by(
                producto_id=producto_id, negocio_id=negocio_id, cliente_email=email
            ).first()
            if existente:
                return jsonify({'success': False, 'error': 'Ya dejaste una reseña para este producto'}), 409

        resena = ProductoReview(
            producto_id=producto_id,
            negocio_id=negocio_id,
            cliente_nombre=nombre,
            cliente_email=email,
            rating=rating,
            titulo=titulo,
            comentario=comentario,
            verificado=verificado,
            # Las reseñas de compradores verificados se aprueban automáticamente
            aprobado=verificado,
            fecha=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
        db.session.add(resena)

        if verificado:
            _recalcular_rating(producto_id, negocio_id)

        db.session.commit()

        logger.info(f"⭐ Reseña creada — producto {producto_id}, negocio {negocio_id}, rating {rating}, verificado={verificado}")

        return jsonify({
            'success': True,
            'message': '¡Gracias por tu reseña!' + (' Fue publicada de inmediato.' if verificado else ' Será revisada pronto.'),
            'verificado': verificado,
            'aprobado': verificado,
            'resena': resena.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error creando reseña: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ─────────────────────────────────────────────────────────────
# GET — Reseñas públicas de un producto
# ─────────────────────────────────────────────────────────────

@resenas_bp.route('/resenas/<int:negocio_id>/productos/<int:producto_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
def listar_resenas_producto(negocio_id, producto_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        limit  = min(int(request.args.get('limit', 10)), 50)
        offset = int(request.args.get('offset', 0))

        query = ProductoReview.query.filter_by(
            producto_id=producto_id,
            negocio_id=negocio_id,
            aprobado=True
        ).order_by(
            ProductoReview.verificado.desc(),   # verificadas primero
            ProductoReview.fecha.desc()
        )

        total = query.count()
        resenas = query.offset(offset).limit(limit).all()

        # Resumen de estrellas
        dist = {str(i): 0 for i in range(1, 6)}
        todas = ProductoReview.query.filter_by(
            producto_id=producto_id, negocio_id=negocio_id, aprobado=True
        ).with_entities(ProductoReview.rating).all()
        for r in todas:
            dist[str(r.rating)] = dist.get(str(r.rating), 0) + 1

        promedio = round(sum(int(k) * v for k, v in dist.items()) / total, 1) if total else 0

        return jsonify({
            'success': True,
            'total': total,
            'promedio': promedio,
            'distribucion': dist,
            'resenas': [r.to_dict() for r in resenas]
        })

    except Exception as e:
        logger.error(f"❌ Error listando reseñas: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ─────────────────────────────────────────────────────────────
# GET — Resumen de rating del negocio (todas sus reseñas)
# ─────────────────────────────────────────────────────────────

@resenas_bp.route('/resenas/<int:negocio_id>/resumen', methods=['GET', 'OPTIONS'])
@cross_origin()
def resumen_negocio(negocio_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        resultado = db.session.query(
            func.avg(ProductoReview.rating).label('promedio'),
            func.count(ProductoReview.id).label('total')
        ).filter(
            ProductoReview.negocio_id == negocio_id,
            ProductoReview.aprobado == True
        ).first()

        return jsonify({
            'success': True,
            'promedio': round(float(resultado.promedio or 0), 1),
            'total': resultado.total or 0
        })
    except Exception as e:
        logger.error(f"❌ Error resumen reseñas: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ─────────────────────────────────────────────────────────────
# GET — Panel tendero: todas sus reseñas (pendientes + aprobadas)
# ─────────────────────────────────────────────────────────────

@resenas_bp.route('/negocio/<int:negocio_id>/resenas', methods=['GET', 'OPTIONS'])
@cross_origin()
def listar_resenas_negocio(negocio_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        solo_pendientes = request.args.get('pendientes') == '1'
        limit  = min(int(request.args.get('limit', 30)), 100)
        offset = int(request.args.get('offset', 0))

        query = ProductoReview.query.filter_by(negocio_id=negocio_id)
        if solo_pendientes:
            query = query.filter_by(aprobado=False)
        query = query.order_by(ProductoReview.created_at.desc())

        total = query.count()
        resenas = query.offset(offset).limit(limit).all()

        # Enriquecer con nombre del producto
        result = []
        for r in resenas:
            d = r.to_dict()
            prod = ProductoCatalogo.query.get(r.producto_id)
            d['producto_nombre'] = prod.nombre if prod else '(eliminado)'
            result.append(d)

        pendientes_count = ProductoReview.query.filter_by(
            negocio_id=negocio_id, aprobado=False
        ).count()

        return jsonify({
            'success': True,
            'total': total,
            'pendientes': pendientes_count,
            'resenas': result
        })

    except Exception as e:
        logger.error(f"❌ Error listando reseñas negocio: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ─────────────────────────────────────────────────────────────
# PUT — Moderar reseña (aprobar / rechazar)
# ─────────────────────────────────────────────────────────────

@resenas_bp.route('/negocio/<int:negocio_id>/resenas/<int:resena_id>/moderar', methods=['PUT', 'OPTIONS'])
@cross_origin()
def moderar_resena(negocio_id, resena_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        data = request.get_json(force=True, silent=True) or {}
        accion = data.get('accion')  # 'aprobar' | 'rechazar'
        if accion not in ('aprobar', 'rechazar'):
            return jsonify({'success': False, 'error': "accion debe ser 'aprobar' o 'rechazar'"}), 400

        resena = ProductoReview.query.filter_by(id=resena_id, negocio_id=negocio_id).first()
        if not resena:
            return jsonify({'success': False, 'error': 'Reseña no encontrada'}), 404

        resena.aprobado = (accion == 'aprobar')
        _recalcular_rating(resena.producto_id, negocio_id)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f"Reseña {'aprobada ✅' if resena.aprobado else 'rechazada ❌'}",
            'aprobado': resena.aprobado
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error moderando reseña: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ─────────────────────────────────────────────────────────────
# DELETE — Eliminar reseña
# ─────────────────────────────────────────────────────────────

@resenas_bp.route('/negocio/<int:negocio_id>/resenas/<int:resena_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin()
def eliminar_resena(negocio_id, resena_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        resena = ProductoReview.query.filter_by(id=resena_id, negocio_id=negocio_id).first()
        if not resena:
            return jsonify({'success': False, 'error': 'Reseña no encontrada'}), 404

        producto_id = resena.producto_id
        db.session.delete(resena)
        _recalcular_rating(producto_id, negocio_id)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Reseña eliminada'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error eliminando reseña: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500
