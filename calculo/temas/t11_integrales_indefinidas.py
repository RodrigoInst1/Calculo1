"""Tema 11: Integrales indefinidas."""

import sympy as sp

from . import Tema
from ._util import L, LA, desde_solver, entero, x


def _ej(f, pistas):
    return desde_solver(f"Calcula $\\displaystyle\\int {LA(f)}\\,dx$.", "integral", {"expr": f, "variable": x}, pistas)


def polinomio(rng):
    a, b, c = entero(rng, -6, 6), entero(rng, -8, 8), entero(rng, -9, 9, ())
    n = entero(rng, 2, 5)
    return _ej(a * x**n + b * x + c, ["Integra término a término: $\\int x^n dx = \\frac{x^{n+1}}{n+1}$."])


def potencias_y_basicas(rng):
    a, b, c = entero(rng, 1, 6), entero(rng, -5, 5), entero(rng, -5, 5)
    f = rng.choice([a * sp.sqrt(x) + b / x**2, a * sp.cos(x) + b * sp.exp(x), a / x + c * sp.sin(x)])
    return _ej(f, ["Escribe raíces y cocientes como potencias, y usa la tabla de integrales básicas."])


def sustitucion_lineal(rng):
    a, b = entero(rng, 2, 6), entero(rng, -5, 5)
    f = rng.choice([sp.exp(a * x + b), sp.cos(a * x), sp.sin(a * x), (a * x + b) ** entero(rng, 3, 6)])
    return _ej(f, ["Sustitución $u = $ lo de adentro (es lineal: $du = a\\,dx$)."])


def sustitucion_clasica(rng):
    a, n = entero(rng, 1, 6), entero(rng, 2, 5)
    f = rng.choice([x * (x**2 + a) ** n, x * sp.exp(x**2), x**2 * sp.cos(x**3), x / (x**2 + a),
                    sp.cos(x) * sp.sin(x) ** n, sp.log(x) / x])
    return _ej(f, ["Busca una función cuya derivada también aparezca multiplicando (salvo constantes)."])


def por_partes(rng):
    a = entero(rng, 1, 4)
    f = rng.choice([x * sp.exp(a * x), x * sp.sin(a * x), x * sp.cos(a * x), x * sp.log(x), x**2 * sp.exp(x)])
    return _ej(f, ["Integración por partes: $\\int u\\,dv = uv - \\int v\\,du$, con $u$ elegido por LIATE."])


def arcotangente(rng):
    a = entero(rng, 1, 5)
    return _ej(sp.Integer(1) / (x**2 + a**2), ["Usa $\\int \\frac{dx}{x^2 + a^2} = \\frac{1}{a}\\arctan\\frac{x}{a}$."])


TEMA = Tema(
    id="integrales_indefinidas",
    nombre="Integrales indefinidas",
    orden=11,
    descripcion="Primitivas: tabla básica, sustitución y por partes.",
    generadores={
        "basico": [polinomio, potencias_y_basicas],
        "medio": [sustitucion_lineal, sustitucion_clasica],
        "parcial": [por_partes, arcotangente, sustitucion_clasica],
    },
    ejemplos=[("basico", 1), ("medio", 2), ("parcial", 1)],
)
