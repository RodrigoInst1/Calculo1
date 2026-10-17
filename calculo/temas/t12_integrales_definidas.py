"""Tema 12: Integrales definidas."""

import sympy as sp

from . import Tema
from ._util import L, LA, desde_solver, entero, x


def _ej(f, a, b, pistas):
    a, b = sp.sympify(a), sp.sympify(b)
    return desde_solver(f"Calcula $\\displaystyle\\int_{{{L(a)}}}^{{{L(b)}}} {LA(f)}\\,dx$.", "integral_definida",
                        {"expr": f, "variable": x, "a": a, "b": b}, pistas)


def polinomio(rng):
    a, b = entero(rng, -3, 6), entero(rng, -6, 6)
    lim_inf = entero(rng, -2, 1, ())
    lim_sup = lim_inf + entero(rng, 1, 3)
    return _ej(a * x**2 + b * x, lim_inf, lim_sup, ["Busca una primitiva $F$ y calcula $F(b) - F(a)$."])


def trig_exp(rng):
    opcion = rng.choice(["sin", "cos", "exp", "inv"])
    if opcion == "sin":
        return _ej(sp.sin(x), 0, sp.pi / entero(rng, 1, 3), ["$\\int \\sin x\\,dx = -\\cos x$."])
    if opcion == "cos":
        return _ej(sp.cos(x), 0, sp.pi / entero(rng, 2, 6), ["$\\int \\cos x\\,dx = \\sin x$."])
    if opcion == "exp":
        return _ej(sp.exp(x), 0, entero(rng, 1, 3), ["$\\int e^x dx = e^x$, y recuerda que $e^0 = 1$."])
    return _ej(1 / x, 1, sp.E ** entero(rng, 1, 3), ["$\\int \\frac{1}{x}dx = \\ln|x|$ y $\\ln(e^k) = k$."])


def con_sustitucion(rng):
    a = entero(rng, 1, 4)
    f = rng.choice([x * (x**2 + a) ** 2, 2 * x * sp.exp(x**2), x / (x**2 + a)])
    return _ej(f, 0, entero(rng, 1, 2), ["Haz la sustitución y luego evalúa (o cambia también los límites a $u$)."])


def por_partes(rng):
    f = rng.choice([x * sp.exp(x), x * sp.cos(x), sp.log(x)])
    if f == sp.log(x):
        return _ej(f, 1, sp.E, ["Por partes con $u = \\ln x$, $dv = dx$."])
    b = 1 if f == x * sp.exp(x) else sp.pi / 2
    return _ej(f, 0, b, ["Por partes: $u = x$."])


def impropia(rng):
    opcion = rng.choice(["potencia", "exp"])
    if opcion == "potencia":
        p = entero(rng, 2, 4)
        return _ej(1 / x**p, 1, sp.oo, ["Es impropia: integra hasta $t$ y calcula el límite cuando $t \\to \\infty$."])
    a = entero(rng, 1, 5)
    return _ej(sp.exp(-a * x), 0, sp.oo, ["Integral impropia: $\\lim_{t\\to\\infty} e^{-at} = 0$."])


TEMA = Tema(
    id="integrales_definidas",
    nombre="Integrales definidas",
    orden=12,
    descripcion="Calcular integrales definidas e impropias sencillas.",
    generadores={
        "basico": [polinomio],
        "medio": [trig_exp, con_sustitucion],
        "parcial": [por_partes, impropia],
    },
    ejemplos=[("basico", 1), ("medio", 1), ("parcial", 1)],
)
