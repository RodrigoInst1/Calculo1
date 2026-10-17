"""Tema 7: Derivación implícita."""

import sympy as sp

from . import Tema
from ._util import L, entero, nuevo, paso, x, y

yp = sp.Symbol("y'")


def _derivar_implicita(izquierda, derecha):
    """Resuelve dy/dx para izquierda(x, y) = derecha(x, y) mostrando los pasos.

    Todo lo calcula SymPy: se reemplaza y por y(x), se deriva, se despeja y'.
    """
    Y = sp.Function("y")(x)
    di = sp.diff(izquierda.subs(y, Y), x).subs(sp.Derivative(Y, x), yp).subs(Y, y)
    dd = sp.diff(derecha.subs(y, Y), x).subs(sp.Derivative(Y, x), yp).subs(Y, y)
    despeje = sp.solve(sp.Eq(di, dd), yp)[0]
    resultado = sp.simplify(despeje)
    # Comprobación independiente con la función de SymPy para derivadas implícitas.
    if sp.simplify(resultado - sp.idiff(izquierda - derecha, y, x)) != 0:
        raise RuntimeError("La derivada implícita no coincide con sympy.idiff")
    pasos = [
        paso("Idea", "No despejamos $y$. Derivamos **ambos lados** respecto de $x$, recordando que $y$ depende de $x$: "
             "cada vez que derivamos algo con $y$, aparece $y'$ por la regla de la cadena (por ejemplo $(y^2)' = 2y\\,y'$)."),
        paso("Derivar ambos lados", "", rf"\frac{{d}}{{dx}}\left[{L(izquierda)}\right] = \frac{{d}}{{dx}}\left[{L(derecha)}\right]"),
        paso("Resultado de derivar", "", rf"{L(di)} = {L(dd)}"),
        paso("Despejar y'", "Pasamos los términos con $y'$ a un lado, sacamos factor común $y'$ y dividimos.",
             rf"y' = {L(resultado)}"),
    ]
    return resultado, pasos


def _ej(izquierda, derecha, pistas):
    resultado, pasos = _derivar_implicita(izquierda, derecha)
    return nuevo(
        f"Usa derivación implícita para hallar $\\frac{{dy}}{{dx}}$ si $\\;{L(izquierda)} = {L(derecha)}$.\n\n"
        "(Tu respuesta puede tener $x$ e $y$.)",
        "expresion", resultado, pasos, pistas, variables=("x", "y"), respuesta_latex="y' = " + L(resultado),
    )


def circunferencia(rng):
    r = entero(rng, 2, 9)
    return _ej(x**2 + y**2, sp.Integer(r**2), ["Deriva ambos lados: $(y^2)' = 2y\\,y'$.", "Despeja $y'$."])


def elipse(rng):
    a, b = entero(rng, 2, 5), entero(rng, 2, 5)
    return _ej(a * x**2 + b * y**2, sp.Integer(a * b * 4), ["Igual que con la circunferencia: deriva y despeja $y'$."])


def con_producto_xy(rng):
    c = entero(rng, 2, 12)
    return _ej(x**2 + x * y + y**2, sp.Integer(c), ["El término $xy$ es un producto: $(xy)' = y + x\\,y'$."])


def con_potencias(rng):
    a = entero(rng, 2, 6)
    return _ej(x**3 + y**3, a * x * y, ["$(y^3)' = 3y^2 y'$ y $(xy)' = y + xy'$.", "Agrupa los términos con $y'$."])


def con_trig(rng):
    a = entero(rng, 1, 4)
    return _ej(sp.sin(y) + a * x**2, x * y, ["$(\\sin y)' = \\cos y \\cdot y'$."])


TEMA = Tema(
    id="implicita",
    nombre="Derivación implícita",
    orden=7,
    descripcion="Hallar dy/dx sin despejar y.",
    generadores={
        "basico": [circunferencia],
        "medio": [elipse, con_producto_xy],
        "parcial": [con_potencias, con_trig],
    },
    ejemplos=[("basico", 1), ("medio", 2), ("parcial", 1)],
)
