"""
Test de Feature Flags v2 — rollout % + overrides (Admin Panel — Sprint A39).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_featureflags_a39.py
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
    from src.models.feature_models import en_rollout, FeatureOverride, FeatureFlag

    print("\n[1] en_rollout — determinista y por bordes")
    check("pct 100 → siempre dentro", en_rollout(1, 'x', 100) is True)
    check("pct None → dentro (default)", en_rollout(1, 'x', None) is True)
    check("pct 0 → siempre fuera", en_rollout(1, 'x', 0) is False)
    check("pct negativo → fuera", en_rollout(1, 'x', -5) is False)
    check("pct >100 → dentro", en_rollout(1, 'x', 150) is True)
    check("no numérico → dentro (no bloquea)", en_rollout(1, 'x', 'abc') is True)
    # Determinismo: misma entrada → mismo resultado
    r1 = en_rollout(42, 'inv_videos', 50); r2 = en_rollout(42, 'inv_videos', 50)
    check("determinista (mismo negocio+feature)", r1 == r2)
    # Distribución aproximada: con 50%, ~mitad de 200 negocios entran
    dentro = sum(1 for i in range(200) if en_rollout(i, 'feat', 50))
    check("pct 50 reparte ~mitad (200 negocios)", 60 <= dentro <= 140)
    # Monotonía: si entra al 30%, entra al 60% (mismo bucket)
    monot = all((not en_rollout(i, 'f', 30)) or en_rollout(i, 'f', 60) for i in range(100))
    check("monótono: dentro al 30% ⇒ dentro al 60%", monot)

    print("\n[2] Modelo override")
    check("FeatureOverride tabla feature_overrides", FeatureOverride.__tablename__ == 'feature_overrides')
    check("FeatureFlag tiene rollout_pct", hasattr(FeatureFlag, 'rollout_pct'))
    check("to_dict incluye rollout_pct", 'rollout_pct' in inspect.getsource(FeatureFlag.to_dict))

    print("\n[3] Motor check_negocio_feature integra override + rollout")
    import src.models.feature_models as fm
    src_chk = inspect.getsource(fm.check_negocio_feature)
    check("considera override OFF", "'override_off'" in src_chk)
    check("considera override ON", "'override_on'" in src_chk)
    check("aplica rollout (rollout_pending)", "'rollout_pending'" in src_chk and 'en_rollout' in src_chk)
    check("override gana sobre plan/rollout (se evalúa primero)",
          src_chk.index('FeatureOverride') < src_chk.index('plan_feature'))

    print("\n[4] Endpoints")
    import src.api.admin_features_api as feat
    for fn in ['set_feature_rollout', 'list_feature_overrides', 'upsert_feature_override', 'delete_feature_override']:
        check(f"{fn} existe", hasattr(feat, fn))
    src_roll = inspect.getsource(feat.set_feature_rollout)
    check("rollout valida rango 0-100", '0 <= pct <= 100' in src_roll)
    check("rollout audita", 'registrar_auditoria' in src_roll)
    src_up = inspect.getsource(feat.upsert_feature_override)
    check("override valida feature_key y negocio", 'feature_key' in src_up and 'Negocio no encontrado' in src_up)
    check("override audita", 'registrar_auditoria' in src_up)

    print("\n[5] Migración en create_app (lección F8)")
    import src as _src
    src_init = inspect.getsource(_src.create_app)
    check("ALTER feature_flags rollout_pct", 'rollout_pct INTEGER DEFAULT 100' in src_init)
    check("CREATE TABLE feature_overrides", 'CREATE TABLE IF NOT EXISTS feature_overrides' in src_init)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
