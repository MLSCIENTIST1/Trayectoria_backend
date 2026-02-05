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






import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para la página de visualización de servicios
view_service_page_bp = Blueprint('view_service_page_bp', __name__)

@view_service_page_bp.route('/update_service/<int:service_id>', methods=['POST'])
@login_required
def update_other_service(service_id):
    """
    API para actualizar un servicio específico asociado al usuario actual.
    Permite la actualización de campos específicos enviados desde el frontend.
    """
    logger.info(f"Procesando solicitud POST para actualizar el servicio con ID: {service_id}")

    try:
        # Obtener datos enviados desde el frontend
        data = request.get_json()
        logger.debug(f"Datos recibidos para actualizar el servicio {service_id}: {data}")

        # Buscar el servicio asociado al usuario actual
        service = Servicio.query.filter_by(id_servicio=service_id, id_usuario=current_user.id_usuario).first()

        if service:
            # Actualizar solo los campos presentes en `data`
            if 'service_name' in data and data['service_name']:
                service.nombre_servicio = data['service_name']
                logger.debug(f"Nombre del servicio actualizado: {service.nombre_servicio}")
            if 'description' in data and data['description']:
                service.descripcion = data['description']
                logger.debug(f"Descripción del servicio actualizada: {service.descripcion}")
            if 'category' in data and data['category']:
                service.categoria = data['category']
                logger.debug(f"Categoría del servicio actualizada: {service.categoria}")
            if 'price' in data and data['price'] is not None:
                service.precio = float(data['price'])
                logger.debug(f"Precio del servicio actualizado: {service.precio}")

            # Guardar los cambios
            db.session.commit()
            logger.info(f"Servicio con ID {service_id} actualizado con éxito.")
            return jsonify({"message": "Servicio actualizado con éxito."}), 200

        else:
            logger.warning(f"El servicio con ID {service_id} no existe o no pertenece al usuario.")
            return jsonify({"error": "El servicio no existe o no pertenece al usuario."}), 400

    except SQLAlchemyError as e:
        logger.error(f"Error al actualizar el servicio en la base de datos: {e}")
        return jsonify({"error": "Hubo un problema al actualizar el servicio en la base de datos."}), 500

    except Exception as e:
        logger.exception("Error inesperado al actualizar el servicio.")
        return jsonify({"error": "Hubo un problema al actualizar el servicio."}), 500
