"""
Test del prefijo robusto del código de pedido (Fix F4).
Verifica que NUNCA se genere un prefijo vacío (bug '-2026-0043').

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_fix_codigo_pedido_f4.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.models.compradores.pedido import Pedido

    print("\n[1] Prefijo desde slug normal")
    check("'rodar' → 'ROD'", Pedido._prefijo_codigo({'slug': 'rodar'}) == 'ROD')
    check("'MiTienda' → 'MIT'", Pedido._prefijo_codigo({'slug': 'MiTienda'}) == 'MIT')

    print("\n[2] Slug vacío / None → no queda vacío (BUG '-2026-0043')")
    check("slug '' → cae a nombre", Pedido._prefijo_codigo({'slug': '', 'nombre': 'Carnes Pepe'}) == 'CAR')
    check("slug None → cae a nombre", Pedido._prefijo_codigo({'slug': None, 'nombre': 'Donas'}) == 'DON')
    check("slug y nombre vacíos → 'PED'", Pedido._prefijo_codigo({'slug': '', 'nombre': ''}) == 'PED')
    check("dict vacío → 'PED'", Pedido._prefijo_codigo({}) == 'PED')
    check("None → 'PED'", Pedido._prefijo_codigo(None) == 'PED')

    print("\n[3] Saneo de caracteres")
    check("'la-tienda' → 'LAT' (sin guion)", Pedido._prefijo_codigo({'slug': 'la-tienda'}) == 'LAT')
    check("'  rodar ' → 'ROD' (trim)", Pedido._prefijo_codigo({'slug': '  rodar '}) == 'ROD')
    check("'🛒x' → 'X' (sin emoji)", Pedido._prefijo_codigo({'slug': '🛒x'}) == 'X')
    check("solo símbolos → 'PED'", Pedido._prefijo_codigo({'slug': '###'}) == 'PED')

    print("\n[4] El prefijo resultante NUNCA es vacío")
    for caso in [{'slug': ''}, {'slug': None}, {}, None, {'slug': '---'}, {'nombre': '...'}]:
        pf = Pedido._prefijo_codigo(caso)
        check(f"{caso} → prefijo no vacío ('{pf}')", bool(pf) and pf != '')

    print("\n[5] Formato del código (no empieza con '-')")
    # Simula el formato sin tocar la BD
    año = '2026'
    for caso in [{'slug': ''}, {'slug': 'rodar'}, None]:
        pf = Pedido._prefijo_codigo(caso)
        codigo = f"{pf}-{año}-0043"
        check(f"código '{codigo}' no empieza con '-'", not codigo.startswith('-'))

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
