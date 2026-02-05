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

# Blueprint para calificar al contratante
rate_contractor_bp = Blueprint('rate_contractor_bp', __name__)

@rate_contractor_bp.route('/rate_contractor', methods=['POST'])
def rate_contratante(servicio_id):
    """
    API para permitir que un contratante califique un servicio,
    asegurándose de que el usuario tenga permiso y de que las calificaciones sean válidas.
    """
    logger.info(f"Procesando solicitud POST para calificar como contratante el servicio con ID: {servicio_id}")

    try:
        # Obtener el servicio
        servicio = Servicio.query.get_or_404(servicio_id)
        logger.debug(f"Servicio encontrado: {servicio}")

        # Validar que el usuario es el contratante
        if servicio.id_contratante != current_user.id_usuario:
            logger.warning(f"El usuario {current_user.id_usuario} no tiene permisos para calificar el servicio {servicio_id}.")
            return jsonify({"error": "No tienes permisos para calificar este servicio."}), 403

        # Obtener datos del formulario
        cal1 = request.json.get('cal_contratante1', type=int)
        cal2 = request.json.get('cal_contratante2', type=int)
        cal3 = request.json.get('cal_contratante3', type=int)
        comentario = request.json.get('comentario_contratante', type=str)
        logger.debug(f"Datos recibidos: cal1={cal1}, cal2={cal2}, cal3={cal3}, comentario={comentario}")

        # Validar valores
        if not (1 <= cal1 <= 10 and 1 <= cal2 <= 10 and 1 <= cal3 <= 10):
            logger.warning("Las calificaciones recibidas no están en el rango válido (1-10).")
            return jsonify({"error": "Las calificaciones deben estar entre 1 y 10."}), 400

        # Crear o actualizar la calificación
        calificacion = ServiceRatings.query.filter_by(servicio_id=servicio.id_servicio, usuario_id=current_user.id_usuario).first()
        if not calificacion:
            calificacion = ServiceRatings(
                servicio_id=servicio.id_servicio,
                usuario_id=current_user.id_usuario,
                calificacion_recived_contratante1=cal1,
                calificacion_recived_contratante2=cal2,
                calificacion_recived_contratante3=cal3,
                comentary_employer_hired=comentario
            )
            db.session.add(calificacion)
            logger.info("Nueva calificación creada con éxito.")
        else:
            calificacion.calificacion_recived_contratante1 = cal1
            calificacion.calificacion_recived_contratante2 = cal2
            calificacion.calificacion_recived_contratante3 = cal3
            calificacion.comentary_employer_hired = comentario
            logger.info("Calificación existente actualizada con éxito.")

        # Guardar cambios en la base de datos
        db.session.commit()
        logger.info("Cambios guardados en la base de datos.")
        return jsonify({"message": "Calificación como contratante guardada correctamente."}), 200

    except Exception as e:
        logger.exception("Error al procesar la calificación como contratante.")
        db.session.rollback()
        return jsonify({"error": "Hubo un error al procesar la calificación."}), 500

# pare
