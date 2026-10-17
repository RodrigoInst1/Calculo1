"""Tema 1: Funciones y álgebra de repaso."""

import sympy as sp

from . import Reintentar, Tema
from ._util import L, distintos, entero, nuevo, paso, polinomio_con_raices, x


# ------------------------------------------------------------------ básico
def evaluar_funcion(rng):
    a, b, c = entero(rng, -4, 4), entero(rng, -6, 6, ()), entero(rng, -9, 9, ())
    k = entero(rng, -3, 3, ())
    f = a * x**2 + b * x + c
    valor = f.subs(x, k)
    pasos = [
        paso("Sustituir", f"Evaluar $f({k})$ significa reemplazar cada $x$ por ${k}$ (con paréntesis si es negativo).",
             rf"f({k}) = {L(a)}\cdot({k})^2 + ({L(b)})\cdot({k}) + ({L(c)})"),
        paso("Potencias primero", f"$({k})^2 = {k**2}$ (un número negativo al cuadrado es positivo).",
             rf"f({k}) = {a * k**2} + ({b * k}) + ({c})"),
        paso("Sumar", "Sumamos los resultados.", rf"f({k}) = {L(valor)}"),
    ]
    return nuevo(
        f"Sea $f(x) = {L(f)}$. Calcula $f({k})$.", "numero", valor, pasos,
        ["Reemplaza cada $x$ por el número, usando paréntesis.", "Haz primero la potencia, luego las multiplicaciones y al final las sumas."],
    )


def factorizar_trinomio(rng):
    r1, r2 = distintos(rng, -6, 6, 2)
    p = polinomio_con_raices([r1, r2])
    b, c = p.coeff(x, 1), p.coeff(x, 0)
    factorizado = sp.factor(p)
    pasos = [
        paso("Buscar dos números", f"Para factorizar $x^2 + bx + c$ buscamos dos números que **multiplicados** den $c = {c}$ "
             f"y **sumados** den $b = {b}$."),
        paso("Encontrarlos", f"Los números son ${-r1}$ y ${-r2}$: $({-r1})\\cdot({-r2}) = {c}$ y $({-r1}) + ({-r2}) = {b}$."),
        paso("Escribir los factores", "Cada número va en un factor $(x + \\text{número})$.", rf"{L(p)} = {L(factorizado)}"),
        paso("Comprobar", "Si multiplicas los factores (propiedad distributiva) vuelves al polinomio original."),
    ]
    return nuevo(
        f"Factoriza el polinomio $\\;{L(p)}$.", "factorizacion", p, pasos,
        [f"Busca dos números que multiplicados den ${c}$ y sumados den ${b}$.",
         "La respuesta tiene la forma $(x + m)(x + n)$."],
        respuesta_latex=L(factorizado),
    )


def pendiente_recta(rng):
    x1, x2 = distintos(rng, -5, 5, 2, ())
    y1, y2 = entero(rng, -8, 8, ()), entero(rng, -8, 8, ())
    m = sp.Rational(y2 - y1, x2 - x1)
    pasos = [
        paso("Fórmula de la pendiente", "La pendiente mide cuánto sube $y$ por cada unidad que avanza $x$.",
             r"m = \frac{y_2 - y_1}{x_2 - x_1}"),
        paso("Sustituir", "", rf"m = \frac{{{y2} - ({y1})}}{{{x2} - ({x1})}} = \frac{{{y2 - y1}}}{{{x2 - x1}}} = {L(m)}"),
    ]
    return nuevo(
        f"Calcula la pendiente de la recta que pasa por los puntos $({x1}, {y1})$ y $({x2}, {y2})$.", "numero", m, pasos,
        ["Usa $m = \\frac{y_2 - y_1}{x_2 - x_1}$.", "Cuidado con los signos al restar números negativos."],
    )


# ------------------------------------------------------------------- medio
def resolver_cuadratica(rng):
    r1, r2 = distintos(rng, -7, 7, 2)
    a = rng.choice([1, 1, 2, -1])
    p = polinomio_con_raices([r1, r2], a)
    A, B, C = p.coeff(x, 2), p.coeff(x, 1), p.coeff(x, 0)
    disc = B**2 - 4 * A * C
    soluciones = sorted(sp.solve(p, x))
    pasos = [
        paso("Fórmula general", "Para $ax^2 + bx + c = 0$ usamos $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$.",
             rf"a = {A},\; b = {B},\; c = {C}"),
        paso("Discriminante", "Primero calculamos lo que va dentro de la raíz.",
             rf"b^2 - 4ac = ({B})^2 - 4({A})({C}) = {disc}"),
        paso("Las dos soluciones", f"Como el discriminante es positivo hay dos soluciones reales; $\\sqrt{{{disc}}} = {L(sp.sqrt(disc))}$.",
             rf"x = \frac{{{-B} \pm {L(sp.sqrt(disc))}}}{{{2 * A}}} \;\Rightarrow\; x_1 = {L(soluciones[0])},\; x_2 = {L(soluciones[1])}"),
    ]
    return nuevo(
        f"Resuelve la ecuación $\\;{L(p)} = 0$.", "conjunto", soluciones, pasos,
        ["Puedes factorizar o usar la fórmula general.", "Hay dos soluciones; escríbelas separadas por coma."],
    )


