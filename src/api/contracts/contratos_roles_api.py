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
