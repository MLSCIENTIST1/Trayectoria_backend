"""
Test de insignias de temporada/vigencia (Admin Panel — Sprint A19).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_temporada_a19.py
"""
import os
import sys
import inspect
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.models.colombia_data.ratings.config_gamificacion import badge_vigente, validar_badge

    print("\n[1] badge_vigente (función pura)")
    check("sin ventana → siempre vigente", badge_vigente(None, None, date(2026, 6, 15)) is True)
    check("dentro de ventana", badge_vigente(date(2026, 12, 1), date(2026, 12, 31), date(2026, 12, 15)) is True)
    check("antes del inicio → no vigente", badge_vigente(date(2026, 12, 1), date(2026, 12, 31), date(2026, 11, 30)) is False)
    check("después del fin → no vigente", badge_vigente(date(2026, 12, 1), date(2026, 12, 31), date(2027, 1, 1)) is False)
    check("solo inicio (sin fin)", badge_vigente(date(2026, 1, 1), None, date(2030, 1, 1)) is True)
    check("solo fin (sin inicio)", badge_vigente(None, date(2026, 12, 31), date(2026, 6, 1)) is True)
    check("bordes inclusivos (inicio)", badge_vigente(date(2026, 12, 1), date(2026, 12, 31), date(2026, 12, 1)) is True)
    check("bordes inclusivos (fin)", badge_vigente(date(2026, 12, 1), date(2026, 12, 31), date(2026, 12, 31)) is True)

    print("\n[2] validar_badge — vigencia")
    ok, limpio, err = validar_badge({'vigencia_inicio': '2026-12-01', 'vigencia_fin': '2026-12-31'})
    check("fechas válidas → ok", ok and err is None)
    check("parseadas a date", limpio['vigencia_inicio'] == date(2026, 12, 1))
    check("inicio > fin → inválido", validar_badge({'vigencia_inicio': '2026-12-31', 'vigencia_fin': '2026-12-01'})[0] is False)
    check("fecha basura → inválido", validar_badge({'vigencia_inicio': 'ayer'})[0] is False)
    ok2, l2, _ = validar_badge({'vigencia_inicio': '', 'vigencia_fin': ''})
    check("vacío → None (sin ventana)", ok2 and l2['vigencia_inicio'] is None and l2['vigencia_fin'] is None)

    print("\n[3] El servicio respeta la vigencia (gating)")
    nb = open(os.path.join(os.path.dirname(__file__), '..', 'api', 'utils', 'badge_verification_service.py'), encoding='utf-8').read()
    check("verificar_badges usa badge_vigente", nb.count('badge_vigente') >= 2)
    check("_get_catalogo_badges trae vigencia", 'vigencia_inicio' in nb and 'vigencia_fin' in nb)

    print("\n[4] Modelo + dict admin")
    from src.models.colombia_data.ratings.negocio_badge import NegocioBadge
    cols = set(NegocioBadge.__table__.columns.keys())
    check("columna vigencia_inicio", 'vigencia_inicio' in cols)
    check("columna vigencia_fin", 'vigencia_fin' in cols)
    import src.api.admin_api as api
    check("dict admin expone vigencia", 'vigencia_inicio' in inspect.getsource(api._badge_admin_dict))

    print("\n[5] Migración en run.py")
    runpy = open(os.path.join(os.path.dirname(__file__), '..', '..', 'run.py'), encoding='utf-8').read()
    check("run.py añade vigencia_inicio/fin", 'vigencia_inicio DATE' in runpy and 'vigencia_fin DATE' in runpy)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
