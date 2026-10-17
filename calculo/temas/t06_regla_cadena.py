"""Tema 6: Derivadas — regla de la cadena."""

import sympy as sp

from . import Tema
from ._util import L, desde_solver, entero, x


def _ej(f, pistas):
    return desde_solver(f"Deriva $f(x) = {L(f)}$.", "derivada", {"expr": f, "variable": x, "orden": 1}, pistas)


def potencia_de_polinomio(rng):
    a, b, n = entero(rng, 1, 5), entero(rng, -6, 6), entero(rng, 3, 7)
    return _ej((a * x**2 + b) ** n, ["Es $u^n$ con $u = $ lo de adentro: $(u^n)' = n u^{n-1} u'$."])


def funcion_de_lineal(rng):
    a = entero(rng, 2, 7)
    g = rng.choice([sp.sin, sp.cos, sp.exp, sp.tan])
    return _ej(g(a * x), ["Deriva la función de afuera y multiplica por la derivada de lo de adentro."])


def trig_de_polinomio(rng):
    a, b = entero(rng, 1, 4), entero(rng, -5, 5)
    g = rng.choice([sp.sin, sp.cos])
    return _ej(g(a * x**2 + b), ["Regla de la cadena: no olvides multiplicar por la derivada del argumento."])


def exp_y_log(rng):
    a, b = entero(rng, 1, 4), entero(rng, -5, 5)
    opcion = rng.choice(["exp", "log", "raiz"])
    if opcion == "exp":
        f = sp.exp(a * x**2 + b * x)
    elif opcion == "log":
        f = sp.log(a * x**2 + abs(b) + 1)
    else:
        f = sp.sqrt(a * x**2 + abs(b) + 1)
    return _ej(f, ["$(e^u)' = e^u u'$, $(\\ln u)' = \\frac{u'}{u}$, $(\\sqrt{u})' = \\frac{u'}{2\\sqrt{u}}$."])


def cadena_doble(rng):
    a = entero(rng, 2, 5)
    f = rng.choice([sp.sin(x**2) ** 3, sp.exp(sp.sin(a * x)), sp.log(sp.cos(a * x)), sp.sqrt(1 + sp.tan(x) ** 2)])
    return _ej(f, ["Hay varias funciones una dentro de otra: aplica la cadena desde afuera hacia adentro."])


def cadena_con_producto(rng):
    a, n = entero(rng, 1, 4), entero(rng, 2, 3)
    f = rng.choice([x**n * sp.exp(-a * x), x * sp.sin(a * x**2), x**2 * sp.sqrt(x + a)])
    return _ej(f, ["Primero la regla del producto; dentro de ella, uno de los factores necesita la regla de la cadena."])


TEMA = Tema(
    id="regla_cadena",
    nombre="Derivadas: regla de la cadena",
    orden=6,
    descripcion="Derivar funciones compuestas.",
    generadores={
        "basico": [funcion_de_lineal, potencia_de_polinomio],
        "medio": [trig_de_polinomio, exp_y_log],
        "parcial": [cadena_doble, cadena_con_producto],
    },
    ejemplos=[("basico", 1), ("medio", 3), ("parcial", 1)],
)
