from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length

# Formulario de inicio de sesión
class LoginForm(FlaskForm):
    correo = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recuérdame')
    submit = SubmitField('Iniciar Sesión')

# Formulario de registro
class RegisterForm(FlaskForm):
    nombre = StringField('Nombre', render_kw={"class": "input-field"}, validators=[DataRequired(), Length(min=2, max=50)])
    apellidos = StringField('Apellidos', render_kw={"class": "input-field"}, validators=[DataRequired(), Length(min=2, max=50)])
    cedula = IntegerField('Cédula', render_kw={"class": "input-field"}, validators=[DataRequired()])
    correo = StringField('Correo Electrónico', render_kw={"class": "input-field"}, validators=[DataRequired(), Email()])
    contrasenia = PasswordField('Contraseña', render_kw={"class": "input-field"}, validators=[DataRequired(), Length(min=6)])
    labor = StringField('Labor', render_kw={"class": "input-field"}, validators=[DataRequired(), Length(min=2, max=100)])
    celular = StringField('Celular', render_kw={"class": "input-field"}, validators=[DataRequired(), Length(min=7, max=15)])
    ciudad = StringField('Ciudad', render_kw={"class": "input-field"}, validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Registrarse', render_kw={"class": "btn btn-primary"})


class EditProfileForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Length(max=50)])
    celular = IntegerField('Celular')
    ciudad = StringField('Ciudad', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Guardar cambios')