"""
F13 — Verifica que create_app() asegure las columnas de la tabla `notification`.

Sin estas columnas (en tablas viejas de prod) las notificaciones automáticas
(A50/A51: badge ganado, plan cambiado, recompensa de liga) fallaban en silencio
y la campanita quedaba vacía.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_fix_notification_columns_f13.py
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
    import src as _src
    src_create = inspect.getsource(_src.create_app)

    print("\n[1] Migración de columnas de notification en create_app")
    columnas = ['negocio_id', 'titulo', 'message', 'type', 'prioridad',
                'is_read', 'is_accepted', 'referencia_tipo', 'referencia_id',
                'action_url', 'extra_data', 'timestamp', 'fecha_lectura']
    for col in columnas:
        check(f"ADD COLUMN IF NOT EXISTS {col}",
              f"ADD COLUMN IF NOT EXISTS {col}" in src_create and 'notification' in src_create)
    check("índice por negocio_id", 'ix_notif_negocio' in src_create)

    print("\n[2] El servicio sigue insertando con esas columnas")
    from src.api.utils import notificaciones_service as ns
    src_notif = inspect.getsource(ns.notificar_negocio)
    for col in ['user_id', 'negocio_id', 'titulo', 'message', 'prioridad', 'is_read']:
        check(f"INSERT usa {col}", col in src_notif)

    print("\n[3] El modelo define esas columnas (consistencia)")
    from src.models.notification import Notification
    cols = set(c.name for c in Notification.__table__.columns)
    for col in ['negocio_id', 'titulo', 'message', 'prioridad', 'is_read', 'type']:
        check(f"modelo tiene {col}", col in cols)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
