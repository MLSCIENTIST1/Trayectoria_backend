from flask import Blueprint, render_template, request, url_for
from flask_login import login_required
from src.models.usuarios import Usuario
from src.models.usuarios import Servicio

from sqlalchemy import or_

import logging
from src.models.colombia_data.ratings import ServiceOverallScores
from src.models.database import db

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

search_bp = Blueprint('search', __name__)

@search_bp.route('/search/resultado_filtro_primera_busqueda', methods=['GET', 'POST'])
@login_required
def resultado_filtro_primera_busqueda():
    ciudad = request.args.get('ciudad')
    labor = request.args.get('labor')

    # Consulta de servicios
    query_servicios = Servicio.query
    condiciones = []

    if ciudad:
        condiciones.append(Servicio.categoria.ilike(f"%{ciudad}%"))  # Filtrar por categoría o ciudad
    if labor:
        condiciones.append(Servicio.nombre_servicio.ilike(f"%{labor}%"))  # Filtrar por nombre del servicio

    if condiciones:
        query_servicios = query_servicios.filter(or_(*condiciones))
    
    servicios = query_servicios.all()

    # Combinar cada servicio con su usuario correspondiente
    resultados = [
        {
            "servicio": servicio,
            "usuario": Usuario.query.get(servicio.id_usuario)  # Consultar el usuario que ofrece el servicio
        }
        for servicio in servicios
    ]

    # Debugging para verificar los resultados encontrados
    logger.debug(f"Servicios encontrados: {len(servicios)}")
    logger.debug(f"Usuarios asociados: {len(resultados)}")

    # Renderizar la plantilla con los servicios encontrados y sus usuarios
    return render_template('resultado_filtro_primera_busqueda.html', resultados=resultados)

@search_bp.route('/detalle_candidato/<int:id_usuario>', methods=['GET', 'POST'])
@login_required
def detalle_candidato(id_usuario):
    # Buscar al usuario por su ID
    usuario = Usuario.query.get_or_404(id_usuario)

    # Obtener todos los servicios ofrecidos por el usuario
    servicios = Servicio.query.filter_by(id_usuario=id_usuario).all()

    # Calcular el puntaje promedio en la última labor como contratado
    calificacion = Calificacion.query.filter_by(usuario_id=id_usuario).first()
    puntaje_ultima_labor = None
    if calificacion:
        # Calcular promedio de las calificaciones si existen
        calificaciones_contratado = [
            calificacion.calificacion_recived_contratado1,
            calificacion.calificacion_recived_contratado2,
            calificacion.calificacion_recived_contratado3
        ]
        validas = [c for c in calificaciones_contratado if c is not None]
        if len(validas) == 3:  # Solo calcular si hay 3 calificaciones válidas
            puntaje_ultima_labor = sum(validas) / 3
            # Guardar el puntaje promedio en la base de datos
            calificacion.puntaje_por_labor = puntaje_ultima_labor
            db.session.commit()

    # Renderizar la página con los datos del usuario, servicios y puntaje
    return render_template(
        'detalle_candidato.html',
        usuario=usuario,
        servicios=servicios,
        puntaje_ultima_labor=puntaje_ultima_labor
    )