"""Tema 9: Razón de cambio (velocidad y razones relacionadas)."""

import sympy as sp

from . import Tema
from ._util import L, entero, nuevo, paso, t

r = sp.Symbol("r")


def velocidad(rng):
    a, b, c = entero(rng, 1, 5), entero(rng, -10, 10), entero(rng, 0, 20, ())
    t0 = entero(rng, 1, 5)
    s = a * t**2 + b * t + c
    v = sp.diff(s, t)
    valor = v.subs(t, t0)
    pasos = [
        paso("Velocidad = derivada de la posición", "La razón de cambio instantánea de la posición es la velocidad: $v(t) = s'(t)$.",
             rf"v(t) = {L(v)}"),
        paso("Evaluar", "", rf"v({t0}) = {L(valor)}\ \text{{m/s}}"),
    ]
    return nuevo(f"La posición de una partícula es $s(t) = {L(s)}$ metros ($t$ en segundos). ¿Cuál es su velocidad en $t = {t0}$ s?",
                 "numero", valor, pasos, ["La velocidad es la derivada de la posición.", "Deriva y luego sustituye el tiempo."],
                 respuesta_latex=f"{L(valor)}\\ \\text{{m/s}}")


def circulo_area(rng):
    k = entero(rng, 1, 5)
    r0 = entero(rng, 2, 12)
    A = sp.pi * r**2
    dA = sp.diff(A, r) * k
    valor = dA.subs(r, r0)
    pasos = [
        paso("Relación entre variables", "El área y el radio están relacionados por la fórmula del círculo; ambos cambian con el tiempo.",
             r"A = \pi r^2"),
        paso("Derivar respecto del tiempo", "Derivamos ambos lados respecto de $t$ (regla de la cadena: $r$ depende de $t$).",
             r"\frac{dA}{dt} = 2\pi r \frac{dr}{dt}"),
        paso("Sustituir los datos", f"$r = {r0}$ cm y $\\frac{{dr}}{{dt}} = {k}$ cm/s.",
             rf"\frac{{dA}}{{dt}} = 2\pi ({r0})({k}) = {L(valor)}\ \text{{cm}}^2/\text{{s}}"),
    ]
    return nuevo(f"El radio de un círculo crece a razón de ${k}$ cm/s. ¿Con qué rapidez crece el área cuando el radio mide ${r0}$ cm?",
                 "numero", valor, pasos, ["Escribe la fórmula del área y deriva ambos lados respecto de $t$.",
                                          "$\\frac{dA}{dt} = 2\\pi r \\frac{dr}{dt}$."],
                 respuesta_latex=f"{L(valor)}\\ \\text{{cm}}^2/\\text{{s}}")


def globo_esfera(rng):
    dV = entero(rng, 10, 100)
    r0 = entero(rng, 2, 10)
    V = sp.Rational(4, 3) * sp.pi * r**3
    drdt = sp.Symbol("drdt")
    ecuacion = sp.Eq(dV, sp.diff(V, r) * drdt)
    valor = sp.solve(ecuacion.subs(r, r0), drdt)[0]
    pasos = [
        paso("Relación", "Volumen de una esfera:", r"V = \frac{4}{3}\pi r^3"),
        paso("Derivar respecto del tiempo", "", r"\frac{dV}{dt} = 4\pi r^2 \frac{dr}{dt}"),
        paso("Sustituir y despejar", f"$\\frac{{dV}}{{dt}} = {dV}$ cm³/s, $r = {r0}$ cm.",
             rf"{dV} = 4\pi ({r0})^2 \frac{{dr}}{{dt}} \;\Rightarrow\; \frac{{dr}}{{dt}} = {L(valor)}\ \text{{cm/s}}"),
    ]
    return nuevo(f"Se infla un globo esférico a razón de ${dV}$ cm³/s. ¿Con qué rapidez aumenta el radio cuando mide ${r0}$ cm?",
                 "numero", valor, pasos, ["$V = \\frac{4}{3}\\pi r^3$. Deriva respecto de $t$.", "Despeja $\\frac{dr}{dt}$."],
                 respuesta_latex=f"{L(valor)}\\ \\text{{cm/s}}")


def escalera(rng):
    longitud, base, altura = rng.choice([(5, 3, 4), (5, 4, 3), (10, 6, 8), (13, 5, 12), (25, 7, 24), (17, 8, 15)])
    v = entero(rng, 1, 4)
    X, Y, dx, dy = sp.symbols("x y dx dy")
    # x^2 + y^2 = L^2  ->  2x dx + 2y dy = 0
    dy_valor = sp.solve(sp.Eq(2 * X * dx + 2 * Y * dy, 0), dy)[0].subs({X: base, Y: altura, dx: v})
    rapidez = -dy_valor
    pasos = [
        paso("Dibujo y relación", "La escalera, la pared y el piso forman un triángulo rectángulo (Pitágoras), con $x$ la distancia "
             "de la base a la pared e $y$ la altura del extremo superior.", rf"x^2 + y^2 = {longitud}^2"),
        paso("Altura en ese instante", "", rf"y = \sqrt{{{longitud}^2 - {base}^2}} = {altura}"),
        paso("Derivar respecto del tiempo", "", r"2x\frac{dx}{dt} + 2y\frac{dy}{dt} = 0"),
        paso("Sustituir", f"$x = {base}$, $y = {altura}$, $\\frac{{dx}}{{dt}} = {v}$ m/s.",
             rf"\frac{{dy}}{{dt}} = -\frac{{x}}{{y}}\frac{{dx}}{{dt}} = {L(dy_valor)}\ \text{{m/s}}"),
        paso("Interpretar", "El signo negativo indica que la altura **disminuye**; la rapidez con que baja es el valor positivo.",
             rf"\text{{rapidez}} = {L(rapidez)}\ \text{{m/s}}"),
    ]
    return nuevo(f"Una escalera de ${longitud}$ m está apoyada en una pared. La base se aleja de la pared a ${v}$ m/s. "
                 f"¿Con qué **rapidez** (valor positivo) baja el extremo superior cuando la base está a ${base}$ m de la pared?",
                 "numero", rapidez, pasos, ["Usa Pitágoras: $x^2 + y^2 = L^2$, y deriva respecto de $t$.",
                                            "Calcula primero la altura $y$ en ese instante."],
                 respuesta_latex=f"{L(rapidez)}\\ \\text{{m/s}}")


TEMA = Tema(
    id="razon_cambio",
    nombre="Razón de cambio",
    orden=9,
    descripcion="Velocidad instantánea y razones relacionadas.",
    generadores={
        "basico": [velocidad],
        "medio": [circulo_area, globo_esfera],
        "parcial": [escalera, globo_esfera],
    },
    ejemplos=[("basico", 1), ("medio", 1), ("parcial", 2)],
)
