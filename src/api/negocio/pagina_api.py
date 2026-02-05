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