"""
F14 — "Miembro desde" usa la fecha MÁS ANTIGUA (no la de la migración).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_trust_miembro_desde.py
"""
import os
import sys
import inspect
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.api.tiendas.analytics_api import _fecha_miembro_desde, get_trust_data

    print("\n[1] _fecha_miembro_desde — PURO")
    d_old = datetime(2026, 1, 15)   # registro real
    d_mig = datetime(2026, 6, 1)    # fecha de la migración (incorrecta, más reciente)
    check("toma la más antigua (ene, no jun)", _fecha_miembro_desde([d_mig, d_old]) == 'Jan 2026')
    check("ignora None", _fecha_miembro_desde([None, d_old, None]) == 'Jan 2026')
    check("lista vacía → None", _fecha_miembro_desde([]) is None)
    check("solo None → None", _fecha_miembro_desde([None, None]) is None)
    check("una sola fecha", _fecha_miembro_desde([d_old]) == 'Jan 2026')

    print("\n[2] El endpoint usa varias señales (negocio, dueño, primer pedido)")
    src = inspect.getsource(get_trust_data)
    check("usa el helper _fecha_miembro_desde", '_fecha_miembro_desde' in src)
    check("considera el dueño (Usuario)", 'Usuario' in src and ('created_at' in src or 'fecha_aceptacion_terminos' in src))
    check("considera el primer pedido", 'Pedido.fecha_pedido' in src or 'min(Pedido' in src)
    check("ya NO usa solo neg.fecha_registro.strftime", "neg.fecha_registro.strftime" not in src)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
