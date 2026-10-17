"""Tema 8: Máximos y mínimos (puntos críticos, crecimiento, extremos absolutos)."""

import sympy as sp

from . import Reintentar, Tema
from ._util import L, distintos, entero, nuevo, paso, x


def _cubica(rng):
    """f con f'(x) = 6(x - r1)(x - r2): coeficientes enteros y raíces enteras."""
    r1, r2 = sorted(distintos(rng, -4, 4, 2, ()))
    c = entero(rng, -6, 6, ())
    f = 2 * x**3 - 3 * (r1 + r2) * x**2 + 6 * r1 * r2 * x + c
    return f, r1, r2


def puntos_criticos(rng):
    f, r1, r2 = _cubica(rng)
    df = sp.diff(f, x)
    criticos = sorted(sp.solve(df, x))
    pasos = [
        paso("Definición", "Los puntos críticos son los $x$ donde $f'(x) = 0$ (o donde $f'$ no existe)."),
        paso("Derivar", "", rf"f'(x) = {L(df)}"),
        paso("Igualar a cero y factorizar", "", rf"{L(df)} = {L(sp.factor(df))} = 0"),
        paso("Soluciones", "", rf"x = {L(criticos[0])},\quad x = {L(criticos[1])}"),
    ]
    return nuevo(f"Halla los puntos críticos de $f(x) = {L(f)}$.", "conjunto", criticos, pasos,
                 ["Deriva e iguala la derivada a cero.", "Saca factor común y factoriza el trinomio."])


def minimo_local(rng):
    f, r1, r2 = _cubica(rng)
    df, d2f = sp.diff(f, x), sp.diff(f, x, 2)
    criticos = sorted(sp.solve(df, x))
    minimos = [c for c in criticos if d2f.subs(x, c) > 0]
    if len(minimos) != 1:
        raise Reintentar
    xm = minimos[0]
    pasos = [
        paso("Puntos críticos", "", rf"f'(x) = {L(sp.factor(df))} = 0 \;\Rightarrow\; x = {L(criticos[0])},\; x = {L(criticos[1])}"),
        paso("Criterio de la segunda derivada", "Si $f''(c) > 0$ la gráfica es cóncava hacia arriba (forma de U): hay un **mínimo**. "
             "Si $f''(c) < 0$ hay un **máximo**.", rf"f''(x) = {L(d2f)}"),
        paso("Evaluar f''", "", ",\\quad ".join(rf"f''({L(c)}) = {L(d2f.subs(x, c))}" for c in criticos)),
        paso("Conclusión", "", rf"\text{{mínimo local en }} x = {L(xm)}"),
    ]
    return nuevo(f"¿En qué valor de $x$ tiene un **mínimo local** la función $f(x) = {L(f)}$?", "numero", xm, pasos,
                 ["Encuentra los puntos críticos.", "Usa la segunda derivada: $f''(c) > 0$ indica mínimo."])


def intervalos_crecimiento(rng):
    f, r1, r2 = _cubica(rng)
    df = sp.diff(f, x)
    crece = sp.solveset(df > 0, x, sp.S.Reals)
    pasos = [
        paso("Idea", "$f$ crece donde $f'(x) > 0$ y decrece donde $f'(x) < 0$."),
        paso("Derivada factorizada", "", rf"f'(x) = {L(sp.factor(df))}"),
        paso("Tabla de signos", f"Los puntos críticos ${r1}$ y ${r2}$ dividen la recta. Probamos un valor en cada parte: "
             f"$f'$ es positiva antes de ${r1}$, negativa entre ambos y positiva después de ${r2}$."),
        paso("Conclusión", "", rf"f \text{{ crece en }} {L(crece)}"),
    ]
    return nuevo(f"¿En qué intervalos es **creciente** $f(x) = {L(f)}$?", "desigualdad", crece, pasos,
                 ["Resuelve $f'(x) > 0$.", "Haz una tabla de signos con los puntos críticos."])


def extremo_absoluto(rng):
    f, r1, r2 = _cubica(rng)
    a = r1 - entero(rng, 1, 2)
    b = r2 + entero(rng, 1, 2)
    criticos = [c for c in sp.solve(sp.diff(f, x), x) if a <= c <= b]
    candidatos = sorted(set(criticos + [a, b]))
    valores = {c: f.subs(x, c) for c in candidatos}
    maximo = max(valores.values())
    pasos = [
        paso("Método del intervalo cerrado", "En $[a, b]$ el máximo absoluto está en un punto crítico o en un extremo del intervalo: "
             "evaluamos $f$ en todos esos candidatos y elegimos el mayor."),
        paso("Candidatos", "", r",\; ".join(L(c) for c in candidatos)),
        paso("Evaluar f", "", r",\quad ".join(rf"f({L(c)}) = {L(v)}" for c, v in valores.items())),
        paso("Conclusión", "", rf"\text{{máximo absoluto}} = {L(maximo)}"),
    ]
    return nuevo(f"Halla el **valor máximo absoluto** de $f(x) = {L(f)}$ en el intervalo $[{a}, {b}]$.", "numero", maximo,
                 pasos, ["Calcula los puntos críticos dentro del intervalo.", "Evalúa $f$ en ellos y en los extremos $a$ y $b$."])


TEMA = Tema(
    id="maximos_minimos",
    nombre="Máximos y mínimos",
    orden=8,
    descripcion="Puntos críticos, crecimiento, criterio de la segunda derivada, extremos absolutos.",
    generadores={
        "basico": [puntos_criticos],
        "medio": [minimo_local, intervalos_crecimiento],
        "parcial": [extremo_absoluto],
    },
    ejemplos=[("basico", 1), ("medio", 1), ("parcial", 1)],
)
