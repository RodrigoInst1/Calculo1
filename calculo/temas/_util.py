"""Ayudas comunes para escribir generadores de ejercicios."""

from __future__ import annotations

import random

import sympy as sp

from ..ejercicios import Ejercicio
from ..interprete import a_latex, a_latex_agrupado
from ..pasos import Paso
from ..solucionador import resolver_datos

x, y, t = sp.symbols("x y t")
L = a_latex
LA = a_latex_agrupado  # con paréntesis si es una suma


def entero(rng: random.Random, a: int, b: int, excluir=(0,)) -> int:
    """Entero al azar en [a, b] evitando los valores de ``excluir``."""
    opciones = [n for n in range(a, b + 1) if n not in excluir]
    return rng.choice(opciones)


def distintos(rng: random.Random, a: int, b: int, cuantos: int, excluir=(0,)) -> list[int]:
    opciones = [n for n in range(a, b + 1) if n not in excluir]
    return rng.sample(opciones, cuantos)


def paso(regla: str, explicacion: str, latex: str | None = None, nivel: int = 0) -> Paso:
    return Paso(regla, explicacion, latex, nivel)


def nuevo(enunciado: str, tipo: str, respuesta, pasos, pistas, respuesta_latex=None,
          variables=("x",), formula_latex="") -> Ejercicio:
    """Crea un ejercicio (el registro completa id, tema y dificultad)."""
    if respuesta_latex is None:
        respuesta_latex = L(respuesta) if not isinstance(respuesta, (list, tuple, set)) else \
            ", ".join(L(v) for v in respuesta)
    return Ejercicio(
        id="", tema="", dificultad="", enunciado=enunciado, tipo_respuesta=tipo, respuesta=respuesta,
        respuesta_latex=respuesta_latex, pasos=list(pasos), pistas=list(pistas), variables=tuple(variables),
        formula_latex=formula_latex,
    )


def desde_solver(enunciado: str, tipo: str, datos: dict, pistas=(), formula_latex: str | None = None) -> Ejercicio:
    """Ejercicio de límite/derivada/integral resuelto con el solucionador paso a paso."""
    sol = resolver_datos(tipo, datos)
    ej = nuevo(enunciado, "solver", sol.resultado, sol.pasos, pistas, respuesta_latex=sol.resultado_latex,
               formula_latex=formula_latex if formula_latex is not None else sol.enunciado_latex)
    ej.solucion = sol
    return ej


def limite(expr, punto, direccion="+-"):
    return {"expr": expr, "variable": x, "punto": sp.sympify(punto), "direccion": direccion}


def polinomio_con_raices(raices, coef=1):
    return sp.expand(coef * sp.prod([x - r for r in raices]))
