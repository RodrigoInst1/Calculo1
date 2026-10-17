"""Pruebas del generador de ejercicios.

Para muchas semillas de cada tema y dificultad se comprueba que:
- el ejercicio se genera sin errores,
- su propia respuesta correcta (escrita como la escribiría un estudiante) se acepta,
- una respuesta claramente incorrecta se rechaza con pistas.
"""

import pytest
import sympy as sp

from calculo.ejercicios import DIFICULTADES, leer_conjunto_real
from calculo.limites import NoExiste
from calculo.temas import TEMAS, generar, lista_temas

SEMILLAS = range(12)
CASOS = [(t, d, s) for t in TEMAS for d in DIFICULTADES for s in SEMILLAS]


def texto_de_conjunto(conjunto) -> str:
    """Escribe un conjunto de SymPy como lo haría un estudiante: «x >= 2», «[2, oo)», «... o ...»."""
    if conjunto == sp.S.Reals:
        return "R"
    partes = conjunto.args if isinstance(conjunto, sp.Union) else [conjunto]
    textos = []
    for p in partes:
        izq = "(" if p.left_open else "["
        der = ")" if p.right_open else "]"
        textos.append(f"{izq}{p.start}, {p.end}{der}")
    return " o ".join(textos)


def respuesta_como_texto(ej) -> str:
    r = ej.respuesta
    if ej.tipo_respuesta == "solver":
        if isinstance(r, NoExiste):
            return "no existe"
        return str(r)
    if ej.tipo_respuesta == "conjunto":
        return ", ".join(str(v) for v in r) if r else "ninguno"
    if ej.tipo_respuesta == "recta":
        return f"y = {r}"
    if ej.tipo_respuesta == "desigualdad":
        return texto_de_conjunto(r)
    if ej.tipo_respuesta == "factorizacion":
        return str(sp.factor(r))
    return str(r)


def test_hay_catorce_temas_en_orden():
    temas = lista_temas()
    assert [t.orden for t in temas] == sorted(t.orden for t in temas)
    assert temas[0].id == "repaso"
    assert len(temas) == 14
    for t in temas:
        assert set(t.generadores) == set(DIFICULTADES), t.id


@pytest.mark.parametrize("tema, dificultad, semilla", CASOS)
def test_ejercicio_acepta_su_respuesta(tema, dificultad, semilla):
    ej = generar(tema, dificultad, semilla)
    assert ej.enunciado and ej.pasos and ej.respuesta_latex
    assert ej.tema == tema and ej.dificultad == dificultad
    v = ej.verificar(respuesta_como_texto(ej))
    assert v.correcto, (ej.enunciado, respuesta_como_texto(ej), v.mensaje)


@pytest.mark.parametrize("tema, dificultad, semilla", [(t, d, 0) for t in TEMAS for d in DIFICULTADES])
def test_ejercicio_rechaza_respuesta_incorrecta(tema, dificultad, semilla):
    ej = generar(tema, dificultad, semilla)
    incorrectas = {
        "conjunto": "123456",
        "recta": "y = 1000x + 7",
        "desigualdad": "x > 1000",
        "factorizacion": "(x + 1000)(x - 1)",
    }
    texto = incorrectas.get(ej.tipo_respuesta, "1000")
    if ej.tipo_respuesta in ("expresion", "simplificacion") or (
        ej.tipo_respuesta == "solver" and ej.solucion.tipo in ("derivada", "integral")
    ):
        texto = "1000 x^7"
    v = ej.verificar(texto)
    assert not v.correcto
    assert v.pistas, "un ejercicio mal respondido debe ofrecer pistas"


def test_misma_semilla_mismo_ejercicio():
    a = generar("limites", "medio", 42)
    b = generar("limites", "medio", 42)
    assert a.enunciado == b.enunciado


def test_semillas_distintas_dan_variedad():
    enunciados = {generar("regla_cadena", "medio", s).enunciado for s in range(20)}
    assert len(enunciados) >= 8


def test_factorizacion_exige_producto():
    ej = generar("repaso", "basico", 0)
    while ej.tipo_respuesta != "factorizacion":
        ej = generar("repaso", "basico", hash(ej.enunciado) % 1000)
    assert not ej.verificar(str(sp.expand(ej.respuesta))).correcto
    assert ej.verificar(str(sp.factor(ej.respuesta))).correcto


def test_lectura_de_conjuntos_reales():
    assert leer_conjunto_real("x >= 2") == sp.Interval(2, sp.oo)
    assert leer_conjunto_real("[2, oo)") == sp.Interval(2, sp.oo)
    assert leer_conjunto_real("x < -1 o x > 3") == sp.Union(sp.Interval.open(-sp.oo, -1), sp.Interval.open(3, sp.oo))
    assert leer_conjunto_real("-2 < x <= 3") == sp.Interval.Lopen(-2, 3)
    assert leer_conjunto_real("R") == sp.S.Reals


def test_numero_con_unidades():
    ej = generar("razon_cambio", "basico", 1)
    assert ej.verificar(f"{ej.respuesta} m/s").correcto
