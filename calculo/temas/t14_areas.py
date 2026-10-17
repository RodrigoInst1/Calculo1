"""Tema 14: Aplicaciones de la integral — áreas."""

import sympy as sp

from . import Tema
from ._util import L, distintos, entero, nuevo, paso, x


def area_bajo_curva(rng):
    a, b = entero(rng, 1, 3), entero(rng, 1, 6)
    c = entero(rng, 1, 3)
    f = a * x**2 + b
    F = sp.integrate(f, x)
    area = sp.integrate(f, (x, 0, c))
    pasos = [
        paso("Planteo", f"La función es positiva en $[0, {c}]$ (es una parábola por encima del eje $x$), así que el área es la integral.",
             rf"A = \int_0^{{{c}}} \left({L(f)}\right)dx"),
        paso("Primitiva", "", rf"F(x) = {L(F)}"),
        paso("Evaluar con el TFC", "", rf"A = F({c}) - F(0) = {L(F.subs(x, c))} - {L(F.subs(x, 0))} = {L(area)}"),
    ]
    return nuevo(f"Calcula el área de la región bajo la curva $y = {L(f)}$, sobre el eje $x$, entre $x = 0$ y $x = {c}$.",
                 "numero", area, pasos, ["El área bajo una curva positiva es $\\int_a^b f(x)\\,dx$."],
                 respuesta_latex=f"{L(area)}\\ \\text{{u}}^2")


def entre_parabola_y_recta(rng):
    r1, r2 = sorted(distintos(rng, -3, 4, 2, ()))
    arriba = (r1 + r2) * x - r1 * r2  # recta que corta a y = x^2 en r1 y r2
    abajo = x**2
    puntos = sorted(sp.solve(sp.Eq(arriba, abajo), x))
    area = sp.integrate(arriba - abajo, (x, puntos[0], puntos[1]))
    medio = sp.Rational(r1 + r2, 2)
    pasos = [
        paso("Puntos de corte", "Igualamos las dos curvas para saber dónde empieza y termina la región.",
             rf"x^2 = {L(arriba)} \;\Rightarrow\; x = {L(puntos[0])},\; x = {L(puntos[1])}"),
        paso("¿Cuál está arriba?", f"Probamos un punto intermedio, $x = {L(medio)}$: la recta vale ${L(arriba.subs(x, medio))}$ y la "
             f"parábola ${L(abajo.subs(x, medio))}$, así que la recta está arriba."),
        paso("Área = ∫ (arriba − abajo)", "", rf"A = \int_{{{L(puntos[0])}}}^{{{L(puntos[1])}}} \left({L(arriba - abajo)}\right)dx"),
        paso("Calcular", "", rf"A = {L(area)}"),
    ]
    return nuevo(f"Calcula el área de la región encerrada entre $y = x^2$ y la recta $y = {L(arriba)}$.", "numero", area, pasos,
                 ["Primero encuentra dónde se cortan las curvas.", "Integra (función de arriba) − (función de abajo)."],
                 respuesta_latex=f"{L(area)}\\ \\text{{u}}^2")


def con_cambio_de_signo(rng):
    c = entero(rng, 1, 3)
    d = c + entero(rng, 1, 2)
    f = x**2 - c**2
    negativa = sp.integrate(f, (x, 0, c))
    positiva = sp.integrate(f, (x, c, d))
    area = -negativa + positiva
    pasos = [
        paso("¡Cuidado con el signo!", f"La función es negativa en $(0, {c})$ y positiva en $({c}, {d})$. "
             "La integral cuenta como negativas las partes bajo el eje; para el **área** hay que separar.",
             rf"f(x) = {L(f)} = 0 \;\Rightarrow\; x = {c}"),
        paso("Parte bajo el eje", "", rf"\int_0^{{{c}}} \left({L(f)}\right)dx = {L(negativa)}"),
        paso("Parte sobre el eje", "", rf"\int_{{{c}}}^{{{d}}} \left({L(f)}\right)dx = {L(positiva)}"),
        paso("Sumar valores absolutos", "", rf"A = |{L(negativa)}| + {L(positiva)} = {L(area)}"),
    ]
    return nuevo(f"Calcula el **área** entre la curva $y = {L(f)}$ y el eje $x$, para $0 \\le x \\le {d}$.", "numero", area, pasos,
                 ["Mira dónde la función corta al eje $x$.", "Separa la integral y suma los valores absolutos."],
                 respuesta_latex=f"{L(area)}\\ \\text{{u}}^2")


TEMA = Tema(
    id="areas",
    nombre="Aplicaciones de la integral: áreas",
    orden=14,
    descripcion="Área bajo una curva y entre curvas.",
    generadores={
        "basico": [area_bajo_curva],
        "medio": [entre_parabola_y_recta],
        "parcial": [con_cambio_de_signo, entre_parabola_y_recta],
    },
    ejemplos=[("basico", 1), ("medio", 1), ("parcial", 1)],
)
