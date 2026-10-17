"""Simulacro de parcial: 5–6 ejercicios mezclando temas, con tiempo límite.

La lógica está separada de la interfaz para poder probarla: se crea el examen,
se lleva el tiempo y se corrige al final con puntaje sobre 100.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

from .ejercicios import Ejercicio
from .temas import TEMAS, generar
from .verificador import Veredicto

# Bloques del curso: el simulacro intenta tomar temas de bloques distintos.
BLOQUES = [
    ["repaso", "limites", "continuidad"],
    ["derivadas_basicas", "producto_cociente", "regla_cadena", "implicita"],
    ["maximos_minimos", "razon_cambio", "optimizacion"],
    ["integrales_indefinidas", "integrales_definidas", "tfc", "areas"],
]
PESO = {"basico": 1, "medio": 1.5, "parcial": 2}  # peso relativo del puntaje
MINUTOS = {"basico": 5, "medio": 8, "parcial": 12}  # tiempo sugerido por ejercicio
NOTA_APROBACION = 51  # ajustable en la app según tu universidad


@dataclass
class ResultadoEjercicio:
    ejercicio: Ejercicio
    respuesta: str
    veredicto: Veredicto
    puntos_maximos: float
    puntos: float


@dataclass
class Correccion:
    puntaje: float
    total: float
    detalle: list[ResultadoEjercicio]
    fuera_de_tiempo: bool
    minutos_usados: float

    def aprobado(self, nota_minima: float = NOTA_APROBACION) -> bool:
        return self.puntaje >= nota_minima


@dataclass
class Simulacro:
    ejercicios: list[Ejercicio]
    puntos: list[float]
    minutos: int
    inicio: float = field(default_factory=time.time)

    @property
    def limite(self) -> float:
        return self.inicio + 60 * self.minutos

    def segundos_restantes(self, ahora: float | None = None) -> float:
        ahora = time.time() if ahora is None else ahora
        return max(0.0, self.limite - ahora)

    def terminado(self, ahora: float | None = None) -> bool:
        return self.segundos_restantes(ahora) <= 0

    def corregir(self, respuestas: list[str], ahora: float | None = None, margen: float = 5.0) -> Correccion:
        """Corrige todas las respuestas. Un ejercicio correcto vale sus puntos completos.

        ``margen``: segundos de tolerancia (por la demora de la página al entregar).
        """
        ahora = time.time() if ahora is None else ahora
        detalle = []
        for ej, maximo, texto in zip(self.ejercicios, self.puntos, list(respuestas) + [""] * len(self.ejercicios)):
            texto = (texto or "").strip()
            veredicto = ej.verificar(texto) if texto else Veredicto(False, "Sin responder.")
            detalle.append(ResultadoEjercicio(ej, texto, veredicto, maximo, maximo if veredicto.correcto else 0.0))
        return Correccion(
            puntaje=round(sum(r.puntos for r in detalle), 1),
            total=round(sum(self.puntos), 1),
            detalle=detalle,
            fuera_de_tiempo=ahora > self.limite + margen,
            minutos_usados=round((min(ahora, self.limite) - self.inicio) / 60, 1),
        )


def elegir_temas(temas: list[str] | None, cuantos: int, rng: random.Random) -> list[str]:
    """Elige ``cuantos`` temas distintos, repartidos entre los bloques del curso."""
    disponibles = [t for t in (temas or list(TEMAS)) if t in TEMAS]
    if not disponibles:
        raise ValueError("Elige al menos un tema para el simulacro.")
    bloques = [[t for t in b if t in disponibles] for b in BLOQUES]
    bloques = [b for b in bloques if b]
    otros = [t for t in disponibles if not any(t in b for b in BLOQUES)]
    if otros:
        bloques.append(otros)
    for b in bloques:
        rng.shuffle(b)
    elegidos: list[str] = []
    # Ronda por bloques: uno de cada bloque, luego otra vuelta, etc.
    while len(elegidos) < cuantos and any(bloques):
        for b in bloques:
            if b and len(elegidos) < cuantos:
                elegidos.append(b.pop())
    # Si hay pocos temas elegidos, se repiten (con ejercicios distintos).
    while len(elegidos) < cuantos:
        elegidos.append(rng.choice(disponibles))
    # Ordenamos según el curso, como en un parcial real.
    orden = {t: i for i, t in enumerate(TEMAS)}
    return sorted(elegidos, key=lambda t: orden.get(t, 99))


def crear_simulacro(temas: list[str] | None = None, cuantos: int = 6, minutos: int | None = None,
                    semilla: int | None = None) -> Simulacro:
    """Crea un simulacro con ``cuantos`` (5 o 6) ejercicios de nivel medio y parcial."""
    if not 5 <= cuantos <= 6:
        raise ValueError("El simulacro tiene entre 5 y 6 ejercicios.")
    semilla = random.randrange(10**9) if semilla is None else semilla
    rng = random.Random(semilla)
    elegidos = elegir_temas(temas, cuantos, rng)
    # Mitad nivel parcial y mitad medio, al azar.
    niveles = ["parcial"] * (cuantos // 2 + cuantos % 2) + ["medio"] * (cuantos // 2)
    rng.shuffle(niveles)
    ejercicios = [generar(t, d, rng.randrange(10**6)) for t, d in zip(elegidos, niveles)]
    pesos = [PESO[e.dificultad] for e in ejercicios]
    puntos = [round(100 * p / sum(pesos), 1) for p in pesos]
    puntos[-1] = round(100 - sum(puntos[:-1]), 1)  # que sume exactamente 100
    if minutos is None:
        minutos = sum(MINUTOS[e.dificultad] for e in ejercicios)
    return Simulacro(ejercicios, puntos, int(minutos))
