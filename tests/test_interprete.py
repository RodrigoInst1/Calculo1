"""Pruebas del intérprete de expresiones escritas en texto."""

import pytest
import sympy as sp

from calculo.interprete import ErrorEntrada, interpretar

x, y = sp.symbols("x y")


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("x^2 + 3x - 1", x**2 + 3 * x - 1),
        ("2x", 2 * x),
        ("x^2 sin x", x**2 * sp.sin(x)),
        ("sen(2x)", sp.sin(2 * x)),
        ("sinx", sp.sin(x)),
        ("xsinx", x * sp.sin(x)),
        ("sin 2x", sp.sin(2 * x)),
        ("sin^2(x)", sp.sin(x) ** 2),
        ("sin^2 x", sp.sin(x) ** 2),
        ("2sinxcosx", 2 * sp.sin(x) * sp.cos(x)),
        ("e^(2x)", sp.exp(2 * x)),
        ("x e^x", x * sp.exp(x)),
        ("ln|x|", sp.log(sp.Abs(x))),
        ("ln x^2", sp.log(x**2)),
        ("raiz(x+1)", sp.sqrt(x + 1)),
        ("arctan(x)", sp.atan(x)),
        ("arcsenx", sp.asin(x)),
        ("tg x", sp.tan(x)),
        ("3,5x", sp.Float(3.5) * x),
        ("x**2", x**2),
        ("pi", sp.pi),
        ("oo", sp.oo),
        ("infinito", sp.oo),
        ("(x+1)(x-1)", (x + 1) * (x - 1)),
        ("√x", sp.sqrt(x)),
        ("x²", x**2),
    ],
)
def test_interpreta_notacion_de_clase(texto, esperado):
    obtenido = interpretar(texto)
    assert obtenido == esperado or sp.simplify(obtenido - esperado) == 0


@pytest.mark.parametrize(
    "texto",
    ["", "   ", "2x+", "(x+1", "x+1)", "x = 2", "sin", "x,y", "__import__('os')", "9^9^9", "x $ 2", "lambda"],
)
def test_entradas_invalidas_dan_mensaje_util(texto):
    with pytest.raises(ErrorEntrada) as info:
        interpretar(texto)
    mensaje = str(info.value)
    assert len(mensaje) > 15  # siempre un mensaje explicativo, nunca vacío
    assert "Traceback" not in mensaje


def test_restriccion_de_variables():
    with pytest.raises(ErrorEntrada, match="letras que no esperaba"):
        interpretar("x + y", variables=("x",))
    assert interpretar("x + 1", variables=("x",)) == x + 1


def test_desigualdades_solo_si_se_permiten():
    with pytest.raises(ErrorEntrada, match="desigualdad"):
        interpretar("x >= 3")
    assert interpretar("x >= 3", relaciones=True) == (x >= 3)
