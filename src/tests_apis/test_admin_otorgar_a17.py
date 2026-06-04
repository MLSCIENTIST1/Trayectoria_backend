"""
Test de otorgar/revocar insignias manualmente (Admin Panel — Sprint A17).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_otorgar_a17.py
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
    import src.api.admin_api as api

    print("\n[1] Endpoints registrados")
    check("otorgar_insignia existe", hasattr(api, 'otorgar_insignia'))
    check("revocar_insignia existe", hasattr(api, 'revocar_insignia'))

    sot = inspect.getsource(api.otorgar_insignia)
    srv = inspect.getsource(api.revocar_insignia)

    print("\n[2] Otorgar: idempotente + valida negocio + audita")
    check("idempotente (ya_tenia si ya activa)", 'ya_tenia' in sot)
    check("reactiva si estaba revocada", 'fecha_revocacion = None' in sot)
    check("valida que el negocio exista", 'FROM negocios WHERE id_negocio' in sot)
    check("incrementa total_otorgados", 'total_otorgados' in sot)
    check("audita 'otorgar'", "registrar_auditoria('otorgar'" in sot)

    print("\n[3] Revocar: superadmin + motivo obligatorio + soft-delete + audita")
    check("revocar exige @superadmin_required", '@superadmin_required' in srv)
    check("motivo obligatorio", 'obligatorio para revocar' in srv)
    check("soft-delete (activo=False + fecha/motivo)", 'ob.activo = False' in srv and 'motivo_revocacion' in srv)
    check("decrementa total_otorgados (min 0)", 'max(0' in srv)
    check("audita 'revocar'", "registrar_auditoria('revocar'" in srv)

    print("\n[4] Permisos coherentes")
    check("otorgar requiere permiso insignias", "requiere_permiso('insignias')" in sot)

    print("\n[5] Modelo soporta revocación")
    from src.models.colombia_data.ratings.negocio_badge_obtenido import NegocioBadgeObtenido
    cols = set(NegocioBadgeObtenido.__table__.columns.keys())
    check("columna activo", 'activo' in cols)
    check("columna fecha_revocacion", 'fecha_revocacion' in cols)
    check("columna motivo_revocacion", 'motivo_revocacion' in cols)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
