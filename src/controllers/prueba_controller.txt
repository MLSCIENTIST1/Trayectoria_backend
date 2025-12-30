@dashboard_bp.route('/new_service_page', methods=['GET', 'POST'])
@login_required
def new_service_page():
    if request.method == 'POST':
        if 'Guardar Archivos' in request.form:  # Si se hace clic en "Guardar Archivos"
            try:
                nombre_servicio = request.form.get('nombre_servicio')
                descripcion = request.form.get('descripcion')
                categoria = request.form.get('categoria')
                precio_hora = request.form.get('precio_hora')
                etapas_calificacion = request.form.get('etapas_calificacion')
                viajar_dentro_pais = request.form.get('viajar_dentro_pais')
                viajar_fuera_pais = request.form.get('viajar_fuera_pais')
                domicilios = request.form.get('viajar_fuera_pais')  # Campo de domicilios
                incluye_asesoria = request.form.get('incluye_asesoria')
                requiere_presencia_cliente = request.form.get('requiere_presencia_cliente')
                experiencia_previa = request.form.get('experiencia_previa')
                facturacion_formal = request.form.get('facturacion_formal')

                # Modelos de negocio
                modelos_negocio_1 = request.form.get('modelo_negocio1')
                modelos_negocio_2 = request.form.get('modelo_negocio2')
                modelos_negocio_3 = request.form.get('modelo_negocio3')
                modelos_negocio_4 = request.form.get('modelo_negocio4')

            if not os.path.exists(TEMP_UPLOAD_FOLDER):
                os.makedirs(TEMP_UPLOAD_FOLDER)

                for file_key in request.files:
                    file = request.files[file_key]
                    if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS + ALLOWED_AUDIO_EXTENSIONS + ALLOWED_VIDEO_EXTENSIONS):
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(TEMP_UPLOAD_FOLDER, filename))

                flash("Archivos guardados temporalmente.", "success")
            except Exception as e:
                logger.exception("Error al guardar archivos temporalmente.")
                flash("Hubo un error al guardar los archivos.", "error")
            return redirect(url_for('dashboard.new_service_page'))

        elif 'Agregar Servicio' in request.form:  # Si se hace clic en "Agregar Servicio"
            try:
                # Obtener los datos del formulario
                nombre_servicio = request.form.get('nombre_servicio')
                descripcion = request.form.get('descripcion')
                categoria = request.form.get('categoria')
                precio_hora = request.form.get('precio_hora')
                etapas_calificacion = request.form.get('etapas_calificacion')

                # Validar los datos obligatorios
                if not nombre_servicio or not descripcion or not precio_hora or not etapas_calificacion:
                    flash("Por favor, completa todos los campos obligatorios.", "error")
                    return redirect(url_for('dashboard.new_service_page'))

                # Crear el nuevo servicio
                nuevo_servicio = Servicio(
                    id_usuario=current_user.id_usuario,
                    nombre_servicio=nombre_servicio,
                    descripcion=descripcion,
                    categoria=categoria,
                    precio=float(precio_hora) if precio_hora else None,
                    etapas_calificacion=int(etapas_calificacion)
                )
                db.session.add(nuevo_servicio)
                db.session.commit()

                # Mover archivos desde la carpeta temporal al destino final
                if os.path.exists(TEMP_UPLOAD_FOLDER):
                    for filename in os.listdir(TEMP_UPLOAD_FOLDER):
                        src_path = os.path.join(TEMP_UPLOAD_FOLDER, filename)
                        dest_path = os.path.join(UPLOAD_FOLDER, filename)
                        shutil.move(src_path, dest_path)
                        # Asocia cada archivo al servicio recién creado
                        # Ejemplo: Si es una foto
                        if filename.endswith(tuple(ALLOWED_IMAGE_EXTENSIONS)):
                            nueva_foto = Foto(url=dest_path, servicio_id=nuevo_servicio.id_servicio)
                            db.session.add(nueva_foto)
                        # Ejemplo: Si es un audio
                        elif filename.endswith(tuple(ALLOWED_AUDIO_EXTENSIONS)):
                            nuevo_audio = Audio(url=dest_path, servicio_id=nuevo_servicio.id_servicio)
                            db.session.add(nuevo_audio)
                        # Ejemplo: Si es un video
                        elif filename.endswith(tuple(ALLOWED_VIDEO_EXTENSIONS)):
                            nuevo_video = Video(url=dest_path, servicio_id=nuevo_servicio.id_servicio)
                            db.session.add(nuevo_video)
                    db.session.commit()

                flash("Servicio agregado exitosamente con archivos incluidos.", "success")
                return redirect(url_for('dashboard.dashboard'))

            except Exception as e:
                db.session.rollback()
                logger.exception("Error al agregar servicio o mover archivos.")
                flash("Hubo un error al agregar el servicio.", "error")
                return redirect(url_for('dashboard.new_service_page'))

    # Renderizar el formulario
    return render_template('new_service.html')