from src.models.database import db
from src.models.usuarios import Usuario
import logging
from flask import Blueprint, jsonify
from flask_login import login_required

# Configuración del Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Blueprint para contratos con roles
contratos_roles_bp = Blueprint('contratos_roles_bp', __name__)

@contratos_roles_bp.route('/contratos_roles', methods=['POST'])
@login_required
def contratos_vigentes_roles():
    """
    API para obtener los contratos vigentes asociados al usuario actual, con su rol en cada contrato.
    Devuelve los datos en formato JSON.
    """
    logger.info("Procesando solicitud GET para obtener contratos vigentes con roles.")

    try:
        # Obtener contratos donde el usuario es contratante o contratado
        contracts = Servicio.query.filter(
            or_(
                Servicio.id_contratante == current_user.id_usuario,
                Servicio.id_contratado == current_user.id_usuario
            )
        ).all()
        logger.debug(f"Contratos obtenidos: {len(contracts)} encontrados para el usuario {current_user.id_usuario}")

        # Procesar contratos para determinar roles y evitar duplicados
        contracts_with_roles = []
        seen_contracts = set()  # Evitar duplicados

        for contract in contracts:
            if contract.id_servicio in seen_contracts:
                logger.debug(f"Contrato duplicado ignorado: ID {contract.id_servicio}")
                continue  # Ignorar contratos duplicados

            # Determinar el rol del usuario en el contrato
            if contract.id_contratante == current_user.id_usuario:
                role = 'contratante'
            elif contract.id_contratado == current_user.id_usuario:
                role = 'contratado'
            else:
                logger.warning(f"Usuario {current_user.id_usuario} no tiene un rol válido en el contrato {contract.id_servicio}")
                continue

            # Agregar contrato con rol al resultado
            contracts_with_roles.append({
                'id_servicio': contract.id_servicio,
                'nombre_servicio': contract.nombre_servicio,
                'fecha_inicio': str(contract.fecha_inicio),
                'fecha_fin': str(contract.fecha_fin),
                'role': role
            })

            seen_contracts.add(contract.id_servicio)  # Registrar contrato procesado
            logger.debug(f"Contrato procesado: ID {contract.id_servicio}, Rol {role}")

        # Devolver datos en formato JSON
        logger.info("Contratos vigentes procesados con éxito.")
        return jsonify({"contracts": contracts_with_roles}), 200

    except Exception as e:
        logger.exception("Error al cargar los contratos vigentes con roles.")
        return jsonify({"error": "Hubo un problema al cargar tus contratos vigentes."}), 500
