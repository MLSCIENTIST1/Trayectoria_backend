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
from sqlalchemy import and_, or_
from src.models.database import db
from src.models.usuarios import Usuario  # Relación con Usuario
from src.models.usuario_servicio import usuario_servicio  # Tabla intermedia
from src.models.colombia_data.colombia_data import Colombia  # Relación con Colombia
from src.models.colombia_data.ratings.service_ratings import ServiceRatings  # Relación con Ratings
from src.models.colombia_data.ratings.service_overall_scores import ServiceOverallScores  # Relación con Overall Scores
from src.models.etapa import Etapa  # Relación con Etapa

# Configuración del Logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Modelo y Blueprint cargados correctamente.")

# Asignación del Blueprint
calificaciones_recibidas_contractor_bp = Blueprint('calificaciones_recibidas_contractor_bp', __name__)

@calificaciones_recibidas_contractor_bp.route('/recibidas', methods=['POST'])
@login_required
def procesar_calificaciones_contractor():
    """
    API para obtener las calificaciones recibidas por el contractor en sus servicios.
    Devuelve una lista en formato JSON con las calificaciones relacionadas.
    """
    logger.info("Procesando solicitud POST para obtener calificaciones recibidas como contractor.")

    try:
        # Consultar las calificaciones relacionadas al contractor actual
        calificaciones = ServiceRatings.query.join(Servicio).filter(
            and_(
                Servicio.id_contratante == current_user.id_usuario,
                or_(
                    ServiceRatings.calificacion_recived_contratante1.isnot(None),
                    ServiceRatings.calificacion_recived_contratante2.isnot(None),
                    ServiceRatings.calificacion_recived_contratante3.isnot(None)
                )
            )
        ).all()

        logger.debug(f"Calificaciones recibidas como contractor: {[c.id_rating for c in calificaciones]}")

        # Crear una lista con los datos a devolver
        calificaciones_data = [
            {
                "id_rating": calificacion.id_rating,
                "calificacion1": calificacion.calificacion_recived_contratante1,
                "calificacion2": calificacion.calificacion_recived_contratante2,
                "calificacion3": calificacion.calificacion_recived_contratante3,
                "comentario": calificacion.comentary_employer_hired
            }
            for calificacion in calificaciones
        ]

        # Devolver datos en formato JSON
        return jsonify({
            "calificaciones": calificaciones_data,
            "rol": "contractor"
        }), 200

    except Exception as e:
        logger.exception("Error al obtener calificaciones recibidas como contractor.")
        return jsonify({"error": "Hubo un error al cargar las calificaciones."}), 500
