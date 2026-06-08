"""
Badges sociales — seguidores y me_gusta (catálogo + lógica de criterio).

Estrategia (§7): helpers puros, sin tocar las ~30 tablas que usa el cálculo
completo de métricas. Verifica que:
  - El catálogo BADGES_INICIALES tiene los 12 badges sociales con los umbrales esperados.
  - NegocioBadge.verificar_criterio (método puro) evalúa bien los umbrales.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_badges_sociales.py
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


# Umbrales esperados por código
SEGUIDORES = {
    'primer_seguidor': 1, 'comunidad_fiel': 25, 'influencer_local': 100,
    'celebridad': 500, 'idolo_de_masas': 1000,
}
ME_GUSTA = {
    'primer_like': 1, 'gustando': 50, 'muy_querido': 200, 'favorito_barrio': 500,
    'sensacion_viral': 1000, 'fenomeno_total': 5000, 'leyenda_imparable': 10000,
}


def main():
    from src.models.colombia_data.ratings.negocio_badge import BADGES_INICIALES, NegocioBadge

    por_codigo = {b['codigo']: b for b in BADGES_INICIALES}

    print("\n[1] Existen los 12 badges sociales en el catálogo")
    for cod in list(SEGUIDORES) + list(ME_GUSTA):
        check(f"existe '{cod}'", cod in por_codigo)

    print("\n[2] Seguidores: criterio_tipo='seguidores', operador '>=', umbral correcto")
    for cod, val in SEGUIDORES.items():
        b = por_codigo.get(cod, {})
        check(f"{cod}: tipo seguidores", b.get('criterio_tipo') == 'seguidores')
        check(f"{cod}: umbral {val} (>=)", b.get('criterio_valor') == val and b.get('criterio_operador') == '>=')

    print("\n[3] Me gusta: criterio_tipo='me_gusta', operador '>=', umbral correcto")
    for cod, val in ME_GUSTA.items():
        b = por_codigo.get(cod, {})
        check(f"{cod}: tipo me_gusta", b.get('criterio_tipo') == 'me_gusta')
        check(f"{cod}: umbral {val} (>=)", b.get('criterio_valor') == val and b.get('criterio_operador') == '>=')

    print("\n[4] Escalabilidad de likes: hay metas altas (1k, 5k, 10k)")
    valores_like = sorted(ME_GUSTA.values())
    check("incluye 1000", 1000 in valores_like)
    check("incluye 5000", 5000 in valores_like)
    check("incluye 10000", 10000 in valores_like)

    print("\n[5] verificar_criterio (método puro) evalúa bien los umbrales")
    viral = por_codigo['sensacion_viral']
    nb = NegocioBadge(criterio_tipo=viral['criterio_tipo'],
                      criterio_valor=viral['criterio_valor'],
                      criterio_operador=viral['criterio_operador'])
    check("999 likes NO desbloquea viral(1000)", nb.verificar_criterio(999) is False)
    check("1000 likes SÍ desbloquea viral", nb.verificar_criterio(1000) is True)
    check("5000 likes SÍ desbloquea viral", nb.verificar_criterio(5000) is True)

    ps = por_codigo['primer_seguidor']
    nb2 = NegocioBadge(criterio_tipo=ps['criterio_tipo'],
                       criterio_valor=ps['criterio_valor'],
                       criterio_operador=ps['criterio_operador'])
    check("0 seguidores NO desbloquea primer_seguidor", nb2.verificar_criterio(0) is False)
    check("1 seguidor SÍ desbloquea primer_seguidor", nb2.verificar_criterio(1) is True)

    print("\n[6] Todos son categoría 'popularidad'")
    for cod in list(SEGUIDORES) + list(ME_GUSTA):
        check(f"{cod}: popularidad", por_codigo.get(cod, {}).get('categoria') == 'popularidad')

    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
