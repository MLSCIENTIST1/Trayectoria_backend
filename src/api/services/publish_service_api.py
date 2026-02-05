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
import os
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para publicar servicios
publish_service_bp = Blueprint('publish_service_bp', __name__)

# Verificar si un archivo tiene una extensión permitida
def allowed_file(filename, allowed_extensions):
    """
    Verifica si el archivo tiene una extensión permitida.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@publish_service_bp.route('/publish_service', methods=['POST'])
@login_required
def new_service_page():
    """
    API para gestionar la creación de nuevos servicios y guardar archivos asociados.
    Permite la subida temporal de archivos y el registro de servicios.
    """
    logger.info("Procesando solicitud POST para nuevo servicio.")

    try:
        # Identificar si es un clic en "Guardar Archivos" o "Agregar Servicio"
        if 'guardar_archivos' in request.form:
            logger.debug("Intentando guardar archivos temporalmente...")
            archivos = request.files.getlist('files')
            if not archivos:
                logger.warning("No se cargaron archivos.")
                return jsonify({"error": "No se cargaron archivos."}), 400

            saved_files = []
            for archivo in archivos:
                if archivo.filename and allowed_file(
                    archivo.filename, ALLOWED_IMAGE_EXTENSIONS.union(
                        ALLOWED_AUDIO_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS
                    )
                ):
                    filename = secure_filename(archivo.filename)
                    file_path = os.path.join(UPLOAD_FOLDER_TEMP, filename)
                    archivo.save(file_path)
                    saved_files.append(file_path)

            logger.debug(f"Archivos guardados temporalmente: {saved_files}")
            return jsonify({"message": f"Archivos guardados temporalmente: {len(saved_files)}"}), 200

        elif 'agregar_servicio' in request.form:
            logger.debug("Intentando agregar un nuevo servicio...")

            # Obtener los datos del formulario
            nombre_servicio = request.form.get('nombre_servicio')
            descripcion = request.form.get('descripcion')
            categoria = request.form.get('categoria')
            precio_hora = request.form.get('precio_hora')
            etapas_calificacion = request.form.get('etapas_calificacion')
            viajar_dentro_pais = request.form.get('viajar_dentro_pais')
            viajar_fuera_pais = request.form.get('viajar_fuera_pais')
            domicilios = request.form.get('domicilios')
            incluye_asesoria = request.form.get('incluye_asesoria')
            requiere_presencia_cliente = request.form.get('requiere_presencia_cliente')
            experiencia_previa = request.form.get('experiencia_previa')
            facturacion_formal = request.form.get('facturacion_formal')
            modelos_negocio = ",".join(filter(None, [
                request.form.get('modelo_negocio1'),
                request.form.get('modelo_negocio2'),
                request.form.get('modelo_negocio3'),
                request.form.get('modelo_negocio4')
            ]))

            logger.debug(f"Datos recibidos para el nuevo servicio: {locals()}")

            # Validar los datos obligatorios
            if not nombre_servicio or not descripcion or not precio_hora or not etapas_calificacion:
                logger.warning("Faltan datos obligatorios en el formulario.")
                return jsonify({"error": "Por favor, completa todos los campos obligatorios."}), 400

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
                modelos_negocio=modelos_negocio
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
            return jsonify({"message": "Servicio agregado exitosamente con los archivos asociados."}), 200

    except Exception as e:
        logger.exception("Error al procesar el servicio.")
        db.session.rollback()
        return jsonify({"error": "Hubo un error al procesar el servicio."}), 500

    return jsonify({"error": "Método no permitido."}), 405
