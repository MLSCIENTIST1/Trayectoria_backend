from flask import Blueprint

# Crear el Blueprint principal
api_bp = Blueprint('api', __name__)

def register_api(app):
    """
    Registra todos los Blueprints en la aplicación Flask.
    """
    # Importar los Blueprints encontrados
    from .auth.auth_api import auth_api_bp
    from .auth.close_sesion_api import close_sesion_bp
    from .auth.init_sesion_api import init_sesion_bp
    from .auth.password_api import password_bp

    from .calificaciones.calificaciones_recibidas_contractor_api import calificaciones_recibidas_contractor_bp
    from .calificaciones.calificaciones_recibidas_hiree_api import calificaciones_recibidas_hiree_bp
    from .calificaciones.calificar_api import calificar_bp
    from .calificaciones.rate_contractor_api import rate_contractor_bp
    from .calificaciones.rate_hiree_api import rate_hiree_bp

    from .candidates.details_candidate_api import details_candidate_bp

    from .contracts.contract_requests_api import contract_requests_bp
    from .contracts.contract_vigent_api import contract_vigent_bp
    from .contracts.contratos_roles_api import contratos_roles_bp
    from .contracts.create_contract_api import create_contract_bp

    from .dashboard.dashboard_main_api import dashboard_main_bp

    from .inicio.index_api import index_bp

    from .notifications.accept_notification_api import accept_notification_bp
    from .notifications.chat_api import chat_bp
    from .notifications.detail_notifications_api import detail_notifications_bp
    from .notifications.notifications_api import notifications_bp
    from .notifications.reject_notification_api import reject_notification_bp
    from .notifications.request_more_details_bp import request_more_details_bp
    from .notifications.show_notifications_api import show_notifications_bp

    from .profile.edit_profile_api import edit_profile_bp
    from .profile.logic_delete_user_api import logic_delete_user_bp
    from .profile.view_logged_user_api import view_logged_user_bp
    from .profile.view_user_info_api import view_user_info_bp

    from .search.search_results_api import search_results_bp

    from .services.count_service_api import count_total_service_bp
    from .services.delete_principal_service_api import delete_principal_service_bp
    from .services.delete_service_api import delete_service_bp
    from .services.edit_service_api import edit_service_bp
    from .services.filter_service_results_api import filter_service_results_bp
    from .services.publish_service_api import publish_service_bp
    from .services.search_service_autocomplete_api import search_service_autocomplete_bp
    from .services.total_service_api import total_service_bp
    from .services.view_service_page_bp import view_service_page_bp

    from .utils.get_cities_api import get_cities_bp
    from .utils.register_user_api import register_user_bp

    # Registrar los Blueprints en el Blueprint principal
    api_bp.register_blueprint(auth_api_bp)
    api_bp.register_blueprint(close_sesion_bp)
    api_bp.register_blueprint(init_sesion_bp)
    api_bp.register_blueprint(password_bp)

    api_bp.register_blueprint(calificaciones_recibidas_contractor_bp)
    api_bp.register_blueprint(calificaciones_recibidas_hiree_bp)
    api_bp.register_blueprint(calificar_bp)
    api_bp.register_blueprint(rate_contractor_bp)
    api_bp.register_blueprint(rate_hiree_bp)

    api_bp.register_blueprint(details_candidate_bp)

    api_bp.register_blueprint(contract_requests_bp)
    api_bp.register_blueprint(contract_vigent_bp)
    api_bp.register_blueprint(contratos_roles_bp)
    api_bp.register_blueprint(create_contract_bp)

    api_bp.register_blueprint(dashboard_main_bp)

    api_bp.register_blueprint(index_bp)

    api_bp.register_blueprint(accept_notification_bp)
    api_bp.register_blueprint(chat_bp)
    api_bp.register_blueprint(detail_notifications_bp)
    api_bp.register_blueprint(notifications_bp)
    api_bp.register_blueprint(reject_notification_bp)
    api_bp.register_blueprint(request_more_details_bp)
    api_bp.register_blueprint(show_notifications_bp)

    api_bp.register_blueprint(edit_profile_bp)
    api_bp.register_blueprint(logic_delete_user_bp)
    api_bp.register_blueprint(view_logged_user_bp)
    api_bp.register_blueprint(view_user_info_bp)

    api_bp.register_blueprint(search_results_bp)

    api_bp.register_blueprint(count_total_service_bp)
    api_bp.register_blueprint(delete_principal_service_bp)
    api_bp.register_blueprint(delete_service_bp)
    api_bp.register_blueprint(edit_service_bp)
    api_bp.register_blueprint(filter_service_results_bp)
    api_bp.register_blueprint(publish_service_bp)
    api_bp.register_blueprint(search_service_autocomplete_bp)
    api_bp.register_blueprint(total_service_bp)
    api_bp.register_blueprint(view_service_page_bp)

    api_bp.register_blueprint(get_cities_bp)
    api_bp.register_blueprint(register_user_bp)

    # Registrar el Blueprint principal en la aplicación
    app.register_blueprint(api_bp, url_prefix='/api')
