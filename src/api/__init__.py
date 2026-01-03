import sys
from flask import Blueprint

api_bp = Blueprint("api", __name__)

# 📌 Importación de Blueprints
try:
    # Blueprints de autenticación (importados aquí pero registrados directamente en src/__init__.py)
    from .auth.close_sesion_api import close_sesion_bp
    from .auth.init_sesion_api import init_sesion_bp
    from .auth.password_api import password_bp
    from .auth.status_sesion_api import status_sesion_bp

    from .perfil_api import perfil_bp
    from .perfil_render_api import perfil_render_bp
    from .notifications.chat_api import chat_bp
    from .notifications.detail_notifications_api import detail_notifications_bp
    from .notifications.notifications_api import notifications_bp
    from .notifications.reject_notification_api import reject_notification_bp
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
    from .services.publish_service_api import publish_service_bp
    from .services.search_service_autocomplete_api import search_service_autocomplete_bp
    from .services.total_service_api import total_service_bp
    from .formulario_api import formulario_bp
    from .utils.get_cities_api import get_cities_bp
    from .utils.register_user_api import register_user_bp
    from .plantillas_api import plantillas_bp
    from .negocio_api import catalogo_api_bp

    try:
        from .services.filter_service_results_api import filter_service_results_bp
    except ImportError as e:
        print(f"❌ Error importando filter_service_results_api: {e}", file=sys.stderr)
        filter_service_results_bp = None

except ImportError as e:
    print(f"❌ Error en `src/api/__init__.py`: {e}", file=sys.stderr)


# ✅ Lista de Blueprints a registrar DENTRO de `api_bp` (excluyendo los de auth)
blueprints = [
    perfil_bp, perfil_render_bp, formulario_bp, chat_bp, detail_notifications_bp, notifications_bp,
    reject_notification_bp, show_notifications_bp,
    edit_profile_bp, logic_delete_user_bp, view_logged_user_bp, view_user_info_bp,
    search_results_bp, count_total_service_bp, delete_principal_service_bp,
    delete_service_bp, edit_service_bp, publish_service_bp,
    search_service_autocomplete_bp, total_service_bp, plantillas_bp,
    get_cities_bp, register_user_bp, catalogo_api_bp
]

# ✅ Registrar los Blueprints en `api_bp` sin prefijos adicionales
for bp in blueprints:
    if bp:
        api_bp.register_blueprint(bp)
    else:
        print(f"⚠️ Se omitió un Blueprint porque es `None`: {bp}")

# ✅ Registrar `filter_service_results_bp` si fue importado correctamente
if filter_service_results_bp:
    api_bp.register_blueprint(filter_service_results_bp)

# 📌 Exportar `api_bp` para que `app.py` lo importe correctamente
__all__ = ["api_bp"]