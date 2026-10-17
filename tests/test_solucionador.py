"""Pruebas del solucionador paso a paso (límites, derivadas, integrales).

Cada resultado se compara con el valor que da SymPy de forma independiente.
"""

import pytest
import sympy as sp

from calculo.derivadas import derivar_con_pasos
from calculo.integrales import integral_con_pasos
from calculo.interprete import ErrorEntrada, interpretar
from calculo.limites import NoExiste, limite_con_pasos
from calculo.solucionador import interpretar_problema, resolver_texto

x, t = sp.symbols("x t")


# ---------------------------------------------------------------- derivadas
@pytest.mark.parametrize(
    "texto, regla",
    [
        ("x^3 - 4x + 2", "Regla de la suma"),
        ("x^2 sin x", "Regla del producto"),
        ("(x^2+1)/(x-3)", "Regla del cociente"),
        ("sin(x^2)", "Regla de la cadena"),
        ("(2x+1)^5", "Regla de la cadena (con potencia)"),
        ("e^(3x)", "Regla de la cadena"),
        ("ln(x^2+1)", "Regla de la cadena"),
        ("sqrt(2x+1)", "Regla de la cadena (con potencia)"),
        ("x^x", "Derivación logarítmica"),
        ("2^x", "Derivada de la exponencial $a^x$"),
        ("7", "Regla de la constante"),
        ("5x^4", "Regla del múltiplo constante"),
        ("tan(3x)^2", "Regla de la cadena (con potencia)"),
        ("x e^x sin x", "Regla del producto"),
        ("arctan(x^2)", "Regla de la cadena"),
        ("log(x, 10)", "Regla del múltiplo constante"),
    ],
)
def test_derivadas_correctas_y_reglas(texto, regla):
    f = interpretar(texto)
    sol = derivar_con_pasos(f, x)
    assert sp.simplify(sol.resultado - sp.diff(f, x)) == 0
    assert regla in sol.reglas_usadas()
    assert not sol.advertencias


def test_derivada_de_orden_superior():
    sol = derivar_con_pasos(interpretar("x^4 + sin x"), x, orden=2)
    assert sp.simplify(sol.resultado - (12 * x**2 - sp.sin(x))) == 0


def test_derivada_en_otra_variable():
    sol = resolver_texto("derivada de t^3 sin t respecto a t")
    assert sp.simplify(sol.resultado - sp.diff(t**3 * sp.sin(t), t)) == 0


# ------------------------------------------------------------------ límites
@pytest.mark.parametrize(
    "texto, punto, direccion, esperado, regla",
    [
        ("x^2 + 1", "3", "+-", 10, "Sustitución directa"),
        ("(x^2-4)/(x-2)", "2", "+-", 4, "Factorizar y simplificar"),
        ("(x^3-1)/(x-1)", "1", "+-", 3, "Factorizar y simplificar"),
        ("sin(x)/x", "0", "+-", 1, "Regla de L'Hôpital"),
        ("(1-cos x)/x^2", "0", "+-", sp.Rational(1, 2), "Regla de L'Hôpital"),
        ("(sqrt(x+4)-2)/x", "0", "+-", sp.Rational(1, 4), "Racionalizar"),
        ("(3x^2+1)/(2x^2-x)", "oo", "+-", sp.Rational(3, 2), "Dividir entre la mayor potencia"),
        ("(2x+1)/(x-3)", "-oo", "+-", 2, "Dividir entre la mayor potencia"),
        ("x ln x", "0", "+", 0, "Forma indeterminada 0·∞"),
        ("(1+1/x)^x", "oo", "+-", sp.E, "Forma indeterminada $1^{\\infty}$"),
        ("x^x", "0", "+", 1, "Forma indeterminada $0^{0}$"),
        ("sqrt(x^2+x)-x", "oo", "+-", sp.Rational(1, 2), "Forma indeterminada ∞ − ∞"),
        ("1/x", "0", "+", sp.oo, "Numerador ≠ 0, denominador → 0"),
        ("1/x^2", "0", "+-", sp.oo, "Numerador ≠ 0, denominador → 0: límites laterales"),
        ("x^3-100x^2", "oo", "+-", sp.oo, "Polinomio en el infinito"),
        ("(e^x-1)/x", "0", "+-", 1, "Regla de L'Hôpital"),
    ],
)
def test_limites_correctos_y_reglas(texto, punto, direccion, esperado, regla):
    f = interpretar(texto)
    a = interpretar(punto)
    sol = limite_con_pasos(f, x, a, direccion)
    assert sol.resultado == esperado or sp.simplify(sol.resultado - esperado) == 0
    # Comprobación independiente con SymPy
    directo = sp.limit(f, x, a, dir=direccion if a not in (sp.oo, -sp.oo) else "-" if a == sp.oo else "+")
    assert directo == esperado or sp.simplify(directo - esperado) == 0
    assert regla in sol.reglas_usadas()


