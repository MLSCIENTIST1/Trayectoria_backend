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
from flask_login import login_required, current_user

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para solicitar más detalles
request_more_details_bp = Blueprint('request_more_details_bp', __name__)

@request_more_details_bp.route('/prueba', methods=['POST'])
@login_required
def more_details(notification_id):
    """
    API para agregar un mensaje con preguntas adicionales asociado a una notificación específica.
    Valida la autorización del usuario y guarda el mensaje en la base de datos.
    """
    logger.info(f"Procesando solicitud POST para agregar detalles a la notificación {notification_id}.")

    try:
        # Obtener las preguntas desde el cuerpo de la solicitud
        data = request.get_json()
        questions = data.get('questions', '').strip()
        logger.debug(f"Pregunta recibida: {questions}")

        if not questions:
            logger.warning("No se proporcionaron preguntas en la solicitud.")
            return jsonify({"error": "Por favor, escribe una pregunta antes de enviar."}), 400

        # Verificar si la notificación existe
        notification = Notification.query.get_or_404(notification_id)
        logger.debug(f"Notificación obtenida - ID: {notification.id}, Receptor: {notification.user_id}, Remitente: {notification.sender_id}")

        # Validar que el usuario esté autorizado
        if current_user.id_usuario not in [notification.user_id, notification.sender_id]:
            logger.warning(f"Acceso denegado: Usuario {current_user.id_usuario} no está autorizado para la notificación {notification_id}.")
            return jsonify({"error": "No estás autorizado para realizar esta acción."}), 403

        # Crear el mensaje en la base de datos
        message = Message(
            notification_id=notification_id,
            sender_id=current_user.id_usuario,
            receiver_id=notification.sender_id if current_user.id_usuario == notification.user_id else notification.user_id,
            content=questions
        )
        db.session.add(message)
        db.session.commit()
        logger.info(f"Mensaje agregado exitosamente a la conversación para la notificación {notification_id}.")

        return jsonify({"message": "Mensaje enviado exitosamente."}), 200

    except Exception as e:
        logger.exception(f"Error al agregar mensaje para la notificación {notification_id}.")
        db.session.rollback()
        return jsonify({"error": "Hubo un error al procesar tu solicitud."}), 500
