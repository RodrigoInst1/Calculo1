"""Tema 4: Derivadas — reglas básicas."""

import sympy as sp

from . import Tema
from ._util import L, desde_solver, entero, nuevo, paso, x


def _ej(f, pistas):
    return desde_solver(f"Deriva $f(x) = {L(f)}$.", "derivada", {"expr": f, "variable": x, "orden": 1}, pistas)


def polinomio(rng):
    a, b, c, d = entero(rng, -6, 6), entero(rng, -8, 8), entero(rng, -9, 9), entero(rng, -9, 9, ())
    n = entero(rng, 3, 5)
    return _ej(a * x**n + b * x**2 + c * x + d, ["Deriva término a término con la regla de la potencia.",
                                                  "La derivada de una constante es 0."])


def potencias_raices(rng):
    a, b, c = entero(rng, 1, 6), entero(rng, -5, 5), entero(rng, -4, 4)
    f = a * sp.sqrt(x) + b / x + c * x ** sp.Rational(2, 3)
    return _ej(f, ["Escribe las raíces y los cocientes como potencias: $\\sqrt{x} = x^{1/2}$, $\\frac{1}{x} = x^{-1}$."])


def basicas_trig_exp(rng):
    a, b, c = entero(rng, -5, 5), entero(rng, -5, 5), entero(rng, -5, 5)
    f = a * sp.sin(x) + b * sp.exp(x) + c * sp.log(x)
    return _ej(f, ["Usa la tabla: $(\\sin x)' = \\cos x$, $(e^x)' = e^x$, $(\\ln x)' = \\frac{1}{x}$."])


def derivada_en_un_punto(rng):
    a, b, c = entero(rng, -4, 4), entero(rng, -6, 6), entero(rng, -9, 9)
    k = entero(rng, -3, 3)
    f = a * x**3 + b * x**2 + c * x
    df = sp.diff(f, x)
    valor = df.subs(x, k)
    pasos = [
        paso("Derivar", "Primero calculamos $f'(x)$ término a término (regla de la potencia).", rf"f'(x) = {L(df)}"),
        paso("Evaluar", f"Sustituimos $x = {k}$ en la derivada (¡no en la función!).", rf"f'({k}) = {L(valor)}"),
        paso("Interpretación", f"Es la pendiente de la recta tangente a la gráfica en $x = {k}$."),
    ]
    return nuevo(f"Si $f(x) = {L(f)}$, calcula $f'({k})$.", "numero", valor, pasos,
                 ["Deriva primero y después sustituye el valor.", "Cuidado con los signos al elevar números negativos."])


def recta_tangente(rng):
    a, b, c = entero(rng, -3, 3), entero(rng, -5, 5), entero(rng, -6, 6)
    k = entero(rng, -2, 2)
    f = a * x**2 + b * x + c
    m = sp.diff(f, x).subs(x, k)
    y0 = f.subs(x, k)
    recta = sp.expand(m * (x - k) + y0)
    pasos = [
        paso("Punto de tangencia", "Calculamos la altura de la gráfica en el punto.", rf"f({k}) = {L(y0)}"),
        paso("Pendiente", "La pendiente de la tangente es la derivada en el punto.",
             rf"f'(x) = {L(sp.diff(f, x))} \;\Rightarrow\; m = f'({k}) = {L(m)}"),
        paso("Ecuación punto-pendiente", "", rf"y - y_0 = m(x - x_0) \;\Rightarrow\; y - ({L(y0)}) = {L(m)}(x - ({k}))"),
        paso("Despejar y", "", rf"y = {L(recta)}"),
    ]
    return nuevo(f"Halla la ecuación de la recta tangente a $f(x) = {L(f)}$ en $x = {k}$.", "recta", recta, pasos,
                 ["Necesitas un punto $(x_0, f(x_0))$ y la pendiente $m = f'(x_0)$.",
                  "Usa la forma punto-pendiente: $y - y_0 = m(x - x_0)$."],
                 respuesta_latex="y = " + L(recta))


TEMA = Tema(
    id="derivadas_basicas",
    nombre="Derivadas: reglas básicas",
    orden=4,
    descripcion="Potencia, suma, múltiplo constante, tabla de derivadas, recta tangente.",
    generadores={
        "basico": [polinomio, potencias_raices],
        "medio": [basicas_trig_exp, derivada_en_un_punto],
        "parcial": [recta_tangente, potencias_raices],
    },
    ejemplos=[("basico", 1), ("medio", 2), ("parcial", 1)],
)
