import logging
import sys
from flask import Blueprint, render_template, jsonify, request
from flask_cors import cross_origin

# Importaciones de modelos
from src.models.colombia_data.negocio import Negocio
from src.models.database import db

# --- CONFIGURACIÓN DE LOGS ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

# Creamos el Blueprint para la visualización de páginas
pagina_api_bp = Blueprint('pagina_api_bp', __name__)

# --- RUTA PARA VISUALIZAR EL MICROSITIO ---
# Esta ruta es PÚBLICA (no lleva @login_required) para que cualquier cliente vea el sitio
@pagina_api_bp.route('/sitio/<slug>', methods=['GET'])
@cross_origin()
def ver_micrositio(slug):
    try:
        logger.info(f"🌐 Accediendo al micrositio: {slug}")
        
        # 1. Buscar el negocio por su slug en la base de datos
        negocio = Negocio.query.filter_by(slug=slug).first()
        
        if not negocio:
            logger.warning(f"⚠️ Micrositio no encontrado: {slug}")
            return "<h1>404 - El micrositio no existe</h1><p>Verifica la dirección o contacta al dueño del negocio.</p>", 404
            
        # 2. Verificar que tenga una página activa
        if not getattr(negocio, 'tiene_pagina', False):
            return "<h1>Este sitio aún no ha sido publicado</h1>", 403

        # 3. Renderizar la plantilla rodar.html
        # Flask buscará 'rodar.html' dentro de tu carpeta /templates
        return render_template('rodar.html', negocio=negocio)

    except Exception as e:
        logger.error(f"🔥 ERROR cargando micrositio '{slug}': {str(e)}")
        return f"Error interno en el servidor", 500

# --- RUTA PARA VISUALIZAR EL CATÁLOGO COMPLETO ---
@pagina_api_bp.route('/sitio/<slug>/catalogo', methods=['GET'])
@cross_origin()
def ver_catalogo(slug):
    try:
        logger.info(f"🛒 Accediendo al catálogo de: {slug}")
        
        negocio = Negocio.query.filter_by(slug=slug).first()
        
        if not negocio:
            return "<h1>404 - Negocio no encontrado</h1>", 404
            
        if not getattr(negocio, 'tiene_pagina', False):
            return "<h1>Catálogo no disponible</h1>", 403

        # Renderizamos una nueva plantilla específica para el catálogo
        return render_template('catalogo_cliente.html', negocio=negocio)

    except Exception as e:
        logger.error(f"🔥 ERROR cargando catálogo de '{slug}': {str(e)}")
        return "Error al cargar el catálogo", 500