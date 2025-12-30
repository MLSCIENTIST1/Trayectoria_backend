import logging
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user
from src.models.servicio import Servicio
from src.models.colombia_data.ratings import ServiceRatings  # Reemplazo de Calificacion
from src.models.database import db
from sqlalchemy import or_, and_

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Crear Blueprint para la funcionalidad de calificación
calificar = Blueprint('calificar', __name__)

@calificar.route('/calificar/<int:servicio_id>', methods=['GET'])
def show_calificar(servicio_id):
    try:
        # Obtener el contrato específico basado en el servicio_id
        contrato = Servicio.query.get_or_404(servicio_id)

        # Validar que el usuario esté relacionado con el contrato
        if contrato.id_contratante != current_user.id_usuario and contrato.id_contratado != current_user.id_usuario:
            flash("No tienes acceso a este contrato.", "error")
            return redirect(url_for('dashboard.dashboard'))

        # Log de depuración
        logger.debug(f"Contrato cargado para calificar: ID Servicio {contrato.id_servicio}, Contratante {contrato.id_contratante}, Contratado {contrato.id_contratado}")

        # Pasar solo el contrato seleccionado al HTML
        return render_template('calificar.html', contracts=[contrato])  # Enviamos una lista con un único contrato
    except Exception as e:
        logger.exception("Error al cargar el contrato para calificar.")
        flash("Hubo un problema al cargar el contrato.", "error")
        return redirect(url_for('dashboard.dashboard')) 


@calificar.route('/rate_contratante/<int:servicio_id>', methods=['POST'])
def rate_contratante(servicio_id):
    try:
        servicio = Servicio.query.get_or_404(servicio_id)

        # Validar que el usuario es el contratante
        if servicio.id_contratante != current_user.id_usuario:
            flash("No tienes permisos para calificar este servicio.", "error")
            return redirect(url_for('calificar.show_calificar'))

        # Obtener datos del formulario
        cal1 = request.form.get('cal_contratante1', type=int)
        cal2 = request.form.get('cal_contratante2', type=int)
        cal3 = request.form.get('cal_contratante3', type=int)
        comentario = request.form.get('comentario_contratante', type=str)

        # Validar valores
        if not (1 <= cal1 <= 10 and 1 <= cal2 <= 10 and 1 <= cal3 <= 10):
            flash("Las calificaciones deben estar entre 1 y 10.", "error")
            return redirect(url_for('calificar.show_calificar'))

        # Crear o actualizar la calificación
        calificacion = ServiceRatings.query.filter_by(servicio_id=servicio.id_servicio, usuario_id=current_user.id_usuario).first()
        if not calificacion:
            calificacion = ServiceRatings(
                servicio_id=servicio.id_servicio,
                usuario_id=current_user.id_usuario,
                calificacion_recived_contratante1=cal1,
                calificacion_recived_contratante2=cal2,
                calificacion_recived_contratante3=cal3,
                comentary_employer_hired=comentario  # Columna correcta
            )
            db.session.add(calificacion)
        else:
            calificacion.calificacion_recived_contratante1 = cal1
            calificacion.calificacion_recived_contratante2 = cal2
            calificacion.calificacion_recived_contratante3 = cal3
            calificacion.comentary_employer_hired = comentario  # Columna correcta

        # Guardar cambios
        db.session.commit()
        flash("Calificación como contratante guardada correctamente.", "success")
    except Exception as e:
        logger.exception("Error al calificar como contratante.")
        db.session.rollback()
        flash("Hubo un error al procesar la calificación.", "error")

    return redirect(url_for('calificar.show_calificar'))


@calificar.route('/rate_contratado/<int:servicio_id>', methods=['POST'])
def rate_contratado(servicio_id):
    try:
        servicio = Servicio.query.get_or_404(servicio_id)

        # Validar que el usuario es el contratado
        if servicio.id_contratado != current_user.id_usuario:
            flash("No tienes permisos para calificar como contratado.", "error")
            return redirect(url_for('calificar.show_calificar'))

        # Obtener datos del formulario
        cal1 = request.form.get('cal_contratado1', type=int)
        cal2 = request.form.get('cal_contratado2', type=int)
        cal3 = request.form.get('cal_contratado3', type=int)
        comentario = request.form.get('comentario_contratado', type=str)

        # Validar valores
        if not (1 <= cal1 <= 10 and 1 <= cal2 <= 10 and 1 <= cal3 <= 10):
            flash("Las calificaciones deben estar entre 1 y 10.", "error")
            return redirect(url_for('calificar.show_calificar'))

        # Crear o actualizar la calificación
        calificacion = ServiceRatings.query.filter_by(servicio_id=servicio.id_servicio, usuario_id=current_user.id_usuario).first()
        if not calificacion:
            calificacion = ServiceRatings(
                servicio_id=servicio.id_servicio,
                usuario_id=current_user.id_usuario,
                calificacion_recived_contratado1=cal1,
                calificacion_recived_contratado2=cal2,
                calificacion_recived_contratado3=cal3,
                comentary_hired_employer=comentario  # Columna correcta
            )
            db.session.add(calificacion)
        else:
            calificacion.calificacion_recived_contratado1 = cal1
            calificacion.calificacion_recived_contratado2 = cal2
            calificacion.calificacion_recived_contratado3 = cal3
            calificacion.comentary_hired_employer = comentario  # Columna correcta

        # Guardar cambios
        db.session.commit()
        flash("Calificación como contratado guardada correctamente.", "success")
    except Exception as e:
        logger.exception("Error al calificar como contratado.")
        db.session.rollback()
        flash("Hubo un error al procesar la calificación.", "error")

    return redirect(url_for('calificar.show_calificar'))


@calificar.route('/calificaciones_recibidas/contratante', methods=['GET'])
def calificaciones_recibidas_contratante():
    try:
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

        logger.debug(f"Calificaciones recibidas como contratante: {[c.id_rating for c in calificaciones]}")
        return render_template('calificaciones_recibidas.html', calificaciones=calificaciones, rol='contratante')
    except Exception as e:
        logger.exception("Error al obtener calificaciones recibidas como contratante.")
        flash("Hubo un error al cargar las calificaciones.", "error")
        return redirect(url_for('dashboard.dashboard'))


@calificar.route('/calificaciones_recibidas/contratado', methods=['GET'])
def calificaciones_recibidas_contratado():
    try:
        calificaciones = ServiceRatings.query.join(Servicio).filter(
            and_(
                Servicio.id_contratado == current_user.id_usuario,
                or_(
                    ServiceRatings.calificacion_recived_contratado1.isnot(None),
                    ServiceRatings.calificacion_recived_contratado2.isnot(None),
                    ServiceRatings.calificacion_recived_contratado3.isnot(None)
                )
            )
        ).all()

        logger.debug(f"Calificaciones recibidas como contratado: {[c.id_rating for c in calificaciones]}")
        return render_template('calificaciones_recibidas.html', calificaciones=calificaciones, rol='contratado')
    except Exception as e:
        logger.exception("Error al obtener calificaciones recibidas como contratado.")
        flash("Hubo un error al cargar las calificaciones.", "error")
        return redirect(url_for('dashboard.dashboard'))