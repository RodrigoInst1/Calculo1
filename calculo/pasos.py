"""Estructuras comunes para guardar una solución paso a paso."""

from __future__ import annotations

from dataclasses import dataclass, field

import sympy as sp


@dataclass
class Paso:
    """Un paso del procedimiento.

    - ``regla``: nombre corto de la regla usada (por ejemplo "Regla del producto").
    - ``explicacion``: texto en español sencillo; puede incluir LaTeX entre ``$...$``.
    - ``latex``: fórmula principal del paso (se muestra centrada), opcional.
    - ``nivel``: sangría; los pasos internos de una regla tienen nivel mayor.
    """

    regla: str
    explicacion: str
    latex: str | None = None
    nivel: int = 0


@dataclass
class Solucion:
    """Resultado completo de un ejercicio resuelto."""

    tipo: str  # "derivada", "limite", "integral", "integral_definida", ...
    enunciado_latex: str
    resultado: object  # expresión de SymPy (o None si "no existe")
    resultado_latex: str
    pasos: list[Paso] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
    # Datos extra que usa el verificador (variable, punto, etc.).
    datos: dict = field(default_factory=dict)

    def texto_pasos(self) -> str:
        """Versión en texto plano (útil para pruebas y la consola)."""
        lineas = []
        for i, p in enumerate(self.pasos, 1):
            sangria = "  " * p.nivel
            lineas.append(f"{sangria}{i}. [{p.regla}] {p.explicacion}")
            if p.latex:
                lineas.append(f"{sangria}   {p.latex}")
        return "\n".join(lineas)

    def reglas_usadas(self) -> list[str]:
        """Lista de reglas (sin repetir, en orden de aparición)."""
        vistas: list[str] = []
        for p in self.pasos:
            if p.regla not in vistas:
                vistas.append(p.regla)
        return vistas


def son_equivalentes(a, b, variables=None, intentos: int = 8) -> bool:
    """¿Son ``a`` y ``b`` la misma expresión matemática?

    Primero intenta simplificar ``a - b`` a cero. Si SymPy no lo logra,
    compara numéricamente en varios puntos (con tolerancia relativa), lo que
    detecta equivalencias como identidades trigonométricas complicadas.
    """
    a = sp.sympify(a)
    b = sp.sympify(b)
    if a == b:
        return True
    try:
        diferencia = sp.simplify(a - b)
        if diferencia == 0:
            return True
    except Exception:  # SymPy puede fallar con expresiones raras
        diferencia = a - b
    simbolos = sorted((a.free_symbols | b.free_symbols), key=str) if variables is None else list(variables)
    if not simbolos:
        try:
            va, vb = complex(sp.N(a, 30)), complex(sp.N(b, 30))
        except (TypeError, ValueError):
            return False
        return _cerca(va, vb)
    return _iguales_numericamente(a, b, simbolos, intentos)


def _cerca(va: complex, vb: complex, tol: float = 1e-8) -> bool:
    return abs(va - vb) <= tol * max(1.0, abs(va), abs(vb))


def _iguales_numericamente(a, b, simbolos, intentos: int) -> bool:
    """Evalúa ``a`` y ``b`` en puntos fijos y compara."""
    puntos_base = [0.37, 1.21, 2.73, 0.81, 1.57, 3.3, 0.55, 2.1, 4.2, 0.13]
    comparados = 0
    for k in range(len(puntos_base)):
        valores = {s: puntos_base[(k + j) % len(puntos_base)] + 0.11 * j for j, s in enumerate(simbolos)}
        try:
            va = complex(sp.N(a.subs(valores), 20))
            vb = complex(sp.N(b.subs(valores), 20))
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if any(map(_no_finito, (va, vb))):
            continue
        if not _cerca(va, vb):
            return False
        comparados += 1
        if comparados >= intentos:
            break
    return comparados >= 3


def _no_finito(z: complex) -> bool:
    import math

    return math.isnan(z.real) or math.isnan(z.imag) or math.isinf(z.real) or math.isinf(z.imag)
