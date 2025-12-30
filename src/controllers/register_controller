from flask import Blueprint, render_template, redirect, url_for, flash
from src.models.usuarios import Usuario
from src.models.database import db
from src.forms.forms import RegisterForm
import logging

register_bp = Blueprint('register', __name__)
logger = logging.getLogger(__name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Verifica si ya existe un usuario con el mismo correo
        existing_user = Usuario.query.filter_by(correo=form.correo.data).first()
        if existing_user:
            flash('Ya existe una cuenta con ese correo.', 'danger')
            return redirect(url_for('register.register'))
        
        # Verifica si la cédula ya está registrada
        existing_cedula = Usuario.query.filter_by(cedula=form.cedula.data).first()
        if existing_cedula:
            flash('Ya existe un usuario con esa cédula.', 'danger')
            return redirect(url_for('register.register'))
        
        try:
            # Crea un nuevo usuario con los datos del formulario
            new_user = Usuario(
                nombre=form.nombre.data,
                apellidos=form.apellidos.data,
                correo=form.correo.data,
                labor=form.labor.data,
                cedula=form.cedula.data,
                celular=form.celular.data,
                ciudad=form.ciudad.data
            )
            
            # Genera el hash de la contraseña utilizando el método del modelo Usuario
            new_user.set_password(form.contrasenia.data.strip())

            # Agrega el nuevo usuario a la base de datos
            db.session.add(new_user)
            db.session.commit()
            
            flash('¡Te has registrado exitosamente!', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            logger.error(f"Error al registrar usuario: {str(e)}")
            db.session.rollback()
            flash('Ocurrió un error durante el registro. Inténtalo de nuevo.', 'danger')
    
    return render_template('register.html', form=form)