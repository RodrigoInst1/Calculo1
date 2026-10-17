"""Pruebas del modo estudio: teoría, plan de 4 semanas y registro de progreso."""

import json

import pytest

from calculo.plan import PLAN, SEMANAS
from calculo.progreso import Progreso
from calculo.temas import TEMAS, generar
from tests.test_generador import TEMAS_BASE


@pytest.mark.parametrize("tema_id", list(TEMAS))
def test_cada_tema_tiene_teoria_y_errores_comunes(tema_id):
    teoria = TEMAS[tema_id].teoria
    assert "Errores comunes" in teoria
    assert len(teoria) > 400


@pytest.mark.parametrize("tema_id", list(TEMAS))
def test_ejemplos_resueltos_se_generan(tema_id):
    for dificultad, semilla in TEMAS[tema_id].ejemplos:
        ej = generar(tema_id, dificultad, semilla)
        assert ej.pasos


def test_plan_de_cuatro_semanas():
    assert len(PLAN) == 28
    assert set(SEMANAS) == {1, 2, 3, 4}
    assert [d.numero for d in PLAN] == list(range(1, 29))
    for dia in PLAN:
        assert 60 <= dia.minutos <= 120, (dia.numero, dia.minutos)  # 1 a 2 horas
        assert all(t in TEMAS for t in dia.temas)
    # todos los temas del curso aparecen en el plan
    assert TEMAS_BASE <= {t for d in PLAN for t in d.temas}
    # un día de repaso con simulacro al final de cada semana
    assert all(d.simulacro for d in PLAN if d.numero % 7 == 0)


def test_progreso_registra_y_detecta_puntos_debiles(tmp_path):
    p = Progreso(tmp_path / "p.json")
    for _ in range(4):
        p.registrar("limites", "medio", False)
    p.registrar("limites", "medio", True)
    for _ in range(5):
        p.registrar("repaso", "basico", True)
    resumen = p.resumen_por_tema()
    assert resumen["limites"]["aciertos"] == 1 and resumen["limites"]["fallos"] == 4
    assert [t for t, _ in p.puntos_debiles()] == ["limites"]
    recomendaciones = p.recomendaciones(list(TEMAS))
    assert recomendaciones[0][0] == "limites"
    # el siguiente sugerido es el primer tema sin practicar, en el orden del curso
    assert recomendaciones[1][0] == "continuidad"


def test_temas_debiles_basicos_van_primero(tmp_path):
    p = Progreso(tmp_path / "p.json")
    for tema in ("areas", "repaso"):
        for _ in range(4):
            p.registrar(tema, "medio", False)
    assert [t for t, _ in p.recomendaciones(list(TEMAS), 2)] == ["repaso", "areas"]


def test_progreso_persiste_y_exporta(tmp_path):
    ruta = tmp_path / "sub" / "p.json"
    p = Progreso(ruta)
    p.registrar("tfc", "parcial", True)
    p.marcar_dia(3, True)
    otra = Progreso(ruta)
    assert otra.resumen_por_tema()["tfc"]["aciertos"] == 1
    assert otra.dia_hecho(3)
    copia = Progreso(tmp_path / "copia.json")
    copia.importar(p.exportar())
    assert copia.resumen_por_tema()["tfc"]["total"] == 1
    with pytest.raises(ValueError):
        copia.importar(json.dumps(["no", "es", "progreso"]))


def test_progreso_tolera_archivo_danado(tmp_path):
    ruta = tmp_path / "p.json"
    ruta.write_text("{esto no es json", encoding="utf-8")
    assert Progreso(ruta).resumen_por_tema() == {}