@pytest.mark.parametrize("texto", ["1/x", "abs(x)/x", "sin(1/x)"])
def test_limites_que_no_existen(texto):
    sol = limite_con_pasos(interpretar(texto), x, 0, "+-")
    assert isinstance(sol.resultado, NoExiste)


def test_sustitucion_directa_no_se_usa_en_cero_a_la_cero():
    sol = limite_con_pasos(interpretar("x^x"), x, 0, "+")
    assert sol.reglas_usadas()[0] != "Sustitución directa"


# --------------------------------------------------------------- integrales
@pytest.mark.parametrize(
    "texto, regla",
    [
        ("3x^2 + 2", "Linealidad (integral de una suma)"),
        ("x e^x", "Integración por partes"),
        ("ln x", "Integración por partes"),
        ("x cos(x^2)", "Sustitución (cambio de variable)"),
        ("x sqrt(x^2+1)", "Sustitución (cambio de variable)"),
        ("cos(x) e^(sin x)", "Sustitución (cambio de variable)"),
        ("1/(x^2+1)", "Fórmula del arcotangente"),
        ("1/sqrt(1-x^2)", "Fórmula del arcoseno"),
        ("sin(x)^2", "Reescribir el integrando"),
        ("e^x sin x", "Integración por partes cíclica"),
        ("1/x", "Integral de 1/x"),
        ("sqrt(x)", "Regla de la potencia"),
        ("sec(x)^2", "Integral de la secante al cuadrado"),
        ("1/(x^2-1)", "Reescribir el integrando"),
        ("x^2 e^(3x)", "Integración por partes"),
    ],
)
def test_integrales_indefinidas(texto, regla):
    f = interpretar(texto)
    sol = integral_con_pasos(f, x)
    # La derivada de la primitiva debe ser el integrando
    assert sp.simplify(sp.diff(sol.resultado, x) - f) == 0
    assert regla in sol.reglas_usadas()
    assert "Comprobación" in sol.reglas_usadas()


@pytest.mark.parametrize(
    "texto, a, b",
    [
        ("x^2", "0", "1"),
        ("1/x", "1", "e"),
        ("sin x", "0", "pi"),
        ("x e^x", "0", "1"),
        ("x sqrt(x^2+1)", "0", "2"),
        ("e^(-x)", "0", "oo"),
        ("1/sqrt(x)", "0", "1"),
        ("ln x", "0", "1"),
        ("1/x^2", "-1", "1"),
        ("1/x", "1", "oo"),
        ("x^3", "1", "-1"),
    ],
)
def test_integrales_definidas(texto, a, b):
    f = interpretar(texto)
    A, B = interpretar(a), interpretar(b)
    sol = integral_con_pasos(f, x, A, B)
    esperado = sp.integrate(f, (x, A, B))
    assert sol.resultado == esperado or sp.simplify(sol.resultado - esperado) == 0


def test_integral_sin_primitiva_elemental_avisa():
    sol = integral_con_pasos(interpretar("e^(x^2)"), x)
    assert any("funciones especiales" in a for a in sol.advertencias)


# ------------------------------------------------ problemas escritos en texto
@pytest.mark.parametrize(
    "texto, tipo",
    [
        ("lim x->0 sin(x)/x", "limite"),
        ("lim(x->2) (x^2-4)/(x-2)", "limite"),
        ("lim_{x->1} (x^3-1)/(x-1)", "limite"),
        ("Límite cuando x tiende a infinito de 1/x", "limite"),
        ("lim x->0 1/x por la derecha", "limite"),
        ("d/dx x^2 sin(x)", "derivada"),
        ("derivada de e^(3x)", "derivada"),
        ("derivada segunda de x^4", "derivada"),
        ("d2/dx2 x^4", "derivada"),
        ("integral x e^x dx", "integral"),
        ("∫ x^2 dx", "integral"),
        ("integral de 0 a 1 x^2 dx", "integral_definida"),
        ("integral x^2 dx de 0 a 1", "integral_definida"),
        ("integral entre 0 y pi de sin(x) dx", "integral_definida"),
        ("int_0^1 x dx", "integral_definida"),
    ],
)
def test_interpretar_problema(texto, tipo):
    assert interpretar_problema(texto)[0] == tipo


def test_direccion_lateral_en_texto():
    _, datos = interpretar_problema("lim x->0- 1/x")
    assert datos["direccion"] == "-"
    assert resolver_texto("lim x->0- 1/x").resultado == -sp.oo
    assert resolver_texto("lim x->-2 x^2").resultado == 4


@pytest.mark.parametrize(
    "texto",
    ["hola", "lim x 0 x", "derivada de", "integral dx", "lim x->a x", "derivada de x^2+", "integral de 0 a y x dx"],
)
def test_problemas_mal_escritos_dan_error_util(texto):
    with pytest.raises(ErrorEntrada):
        resolver_texto(texto)


def test_todos_los_pasos_tienen_texto():
    sol = resolver_texto("integral x^2 e^(3x) dx")
    assert all(p.regla for p in sol.pasos)
    assert sol.texto_pasos().count("\n") >= len(sol.pasos) - 1
