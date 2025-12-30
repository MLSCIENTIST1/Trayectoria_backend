from src.models.notification import Notification
from src.models.servicio import Servicio
from flask_login import current_user


def get_contract_count():
    """ Obtiene la cantidad de notificaciones aceptadas. """
    return Notification.query.filter_by(is_accepted=True).count()

def get_vigent_contracts():
    """ Obtiene la lista de contratos vigentes del usuario actual. """
    try:
        contracts = Servicio.query.join(Servicio.usuarios).filter(Servicio.usuarios.any(id_usuario=current_user.id_usuario)).all()
        
        if not contracts:
            print("No se encontraron contratos vigentes.")
        else:
            for contract in contracts:
                print(f"Contrato: {contract.nombre_servicio}, {contract.fecha_solicitud}, {contract.fecha_aceptacion}, {contract.fecha_inicio}, {contract.fecha_fin}, {contract.nombre_contratante}")
                
        return contracts
    except Exception as e:
        print(f"Error al obtener contratos vigentes: {e}")
        return