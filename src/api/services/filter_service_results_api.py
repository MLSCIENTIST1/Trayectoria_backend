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
from sqlalchemy import or_

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para resultados de filtro de servicio
filter_service_results_bp = Blueprint('filter_service_results_bp', __name__)

@filter_service_results_bp.route('/filter_service_results', methods=['POST'])
@login_required
def resultado_filtro_servicio():
    """
    API para filtrar servicios con base en la ciudad y la labor.
    Devuelve los servicios encontrados y los detalles del usuario asociado en formato JSON.
    """
    logger.info(f"Procesando solicitud POST para filtrar servicios del usuario {current_user.id_usuario}.")

    try:
        # Obtener parámetros de la solicitud
        ciudad = request.args.get('city')
        labor = request.args.get('job')

        logger.debug(f"Parámetros de búsqueda - Ciudad: {ciudad}, Labor: {labor}")

        # Construir consulta con filtros dinámicos
        query_servicios = Servicio.query
        condiciones = []

        if ciudad:
            condiciones.append(Servicio.categoria.ilike(f"%{ciudad}%"))
        if labor:
            condiciones.append(Servicio.nombre_servicio.ilike(f"%{labor}%"))

        if condiciones:
            query_servicios = query_servicios.filter(or_(*condiciones))

        servicios = query_servicios.all()

        # Validar si no hay resultados
        if not servicios:
            logger.info("No se encontraron servicios para los criterios proporcionados.")
            return jsonify({"mensaje": "No se encontraron servicios para los criterios proporcionados"}), 404

        # Construir resultados a devolver
        resultados = [
            {
                "servicio_id": servicio.id_servicio,
                "nombre_servicio": servicio.nombre_servicio,
                "descripcion": servicio.descripcion,
                "categoria": servicio.categoria,
                "precio": servicio.precio,
                "service_active": servicio.service_active,
                "datos_usuario": {
                    "usuario_id": servicio.id_usuario,
                    "nombre": Usuario.query.get(servicio.id_usuario).nombre,
                    "apellidos": Usuario.query.get(servicio.id_usuario).apellidos,
                    "correo": Usuario.query.get(servicio.id_usuario).correo,
                    "celular": Usuario.query.get(servicio.id_usuario).celular,
                    "ciudad": Usuario.query.get(servicio.id_usuario).ciudad,
                    "labor": Usuario.query.get(servicio.id_usuario).labor,
                    "calificaciones": [
                        {
                            "calificacion1": c.calificacion_recived_contratado1,
                            "calificacion2": c.calificacion_recived_contratado2,
                            "calificacion3": c.calificacion_recived_contratado3
                        }
                        for c in ServiceRatings.query.filter_by(servicio_id=servicio.id_servicio).all()
                    ]
                }
            }
            for servicio in servicios
        ]

        logger.info(f"Servicios encontrados y procesados con éxito. Total: {len(servicios)}")
        return jsonify({"resultados": resultados}), 200

    except Exception as e:
        logger.exception(f"Error al realizar la consulta: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
