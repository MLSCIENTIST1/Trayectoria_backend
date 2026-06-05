"""
Test de moderación de videos/feed + perfiles de creador (Admin Panel — Sprint A31).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_videos_a31.py
"""
import os
import sys
import inspect
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.models.colombia_data.negocio_video import aplicar_accion_video, ACCIONES_MODERACION_VIDEO

    print("\n[1] aplicar_accion_video — función pura")
    check("aprobar → aprobado + visible", aplicar_accion_video('aprobar') == {'estado_moderacion': 'aprobado', 'visible': True})
    check("rechazar → rechazado + oculto", aplicar_accion_video('rechazar') == {'estado_moderacion': 'rechazado', 'visible': False})
    check("ocultar → visible False", aplicar_accion_video('ocultar') == {'visible': False})
    check("mostrar → visible True", aplicar_accion_video('mostrar') == {'visible': True})
    check("destacar → destacado True", aplicar_accion_video('destacar') == {'destacado': True})
    check("quitar_destacado → destacado False", aplicar_accion_video('quitar_destacado') == {'destacado': False})
    check("mayúsculas/espacios tolerados", aplicar_accion_video('  APROBAR ') is not None)
    check("acción inválida → None", aplicar_accion_video('borrar') is None)
    check("None → None", aplicar_accion_video(None) is None)
    check("set de acciones completo", ACCIONES_MODERACION_VIDEO == {
        'aprobar', 'rechazar', 'ocultar', 'mostrar', 'destacar', 'quitar_destacado'})

    print("\n[2] Endpoints de moderación de video")
    import src.api.admin_api as api
    check("admin_videos existe", hasattr(api, 'admin_videos'))
    check("moderar_video existe", hasattr(api, 'moderar_video'))
    src_list = inspect.getsource(api.admin_videos)
    check("listado join nombre_negocio", 'nombre_negocio' in src_list and 'id_negocio' in src_list)
    check("listado filtra ocultos por visible", "v.visible = FALSE" in src_list)
    check("listado resume por estado_moderacion", 'GROUP BY LOWER(estado_moderacion)' in src_list)
    src_mod = inspect.getsource(api.moderar_video)
    check("moderar usa aplicar_accion_video", 'aplicar_accion_video' in src_mod)
    check("moderar valida acción", "'Acción inválida'" in src_mod)
    check("moderar 404 si no existe", '404' in src_mod)
    check("moderar audita", 'registrar_auditoria' in src_mod)
    check("rechazo guarda motivo", 'motivo_rechazo' in src_mod)

    print("\n[3] Perfiles de creador")
    check("admin_perfiles_creador existe", hasattr(api, 'admin_perfiles_creador'))
    check("moderar_perfil_creador existe", hasattr(api, 'moderar_perfil_creador'))
    src_pc = inspect.getsource(api.admin_perfiles_creador)
    check("excluye negocios en papelera", 'eliminado' in src_pc)
    src_mpc = inspect.getsource(api.moderar_perfil_creador)
    check("actualiza perfil_publico", 'perfil_publico' in src_mpc)
    check("perfil audita", 'registrar_auditoria' in src_mpc)

    print("\n[4] Permisos")
    check("admin_videos requiere permiso negocios", "requiere_permiso('negocios')" in src_list)
    check("moderar_perfil requiere permiso negocios", "requiere_permiso('negocios')" in src_mpc)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
