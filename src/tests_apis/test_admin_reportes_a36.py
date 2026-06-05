"""
Test del centro de reportes exportables (Admin Panel — Sprint A36).

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_admin_reportes_a36.py
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
    from src.api.utils.reportes_service import a_csv, _celda_csv

    print("\n[1] _celda_csv — escape PURO")
    check("texto simple sin cambios", _celda_csv('hola') == 'hola')
    check("None → vacío", _celda_csv(None) == '')
    check("número → str", _celda_csv(42) == '42')
    check("coma → entre comillas", _celda_csv('a,b') == '"a,b"')
    check("comillas → escapadas y envueltas", _celda_csv('di "hola"') == '"di ""hola"""')
    check("salto de línea → entre comillas", _celda_csv('a\nb') == '"a\nb"')

    print("\n[2] a_csv — serialización")
    headers = [('id', 'ID'), ('nombre', 'Nombre')]
    filas = [{'id': 1, 'nombre': 'Tienda A'}, {'id': 2, 'nombre': 'B, con coma'}]
    csv = a_csv(headers, filas)
    check("empieza con BOM (Excel UTF-8)", csv.startswith('﻿'))
    lineas = csv.replace('﻿', '').split('\r\n')
    check("encabezado correcto", lineas[0] == 'ID,Nombre')
    check("primera fila", lineas[1] == '1,Tienda A')
    check("coma escapada en fila", lineas[2] == '2,"B, con coma"')
    check("usa CRLF", '\r\n' in csv)

    print("\n[3] a_csv — bordes")
    check("filas vacías → solo encabezado", a_csv(headers, []).replace('﻿', '') == 'ID,Nombre')
    check("filas None → solo encabezado", a_csv(headers, None).replace('﻿', '') == 'ID,Nombre')
    check("clave faltante → celda vacía", a_csv(headers, [{'id': 9}]).endswith('9,'))

    print("\n[4] Endpoints")
    import src.api.admin_api as api
    check("reportes_resumen existe", hasattr(api, 'reportes_resumen'))
    check("reportes_export existe", hasattr(api, 'reportes_export'))
    src_r = inspect.getsource(api.reportes_resumen)
    check("resumen calcula economía tukoins", 'tukoins_transacciones' in src_r)
    check("resumen calcula crecimiento", 'date_trunc' in src_r)
    check("resumen excluye papelera", 'eliminado' in src_r)
    src_e = inspect.getsource(api.reportes_export)
    check("export usa a_csv", 'a_csv' in src_e)
    check("export soporta tipos negocios/usuarios/tukoins/crecimiento",
          all(t in src_e for t in ('negocios', 'usuarios', 'tukoins', 'crecimiento')))
    check("export audita", "registrar_auditoria('export'" in src_e)
    check("export valida tipo inválido", 'Tipo de reporte inválido' in src_e)
    check("ambos requieren permiso reportes", "requiere_permiso('reportes')" in src_r and "requiere_permiso('reportes')" in src_e)

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
