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

from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para solicitudes de contratación
contract_requests_bp = Blueprint('contract-requests-bp', __name__)

@contract_requests_bp.route('/prueba', methods=['POST'])
@login_required
def send_contract_request(candidato_id):
    """
    API para enviar solicitudes de contratación a un candidato.
    Devuelve el estado y detalles de la operación en formato JSON.
    """
    logger.info(f"Procesando solicitud POST para el candidato ID {candidato_id}")

    try:
        # Buscar al candidato
        candidato = Usuario.query.get_or_404(candidato_id)
        logger.debug(f"Candidato encontrado: {candidato.nombre}")
    except SQLAlchemyError:
        logger.exception("Error al buscar el candidato.")
        return jsonify({"error": "Error al buscar el candidato."}), 500

    # Obtener datos del cuerpo de la solicitud
    data = request.get_json()
    user_message = data.get('mensaje', '')
    id_service = data.get('id_service', None)

    if id_service:
        try:
            # Buscar detalles del servicio
            service_details = Servicio.query.filter_by(id_servicio=id_service, id_usuario=candidato.id_usuario).first()
            if not service_details:
                logger.warning("El servicio seleccionado no existe o no pertenece al candidato.")
                return jsonify({"error": "El servicio seleccionado no existe o no pertenece al candidato."}), 404
        except SQLAlchemyError:
            logger.exception("Error al buscar el servicio.")
            return jsonify({"error": "Error interno al buscar el servicio."}), 500
    else:
        service_details = None

    # Generar el mensaje de notificación
    if service_details:
        notification_message = (
            f'{current_user.nombre} te ha enviado una solicitud de contratación para el servicio: {service_details.nombre_servicio}. '
            f'Mensaje: {user_message}'
        )
    else:
        notification_message = (
            f'{current_user.nombre} te ha enviado una solicitud de contratación. '
            f'Mensaje: {user_message}'
        )

    logger.debug(f"Mensaje de notificación generado: {notification_message}")

    # Verificar notificaciones duplicadas
    if Notification.query.filter_by(user_id=candidato.id_usuario, message=notification_message).first():
        logger.warning("Notificación duplicada detectada.")
        return jsonify({"warning": "Ya existe una solicitud para este candidato."}), 400

    # Generar un nuevo request_id
    try:
        request_id = db.session.query(func.coalesce(func.max(Notification.request_id), 0) + 1).scalar()
        logger.debug(f"Nuevo request_id generado: {request_id}")
    except SQLAlchemyError:
        logger.exception("Error al generar request_id.")
        return jsonify({"error": "Error interno al generar el request_id."}), 500

    # Crear la notificación y registrar el mensaje
    try:
        new_notification = Notification.create_notification(
            user_id=candidato.id_usuario,
            sender_id=current_user.id_usuario,
            request_id=request_id,
            message=notification_message,
            params={'type': 'contract_request'},
            extra_data={"sender_id": current_user.id_usuario}
        )

        new_message = Message(
            notification_id=new_notification.id,
            sender_id=current_user.id_usuario,
            receiver_id=candidato.id_usuario,
            content=user_message
        )
        db.session.add(new_message)
        db.session.commit()

        logger.info(f"Notificación creada con ID {new_notification.id}")
        send_contract_request_notification(candidato.id_usuario, notification_message)

        return jsonify({
            "message": "Solicitud de contratación enviada exitosamente.",
            "notification_id": new_notification.id,
            "request_id": request_id
        }), 201

    except SQLAlchemyError:
        logger.exception("Error al registrar en la base de datos.")
        db.session.rollback()
        return jsonify({"error": "Error al registrar la solicitud."}), 500
