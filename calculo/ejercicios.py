"""Ejercicios generados: enunciado, solución oculta y corrección.

Un ``Ejercicio`` guarda la respuesta correcta (calculada con SymPy), los pasos
de la solución y las pistas. La solución solo se muestra cuando el estudiante
la pide. ``Ejercicio.verificar(texto)`` corrige la respuesta del estudiante.

Tipos de respuesta admitidos (``tipo_respuesta``):

- ``"expresion"``: una función de la variable (se compara por equivalencia).
- ``"factorizacion"``: equivalente y, además, escrita como producto.
- ``"simplificacion"``: equivalente y sin factores que se puedan cancelar.
- ``"numero"``: un número exacto (o decimal bien redondeado).
- ``"conjunto"``: varios números separados por comas (o «ninguno»).
- ``"recta"``: la ecuación de una recta, por ejemplo ``y = 3x - 2``.
- ``"desigualdad"``: un conjunto de la recta real, como ``x >= 2`` o ``[2, oo)``.
- ``"solver"``: límite, derivada o integral; se corrige con el verificador
  general usando la ``Solucion`` del solucionador.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import sympy as sp

from .interprete import ErrorEntrada, a_latex, interpretar
from .pasos import Paso, Solucion, son_equivalentes
from .verificador import Veredicto, _aproximacion_valida, _quitar_lado_izquierdo, verificar

DIFICULTADES = ("basico", "medio", "parcial")
NOMBRE_DIFICULTAD = {"basico": "Básico", "medio": "Medio", "parcial": "Nivel parcial"}

AYUDA_FORMATO = {
    "expresion": "Escribe la expresión, por ejemplo «3x^2 - 2».",
    "factorizacion": "Escribe el polinomio factorizado, por ejemplo «(x - 2)(x + 3)».",
    "simplificacion": "Escribe la expresión ya simplificada.",
    "numero": "Escribe un número exacto (como «3/4», «2pi», «sqrt(2)») o un decimal con al menos 2 decimales.",
    "conjunto": "Escribe los valores separados por comas, por ejemplo «-2, 3». Si no hay ninguno escribe «ninguno».",
    "recta": "Escribe la recta como «y = mx + b», por ejemplo «y = 3x - 2».",
    "desigualdad": "Escribe el conjunto como «x >= 2», «x < -1 o x > 3» o en intervalo «[2, oo)». Todos los reales: «R».",
}


@dataclass
class Ejercicio:
    id: str
    tema: str
    dificultad: str
    enunciado: str  # Markdown con fórmulas entre $...$
    tipo_respuesta: str
    respuesta: object = None
    respuesta_latex: str = ""
    pasos: list[Paso] = field(default_factory=list)
    pistas: list[str] = field(default_factory=list)
    variables: tuple[str, ...] = ("x",)
    solucion: Solucion | None = None  # para límites/derivadas/integrales
    formula_latex: str = ""  # fórmula destacada del enunciado (opcional)

    @property
    def ayuda_formato(self) -> str:
        if self.tipo_respuesta == "solver" and self.solucion is not None:
            return {
                "limite": "Escribe el valor del límite: un número, «oo», «-oo» o «no existe».",
                "derivada": "Escribe la derivada, por ejemplo «2x cos(x^2)».",
                "integral": "Escribe una primitiva (puedes agregar «+ C»).",
                "integral_definida": "Escribe el valor exacto (como «1/3») o un decimal con 2 o más decimales.",
            }.get(self.solucion.tipo, "")
        return AYUDA_FORMATO.get(self.tipo_respuesta, "")

    def verificar(self, texto: str) -> Veredicto:
        """Corrige la respuesta escrita por el estudiante."""
        if texto is None or not str(texto).strip():
            return Veredicto(False, "Escribe tu respuesta para poder revisarla.")
        if self.tipo_respuesta == "solver" and self.solucion is not None:
            veredicto = verificar(self.solucion, texto)
            if not veredicto.correcto and self.pistas:
                veredicto.pistas = _mezclar(self.pistas, veredicto.pistas)
            return veredicto
        try:
            correcto, mensaje, interpretado = _COMPARADORES[self.tipo_respuesta](self, texto)
        except ErrorEntrada as error:
            return Veredicto(False, f"No pude leer tu respuesta: {error}")
        if correcto:
            return Veredicto(True, mensaje or "¡Correcto!", [], interpretado)
        return Veredicto(False, mensaje or "Todavía no es correcto.", list(self.pistas), interpretado)


def _mezclar(primero, segundo):
    salida = []
    for p in list(primero) + list(segundo):
        if p not in salida:
            salida.append(p)
    return salida


# --------------------------------------------------------------------------
# Comparadores
# --------------------------------------------------------------------------

def _simbolos(ej: Ejercicio):
    return [sp.Symbol(v) for v in ej.variables]


def _leer(ej: Ejercicio, texto: str):
    return interpretar(_quitar_lado_izquierdo(texto), variables=ej.variables)


def _cmp_expresion(ej, texto):
    u = _leer(ej, texto)
    ok = son_equivalentes(u, ej.respuesta, _simbolos(ej))
    if not ok and son_equivalentes(u, -ej.respuesta, _simbolos(ej)):
        return False, "Casi: tu resultado tiene el signo cambiado.", a_latex(u)
    return ok, "", a_latex(u)


def _cmp_factorizacion(ej, texto):
    u = _leer(ej, texto)
    if not son_equivalentes(u, ej.respuesta, _simbolos(ej)):
        return False, "Tu expresión no es igual al polinomio original: revisa los signos de cada factor.", a_latex(u)
    if isinstance(sp.expand(u), sp.Add) and isinstance(u, sp.Add):
        return False, "Es equivalente, pero no está factorizada: escríbela como producto de factores.", a_latex(u)
    return True, "¡Correcto! Está bien factorizado.", a_latex(u)


def _cmp_simplificacion(ej, texto):
    u = _leer(ej, texto)
    x = _simbolos(ej)[0]
    if not son_equivalentes(u, ej.respuesta, [x]):
        return False, "", a_latex(u)
    grado = lambda e: sp.degree(sp.fraction(sp.together(e))[1], x)  # noqa: E731
    if grado(u) > grado(ej.respuesta):
        return False, "Es equivalente, pero todavía se puede simplificar más (cancela el factor común).", a_latex(u)
    return True, "¡Correcto!", a_latex(u)


_UNIDADES = re.compile(r"(?:\s*(?:cm|mm|km|m|s|u|unidades)(?:\^?[23²³])?(?:\s*/\s*s)?)+\s*$", re.IGNORECASE)


def _quitar_unidades(texto: str) -> str:
    """Quita unidades al final («46 m/s», «512 m^2», «6 cm») para leer solo el número."""
    sin = _UNIDADES.sub("", texto.strip())
    return sin if sin.strip() else texto


def _cmp_numero(ej, texto):
    t = _quitar_unidades(_quitar_lado_izquierdo(texto))
    u = interpretar(t)
    if u.free_symbols:
        return False, "La respuesta debe ser un número, sin variables.", a_latex(u)
    c = sp.sympify(ej.respuesta)
    if u in (sp.oo, -sp.oo) or c in (sp.oo, -sp.oo):
        return u == c, "", a_latex(u)
    if son_equivalentes(u, c):
        return True, "¡Correcto!", a_latex(u)
    if _aproximacion_valida(t, u, c):
        return True, f"¡Correcto! (aproximación bien redondeada; el valor exacto es ${a_latex(c)}$)", a_latex(u)
    if son_equivalentes(u, -c):
        return False, "Casi: tu resultado tiene el signo cambiado.", a_latex(u)
    return False, "", a_latex(u)


def leer_conjunto(texto: str, variables=("x",)):
    t = texto.strip().lower()
    if t in ("ninguno", "ninguna", "no hay", "vacio", "vacío", "{}", "∅", "ningun", "ningún"):
        return set()
    t = t.strip("{}[]")
    partes = [p for p in re.split(r"[;,]|\by\b", t) if p.strip()]
    valores = []
    for p in partes:
        p = _quitar_lado_izquierdo(p)
        v = interpretar(p)
        if v.free_symbols:
            raise ErrorEntrada("Cada elemento debe ser un número.")
        valores.append(v)
    return valores


def _cmp_conjunto(ej, texto):
    valores = leer_conjunto(texto, ej.variables)
    correctos = list(ej.respuesta)
    interpretado = r"\varnothing" if not valores else r"\{" + ", ".join(a_latex(v) for v in valores) + r"\}"
    usados = []
    for v in valores:
        coincide = [c for c in correctos if son_equivalentes(v, c)]
        if not coincide:
            return False, f"El valor ${a_latex(v)}$ no es correcto.", interpretado
        usados.append(coincide[0])
    faltan = [c for c in correctos if c not in usados]
    if faltan:
        n = len(faltan)
        return False, f"Vas bien, pero te falta{'n' if n > 1 else ''} {n} valor{'es' if n > 1 else ''}.", interpretado
    return True, "¡Correcto!", interpretado


def _cmp_recta(ej, texto):
    t = texto.strip()
    if "=" not in t:
        raise ErrorEntrada("Escribe la ecuación completa, por ejemplo «y = 3x - 2».")
    izquierda, derecha = t.split("=", 1)
    x, y = sp.Symbol("x"), sp.Symbol("y")
    li = interpretar(izquierda, variables=("x", "y"))
    ld = interpretar(derecha, variables=("x", "y"))
    soluciones = sp.solve(sp.Eq(li, ld), y)
    if len(soluciones) != 1:
        return False, "No pude despejar y de tu ecuación; escríbela como «y = mx + b».", ""
    u = soluciones[0]
    ok = son_equivalentes(u, ej.respuesta, [x])
    mensaje = ""
    if not ok:
        pend_u = sp.diff(u, x)
        pend_c = sp.diff(ej.respuesta, x)
        if son_equivalentes(pend_u, pend_c, [x]):
            mensaje = "La pendiente es correcta, pero la recta no pasa por el punto: revisa la ordenada al origen."
        else:
            mensaje = "La pendiente no es correcta: recuerda que es la derivada evaluada en el punto."
    return ok, mensaje, "y = " + a_latex(u)


def leer_conjunto_real(texto: str) -> sp.Set:
    """Convierte «x >= 2», «x < -1 o x > 3», «[2, oo)» o «R» en un conjunto de SymPy."""
    t = texto.strip().lower().replace("≥", ">=").replace("≤", "<=")
    if t in ("r", "todos los reales", "reales", "(-oo, oo)", "ℝ"):
        return sp.S.Reals
    if t in ("ninguno", "vacio", "vacío", "∅", "{}"):
        return sp.S.EmptySet
    x = sp.Symbol("x")
    union_partes = re.split(r"\s+(?:o|or|u)\s+|∪|\|", t)
    conjunto = sp.S.EmptySet
    for parte in union_partes:
        conjunto = conjunto | _leer_interseccion(parte.strip(), x)
    return conjunto


def _leer_interseccion(t: str, x) -> sp.Set:
    partes = re.split(r"\s+(?:y|and)\s+|&|∩", t)
    resultado = sp.S.Reals
    for p in partes:
        resultado = resultado & _leer_simple(p.strip(), x)
    return resultado


def _leer_simple(t: str, x) -> sp.Set:
    m = re.fullmatch(r"([\[\(])\s*(.+?)\s*[,;]\s*(.+?)\s*([\]\)])", t)
    if m:
        abre, a, b, cierra = m.groups()
        a, b = interpretar(a), interpretar(b)
        return sp.Interval(a, b, left_open=(abre == "(" or a == -sp.oo), right_open=(cierra == ")" or b == sp.oo))
    # Desigualdad doble: -2 < x <= 3
    m = re.fullmatch(r"(.+?)\s*(<=|<)\s*x\s*(<=|<)\s*(.+)", t)
    if m:
        a, op1, op2, b = m.groups()
        return sp.Interval(interpretar(a), interpretar(b), left_open=(op1 == "<"), right_open=(op2 == "<"))
    relacion = interpretar(t)
    if not isinstance(relacion, sp.core.relational.Relational):
        raise ErrorEntrada("Escribe una desigualdad (como «x >= 2») o un intervalo (como «[2, oo)»).")
    if relacion.free_symbols - {x}:
        raise ErrorEntrada("Usa la letra x en la desigualdad.")
    return relacion.as_set()


def _cmp_desigualdad(ej, texto):
    u = leer_conjunto_real(texto)
    return u == ej.respuesta, "", a_latex(u)


_COMPARADORES = {
    "expresion": _cmp_expresion,
    "factorizacion": _cmp_factorizacion,
    "simplificacion": _cmp_simplificacion,
    "numero": _cmp_numero,
    "conjunto": _cmp_conjunto,
    "recta": _cmp_recta,
    "desigualdad": _cmp_desigualdad,
}
