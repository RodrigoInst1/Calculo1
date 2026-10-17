"""Pruebas del simulacro de parcial."""

import pytest

from calculo.simulacro import BLOQUES, crear_simulacro, elegir_temas
from calculo.temas import TEMAS
from tests.test_generador import respuesta_como_texto


@pytest.mark.parametrize("cuantos", [5, 6])
@pytest.mark.parametrize("semilla", range(5))
def test_simulacro_mezcla_temas_y_suma_cien(cuantos, semilla):
    s = crear_simulacro(cuantos=cuantos, semilla=semilla)
    assert len(s.ejercicios) == cuantos
    assert abs(sum(s.puntos) - 100) < 1e-9
    temas = [e.tema for e in s.ejercicios]
    assert len(set(temas)) == cuantos  # sin temas repetidos cuando hay suficientes
    bloques = {i for i, b in enumerate(BLOQUES) for t in temas if t in b}
    assert len(bloques) == 4  # cubre los cuatro bloques del curso
    assert {e.dificultad for e in s.ejercicios} <= {"medio", "parcial"}
    assert 30 <= s.minutos <= 90


def test_todas_correctas_dan_cien_y_todas_mal_cero():
    s = crear_simulacro(cuantos=6, semilla=7, minutos=60)
    buenas = [respuesta_como_texto(e) for e in s.ejercicios]
    c = s.corregir(buenas, ahora=s.inicio + 600)
    assert c.puntaje == 100 and c.total == 100
    assert c.aprobado()
    assert not c.fuera_de_tiempo
    malas = s.corregir(["999999"] * 6, ahora=s.inicio + 600)
    assert malas.puntaje == 0 and not malas.aprobado()
    vacias = s.corregir([], ahora=s.inicio + 600)
    assert vacias.puntaje == 0
    assert all(r.veredicto.mensaje == "Sin responder." for r in vacias.detalle)


def test_puntaje_parcial():
    s = crear_simulacro(cuantos=5, semilla=3)
    respuestas = [respuesta_como_texto(e) for e in s.ejercicios]
    respuestas[0] = "123456"
    c = s.corregir(respuestas, ahora=s.inicio + 60)
    assert c.puntaje == pytest.approx(100 - s.puntos[0], abs=0.11)


def test_tiempo_limite():
    s = crear_simulacro(cuantos=5, semilla=1, minutos=30)
    assert s.segundos_restantes(s.inicio + 60) == pytest.approx(29 * 60)
    assert not s.terminado(s.inicio + 29 * 60)
    assert s.terminado(s.inicio + 30 * 60)
    tarde = s.corregir([], ahora=s.inicio + 31 * 60)
    assert tarde.fuera_de_tiempo
    assert tarde.minutos_usados == 30


def test_temas_elegidos_por_el_estudiante():
    import random

    elegidos = elegir_temas(["limites", "tfc"], 5, random.Random(0))
    assert set(elegidos) == {"limites", "tfc"} and len(elegidos) == 5
    with pytest.raises(ValueError):
        elegir_temas(["no_existe"], 5, random.Random(0))
    with pytest.raises(ValueError):
        crear_simulacro(cuantos=8)


def test_los_bloques_cubren_todos_los_temas():
    assert {t for b in BLOQUES for t in b} == set(TEMAS)
