"""Registro de temas.

Cada tema vive en su propio módulo dentro de este paquete y define una variable
``TEMA`` (instancia de ``Tema``). Aquí se descubren automáticamente todos los
módulos, así que para agregar un tema nuevo basta con crear un archivo nuevo
(ver README, sección «Cómo agregar temas nuevos»).
"""

from __future__ import annotations

import importlib
import pkgutil
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..ejercicios import DIFICULTADES, Ejercicio

CARPETA_TEORIA = Path(__file__).parent / "teoria"


class Reintentar(Exception):
    """Un generador la lanza si los números al azar dieron un caso feo."""


@dataclass
class Tema:
    id: str
    nombre: str
    orden: int
    descripcion: str
    # dificultad -> lista de funciones generadoras f(rng) -> Ejercicio
    generadores: dict[str, list[Callable[[random.Random], Ejercicio]]]
    # Ejemplos resueltos que se muestran en el modo estudio: (dificultad, semilla)
    ejemplos: list[tuple[str, int]] = field(default_factory=lambda: [("basico", 1), ("medio", 2)])

    @property
    def teoria(self) -> str:
        archivo = CARPETA_TEORIA / f"{self.id}.md"
        if archivo.exists():
            return archivo.read_text(encoding="utf-8")
        return "_Todavía no hay resumen de teoría para este tema._"


def _descubrir() -> dict[str, Tema]:
    temas: dict[str, Tema] = {}
    for modulo in pkgutil.iter_modules([str(Path(__file__).parent)]):
        if modulo.name.startswith("_"):
            continue
        m = importlib.import_module(f"{__name__}.{modulo.name}")
        tema = getattr(m, "TEMA", None)
        if isinstance(tema, Tema):
            if tema.id in temas:
                raise ValueError(f"Hay dos temas con el mismo id: {tema.id}")
            temas[tema.id] = tema
    return dict(sorted(temas.items(), key=lambda par: par[1].orden))


TEMAS: dict[str, Tema] = _descubrir()


def lista_temas() -> list[Tema]:
    return list(TEMAS.values())


def generar(tema_id: str, dificultad: str, semilla: int | None = None, intentos: int = 30) -> Ejercicio:
    """Genera un ejercicio original del tema y dificultad pedidos.

    Con la misma ``semilla`` siempre sale el mismo ejercicio (útil para
    pruebas y para los ejemplos resueltos).
    """
    if tema_id not in TEMAS:
        raise KeyError(f"Tema desconocido: {tema_id}")
    if dificultad not in DIFICULTADES:
        raise KeyError(f"Dificultad desconocida: {dificultad}")
    tema = TEMAS[tema_id]
    if semilla is None:
        semilla = random.randrange(10**9)
    generadores = tema.generadores.get(dificultad) or []
    if not generadores:
        raise KeyError(f"El tema {tema.nombre} no tiene ejercicios de dificultad {dificultad}")
    for k in range(intentos):
        rng = random.Random(f"{tema_id}-{dificultad}-{semilla}-{k}")
        plantilla = rng.choice(generadores)
        try:
            ej = plantilla(rng)
        except Reintentar:
            continue
        ej.id = f"{tema_id}:{dificultad}:{semilla}"
        ej.tema = tema_id
        ej.dificultad = dificultad
        return ej
    raise RuntimeError(f"No se pudo generar un ejercicio para {tema_id}/{dificultad}")