def dominio_racional(rng):
    r1, r2 = distintos(rng, -6, 6, 2)
    p = entero(rng, -5, 5)
    if p in (-r1, -r2):
        raise Reintentar
    den = polinomio_con_raices([r1, r2])
    f = (x + p) / den
    pasos = [
        paso("¿Dónde falla una fracción?", "No se puede dividir entre cero: quitamos del dominio los $x$ que anulan el denominador."),
        paso("Igualar el denominador a cero", "", rf"{L(den)} = 0 \;\Rightarrow\; {L(sp.factor(den))} = 0"),
        paso("Resolver", "Un producto es cero si algún factor es cero.", rf"x = {min(r1, r2)} \quad\text{{o}}\quad x = {max(r1, r2)}"),
    ]
    return nuevo(
        f"¿Qué valores de $x$ **no** pertenecen al dominio de $f(x) = {L(f)}$?", "conjunto", sorted([r1, r2]), pasos,
        ["Busca los valores que hacen cero el denominador.", "Factoriza el denominador."],
    )


def composicion(rng):
    a, b = entero(rng, -4, 4), entero(rng, -5, 5)
    c = entero(rng, -5, 5)
    f = a * x + b
    g = x**2 + c
    fog = sp.expand(f.subs(x, g))
    pasos = [
        paso("Qué significa $f(g(x))$", "Primero aplicamos $g$ y al resultado le aplicamos $f$: donde dice $x$ en $f$, ponemos $g(x)$ completo."),
        paso("Sustituir", "", rf"f(g(x)) = {L(a)}\left({L(g)}\right) + {L(b)}"),
        paso("Distribuir y simplificar", "", rf"f(g(x)) = {L(fog)}"),
    ]
    return nuevo(
        f"Si $f(x) = {L(f)}$ y $g(x) = {L(g)}$, calcula $f(g(x))$.", "expresion", fog, pasos,
        ["Reemplaza la $x$ de $f$ por la expresión completa de $g(x)$, entre paréntesis.",
         "¡Ojo! $f(g(x))$ no es lo mismo que $g(f(x))$."],
    )


# ----------------------------------------------------------------- parcial
def dominio_raiz(rng):
    a = rng.choice([1, 2, 3, -1, -2])
    b = entero(rng, -9, 9)
    if b % a != 0:
        raise Reintentar
    f = sp.sqrt(a * x + b)
    dominio = sp.solveset(a * x + b >= 0, x, sp.S.Reals)
    frontera = sp.Rational(-b, a)
    signo = r"\geq" if a > 0 else r"\leq"
    pasos = [
        paso("Condición de la raíz", "Una raíz cuadrada solo está definida (en los reales) si lo de adentro es mayor o igual a 0.",
             rf"{L(a * x + b)} \geq 0"),
        paso("Despejar", "Pasamos el número al otro lado y dividimos entre el coeficiente de $x$"
             + (" (como es negativo, **la desigualdad se invierte**)." if a < 0 else "."),
             rf"x {signo} {L(frontera)}"),
        paso("Dominio", "", rf"\text{{Dom}}(f) = {L(dominio)}"),
    ]
    return nuevo(
        f"Halla el dominio de $f(x) = {L(f)}$.", "desigualdad", dominio, pasos,
        ["Lo de adentro de la raíz debe ser $\\geq 0$.", "Si divides entre un número negativo, la desigualdad cambia de sentido."],
    )


def simplificar_racional(rng):
    r, s, u = distintos(rng, -6, 6, 3)
    num = polinomio_con_raices([r, s])
    den = polinomio_con_raices([r, u])
    simplificada = sp.cancel(num / den)
    pasos = [
        paso("Factorizar arriba y abajo", "", rf"\frac{{{L(num)}}}{{{L(den)}}} = \frac{{{L(sp.factor(num))}}}{{{L(sp.factor(den))}}}"),
        paso("Cancelar el factor común", f"El factor $({L(x - r)})$ aparece arriba y abajo; se cancela (para $x \\neq {r}$).",
             rf"= {L(simplificada)}"),
        paso("Error común", "Solo se cancelan **factores** (cosas que multiplican), nunca términos que se suman."),
    ]
    return nuevo(
        f"Simplifica la expresión $\\;\\dfrac{{{L(num)}}}{{{L(den)}}}$.", "simplificacion", simplificada, pasos,
        ["Factoriza el numerador y el denominador.", "Busca un factor que se repita arriba y abajo."],
    )


def funcion_inversa(rng):
    a, b = entero(rng, -5, 5, (0, 1)), entero(rng, -7, 7)
    f = a * x + b
    yy = sp.Symbol("y")
    inversa = sp.solve(sp.Eq(yy, a * x + b), x)[0].subs(yy, x)
    pasos = [
        paso("Escribir y = f(x)", "", rf"y = {L(f)}"),
        paso("Despejar x", "", rf"x = {L(sp.solve(sp.Eq(yy, a * x + b), x)[0])}"),
        paso("Intercambiar letras", "La inversa se escribe con $x$ como variable.", rf"f^{{-1}}(x) = {L(inversa)}"),
        paso("Comprobar", "Debe cumplirse $f(f^{-1}(x)) = x$.", rf"f(f^{{-1}}(x)) = {L(sp.simplify(f.subs(x, inversa)))}"),
    ]
    return nuevo(
        f"Halla la función inversa de $f(x) = {L(f)}$.", "expresion", inversa, pasos,
        ["Escribe $y = f(x)$ y despeja $x$.", "Al final cambia el nombre de las variables."],
    )


TEMA = Tema(
    id="repaso",
    nombre="Funciones y álgebra de repaso",
    orden=1,
    descripcion="Evaluar funciones, factorizar, ecuaciones, dominio, composición e inversa.",
    generadores={
        "basico": [evaluar_funcion, factorizar_trinomio, pendiente_recta],
        "medio": [resolver_cuadratica, dominio_racional, composicion],
        "parcial": [dominio_raiz, simplificar_racional, funcion_inversa],
    },
    ejemplos=[("basico", 3), ("medio", 1), ("parcial", 2)],
)
