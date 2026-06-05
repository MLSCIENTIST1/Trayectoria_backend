"""
Test de anuncios / notificaciones masivas (Admin Panel — Sprint A33).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_anuncios_a33.py
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
    from src.api.utils.anuncios_service import (
        construir_filtros_segmento, PLANTILLAS_ANUNCIO
    )

    print("\n[1] Plantillas")
    check("hay plantillas predefinidas", isinstance(PLANTILLAS_ANUNCIO, list) and len(PLANTILLAS_ANUNCIO) >= 3)
    check("cada plantilla tiene titulo y mensaje",
          all(p.get('titulo') and p.get('mensaje') for p in PLANTILLAS_ANUNCIO))

    print("\n[2] construir_filtros_segmento — función pura")
    conds, params = construir_filtros_segmento({})
    check("siempre excluye eliminados", any('eliminado' in c for c in conds))
    check("siempre exige usuario_id", any('usuario_id IS NOT NULL' in c for c in conds))
    check("sin filtros → sin params extra", params == {})

    conds2, params2 = construir_filtros_segmento({'ciudad': 'Bogota', 'plan': 'delux', 'nivel_min': 3})
    check("ciudad agrega condición + param", any('ciudad' in c for c in conds2) and params2.get('ciudad') == '%Bogota%')
    check("plan agrega condición + param", any('plan_key' in c for c in conds2) and params2.get('plan') == 'delux')
    check("nivel_min agrega condición + param", any('nivel' in c for c in conds2) and params2.get('nivel_min') == 3)

    print("\n[3] construir_filtros_segmento — bordes")
    check("nivel_min 0 → ignorado", 'nivel_min' not in construir_filtros_segmento({'nivel_min': 0})[1])
    check("nivel_min vacío → ignorado", 'nivel_min' not in construir_filtros_segmento({'nivel_min': ''})[1])
    check("nivel_min no numérico → ignorado", 'nivel_min' not in construir_filtros_segmento({'nivel_min': 'x'})[1])
    check("ciudad vacía → ignorada", 'ciudad' not in construir_filtros_segmento({'ciudad': '   '})[1])
    check("None → no rompe", construir_filtros_segmento(None)[0] is not None)

    print("\n[4] Servicio de envío")
    import src.api.utils.anuncios_service as svc
    check("contar_destinatarios existe", hasattr(svc, 'contar_destinatarios'))
    check("enviar_anuncio existe", hasattr(svc, 'enviar_anuncio'))
    src_env = inspect.getsource(svc.enviar_anuncio)
    check("usa INSERT ... SELECT (eficiente)", 'INSERT INTO notification' in src_env and 'SELECT DISTINCT' in src_env)
    check("type 'anuncio'", "'anuncio'" in src_env)
    check("sanea prioridad", "('alta', 'media', 'baja')" in src_env)

    print("\n[5] Endpoints + auditoría")
    import src.api.admin_api as api
    for fn in ['get_anuncio_plantillas', 'preview_anuncio', 'enviar_anuncio_masivo']:
        check(f"{fn} existe", hasattr(api, fn))
    src_send = inspect.getsource(api.enviar_anuncio_masivo)
    check("envío exige mensaje", "El mensaje es obligatorio" in src_send)
    check("envío exige confirmar", "confirmar" in src_send)
    check("envío audita con conteo", 'registrar_auditoria' in src_send and 'destinatarios' in src_send)
    check("endpoints requieren permiso usuarios", "requiere_permiso('usuarios')" in inspect.getsource(api.preview_anuncio))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
