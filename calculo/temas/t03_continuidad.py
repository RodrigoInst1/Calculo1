"""Tema 3: Continuidad."""

import sympy as sp

from . import Reintentar, Tema
from ._util import L, distintos, entero, nuevo, paso, polinomio_con_raices, x


def _a_trozos(izquierda, derecha, c):
    return (rf"f(x) = \begin{{cases}} {L(izquierda)} & \text{{si }} x < {c} \\ "
            rf"{L(derecha)} & \text{{si }} x \geq {c} \end{{cases}}")


# ------------------------------------------------------------------ básico
def discontinuidades_racional(rng):
    r1, r2 = distintos(rng, -6, 6, 2)
    p = entero(rng, -5, 5)
    if p in (-r1, -r2):
        raise Reintentar
    den = polinomio_con_raices([r1, r2])
    f = (x + p) / den
    puntos = sorted([r1, r2])
    pasos = [
        paso("¿Dónde puede fallar?", "Una función racional es continua en todo su dominio; solo falla donde el denominador es 0."),
        paso("Denominador = 0", "", rf"{L(den)} = {L(sp.factor(den))} = 0 \;\Rightarrow\; x = {puntos[0]},\; x = {puntos[1]}"),
        paso("Conclusión", "En esos puntos $f$ no está definida, así que es discontinua."),
    ]
    return nuevo(
        f"¿En qué valores de $x$ es discontinua $f(x) = {L(f)}$?", "conjunto", puntos, pasos,
        ["Una fracción no está definida donde su denominador vale 0.", "Factoriza el denominador."],
    )


# ------------------------------------------------------------------- medio
def constante_a_trozos(rng):
    c = entero(rng, -3, 3)
    k = entero(rng, -6, 6)
    m = entero(rng, -6, 6, ())
    b = c * k + m - c**2
    kk = sp.Symbol("k")
    izquierda = kk * x + m
    derecha = x**2 + b
    lim_izq = izquierda.subs(x, c)
    lim_der = derecha.subs(x, c)
    pasos = [
        paso("Condición de continuidad", f"$f$ es continua en $x = {c}$ si los dos límites laterales son iguales al valor $f({c})$."),
        paso("Límite por la izquierda", "Para $x$ menor que el punto se usa la primera fórmula.",
             rf"\lim_{{x\to {c}^-}} f(x) = {L(lim_izq)}"),
        paso("Límite por la derecha", "Para $x$ mayor o igual se usa la segunda fórmula.",
             rf"\lim_{{x\to {c}^+}} f(x) = {L(lim_der)} = f({c})"),
        paso("Igualar y despejar", "", rf"{L(lim_izq)} = {L(lim_der)} \;\Rightarrow\; k = {k}"),
    ]
    return nuevo(
        f"Halla el valor de $k$ para que la función sea continua en todo $\\mathbb{{R}}$:\n\n$${_a_trozos(izquierda, derecha, c)}$$",
        "numero", sp.Integer(k), pasos,
        [f"Las dos fórmulas son polinomios (continuos); solo puede fallar en $x = {c}$.",
         "Iguala el límite por la izquierda con el límite por la derecha."],
    )


# ----------------------------------------------------------------- parcial
def discontinuidad_evitable(rng):
    a = entero(rng, -5, 5)
    f = (x**2 - a**2) / (x - a)
    k = 2 * a
    pasos = [
        paso("Condición", f"Para que sea continua en $x={a}$ se necesita $\\lim_{{x\\to {a}}} f(x) = f({a}) = k$."),
        paso("Calcular el límite", "Al sustituir sale 0/0: factorizamos la diferencia de cuadrados.",
             rf"\lim_{{x\to {a}}} \frac{{{L(x**2 - a**2)}}}{{{L(x - a)}}} = \lim_{{x\to {a}}} \frac{{(x-{a})(x+{a})}}{{x-{a}}} = \lim_{{x\to {a}}} (x + {a}) = {k}"
             if a else rf"\lim_{{x\to 0}} \frac{{x^2}}{{x}} = \lim_{{x\to 0}} x = 0"),
        paso("Conclusión", "La discontinuidad era **evitable**: se «arregla» definiendo $f$ en el punto con el valor del límite.",
             rf"k = {k}"),
    ]
    caso = (rf"f(x) = \begin{{cases}} \dfrac{{{L(x**2 - a**2)}}}{{{L(x - a)}}} & \text{{si }} x \neq {a} \\ "
            rf"k & \text{{si }} x = {a} \end{{cases}}")
    return nuevo(
        f"¿Qué valor debe tener $k$ para que $f$ sea continua en $x = {a}$?\n\n$${caso}$$", "numero", sp.Integer(k), pasos,
        ["Calcula el límite cuando $x$ tiende al punto.", "Sale 0/0: factoriza el numerador."],
    )


def seno_sobre_x(rng):
    m = entero(rng, 2, 7)
    k = sp.limit(sp.sin(m * x) / x, x, 0)  # el valor lo calcula SymPy
    pasos = [
        paso("Condición", "Se necesita $\\lim_{x\\to 0} f(x) = f(0) = k$."),
        paso("Límite notable", f"Escribimos $\\frac{{\\sin({m}x)}}{{x}} = {m}\\cdot\\frac{{\\sin({m}x)}}{{{m}x}}$ y usamos $\\lim_{{u\\to0}}\\frac{{\\sin u}}{{u}} = 1$.",
             rf"\lim_{{x\to 0}} \frac{{\sin({m}x)}}{{x}} = {m}\cdot 1 = {m}"),
        paso("Conclusión", "", rf"k = {L(k)}"),
    ]
    caso = rf"f(x) = \begin{{cases}} \dfrac{{\sin({m}x)}}{{x}} & \text{{si }} x \neq 0 \\ k & \text{{si }} x = 0 \end{{cases}}"
    return nuevo(
        f"Halla $k$ para que $f$ sea continua en $x = 0$:\n\n$${caso}$$", "numero", k, pasos,
        ["Calcula $\\lim_{x\\to0} f(x)$.", "Multiplica y divide por el número que acompaña a $x$ dentro del seno."],
    )


TEMA = Tema(
    id="continuidad",
    nombre="Continuidad",
    orden=3,
    descripcion="Puntos de discontinuidad, funciones a trozos y discontinuidades evitables.",
    generadores={
        "basico": [discontinuidades_racional],
        "medio": [constante_a_trozos],
        "parcial": [discontinuidad_evitable, seno_sobre_x],
    },
    ejemplos=[("basico", 1), ("medio", 2), ("parcial", 1)],
)
