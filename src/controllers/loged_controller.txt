from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, logout_user, current_user
from src.forms.forms import LoginForm

loged_bp = Blueprint('loged',__name__)

@loged_bp.route('/loged')
@login_required
def principal_usuario_logueado():
    return render_template('main/principal_usuario_logueado.html')