"""Tema 2: Límites."""

import sympy as sp

from . import Reintentar, Tema
from ._util import L, desde_solver, distintos, entero, limite, polinomio_con_raices, x


def _enunciado(expr, punto, direccion="+-"):
    from ..limites import latex_limite

    return f"Calcula $\\displaystyle {latex_limite(expr, x, sp.sympify(punto), direccion)}$."


def _ej(expr, punto, pistas, direccion="+-"):
    return desde_solver(_enunciado(expr, punto, direccion), "limite", limite(expr, punto, direccion), pistas)


# ------------------------------------------------------------------ básico
def sustitucion_polinomio(rng):
    a, b, c = entero(rng, -4, 4), entero(rng, -6, 6, ()), entero(rng, -9, 9, ())
    k = entero(rng, -3, 4, ())
    return _ej(a * x**2 + b * x + c, k, ["Un polinomio es continuo en todos los reales: sustituye directamente."])


def sustitucion_racional(rng):
    a, b = entero(rng, -5, 5), entero(rng, -5, 5)
    c = entero(rng, -6, 6)
    k = entero(rng, -3, 3, ())
    if k + c == 0:
        raise Reintentar
    return _ej((a * x + b) / (x + c), k, ["Mira primero si el denominador se anula en el punto. Si no, sustituye."])


# ------------------------------------------------------------------- medio
def cero_sobre_cero_factorizable(rng):
    r, s = distintos(rng, -5, 5, 2, ())
    num = polinomio_con_raices([r, s])
    return _ej(num / (x - r), r, ["Sustituye: si obtienes 0/0, factoriza el numerador."])


def racional_en_infinito(rng):
    a, d = entero(rng, -6, 6), entero(rng, 1, 5)
    b, c, e = entero(rng, -5, 5, ()), entero(rng, -5, 5, ()), entero(rng, -5, 5)
    # Dos de cada tres veces los grados son iguales; a veces el denominador es cúbico.
    num = a * x**2 + b * x + c
    den = d * x**2 + e * x + 1 if rng.random() < 0.67 else d * x**3 + e
    return _ej(num / den, sp.oo, ["Divide numerador y denominador entre la mayor potencia de $x$ del denominador."])


def con_raiz(rng):
    k = entero(rng, 1, 5)
    return _ej((sp.sqrt(x + k**2) - k) / x, 0, ["Hay una raíz: multiplica por el conjugado."])


# ----------------------------------------------------------------- parcial
def trig_notable(rng):
    a, b = distintos(rng, 1, 7, 2)
    return _ej(sp.sin(a * x) / (b * x), 0, ["Recuerda el límite notable $\\lim_{u\\to0}\\frac{\\sin u}{u} = 1$, o usa L'Hôpital."])


def uno_menos_coseno(rng):
    a = entero(rng, 1, 5)
    return _ej((1 - sp.cos(a * x)) / x**2, 0, ["Es 0/0. Puedes aplicar L'Hôpital (quizá dos veces)."])


def exponencial_lhopital(rng):
    a, b = distintos(rng, 1, 6, 2)
    return _ej((sp.exp(a * x) - 1) / sp.sin(b * x), 0, ["Sustituye: aparece 0/0. Prueba L'Hôpital."])


def uno_al_infinito(rng):
    a, b = entero(rng, 1, 4), entero(rng, 1, 3)
    return _ej((1 + sp.Rational(a, 1) / x) ** (b * x), sp.oo, ["Es de la forma $1^\\infty$: usa $f^g = e^{g\\ln f}$."])


def no_existe_laterales(rng):
    r = entero(rng, -4, 4)
    k = entero(rng, -5, 5)
    return _ej(k / (x - r), r, ["El denominador tiende a 0 y el numerador no: calcula los límites laterales."])


def infinito_menos_infinito(rng):
    a = entero(rng, 1, 8, (0,))
    return _ej(sp.sqrt(x**2 + a * x) - x, sp.oo, ["Es $\\infty - \\infty$: multiplica y divide por el conjugado."])


TEMA = Tema(
    id="limites",
    nombre="Límites",
    orden=2,
    descripcion="Sustitución directa, formas indeterminadas, factorizar, racionalizar, L'Hôpital, laterales.",
    generadores={
        "basico": [sustitucion_polinomio, sustitucion_racional],
        "medio": [cero_sobre_cero_factorizable, racional_en_infinito, con_raiz],
        "parcial": [trig_notable, uno_menos_coseno, exponencial_lhopital, uno_al_infinito, no_existe_laterales,
                    infinito_menos_infinito],
    },
    ejemplos=[("basico", 1), ("medio", 4), ("parcial", 3)],
)
