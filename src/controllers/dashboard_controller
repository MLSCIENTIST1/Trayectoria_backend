import logging
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from src.models.servicio import Servicio
from src.models.database import db
from sqlalchemy import or_, and_
from src.models.colombia_data.ratings import ServiceRatings  # Nuevo modelo para calificaciones
from src.models.etapa import Etapa
import shutil

TEMP_UPLOAD_FOLDER = 'temp_uploads' 

UPLOAD_FOLDER_TEMP = 'static/uploads/temp'
UPLOAD_FOLDER_FINAL = 'static/uploads/final'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov'}

# Configuración del logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


# Función reutilizable
def calcular_total_servicios():
    # Inicializa el contador con el servicio principal
    total_services = 1 if current_user.labor else 0

    # Contar servicios adicionales (ahora con el modelo Servicio directamente)
    additional_services = Servicio.query.filter_by(id_usuario=current_user.id_usuario).count()  # Contando todos los servicios asociados
    total_services += additional_services

    return total_services

dashboard_bp = Blueprint('dashboard', __name__)

def allowed_file(filename, allowed_extensions):
    """
    Verifica si el archivo tiene una extensión permitida
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        # Contar contratos vigentes donde el usuario es contratante
        contract_count_contratante = Servicio.query.filter_by(id_contratante=current_user.id_usuario).count()
        logger.debug(f"Cantidad de contratos actuales como contratante: {contract_count_contratante}")

        # Contar contratos vigentes donde el usuario es contratado
        contract_count_contratado = Servicio.query.filter_by(id_contratado=current_user.id_usuario).count()
        logger.debug(f"Cantidad de contratos actuales como contratado: {contract_count_contratado}")

        # Calificaciones recibidas como contratante
        calification_count_contratante = ServiceRatings.query.filter(
            and_(
                ServiceRatings.usuario_id == current_user.id_usuario,
                or_(
                    ServiceRatings.calificacion_recived_contratante1.isnot(None),
                    ServiceRatings.calificacion_recived_contratante2.isnot(None),
                    ServiceRatings.calificacion_recived_contratante3.isnot(None)
                )
            )
        ).count()
        logger.debug(f"Cantidad de calificaciones recibidas como contratante: {calification_count_contratante}")

        # Calificaciones recibidas como contratado
        calification_count_contratado = ServiceRatings.query.filter(
            and_(
                ServiceRatings.usuario_id == current_user.id_usuario,
                or_(
                    ServiceRatings.calificacion_recived_contratado1.isnot(None),
                    ServiceRatings.calificacion_recived_contratado2.isnot(None),
                    ServiceRatings.calificacion_recived_contratado3.isnot(None)
                )
            )
        ).count()
        logger.debug(f"Cantidad de calificaciones recibidas como contratado: {calification_count_contratado}")

        # Renderizar el template con todos los datos
        return render_template(
            'dashboard.html',
            contract_count_contratante=contract_count_contratante,
            contract_count_contratado=contract_count_contratado,
            calification_count_contratante=calification_count_contratante,
            calification_count_contratado=calification_count_contratado
        )
    except Exception as e:
        logger.exception("Error al cargar el dashboard.")
        flash("Hubo un error al cargar el dashboard.", "error")
        return redirect(url_for('main.home'))

@dashboard_bp.route('/vigent_contracts/<string:role>', methods=['GET'])
@login_required
def vigent_contracts(role):
    try:
        # Verificar si el rol es válido
        if role not in ['contratante', 'contratado']:
            flash("Rol inválido seleccionado.", "error")
            return redirect(url_for('dashboard.dashboard'))

        # Obtener contratos según el rol seleccionado
        if role == 'contratante':
            contracts = Servicio.query.filter_by(id_contratante=current_user.id_usuario).all()
        else:  # role == 'contratado'
            contracts = Servicio.query.filter_by(id_contratado=current_user.id_usuario).all()

        # Añadir el nombre de la persona a calificar
        contracts_with_names = []
        for contract in contracts:
            if role == 'contratante':
                # Si el usuario es contratante, califica al contratado
                person_to_rate = contract.contratado.nombre if contract.contratado else "No definido"
            elif role == 'contratado':
                # Si el usuario es contratado, califica al contratante
                person_to_rate = contract.contratante.nombre if contract.contratante else "No definido"

            contracts_with_names.append({
                'id_servicio': contract.id_servicio,
                'nombre_servicio': contract.nombre_servicio,
                'fecha_inicio': contract.fecha_inicio,
                'fecha_fin': contract.fecha_fin,
                'person_to_rate': person_to_rate  # Nombre dinámico para el botón
            })

        # Log de depuración
        logger.debug(f"Contratos procesados para {role}: {contracts_with_names}")

        # Renderizar la página con contratos y nombres
        return render_template(
            'vigent_contracts.html',
            contracts=contracts_with_names,
            role=role
        )
    except Exception as e:
        logger.exception("Error al obtener los contratos vigentes.")
        flash("Hubo un error al cargar los contratos vigentes.", "error")
        return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/offered_service', methods=['GET'])
@login_required
def service_count_offered():
    try:
        total_services = calcular_total_servicios()
        logger.debug(f"✅ Total de servicios calculados: {total_services}")
        return {"services_offered": total_services}, 200
    except Exception as e:
        logger.exception(f"Error al contar los servicios ofertados: {e}")
        return {"error": "Ocurrió un error al procesar la solicitud."}, 500


@dashboard_bp.route('/offered_service_page', methods=['GET'])
@login_required
def offered_service_page():
    try:
        total_services = calcular_total_servicios()
        logger.debug(f"Renderizando HTML con total_services={total_services}")
        return render_template('offered_service.html', services_offered=total_services)
    except Exception as e:
        logger.exception(f"Error al renderizar offered_service.html: {e}")
        flash("Hubo un error al cargar la página.", "error")
        return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/edit_service_page', methods=['GET'])
@login_required
def edit_service_page():
    try:
        # Servicio principal del usuario
        principal_service = current_user.labor

        # Otros servicios asociados al usuario (desde Servicio directamente)
        other_services = Servicio.query.filter_by(id_usuario=current_user.id_usuario).all()

        logger.debug(f"Servicios adicionales encontrados: {[s.nombre_servicio for s in other_services]}")

        # Renderizar la página y pasar los datos
        return render_template(
            'edit_services.html',
            principal_service=principal_service,
            other_services=other_services
        )
    except Exception as e:
        logger.exception("Error al cargar la página de edición de servicios.")
        flash("Hubo un error al cargar la página.", "error")
        return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/update_other_service/<int:service_id>', methods=['POST'])
@login_required
def update_other_service(service_id):
    try:
        # Obtener datos enviados desde el frontend
        data = request.get_json()
        logger.debug(f"Datos recibidos para actualizar servicio {service_id}: {data}")

        # Buscar el servicio asociado al usuario actual
        service = Servicio.query.filter_by(id_servicio=service_id, id_usuario=current_user.id_usuario).first()

        if service:
            # Actualizar solo los campos que están presentes en `data`
            if 'service_name' in data and data['service_name']:
                service.nombre_servicio = data['service_name']
            if 'description' in data and data['description']:
                service.descripcion = data['description']
            if 'category' in data and data['category']:
                service.categoria = data['category']
            if 'price' in data and data['price'] is not None:
                service.precio = float(data['price'])

            # Guardar los cambios
            db.session.commit()
            logger.debug(f"Servicio actualizado con éxito: {service}")
            return {"message": "Servicio actualizado con éxito."}, 200
        else:
            return {"error": "El servicio no existe o no pertenece al usuario."}, 400
    except Exception as e:
        logger.exception("Error al actualizar el servicio adicional.")
        return {"error": "Hubo un problema al actualizar el servicio adicional."}, 500


@dashboard_bp.route('/delete_principal_service', methods=['DELETE'])
@login_required
def delete_principal_service():
    try:
        current_user.labor = None  # Elimina el servicio principal
        db.session.commit()
        logger.debug(f"Servicio principal eliminado para el usuario {current_user.id_usuario}")
        return {"message": "Servicio principal eliminado con éxito."}, 200
    except Exception as e:
        logger.exception("Error al eliminar el servicio principal.")
        return {"error": "Hubo un problema al eliminar el servicio principal."}, 500


@dashboard_bp.route('/additional_service_page', methods=['GET'])
@login_required
def additional_service_page():
    try:
        # Servicio principal del usuario
        principal_service = current_user.labor

        # Otros servicios asociados al usuario (desde Servicio directamente)
        other_services = Servicio.query.filter_by(id_usuario=current_user.id_usuario).all()

        logger.debug(f"Servicios adicionales encontrados: {[s.nombre_servicio for s in other_services]}")

        # Renderizar la página y pasar los datos
        return render_template(
            'additional_service.html',
            principal_service=principal_service,
            other_services=other_services
        )
    except Exception as e:
        logger.exception("Error al cargar la página de servicios adicionales.")
        flash("Hubo un error al cargar la página.", "error")
        return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/delete_other_service/<int:service_id>', methods=['DELETE'])
@login_required
def delete_other_service(service_id):
    try:
        logger.debug(f"Intentando eliminar el servicio con ID: {service_id}")

        # Buscar el servicio en el modelo Servicio en lugar de AditionalService
        service = Servicio.query.filter_by(id_servicio=service_id, id_usuario=current_user.id_usuario).first()

        if service:
            logger.debug(f"Servicio encontrado: {service.nombre_servicio}. Procediendo a eliminar.")
            db.session.delete(service)
            db.session.commit()
            logger.debug(f"Servicio con ID {service_id} eliminado.")
            return {"message": "Servicio eliminado con éxito."}, 200
        else:
            logger.warning(f"Servicio con ID {service_id} no encontrado o no pertenece al usuario.")
            return {"error": "El servicio no existe o no pertenece al usuario."}, 400
    except Exception as e:
        logger.exception("Error al eliminar el servicio.")
        return {"error": "Hubo un problema al eliminar el servicio."}, 500


@dashboard_bp.route('/new_service_page', methods=['GET', 'POST'])
@login_required
def new_service_page():
    if request.method == 'POST':
        logger.debug("Se recibió una solicitud POST.")

        # Identificar si es un clic en "Guardar Archivos" o "Agregar Servicio"
        if 'guardar_archivos' in request.form:
            try:
                logger.debug("Intentando guardar archivos temporalmente...")
                # Guardar archivos temporalmente
                archivos = request.files.getlist('files')
                if not archivos:
                    logger.warning("No se cargaron archivos.")
                    flash('No se cargaron archivos.', 'warning')
                    return redirect(url_for('dashboard.new_service_page'))

                saved_files = []
                for archivo in archivos:
                    if archivo.filename and allowed_file(archivo.filename, ALLOWED_IMAGE_EXTENSIONS.union(ALLOWED_AUDIO_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS)):
                        filename = secure_filename(archivo.filename)
                        file_path = os.path.join(UPLOAD_FOLDER_TEMP, filename)
                        archivo.save(file_path)
                        saved_files.append(file_path)

                logger.debug(f"Archivos guardados temporalmente: {saved_files}")
                flash(f'Archivos guardados temporalmente: {len(saved_files)}', 'success')
                return redirect(url_for('dashboard.new_service_page'))

            except Exception as e:
                logger.error(f"Error al guardar archivos temporalmente: {e}")
                flash('Ocurrió un error al guardar los archivos.', 'danger')
                return redirect(url_for('dashboard.new_service_page'))

        elif 'agregar_servicio' in request.form:
            try:
                logger.debug("Intentando agregar un nuevo servicio...")
                # Obtener los datos del formulario
                nombre_servicio = request.form.get('nombre_servicio')
                descripcion = request.form.get('descripcion')
                categoria = request.form.get('categoria')
                precio_hora = request.form.get('precio_hora')
                etapas_calificacion = request.form.get('etapas_calificacion')
                viajar_dentro_pais = request.form.get('viajar_dentro_pais')
                viajar_fuera_pais = request.form.get('viajar_fuera_pais')
                domicilios = request.form.get('viajar_fuera_pais')
                incluye_asesoria = request.form.get('incluye_asesoria')
                requiere_presencia_cliente = request.form.get('requiere_presencia_cliente')
                experiencia_previa = request.form.get('experiencia_previa')
                facturacion_formal = request.form.get('facturacion_formal')
                modelos_negocio_1 = request.form.get('modelo_negocio1')
                modelos_negocio_2 = request.form.get('modelo_negocio2')
                modelos_negocio_3 = request.form.get('modelo_negocio3')
                modelos_negocio_4 = request.form.get('modelo_negocio4')

                logger.debug(f"Datos recibidos para el nuevo servicio: {locals()}")

                # Validar los datos obligatorios
                if not nombre_servicio or not descripcion or not precio_hora or not etapas_calificacion:
                    logger.warning("Faltan datos obligatorios en el formulario.")
                    flash("Por favor, completa todos los campos obligatorios.", "error")
                    return redirect(url_for('dashboard.new_service_page'))

                # Crear el nuevo servicio
                nuevo_servicio = Servicio(
                    id_usuario=current_user.id_usuario,
                    nombre_servicio=nombre_servicio,
                    descripcion=descripcion,
                    categoria=categoria,
                    precio=float(precio_hora) if precio_hora else None,
                    etapas_calificacion=int(etapas_calificacion),
                    viajar_dentro_pais=True if viajar_dentro_pais == "sí" else False,
                    viajar_fuera_pais=True if viajar_fuera_pais == "sí" else False,
                    domicilios=True if domicilios == "sí" else False,
                    incluye_asesoria=True if incluye_asesoria == "sí" else False,
                    requiere_presencia_cliente=True if requiere_presencia_cliente == "sí" else False,
                    experiencia_previa=True if experiencia_previa == "sí" else False,
                    facturacion_formal=True if facturacion_formal == "sí" else False,
                    modelos_negocio=",".join(filter(None, [modelos_negocio_1, modelos_negocio_2, modelos_negocio_3, modelos_negocio_4]))
                )
                db.session.add(nuevo_servicio)
                db.session.commit()

                logger.debug(f"Servicio creado exitosamente: {nuevo_servicio}")

                # Mover archivos de la carpeta temporal a la carpeta final
                temp_files = os.listdir(UPLOAD_FOLDER_TEMP)
                for file in temp_files:
                    temp_file_path = os.path.join(UPLOAD_FOLDER_TEMP, file)
                    final_file_path = os.path.join(UPLOAD_FOLDER_FINAL, file)
                    os.rename(temp_file_path, final_file_path)

                logger.debug(f"Archivos movidos a la carpeta final: {temp_files}")
                flash("Servicio agregado exitosamente con los archivos asociados.", 'success')
                return redirect(url_for('dashboard.dashboard'))

            except Exception as e:
                db.session.rollback()
                logger.error(f"Error al agregar servicio: {e}")
                flash("Hubo un error al agregar el servicio.", "danger")
                return redirect(url_for('dashboard.new_service_page'))

    logger.debug("Renderizando la página de nuevo servicio...")
    return render_template('new_service.html')

@dashboard_bp.route('/contratos_vigentes_roles', methods=['GET'])
@login_required
def contratos_vigentes_roles():
    try:
        # Obtener contratos donde el usuario es contratante o contratado
        contracts = Servicio.query.filter(
            or_(
                Servicio.id_contratante == current_user.id_usuario,
                Servicio.id_contratado == current_user.id_usuario
            )
        ).all()

        # Procesar contratos para determinar roles y evitar duplicados
        contracts_with_roles = []
        seen_contracts = set()  # Evitar duplicados

        for contract in contracts:
            if contract.id_servicio in seen_contracts:
                continue  # Ignorar contratos duplicados

            # Determinar el rol del usuario en el contrato
            if contract.id_contratante == current_user.id_usuario:
                role = 'contratante'
            elif contract.id_contratado == current_user.id_usuario:
                role = 'contratado'
            else:
                continue

            # Agregar contrato con rol al resultado
            contracts_with_roles.append({
                'id_servicio': contract.id_servicio,
                'nombre_servicio': contract.nombre_servicio,
                'fecha_inicio': contract.fecha_inicio,
                'fecha_fin': contract.fecha_fin,
                'role': role
            })

            seen_contracts.add(contract.id_servicio)  # Registrar contrato procesado

        # Log para depuración
        logger.debug(f"Contratos vigentes procesados con roles: {contracts_with_roles}")

        # Renderizar la página de contratos vigentes con roles
        return render_template('contratos_vigentes.html', contracts=contracts_with_roles)
    except Exception as e:
        logger.exception("Error al cargar los contratos vigentes con roles.")
        flash("Hubo un problema al cargar tus contratos vigentes.", "error")
        return redirect(url_for('dashboard.dashboard'))