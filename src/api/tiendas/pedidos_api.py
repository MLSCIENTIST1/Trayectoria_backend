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

tiendas_pedidos_bp = Blueprint('tiendas_pedidos_bp', __name__, url_prefix='/api')


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
@tiendas_pedidos_bp.route('/pedidos/negocio/<int:negocio_id>', methods=['GET'])
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
@tiendas_pedidos_bp.route('/pedidos/<int:pedido_id>', methods=['GET'])
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
@tiendas_pedidos_bp.route('/pedidos/<int:pedido_id>/estado', methods=['PUT', 'PATCH'])
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
# CORREGIR PEDIDO (editar total, productos, pago, notas)
# ==========================================
@tiendas_pedidos_bp.route('/pedidos/<int:pedido_id>/corregir', methods=['PATCH', 'OPTIONS'])
@cross_origin()
def corregir_pedido(pedido_id):
    """
    PATCH /api/pedidos/{id}/corregir
    Permite corregir datos de un pedido (total, productos, pago, notas).
    Solo disponible en estados que no sean 'entregado' o 'cancelado'.
    Body: {
        "productos": [...],   # lista completa de productos
        "subtotal": 0,
        "costo_envio": 0,
        "descuento": 0,
        "total": 0,
        "metodo_pago": "efectivo",
        "estado_pago": "pendiente",
        "notas_vendedor": "...",
        "motivo_correccion": "..."  # para auditoría en historial
    }
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    try:
        user_id = get_user_id()
        data = request.get_json() or {}

        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({"success": False, "error": "Pedido no encontrado"}), 404

        # No permitir editar pedidos ya cerrados
        if pedido.estado in ['entregado', 'cancelado']:
            return jsonify({
                "success": False,
                "error": f"No se puede corregir un pedido en estado '{pedido.estado}'"
            }), 400

        total_anterior = float(pedido.total or 0)
        motivo = data.get('motivo_correccion', 'Corrección manual').strip() or 'Corrección manual'

        # Actualizar productos si vienen
        if 'productos' in data and isinstance(data['productos'], list):
            pedido.productos = data['productos']

        # Actualizar totales si vienen
        if 'subtotal' in data:
            pedido.subtotal = float(data['subtotal'])
        if 'costo_envio' in data:
            pedido.costo_envio = float(data['costo_envio'])
        if 'descuento' in data:
            pedido.descuento = float(data['descuento'])
        if 'total' in data:
            pedido.total = float(data['total'])

        # Actualizar pago
        if 'metodo_pago' in data and data['metodo_pago']:
            pedido.metodo_pago = data['metodo_pago']
        if 'estado_pago' in data and data['estado_pago']:
            pedido.estado_pago = data['estado_pago']

        # Actualizar notas
        if 'notas_vendedor' in data:
            pedido.notas_vendedor = data['notas_vendedor']

        pedido.fecha_actualizacion = datetime.utcnow()

        # Registrar en historial del pedido
        historial = PedidoHistorial(
            pedido_id=pedido.id_pedido,
            usuario_id=user_id,
            accion='CORRECCION',
            descripcion=f"Corrección manual. {motivo}. Total: ${total_anterior:,.0f} → ${float(pedido.total):,.0f}"
        )
        db.session.add(historial)

        # Si cambió el total, actualizar también la TransaccionOperativa asociada
        if TIENE_TRANSACCIONES and abs(float(pedido.total) - total_anterior) > 0.01:
            try:
                tx = TransaccionOperativa.query.filter_by(
                    negocio_id=pedido.negocio_id
                ).filter(
                    TransaccionOperativa.concepto.ilike(f"%{pedido.codigo_pedido}%")
                ).order_by(TransaccionOperativa.fecha.desc()).first()

                if tx:
                    tx.monto = float(pedido.total)
                    tx.concepto = f"Pedido {pedido.codigo_pedido} [CORREGIDO: {motivo}]"
                    logger.info(f"💰 TransaccionOperativa actualizada: ${total_anterior} → ${pedido.total}")
            except Exception as tx_err:
                logger.warning(f"⚠️ No se pudo actualizar TransaccionOperativa: {tx_err}")

        db.session.commit()
        logger.info(f"✏️ Pedido {pedido.codigo_pedido} corregido. {motivo}")

        return jsonify({
            "success": True,
            "message": "Pedido corregido correctamente",
            "pedido": {
                "id": pedido.id_pedido,
                "codigo": pedido.codigo_pedido,
                "total": float(pedido.total),
                "estado_pago": pedido.estado_pago,
                "metodo_pago": pedido.metodo_pago,
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error corrigiendo pedido {pedido_id}: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# CANCELAR PEDIDO
# ==========================================
@tiendas_pedidos_bp.route('/pedidos/<int:pedido_id>/cancelar', methods=['POST'])
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
@tiendas_pedidos_bp.route('/pedidos/<int:pedido_id>/pago', methods=['POST'])
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
@tiendas_pedidos_bp.route('/pedidos/<int:pedido_id>/notas', methods=['POST'])
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
@tiendas_pedidos_bp.route('/pedidos/<int:pedido_id>/enviar', methods=['POST'])
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
@tiendas_pedidos_bp.route('/pedidos/<int:pedido_id>/devolucion', methods=['POST'])
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
@tiendas_pedidos_bp.route('/pedidos/devolucion/<int:devolucion_id>/recibir', methods=['POST'])
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
# ★ DEVOLUCIÓN LIBRE (sin pedido digital)
# ==========================================
@tiendas_pedidos_bp.route('/pedidos/devolucion/libre', methods=['POST', 'OPTIONS'])
@cross_origin()
def devolucion_libre():
    """
    POST /api/pedidos/devolucion/libre
    Para devoluciones de ventas informales (WhatsApp, efectivo, marketplace)
    que NO tienen pedido digital registrado.

    Body: {
        "negocio_id": 1,
        "cliente_nombre": "Juan Pérez",
        "producto_nombre": "Multímetro Digital",
        "producto_id": 42,           # opcional — para actualizar stock
        "cantidad": 1,
        "monto": 50000,
        "motivo": "rechazo_cliente",
        "notas": "...",
        "reingresar_inventario": true
    }
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        user_id    = get_user_id()
        data       = request.get_json() or {}

        negocio_id  = int(data.get('negocio_id') or 0)
        cliente     = data.get('cliente_nombre', 'Sin registrar').strip()
        producto_n  = data.get('producto_nombre', 'Producto').strip()
        producto_id = data.get('producto_id')
        cantidad    = int(data.get('cantidad') or 1)
        monto       = float(data.get('monto') or 0)
        motivo      = data.get('motivo', 'otro')
        notas       = data.get('notas', '').strip()
        reingresar  = bool(data.get('reingresar_inventario', True))

        if not negocio_id:
            return jsonify({"success": False, "error": "negocio_id requerido"}), 400
        if monto <= 0:
            return jsonify({"success": False, "error": "El monto debe ser mayor a 0"}), 400

        stock_reingresado = False

        # Asegurar que pedido_id sea nullable (migración suave, solo una vez)
        try:
            db.session.execute(text(
                "ALTER TABLE devoluciones ALTER COLUMN pedido_id DROP NOT NULL"
            ))
            db.session.execute(text("COMMIT"))
        except Exception:
            db.session.rollback()  # Ya es nullable o no existe la tabla — continúa

        # 1. Registrar en tabla devoluciones con pedido_id=NULL
        db.session.execute(text("""
            INSERT INTO devoluciones
                (pedido_id, negocio_id, motivo, estado, notas,
                 fecha_solicitud, fecha_recepcion, producto_reingresado)
            VALUES
                (NULL, :negocio_id, :motivo,
                 :estado, :notas,
                 NOW(), NOW(), :reingresado)
        """), {
            'negocio_id': negocio_id,
            'motivo': motivo,
            'estado': 'reingresado_inventario' if reingresar else 'dado_de_baja',
            'notas': f"Cliente: {cliente} | Producto: {producto_n} | {notas}".strip(' |'),
            'reingresado': reingresar
        })

        # 2. Reingresar stock si aplica y hay producto_id
        if reingresar and producto_id and TIENE_TRANSACCIONES:
            try:
                from src.models.colombia_data.contabilidad.operaciones_y_catalogo import (
                    ProductoCatalogo, MovimientoStock
                )
                producto = ProductoCatalogo.query.get(int(producto_id))
                if producto and producto.negocio_id == negocio_id:
                    stock_anterior = producto.stock
                    producto.stock = producto.stock + cantidad
                    mov = MovimientoStock(
                        producto_id=producto.id_producto,
                        usuario_id=user_id or 1,
                        negocio_id=negocio_id,
                        sucursal_id=1,
                        tipo='ENTRADA',
                        cantidad=cantidad,
                        stock_anterior=stock_anterior,
                        stock_nuevo=producto.stock,
                        nota=f"Reingreso por devolución libre | {producto_n} | Cliente: {cliente}"
                    )
                    db.session.add(mov)
                    stock_reingresado = True
                    logger.info(f"📦 Stock reingresado (dev libre) {producto.nombre}: {stock_anterior} → {producto.stock}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo reingresar stock: {e}")

        # 3. Transacción contable DEVOLUCION
        if TIENE_TRANSACCIONES:
            try:
                from src.models.colombia_data.contabilidad.operaciones_y_catalogo import TransaccionOperativa
                trans = TransaccionOperativa(
                    negocio_id=negocio_id,
                    usuario_id=user_id or 1,
                    sucursal_id=1,
                    tipo='DEVOLUCION',
                    concepto=f"Devolución libre: {producto_n} | Cliente: {cliente}",
                    monto=monto,
                    categoria='Devoluciones',
                    metodo_pago='Efectivo',
                    notas=f"Motivo: {motivo}. {notas}"
                )
                db.session.add(trans)
            except Exception as e:
                logger.warning(f"⚠️ No se pudo crear transacción contable: {e}")

        db.session.commit()

        accion = "reingresado al inventario" if reingresar else "dado de baja"
        logger.info(f"↩️ Devolución libre registrada | {producto_n} | Negocio: {negocio_id} | {accion}")

        return jsonify({
            "success": True,
            "message": f"Devolución registrada. Producto {accion}.",
            "stock_reingresado": stock_reingresado,
            "estado": "reingresado_inventario" if reingresar else "dado_de_baja"
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error devolucion libre: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# ★ NUEVO v2.0: LISTAR DEVOLUCIONES
# ==========================================
@tiendas_pedidos_bp.route('/pedidos/negocio/<int:negocio_id>/devoluciones', methods=['GET'])
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
            LEFT JOIN pedidos p ON d.pedido_id = p.id_pedido
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
@tiendas_pedidos_bp.route('/pedidos/negocio/<int:negocio_id>/stats', methods=['GET'])
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
@tiendas_pedidos_bp.route('/pedidos/<int:pedido_id>/historial', methods=['GET'])
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
@tiendas_pedidos_bp.route('/pedidos/buscar', methods=['GET'])
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


# ════════════════════════════════════════════════════════════════════════════
# ★ NUEVO v2.1: REGISTRO MANUAL DE VENTAS
# ────────────────────────────────────────────────────────────────────────────
# Permite registrar manualmente ventas que NO entraron por la tienda online:
#   • Marketplace de Facebook
#   • WhatsApp informal (sin pasar por el checkout web)
#   • Ventas a familia / amigos / referidos
#   • Ventas en local físico con envío
#   • Ventas por Instagram
#
# A diferencia del POS (venta.html) que solo registra "Público General",
# este endpoint acepta TODOS los datos del cliente, dirección, productos,
# guía de envío y permite especificar el estado inicial (porque una venta
# manual generalmente ya está confirmada o incluso enviada).
# ════════════════════════════════════════════════════════════════════════════
@tiendas_pedidos_bp.route('/pedidos/manual', methods=['POST', 'OPTIONS'])
@cross_origin()
def crear_pedido_manual():
    """
    POST /api/pedidos/manual

    Body JSON esperado:
    {
        "negocio_id": 4,
        "nombre_negocio": "Rodar",
        "slug_negocio": "rodar",

        "cliente": {
            "nombre": "Juan Pérez",
            "telefono": "+57 311 1234567",
            "correo": "juan@email.com",         (opcional)
            "documento": "1234567890"           (opcional)
        },

        "envio": {
            "ciudad": "Buenaventura",
            "departamento": "Valle del Cauca",
            "direccion": "Cra 5 #12-34",
            "barrio": "Centro",                  (opcional)
            "referencias": "Frente al parque"   (opcional)
        },

        "productos": [
            {"id": 12, "nombre": "Scanner V520",
             "precio": 85000, "cantidad": 1,
             "subtotal": 85000, "imagen_url": "...", "categoria": "..."}
        ],

        "subtotal": 85000,
        "costo_envio": 7500,
        "descuento": 0,                          (opcional)
        "total": 92500,

        "metodo_pago": "efectivo",
        "estado_pago": "pendiente",              (opcional, default 'pendiente')

        "origen": "marketplace",
        "metodo_contacto": "whatsapp",           (opcional)
        "notas_cliente": "Pidió empaque regalo", (opcional)
        "notas_vendedor": "Conocido del barrio", (opcional)

        "estado_inicial": "confirmado",          (opcional, default 'confirmado')
        "numero_guia": "999888777",              (opcional)
        "transportadora": "Interrapidisimo",     (opcional)
        "url_tracking": "https://..."            (opcional)
    }

    Estados iniciales válidos: pendiente, confirmado, preparando, enviado, entregado
    Orígenes válidos: web, whatsapp, app, marketplace, instagram, local, familia, referido, otro
    """
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200

    try:
        data = request.get_json(silent=True) or {}

        # ── Validación mínima ───────────────────────────────────────────────
        negocio_id = data.get('negocio_id')
        if not negocio_id:
            return jsonify({"success": False, "error": "negocio_id es requerido"}), 400

        cliente_data = data.get('cliente') or {}
        if not cliente_data.get('nombre'):
            return jsonify({"success": False, "error": "cliente.nombre es requerido"}), 400

        productos = data.get('productos') or []
        if not productos or not isinstance(productos, list):
            return jsonify({"success": False, "error": "productos debe ser una lista no vacía"}), 400

        envio_data = data.get('envio') or {}

        # ── Validar origen ──────────────────────────────────────────────────
        ORIGENES_VALIDOS = {
            'web', 'whatsapp', 'app',
            'marketplace', 'instagram', 'local',
            'familia', 'referido', 'otro'
        }
        origen = (data.get('origen') or 'otro').lower().strip()
        if origen not in ORIGENES_VALIDOS:
            origen = 'otro'

        # ── Validar estado inicial ──────────────────────────────────────────
        ESTADOS_INICIALES_VALIDOS = {
            'pendiente', 'confirmado', 'preparando', 'enviado', 'entregado'
        }
        estado_inicial = (data.get('estado_inicial') or 'confirmado').lower().strip()
        if estado_inicial not in ESTADOS_INICIALES_VALIDOS:
            estado_inicial = 'confirmado'

        # ── Snapshots simples (sin Comprador/DireccionComprador formales) ───
        datos_comprador = {
            'nombre':    cliente_data.get('nombre', '').strip(),
            'telefono':  cliente_data.get('telefono', '').strip(),
            'correo':    cliente_data.get('correo', '').strip(),
            'documento': cliente_data.get('documento', '').strip(),
        }

        datos_envio = {
            'tipo':          envio_data.get('tipo', 'domicilio'),
            'ciudad':        envio_data.get('ciudad', '').strip(),
            'departamento':  envio_data.get('departamento', '').strip(),
            'direccion':     envio_data.get('direccion', '').strip(),
            'barrio':        envio_data.get('barrio', '').strip(),
            'referencias':   envio_data.get('referencias', '').strip(),
        }

        negocio_data = {
            'id':     int(negocio_id),
            'slug':   data.get('slug_negocio', 'PED'),
            'nombre': data.get('nombre_negocio', ''),
        }

        # ── Crear pedido reutilizando el método del modelo ──────────────────
        pedido = Pedido.crear_pedido(
            comprador=datos_comprador,        # dict directo (acepta el método)
            direccion=datos_envio,            # dict directo
            negocio_data=negocio_data,
            productos=productos,
            subtotal=float(data.get('subtotal', 0)),
            costo_envio=float(data.get('costo_envio', 0)),
            total=float(data.get('total', 0)),
            metodo_pago=data.get('metodo_pago', 'efectivo'),
            notas_cliente=data.get('notas_cliente'),
            metodo_contacto=data.get('metodo_contacto', 'whatsapp'),
            origen=origen,
        )

        # ── Campos adicionales que el método base no setea ──────────────────
        if data.get('descuento'):
            try:
                pedido.descuento = float(data.get('descuento', 0))
            except (TypeError, ValueError):
                pass

        if data.get('estado_pago'):
            pedido.estado_pago = data['estado_pago']

        if data.get('notas_vendedor'):
            pedido.notas_vendedor = data['notas_vendedor']

        # Si trae guía/transportadora, las setea desde el inicio
        if data.get('numero_guia'):
            pedido.numero_guia = data['numero_guia']
        if data.get('transportadora'):
            pedido.transportadora = data['transportadora']
        if data.get('url_tracking'):
            pedido.url_tracking = data['url_tracking']

        # Flush para obtener id_pedido antes de cualquier historial
        db.session.flush()

        # ── Estado inicial: si no es 'pendiente', usamos cambiar_estado para
        #    que registre el cambio en el historial automáticamente ─────────
        if estado_inicial != 'pendiente':
            pedido.cambiar_estado(
                estado_inicial,
                usuario_id=get_user_id(),
                comentario=f'Venta manual registrada (origen: {origen})'
            )

        # Registrar entrada inicial en historial (origen visible para auditoría)
        hist_inicial = PedidoHistorial(
            pedido_id=pedido.id_pedido,
            estado_anterior=None,
            estado_nuevo=estado_inicial,
            comentario=f'Venta manual creada · canal: {origen}',
            usuario_id=get_user_id(),
        )
        db.session.add(hist_inicial)

        # ★ v2.2: Registrar transacción contable y descontar stock
        if TIENE_TRANSACCIONES:
            # Transacción operativa — aparece en contabilidad
            try:
                CATEGORIAS_ORIGEN = {
                    'marketplace': 'Venta Marketplace',
                    'whatsapp':    'Venta WhatsApp',
                    'instagram':   'Venta Instagram',
                    'local':       'Venta Local',
                    'familia':     'Venta Familia/Amigos',
                    'referido':    'Venta Referido',
                    'web':         'Ventas Online',
                }
                categoria = CATEGORIAS_ORIGEN.get(origen, 'Venta Manual')
                transaccion = TransaccionOperativa(
                    negocio_id=int(negocio_id),
                    usuario_id=get_user_id() or 1,
                    sucursal_id=pedido.sucursal_id or 1,
                    tipo='VENTA',
                    concepto=f"Venta manual #{pedido.codigo_pedido} – {datos_comprador['nombre']}",
                    monto=float(pedido.total or 0),
                    categoria=categoria,
                    metodo_pago=(data.get('metodo_pago') or 'efectivo').capitalize(),
                )
                db.session.add(transaccion)
                logger.info(f"💰 Transacción contable registrada: ${pedido.total} [{categoria}]")
            except Exception as e:
                logger.error(f"⚠️ Error registrando transacción contable en venta manual: {e}")

            # Descuento de inventario por producto
            try:
                for item in (productos or []):
                    producto_id = item.get('id') or item.get('id_producto')
                    cantidad = int(item.get('cantidad', 1))
                    if not producto_id or cantidad <= 0:
                        continue
                    producto = ProductoCatalogo.query.get(producto_id)
                    if not producto:
                        continue
                    stock_anterior = producto.stock
                    producto.stock = max(0, producto.stock - cantidad)
                    movimiento = MovimientoStock(
                        producto_id=producto_id,
                        usuario_id=get_user_id() or 1,
                        negocio_id=int(negocio_id),
                        sucursal_id=pedido.sucursal_id or 1,
                        tipo='SALIDA',
                        cantidad=cantidad,
                        stock_anterior=stock_anterior,
                        stock_nuevo=producto.stock,
                        nota=f"Venta manual #{pedido.codigo_pedido} ({origen})",
                    )
                    db.session.add(movimiento)
                    logger.info(f"📦 Stock {producto.nombre}: {stock_anterior} → {producto.stock}")
            except Exception as e:
                logger.error(f"⚠️ Error descontando stock en venta manual: {e}")

        db.session.commit()

        logger.info(
            f"✅ Venta manual creada: {pedido.codigo_pedido} "
            f"(origen={origen}, estado={estado_inicial}, total={pedido.total})"
        )

        return jsonify({
            "success": True,
            "message": "Venta manual registrada correctamente",
            "pedido": pedido.to_dict() if hasattr(pedido, 'to_dict') else {
                "id_pedido": pedido.id_pedido,
                "codigo_pedido": pedido.codigo_pedido,
                "estado": pedido.estado,
                "origen": pedido.origen,
                "total": float(pedido.total) if pedido.total else 0,
            }
        }), 201

    except ValueError as ve:
        db.session.rollback()
        logger.warning(f"Validación falló al crear venta manual: {ve}")
        return jsonify({"success": False, "error": str(ve)}), 400

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error creando venta manual: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# HEALTH CHECK
# ==========================================
@tiendas_pedidos_bp.route('/pedidos/health', methods=['GET'])
def pedidos_health():
    return jsonify({
        "status": "online",
        "module": "pedidos_api",
        "version": "2.1.0"
    }), 200