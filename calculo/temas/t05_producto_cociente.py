"""Tema 5: Derivadas — regla del producto y del cociente."""

import sympy as sp

from . import Tema
from ._util import L, desde_solver, entero, x


def _ej(f, pistas):
    return desde_solver(f"Deriva $f(x) = {L(f)}$.", "derivada", {"expr": f, "variable": x, "orden": 1}, pistas)


def producto_simple(rng):
    a, b = entero(rng, 1, 5), entero(rng, -6, 6)
    g = rng.choice([sp.sin(x), sp.cos(x), sp.exp(x), sp.log(x)])
    return _ej((a * x**2 + b) * g, ["Es un producto: $(fg)' = f'g + fg'$."])


def cociente_lineal(rng):
    a, b, c, d = entero(rng, 1, 5), entero(rng, -6, 6), entero(rng, 1, 4), entero(rng, -6, 6)
    if a * d - b * c == 0:
        d += 1
    return _ej((a * x + b) / (c * x + d), ["Es un cociente: $\\left(\\frac{f}{g}\\right)' = \\frac{f'g - fg'}{g^2}$."])


def producto_trig(rng):
    n = entero(rng, 2, 4)
    return _ej(x**n * rng.choice([sp.sin(x), sp.cos(x), sp.exp(x)]), ["Regla del producto con $f = x^n$."])


def cociente_cuadratico(rng):
    a, b = entero(rng, -5, 5), entero(rng, -5, 5)
    return _ej((x**2 + a) / (x + b), ["Regla del cociente. Ojo con el orden de la resta en el numerador."])


def cociente_trig_exp(rng):
    num = rng.choice([sp.sin(x), sp.exp(x), sp.log(x)])
    den = rng.choice([x, x**2 + 1, sp.cos(x)])
    if num == sp.log(x) and den == sp.cos(x):
        den = x**2 + 1
    return _ej(num / den, ["Identifica $f$ (arriba) y $g$ (abajo) y aplica la regla del cociente."])


def producto_triple(rng):
    return _ej(x * sp.exp(x) * rng.choice([sp.sin(x), sp.cos(x)]),
               ["Agrupa: $x\\cdot(e^x \\sin x)$ y aplica la regla del producto dos veces."])


TEMA = Tema(
    id="producto_cociente",
    nombre="Derivadas: producto y cociente",
    orden=5,
    descripcion="Regla del producto y regla del cociente.",
    generadores={
        "basico": [producto_simple, cociente_lineal],
        "medio": [producto_trig, cociente_cuadratico],
        "parcial": [cociente_trig_exp, producto_triple],
    },
    ejemplos=[("basico", 1), ("medio", 1), ("parcial", 2)],
)
