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
TUKOMERCIO - Pedidos API v2.0
Gestión completa de pedidos para el dueño del negocio
★ NUEVO v2.0: Guías de envío, Devoluciones, Movimientos de stock
Ubicación: src/api/tiendas/pedidos_api.py
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from sqlalchemy import func, text
from src.models.database import db
from src.models.compradores.pedido import Pedido, PedidoHistorial

# ★ NUEVO v2.0: Modelos para stock y contabilidad
try:
    from src.models.colombia_data.contabilidad.operaciones_y_catalogo import (
        TransaccionOperativa,
        MovimientoStock,
        ProductoCatalogo
    )
    TIENE_TRANSACCIONES = True
except ImportError:
    TIENE_TRANSACCIONES = False
    logging.warning("⚠️ Modelos contables no disponibles en pedidos_api")

logger = logging.getLogger(__name__)

pedidos_api_bp = Blueprint('tiendas_pedidos_bp', __name__, url_prefix='/api')


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
        estado = request.args.get('estado')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        orden = request.args.get('orden', 'desc')

        query = Pedido.query.filter_by(negocio_id=negocio_id)

        if estado and estado != 'todos':
            query = query.filter_by(estado=estado)

        if orden == 'asc':
            query = query.order_by(Pedido.fecha_pedido.asc())
        else:
            query = query.order_by(Pedido.fecha_pedido.desc())

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

        if nuevo_estado not in Pedido.ESTADOS:
            return jsonify({
                "success": False,
                "error": f"Estado inválido. Válidos: {list(Pedido.ESTADOS.keys())}"
            }), 400

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

        estado_anterior = pedido.estado
        pedido.cancelar(motivo=motivo, usuario_id=user_id)

        # ★ NUEVO v2.0: Revertir transacción y stock si ya estaba confirmado
        if estado_anterior == 'confirmado' and TIENE_TRANSACCIONES:
            try:
                contra = TransaccionOperativa(
                    negocio_id=pedido.negocio_id,
                    usuario_id=user_id or 1,
                    sucursal_id=pedido.sucursal_id or 1,
                    tipo='DEVOLUCION',
                    concepto=f"Cancelación Pedido #{pedido.codigo_pedido} - {pedido.cliente_nombre}",
                    monto=float(pedido.total),
                    categoria='Devoluciones',
                    metodo_pago=pedido.metodo_pago or 'Efectivo',
                    notas=f"Motivo: {motivo}"
                )
                db.session.add(contra)
            except Exception as e:
                logger.error(f"⚠️ Error en contra-transacción: {e}")

            try:
                for item in (pedido.productos or []):
                    producto_id = item.get('id') or item.get('id_producto')
                    cantidad = item.get('cantidad', 1)
                    if not producto_id:
                        continue
                    producto = ProductoCatalogo.query.get(producto_id)
                    if not producto:
                        continue
                    stock_anterior = producto.stock
                    producto.stock = producto.stock + cantidad
                    movimiento = MovimientoStock(
                        producto_id=producto_id,
                        usuario_id=user_id or 1,
                        negocio_id=pedido.negocio_id,
                        sucursal_id=pedido.sucursal_id or 1,
                        tipo='ENTRADA',
                        cantidad=cantidad,
                        stock_anterior=stock_anterior,
                        stock_nuevo=producto.stock,
                        nota=f"Devolución por cancelación Pedido #{pedido.codigo_pedido}"
                    )
                    db.session.add(movimiento)
            except Exception as e:
                logger.error(f"⚠️ Error devolviendo stock: {e}")

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
# ★ NUEVO v2.0: REGISTRAR GUÍA DE ENVÍO
# ==========================================
@pedidos_api_bp.route('/pedidos/<int:pedido_id>/enviar', methods=['POST'])
@cross_origin()
def registrar_guia(pedido_id):
    """
    POST /api/pedidos/{id}/enviar
    Body: {
        "numero_guia": "123456789",
        "transportadora": "Interrapidísimo",
        "url_tracking": "https://..." (opcional)
    }
    Registra la guía y cambia estado a 'enviado'.
    """
    try:
        user_id = get_user_id()
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400

        numero_guia = data.get('numero_guia', '').strip()
        transportadora = data.get('transportadora', '').strip()
        url_tracking = data.get('url_tracking', '').strip() or None

        if not numero_guia:
            return jsonify({"success": False, "error": "numero_guia es requerido"}), 400
        if not transportadora:
            return jsonify({"success": False, "error": "transportadora es requerido"}), 400

        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404

        if pedido.estado not in ['confirmado', 'preparando']:
            return jsonify({
                "success": False,
                "error": f"No se puede registrar guía en estado '{pedido.estado}'. Debe estar confirmado o en preparación."
            }), 400

        pedido.registrar_guia(
            numero_guia=numero_guia,
            transportadora=transportadora,
            url_tracking=url_tracking,
            usuario_id=user_id
        )

        db.session.commit()

        logger.info(f"🚚 Guía registrada: Pedido #{pedido.codigo_pedido} → {transportadora} {numero_guia}")

        return jsonify({
            "success": True,
            "message": f"Guía {numero_guia} registrada. Pedido marcado como enviado.",
            "pedido": {
                "id": pedido.id_pedido,
                "codigo": pedido.codigo_pedido,
                "estado": pedido.estado,
                "numero_guia": pedido.numero_guia,
                "transportadora": pedido.transportadora,
                "url_tracking": pedido.url_tracking,
                "fecha_envio": pedido.fecha_envio.isoformat() if pedido.fecha_envio else None
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error registrando guía: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ★ NUEVO v2.0: REGISTRAR DEVOLUCIÓN
# ==========================================
@pedidos_api_bp.route('/pedidos/<int:pedido_id>/devolucion', methods=['POST'])
@cross_origin()
def registrar_devolucion(pedido_id):
    """
    POST /api/pedidos/{id}/devolucion
    Body: {
        "motivo": "rechazo_cliente",
        "notas": "El cliente no tenía el dinero",
        "numero_guia_devolucion": "987654321" (opcional),
        "transportadora": "Interrapidísimo" (opcional)
    }
    Motivos: rechazo_cliente | direccion_errada | producto_dañado |
             cliente_no_tenia_dinero | otro
    """
    try:
        user_id = get_user_id()
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "Datos requeridos"}), 400

        motivo = data.get('motivo', 'otro')
        notas = data.get('notas', '')
        numero_guia_dev = data.get('numero_guia_devolucion', '').strip() or None
        transportadora = data.get('transportadora', '').strip() or None

        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404

        if not pedido.puede_registrar_devolucion:
            return jsonify({
                "success": False,
                "error": f"No se puede registrar devolución en estado '{pedido.estado}'. Debe estar enviado, en camino o entregado."
            }), 400

        # Insertar en tabla devoluciones
        db.session.execute(text("""
            INSERT INTO devoluciones
                (pedido_id, negocio_id, numero_guia_devolucion, transportadora,
                 motivo, estado, notas, fecha_solicitud, producto_reingresado)
            VALUES
                (:pedido_id, :negocio_id, :numero_guia, :transportadora,
                 :motivo, 'en_transito', :notas, NOW(), false)
        """), {
            'pedido_id': pedido_id,
            'negocio_id': pedido.negocio_id,
            'numero_guia': numero_guia_dev,
            'transportadora': transportadora or pedido.transportadora,
            'motivo': motivo,
            'notas': notas
        })

        # Cambiar estado del pedido
        pedido.cambiar_estado(
            'devuelto',
            usuario_id=user_id,
            comentario=f"Devolución registrada. Motivo: {motivo}. {notas}"
        )

        db.session.commit()

        logger.info(f"↩️ Devolución registrada: Pedido #{pedido.codigo_pedido} - {motivo}")

        return jsonify({
            "success": True,
            "message": "Devolución registrada. El pedido quedó marcado como devuelto.",
            "pedido": {
                "id": pedido.id_pedido,
                "codigo": pedido.codigo_pedido,
                "estado": pedido.estado,
                "motivo_devolucion": motivo
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error registrando devolución: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ★ NUEVO v2.0: RECIBIR DEVOLUCIÓN
# ==========================================
@pedidos_api_bp.route('/pedidos/devolucion/<int:devolucion_id>/recibir', methods=['POST'])
@cross_origin()
def recibir_devolucion(devolucion_id):
    """
    POST /api/pedidos/devolucion/{id}/recibir
    Body: {
        "reingresar_inventario": true,
        "notas": "Producto en buen estado"
    }
    Si reingresar_inventario=true devuelve el stock.
    Si reingresar_inventario=false solo da de baja (producto dañado).
    """
    try:
        user_id = get_user_id()
        data = request.get_json() or {}

        reingresar = data.get('reingresar_inventario', True)
        notas = data.get('notas', '')

        # Obtener devolución con datos del pedido
        result = db.session.execute(text("""
            SELECT d.*, p.negocio_id, p.codigo_pedido, p.productos,
                   p.sucursal_id, p.total, p.metodo_pago
            FROM devoluciones d
            JOIN pedidos p ON d.pedido_id = p.id_pedido
            WHERE d.id_devolucion = :id
        """), {'id': devolucion_id}).fetchone()

        if not result:
            return jsonify({"success": False, "error": "Devolución no encontrada"}), 404

        if result.estado != 'en_transito':
            return jsonify({
                "success": False,
                "error": f"La devolución ya fue procesada (estado: {result.estado})"
            }), 400

        negocio_id = result.negocio_id
        nuevo_estado = 'reingresado_inventario' if reingresar else 'dado_de_baja'

        # Actualizar devolución
        db.session.execute(text("""
            UPDATE devoluciones
            SET estado = :estado,
                fecha_recepcion = NOW(),
                producto_reingresado = :reingresado,
                notas = COALESCE(notas || ' | ', '') || :notas
            WHERE id_devolucion = :id
        """), {
            'estado': nuevo_estado,
            'reingresado': reingresar,
            'notas': notas,
            'id': devolucion_id
        })

        # Reingresar stock si aplica
        if reingresar and TIENE_TRANSACCIONES:
            import json
            productos = result.productos
            if isinstance(productos, str):
                productos = json.loads(productos)

            for item in (productos or []):
                producto_id = item.get('id') or item.get('id_producto')
                cantidad = item.get('cantidad', 1)
                if not producto_id:
                    continue
                producto = ProductoCatalogo.query.get(producto_id)
                if not producto:
                    continue
                stock_anterior = producto.stock
                producto.stock = producto.stock + cantidad
                movimiento = MovimientoStock(
                    producto_id=producto_id,
                    usuario_id=user_id or 1,
                    negocio_id=negocio_id,
                    sucursal_id=result.sucursal_id or 1,
                    tipo='ENTRADA',
                    cantidad=cantidad,
                    stock_anterior=stock_anterior,
                    stock_nuevo=producto.stock,
                    nota=f"Reingreso por devolución ID#{devolucion_id}"
                )
                db.session.add(movimiento)
                logger.info(f"📦 Stock reingresado {producto.nombre}: {stock_anterior} → {producto.stock}")

        # Contra-transacción contable
        if TIENE_TRANSACCIONES:
            try:
                contra = TransaccionOperativa(
                    negocio_id=negocio_id,
                    usuario_id=user_id or 1,
                    sucursal_id=result.sucursal_id or 1,
                    tipo='DEVOLUCION',
                    concepto=f"Devolución recibida Pedido #{result.codigo_pedido}",
                    monto=float(result.total),
                    categoria='Devoluciones',
                    metodo_pago=result.metodo_pago or 'Efectivo',
                    notas=f"Motivo: {result.motivo}. {notas}"
                )
                db.session.add(contra)
            except Exception as e:
                logger.error(f"⚠️ Error registrando contra-transacción: {e}")

        db.session.commit()

        accion = "reingresado al inventario" if reingresar else "dado de baja"
        logger.info(f"✅ Devolución #{devolucion_id} recibida y {accion}")

        return jsonify({
            "success": True,
            "message": f"Devolución recibida. Producto {accion}.",
            "devolucion_id": devolucion_id,
            "estado": nuevo_estado,
            "producto_reingresado": reingresar
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error recibiendo devolución: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ★ NUEVO v2.0: LISTAR DEVOLUCIONES
# ==========================================
@pedidos_api_bp.route('/pedidos/negocio/<int:negocio_id>/devoluciones', methods=['GET'])
@cross_origin()
def listar_devoluciones(negocio_id):
    """
    GET /api/pedidos/negocio/{id}/devoluciones
    """
    try:
        rows = db.session.execute(text("""
            SELECT
                d.id_devolucion, d.pedido_id, d.numero_guia_devolucion,
                d.transportadora, d.motivo, d.estado, d.notas,
                d.fecha_solicitud, d.fecha_recepcion, d.producto_reingresado,
                p.codigo_pedido, p.total,
                p.datos_comprador->>'nombre' as cliente_nombre,
                p.datos_envio->>'ciudad' as ciudad
            FROM devoluciones d
            JOIN pedidos p ON d.pedido_id = p.id_pedido
            WHERE d.negocio_id = :negocio_id
            ORDER BY d.fecha_solicitud DESC
        """), {'negocio_id': negocio_id}).fetchall()

        devoluciones = [{
            "id_devolucion": r.id_devolucion,
            "pedido_id": r.pedido_id,
            "codigo_pedido": r.codigo_pedido,
            "cliente_nombre": r.cliente_nombre,
            "ciudad": r.ciudad,
            "total": float(r.total) if r.total else 0,
            "numero_guia_devolucion": r.numero_guia_devolucion,
            "transportadora": r.transportadora,
            "motivo": r.motivo,
            "estado": r.estado,
            "notas": r.notas,
            "producto_reingresado": r.producto_reingresado,
            "fecha_solicitud": r.fecha_solicitud.isoformat() if r.fecha_solicitud else None,
            "fecha_recepcion": r.fecha_recepcion.isoformat() if r.fecha_recepcion else None
        } for r in rows]

        return jsonify({
            "success": True,
            "devoluciones": devoluciones,
            "total": len(devoluciones)
        }), 200

    except Exception as e:
        logger.error(f"Error listando devoluciones: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ESTADÍSTICAS DE PEDIDOS
# ==========================================
@pedidos_api_bp.route('/pedidos/negocio/<int:negocio_id>/stats', methods=['GET'])
@cross_origin()
def estadisticas_pedidos(negocio_id):
    """
    GET /api/pedidos/negocio/{id}/stats
    """
    try:
        stats_estado = db.session.query(
            Pedido.estado,
            func.count(Pedido.id_pedido).label('cantidad'),
            func.sum(Pedido.total).label('total')
        ).filter_by(negocio_id=negocio_id).group_by(Pedido.estado).all()

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

        hoy = datetime.now().date()
        pedidos_hoy = Pedido.query.filter(
            Pedido.negocio_id == negocio_id,
            func.date(Pedido.fecha_pedido) == hoy
        ).count()

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
    GET /api/pedidos/{id}/historial
    """
    try:
        pedido = Pedido.query.get(pedido_id)

        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404

        historial = PedidoHistorial.query.filter_by(
            pedido_id=pedido_id
        ).order_by(PedidoHistorial.fecha.desc()).all()

        return jsonify({
            "success": True,
            "historial": [h.to_dict() for h in historial]
        }), 200

    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# BUSCAR PEDIDO
# ==========================================
@pedidos_api_bp.route('/pedidos/buscar', methods=['GET'])
@cross_origin()
def buscar_pedido():
    """
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
                return jsonify({"success": True, "pedido": pedido.to_dict()}), 200
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
        "version": "2.0.0"
    }), 200