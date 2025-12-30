import logging
from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, current_user
from src.models.usuarios import Usuario
from src.forms.forms import LoginForm

# Configuración de Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Definición del Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(f"Ya has iniciado sesión como {current_user.nombre}.", "info")
        return redirect(url_for('loged.principal_usuario_logueado'))

    form = LoginForm()

    if form.validate_on_submit():
        correo = form.correo.data.strip()
        password_input = form.password.data.strip()

        # Manejo de intentos fallidos
        if 'login_attempts' not in session:
            session['login_attempts'] = 0

        if session['login_attempts'] >= 5:
            flash('Has alcanzado el número máximo de intentos. Intenta más tarde.', 'danger')
            return redirect(url_for('auth.login'))

        try:
            # Buscar al usuario por su correo
            usuario = Usuario.query.filter_by(correo=correo).first()
        except Exception as e:
            logger.error(f"Error al consultar la base de datos: {e}")
            flash('Hubo un problema al procesar tu solicitud. Por favor, intenta nuevamente.', 'danger')
            return redirect(url_for('auth.login'))

        if usuario:
            if not usuario.active:
                logger.debug("El usuario no está activo.")
                flash('Tu cuenta está desactivada. Contacta con soporte para reactivarla.', 'warning')
                return redirect(url_for('auth.login'))

            # Verificación de la contraseña
            if usuario.check_password(password_input):  # Usa el método del modelo Usuario
                login_user(usuario, remember=form.remember.data)
                session['login_attempts'] = 0  # Reinicia intentos fallidos
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('loged.principal_usuario_logueado'))
            else:
                logger.debug("Contraseña incorrecta.")
                session['login_attempts'] += 1
                flash('Correo o contraseña incorrectos.', 'danger')
        else:
            logger.debug("Usuario no encontrado.")
            session['login_attempts'] += 1
            flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html', form=form)