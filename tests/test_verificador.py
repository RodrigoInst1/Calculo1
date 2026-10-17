"""Pruebas del modo verificar: equivalencias y pistas."""

import pytest

from calculo.solucionador import resolver_texto
from calculo.verificador import verificar


@pytest.mark.parametrize(
    "problema, respuesta",
    [
        ("d/dx sin(x^2)", "2x cos(x^2)"),
        ("d/dx x^2 sin x", "y' = 2x sin x + x^2 cos x"),
        ("d/dx sin(x)^2", "sin(2x)"),  # forma distinta pero equivalente
        ("d/dx sin(x)^2", "2 sin x cos x"),
        ("d/dx (x^2+1)/(x-3)", "(x^2 - 6x - 1)/(x-3)^2"),
        ("d/dx ln(x^2)", "2/x"),
        ("integral x e^x dx", "x e^x - e^x + C"),
        ("integral x e^x dx", "e^x (x - 1)"),
        ("integral 2x dx", "x^2 + 7"),  # cualquier constante vale
        ("integral sin(x) cos(x) dx", "sin(x)^2/2 + C"),  # difiere en una constante de la de SymPy
        ("integral de 0 a 1 x^2 dx", "1/3"),
        ("integral de 0 a 1 x^2 dx", "0.333"),
        ("lim x->2 (x^2-4)/(x-2)", "4"),
        ("lim x->0 1/x", "no existe"),
        ("lim x->0+ 1/x", "infinito"),
        ("lim x->oo (1+1/x)^x", "e"),
        ("lim x->oo (1+1/x)^x", "2.718"),
    ],
)
def test_respuestas_correctas(problema, respuesta):
    v = verificar(resolver_texto(problema), respuesta)
    assert v.correcto, v.mensaje


@pytest.mark.parametrize(
    "problema, respuesta, pista",
    [
        ("d/dx sin(x^2)", "cos(x^2)", "regla de la cadena"),
        ("d/dx sin(x^2)", "-2x cos(x^2)", "signo"),
        ("d/dx x^2 sin x", "2x cos x", "producto NO es el producto"),
        ("d/dx (x^2+1)/(x-3)", "2x", "cociente NO es el cociente"),
        ("d/dx x^3", "x^4/4", "integraste"),
        ("d/dx x^3", "6x^2", "factor constante"),
        ("d/dx x^3", "x^3", "falta derivarla"),
        ("integral x e^x dx", "x e^x + e^x", "derivaste"),
        ("integral x cos(x^2) dx", "sin(x^2)", "factor constante"),
        ("integral x cos(x^2) dx", "cos(x^2)", "sustitución"),
        ("integral x e^x dx", "x^2 e^x", "partes"),
        ("integral de 0 a 1 x^2 dx", "-1/3", "al revés"),
        ("lim x->2 (x^2-4)/(x-2)", "0", "factorizar"),
        ("lim x->0 sin(x)/x", "no existe", "sí existe"),
        ("lim x->0 1/x", "oo", "laterales"),
        ("lim x->oo (1+1/x)^x", "1", "logaritmos"),
    ],
)
def test_respuestas_incorrectas_dan_pistas(problema, respuesta, pista):
    v = verificar(resolver_texto(problema), respuesta)
    assert not v.correcto
    assert v.pistas, "debe haber al menos una pista"
    assert any(pista.lower() in p.lower() for p in v.pistas), v.pistas


def test_las_pistas_no_revelan_la_respuesta():
    sol = resolver_texto("d/dx x^2 sin x")
    v = verificar(sol, "2x cos x")
    from calculo.interprete import a_latex

    assert all(a_latex(sol.resultado) not in p for p in v.pistas)


@pytest.mark.parametrize("respuesta", ["", "2x+", "hola =", "x + y"])
def test_respuestas_ilegibles_no_rompen(respuesta):
    v = verificar(resolver_texto("d/dx x^2"), respuesta)
    assert not v.correcto
    assert v.mensaje


def test_falta_constante_de_integracion_se_avisa():
    v = verificar(resolver_texto("integral 3x^2 dx"), "x^3")
    assert v.correcto
    assert "+ C" in v.mensaje
