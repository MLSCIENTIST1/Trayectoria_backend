from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, logout_user, current_user
from src.forms.forms import LoginForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    print("Renderizando pàgina principal")
    return render_template('main/index.html')

@main_bp.route('/logout')
def logout():
    logout_user()
    flash('La sesión se ha cerrado exitosamente', 'info')
    return redirect(url_for('main.index'))

