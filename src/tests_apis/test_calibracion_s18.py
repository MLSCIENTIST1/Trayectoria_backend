"""
Test de calibración de dificultad de badges (Sprint 18).
Bloquea la curva: badges futuros no pueden romper la monotonicidad ni
introducir niveles/operadores inválidos. Es un test de REGRESIÓN.

Ejecutar:
    PYTHONUTF8=1 venv/Scripts/python.exe src/tests_apis/test_calibracion_s18.py
"""
import os
import sys
from collections import defaultdict, Counter
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

PASS = 0; FAIL = 0
def check(n, c):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n}")
    else: FAIL += 1; print(f"  ❌ {n}")


def main():
    from src.models.colombia_data.ratings.negocio_badge import BADGES_INICIALES, CURVA_DIFICULTAD

    print("\n[1] Integridad básica del catálogo")
    cods = [b['codigo'] for b in BADGES_INICIALES]
    check("sin códigos duplicados", len(cods) == len(set(cods)))
    check("todos tienen criterio_tipo", all(b.get('criterio_tipo') for b in BADGES_INICIALES))
    check("todos los niveles entre 1 y 5", all(1 <= b['nivel'] <= 5 for b in BADGES_INICIALES))
    OPS = {'>=', '<=', '==', '>', '<', '!='}
    check("operadores válidos", all(b.get('criterio_operador', '>=') in OPS for b in BADGES_INICIALES))
    check("CURVA_DIFICULTAD tiene 5 niveles", len(CURVA_DIFICULTAD) == 5)

    print("\n[2] Monotonicidad por familia de métrica")
    # Dentro de un mismo criterio_tipo con operador '>=', a mayor valor → nivel >=
    fam = defaultdict(list)
    for b in BADGES_INICIALES:
        if b.get('criterio_operador', '>=') == '>=':
            fam[b['criterio_tipo']].append((b['criterio_valor'], b['nivel'], b['codigo']))
    violaciones = []
    for tipo, items in fam.items():
        items.sort()
        for i in range(len(items) - 1):
            if items[i + 1][1] < items[i][1]:
                violaciones.append(f"{items[i+1][2]} en {tipo}")
    check("0 violaciones de monotonicidad", len(violaciones) == 0)
    if violaciones:
        for v in violaciones:
            print(f"     ⚠️ {v}")

    print("\n[3] Distribución piramidal (élite es raro)")
    dist = Counter(b['nivel'] for b in BADGES_INICIALES)
    check("hay badges Bronce (nivel 1)", dist[1] >= 1)
    check("Diamante (5) es el más escaso o empatado", dist[5] <= dist[1])
    check("Platino+Diamante < Bronce+Plata (pirámide)",
          (dist[4] + dist[5]) < (dist[1] + dist[2]))

    print("\n[4] Coherencia puntos vs nivel (no decrecientes por nivel promedio)")
    # El promedio de puntos por nivel debe crecer con el nivel
    pts = defaultdict(list)
    for b in BADGES_INICIALES:
        pts[b['nivel']].append(b.get('puntos', 0))
    proms = {n: (sum(v) / len(v)) for n, v in pts.items()}
    niveles_ordenados = sorted(proms)
    creciente = all(proms[niveles_ordenados[i]] <= proms[niveles_ordenados[i + 1]]
                    for i in range(len(niveles_ordenados) - 1))
    check("puntos promedio crecen (o se mantienen) con el nivel", creciente)

    print(f"\n  Distribución: " + ", ".join(f"{CURVA_DIFICULTAD[n]}={dist[n]}" for n in sorted(dist)))
    print(f"\n{'='*50}\n  RESULTADO: {PASS} pasaron, {FAIL} fallaron\n{'='*50}")
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
