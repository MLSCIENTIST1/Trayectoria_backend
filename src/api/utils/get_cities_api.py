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
# CORRECCIÓN: El archivo se llama colombia_data y la clase Colombia
 
from src.models.colombia_data.colombia_data import Colombia
import logging
import sys
from flask import Blueprint, jsonify, request
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

# --- CONFIGURACIÓN DE LOGS PARA RENDER ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Blueprint
get_cities_bp = Blueprint('get_cities_bp', __name__)

@get_cities_bp.route('/ciudades', methods=['GET'])
def obtener_nombre_ciudades():
    """
    API para buscar ciudades por nombre o ID. 
    Ajustada para usar 'ciudad_id' como llave primaria según colombia_data.py
    """
    logger.info("========================================")
    logger.info("🚀 SOLICITUD RECIBIDA: /api/ciudades")
    
    # 1. Obtener parámetros de la URL
    termino = request.args.get('q', '').strip()
    id_param = request.args.get('id', '').strip()
    
    logger.debug(f"📥 Query Params -> q: '{termino}', id: '{id_param}'")

    try:
        # --- CASO A: Búsqueda por ID específico ---
        if id_param:
            if not id_param.isdigit():
                return jsonify({"error": "El ID debe ser un número"}), 400

            # CORRECCIÓN: Tu modelo usa ciudad_id, no id
            ciudad = Colombia.query.filter_by(ciudad_id=int(id_param)).first()
            if ciudad:
                logger.info(f"✅ Ciudad encontrada: {ciudad.ciudad_nombre}")
                return jsonify({"id": ciudad.ciudad_id, "nombre": ciudad.ciudad_nombre}), 200
            else:
                return jsonify({"error": "Ciudad no encontrada"}), 404

        # --- CASO B: Búsqueda por Nombre o Carga Inicial ---
        query = Colombia.query
        if termino:
            query = query.filter(Colombia.ciudad_nombre.ilike(f"%{termino}%"))
        
        # Ordenamos y limitamos resultados
        ciudades = query.order_by(Colombia.ciudad_nombre.asc()).limit(50).all()
        
        # CORRECCIÓN: Mapeo usando ciudad_id y ciudad_nombre
        resultados = [
            {
                "id": c.ciudad_id, 
                "nombre": c.ciudad_nombre
            } for c in ciudades
        ]
        
        logger.info(f"📊 Ciudades recuperadas: {len(resultados)}")
        return jsonify(resultados), 200

    except SQLAlchemyError as e:
        logger.error(f"❌ ERROR SQLALCHEMY: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error en la base de datos"}), 500

    except Exception as e:
        logger.error(f"❌ ERROR INESPERADO: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500