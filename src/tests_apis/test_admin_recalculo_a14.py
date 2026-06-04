"""
Test del recálculo masivo (Admin Panel — Sprint A14).
Verifica: lógica de diffs de nivel, dry-run del servicio de insignias,
y que el flujo cumple las 2 condiciones (preview obligatorio + aplicar superadmin/auditado).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_recalculo_a14.py
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


NIVELES = [(0,1,'🌱 Semilla'), (100,2,'🌱 II'), (250,3,'🌿 Brote'), (25000,30,'🏆 Leyenda')]


def main():
    from src.models.colombia_data.ratings.config_gamificacion import nivel_por_xp
    import src.api.admin_api as api
    from src.api.utils.badge_verification_service import BadgeVerificationService

    print("\n[1] Diff de nivel (lógica del recálculo)")
    # negocio con xp 150 pero nivel guardado 1 → debería pasar a 2
    def diff(xp, nivel_guardado):
        nuevo, _ = nivel_por_xp(xp, NIVELES)
        return nuevo if nuevo != nivel_guardado else None
    check("xp 150 guardado nivel 1 → cambia a 2", diff(150, 1) == 2)
    check("xp 150 guardado nivel 2 → sin cambio", diff(150, 2) is None)
    check("xp 25000 guardado nivel 3 → cambia a 30", diff(25000, 3) == 30)
    check("xp 50 guardado nivel 1 → sin cambio", diff(50, 1) is None)

    print("\n[2] Dry-run de insignias en el servicio (sin escribir)")
    check("simular_badges existe", hasattr(BadgeVerificationService, 'simular_badges'))
    src_sim = inspect.getsource(BadgeVerificationService.simular_badges)
    check("simular_badges NO asigna (sin _asignar_badge)", '_asignar_badge' not in src_sim)
    check("simular_badges NO hace commit", 'commit' not in src_sim)

    print("\n[3] Endpoints registrados")
    check("recalcular_preview existe", hasattr(api, 'recalcular_preview'))
    check("recalcular_aplicar existe", hasattr(api, 'recalcular_aplicar'))

    print("\n[4] Condición 1: dry-run obligatorio (aplicar exige confirmar)")
    src_apl = inspect.getsource(api.recalcular_aplicar)
    check("aplicar exige confirmar=true", "confirmar" in src_apl and "is not True" in src_apl)
    src_prev = inspect.getsource(api.recalcular_preview)
    check("preview es dry_run y no escribe", "'dry_run': True" in src_prev and 'commit' not in src_prev)

    print("\n[5] Condición 2: aplicar exige superadmin + auditoría con conteo")
    check("recalcular_aplicar decorado con @superadmin_required",
          "@superadmin_required" in src_apl)
    check("aplicar audita con 'recalcular' + modificados",
          "registrar_auditoria('recalcular'" in src_apl and "modificados" in src_apl)
    check("preview NO es superadmin (basta permiso de módulo)",
          "@requiere_permiso('gamificacion')" in src_prev)

    print("\n[6] Tope de seguridad (no silent cap)")
    check("hay RECALC_CAP", hasattr(api, 'RECALC_CAP'))
    check("preview reporta 'capado'", "'capado'" in src_prev)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
