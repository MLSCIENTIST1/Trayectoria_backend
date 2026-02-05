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
import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from src.models.servicio import Servicio  # Relación con el modelo Servicio

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para contratos vigentes
contract_vigent_bp = Blueprint('contract_vigent_bp', __name__)

@contract_vigent_bp.route('/contract_vigent', methods=['POST'])
@login_required
def vigent_contracts():
    """
    API para obtener contratos vigentes según el rol (contratante o contratado).
    Devuelve los datos en formato JSON.
    """
    try:
        # Obtener el rol desde el cuerpo de la solicitud
        role = request.json.get('role')
        logger.info(f"Procesando solicitud POST para contratos vigentes con rol: {role} del usuario {current_user.id_usuario}.")

        # Validar si el rol es válido
        if role not in ['contratante', 'contratado']:
            logger.warning("Rol inválido seleccionado.")
            return jsonify({"error": "Rol inválido seleccionado."}), 400

        # Obtener contratos según el rol seleccionado
        if role == 'contratante':
            contracts = Servicio.query.filter_by(id_contratante=current_user.id_usuario).all()
        else:  # role == 'contratado'
            contracts = Servicio.query.filter_by(id_contratado=current_user.id_usuario).all()

        logger.debug(f"Contratos obtenidos para el rol {role}: {len(contracts)} encontrados.")

        # Añadir el nombre de la persona a calificar
        contracts_with_names = []
        for contract in contracts:
            if role == 'contratante':
                # Si el usuario es contratante, califica al contratado
                person_to_rate = contract.contratado.nombre if contract.contratado else "No definido"
            elif role == 'contratado':
                # Si el usuario es contratado, califica al contratante
                person_to_rate = contract.contratante.nombre if contract.contratante else "No definido"

            contracts_with_names.append({
                'id_servicio': contract.id_servicio,
                'nombre_servicio': contract.nombre_servicio,
                'fecha_inicio': str(contract.fecha_inicio),
                'fecha_fin': str(contract.fecha_fin),
                'person_to_rate': person_to_rate  # Nombre dinámico para el botón
            })

        logger.debug(f"Contratos procesados para el rol {role}: {contracts_with_names}")

        return jsonify({
            "contratos": contracts_with_names,
            "rol": role
        }), 200

    except SQLAlchemyError as e:
        logger.error(f"Error al consultar la base de datos: {e}")
        return jsonify({"error": "Hubo un problema al consultar la base de datos."}), 500

    except Exception as e:
        logger.exception("Error inesperado al procesar los contratos vigentes.")
        return jsonify({"error": "Hubo un error al procesar la solicitud."}), 500
