"""Tema 13: Teorema Fundamental del Cálculo."""

import sympy as sp

from . import Tema
from ._util import L, LA, entero, nuevo, paso, t, x


def _integrando(rng):
    a, b = entero(rng, 1, 5), entero(rng, -4, 4)
    return rng.choice([t**2 + a, sp.sin(t) + a * t, sp.exp(t) * b if b else sp.exp(t), sp.sqrt(t**2 + a), sp.cos(a * t)])


def _derivada_de_integral(f, inferior, superior):
    """d/dx de la integral de f(t) entre límites que dependen de x (regla de Leibniz, calculada por SymPy)."""
    return sp.simplify(sp.diff(sp.Integral(f, (t, inferior, superior)), x))


def _F(f, inferior, superior):
    return rf"F(x) = \int_{{{L(inferior)}}}^{{{L(superior)}}} {LA(f)}\,dt"


def parte1_basico(rng):
    f = _integrando(rng)
    a = entero(rng, -2, 3, ())
    resultado = _derivada_de_integral(f, a, x)
    pasos = [
        paso("TFC, primera parte", "Si $f$ es continua, $F(x) = \\int_a^x f(t)\\,dt$ es derivable y $F'(x) = f(x)$: "
             "la derivada «deshace» la integral. **No hace falta integrar.**"),
        paso("Aplicar", "Reemplazamos $t$ por $x$ en el integrando.", rf"F'(x) = {L(resultado)}"),
    ]
    return nuevo(f"Si $\\displaystyle {_F(f, a, x)}$, halla $F'(x)$.", "expresion", resultado, pasos,
                 ["No integres: usa la primera parte del TFC.", "$F'(x)$ es el integrando evaluado en $x$."])


def parte1_cadena(rng):
    f = _integrando(rng)
    a = entero(rng, -2, 3, ())
    g = rng.choice([x**2, x**3, sp.sin(x), 3 * x, sp.exp(x)])
    resultado = _derivada_de_integral(f, a, g)
    pasos = [
        paso("TFC con regla de la cadena", "Si el límite de arriba es $g(x)$, entonces "
             "$\\frac{d}{dx}\\int_a^{g(x)} f(t)\\,dt = f(g(x))\\cdot g'(x)$."),
        paso("Identificar", "", rf"f(t) = {L(f)},\quad g(x) = {L(g)},\quad g'(x) = {L(sp.diff(g, x))}"),
        paso("Aplicar", "", rf"F'(x) = {L(f.subs(t, g))}\cdot {L(sp.diff(g, x))} = {L(resultado)}"),
    ]
    return nuevo(f"Si $\\displaystyle {_F(f, a, g)}$, halla $F'(x)$.", "expresion", resultado, pasos,
                 ["Usa el TFC y no olvides la regla de la cadena.", "Multiplica por la derivada del límite superior."])


def parte1_dos_limites(rng):
    f = _integrando(rng)
    g = rng.choice([x**2, x**3, 2 * x])
    h = rng.choice([x, sp.sin(x), sp.cos(x)])
    resultado = _derivada_de_integral(f, h, g)
    pasos = [
        paso("Partir la integral", "Separamos en dos integrales usando un número fijo $c$ en medio:",
             rf"\int_{{{L(h)}}}^{{{L(g)}}} f = \int_c^{{{L(g)}}} f - \int_c^{{{L(h)}}} f"),
        paso("Derivar cada parte (TFC + cadena)", "",
             rf"F'(x) = f({L(g)})\cdot {L(sp.diff(g, x))} - f({L(h)})\cdot {L(sp.diff(h, x))}"),
        paso("Resultado", "", rf"F'(x) = {L(resultado)}"),
    ]
    return nuevo(f"Si $\\displaystyle {_F(f, h, g)}$, halla $F'(x)$.", "expresion", resultado, pasos,
                 ["Fórmula: $f(g(x))g'(x) - f(h(x))h'(x)$.", "El límite de abajo entra con signo menos."])


def derivada_en_punto(rng):
    f = rng.choice([t**3 + 1, t**2 + 2 * t, sp.sqrt(t + 8)])
    k = entero(rng, 1, 2)
    valor = sp.simplify(_derivada_de_integral(f, 0, x**2).subs(x, k))
    pasos = [
        paso("Derivar con TFC + cadena", "", rf"F'(x) = f(x^2)\cdot 2x = \left({L(f.subs(t, x**2))}\right)\cdot 2x"),
        paso("Evaluar", "", rf"F'({k}) = {L(valor)}"),
    ]
    return nuevo(f"Si $\\displaystyle {_F(f, 0, x**2)}$, calcula $F'({k})$.", "numero", valor, pasos,
                 ["Primero halla $F'(x)$ con TFC y regla de la cadena.", "Luego sustituye el valor."])


TEMA = Tema(
    id="tfc",
    nombre="Teorema Fundamental del Cálculo",
    orden=13,
    descripcion="Derivar funciones definidas por integrales; relación entre derivada e integral.",
    generadores={
        "basico": [parte1_basico],
        "medio": [parte1_cadena, derivada_en_punto],
        "parcial": [parte1_dos_limites, parte1_cadena],
    },
    ejemplos=[("basico", 1), ("medio", 1), ("parcial", 1)],
)
