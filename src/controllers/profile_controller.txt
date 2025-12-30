from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models.database import db
from src.forms import EditProfileForm
from src.models.usuarios import Usuario
from flask import request

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/loged')
@login_required
def editando():
    usuario = current_user
    return render_template('editando.html', usuario = usuario)





@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)  # Cargar datos del usuario actual en el formulario
    if form.validate_on_submit():
        # Actualizar los datos del usuario logueado
        current_user.nombre = form.nombre.data
        current_user.apellidos = form.apellidos.data
        current_user.celular = form.celular.data
        current_user.ciudad = form.ciudad.data
        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('profile.editando'))
    return render_template('editar_perfil.html', form=form)


@profile_bp.route('/logic_delete_user', methods=['POST'])
@login_required
def logic_delete_user():
    print("📥 Depuración: La solicitud llegó correctamente al endpoint logic_delete_user.")
    try:
        # Comprobación: Verificar si la solicitud POST llegó al servidor
        print("📥 Depuración: La solicitud POST llegó correctamente al servidor.")

        # Extraer información específica del HTML (aunque en este caso no se envían datos, confirmamos la solicitud)
        print(f"🔍 Depuración: Datos recibidos del formulario - Método de solicitud: {request.method}")

        # Información del usuario actual antes del cambio
        print(f"🔍 Depuración: Usuario actual - ID: {current_user.id_usuario}, Nombre: {current_user.nombre}, Estado activo antes del cambio: {current_user.active}")

        # Marcar al usuario como inactivo
        current_user.active = False
        print(f"✏️ Depuración: Cambiando el estado de 'active' a False para el usuario con ID: {current_user.id_usuario}")

        # Guardar los cambios en la base de datos
        db.session.commit()
        print(f"✅ Depuración: Cambios guardados exitosamente en la base de datos. Estado activo ahora: {current_user.active}")

        # Notificar al usuario
        flash('El perfil se eliminará de la plataforma, si deseas reactivarlo contacta con soporte.', 'success')

        # Redirigir tras finalizar la baja
        print("🔄 Depuración: Redirigiendo al archivo de logout.")
        return redirect(url_for('main.logout'))
    except Exception as e:
        # Depurar errores
        print(f"❌ Depuración: Error al desactivar el perfil del usuario. Detalles: {e}")

        # Revertir cambios en caso de error
        db.session.rollback()
        flash("Hubo un error al intentar desactivar tu cuenta. Inténtalo de nuevo.", 'danger')
        return redirect(url_for('dashboard.dashboard'))

    
