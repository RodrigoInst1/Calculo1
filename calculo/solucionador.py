"""Punto de entrada del solucionador: entiende el problema escrito en texto.

Formatos aceptados (no importan mayúsculas ni acentos):

Límites
    lim x->0 sin(x)/x
    lim(x->2) (x^2-4)/(x-2)
    lim x->0+ 1/x            (por la derecha; "0-" por la izquierda)
    límite cuando x tiende a infinito de (3x^2+1)/(x^2)

Derivadas
    d/dx x^2 sin(x)
    derivada de e^(3x)
    derivada segunda de x^4      (también "d2/dx2 x^4")
    derivada de t^3 respecto a t

Integrales
    integral x e^x dx
    ∫ x^2 dx
    integral de 0 a 1 x^2 dx
    integral x^2 dx de 0 a 1
    integral entre 0 y pi de sin(x) dx
"""

from __future__ import annotations

import concurrent.futures
import re
import unicodedata

import sympy as sp

from .derivadas import derivar_con_pasos
from .integrales import integral_con_pasos
from .interprete import ErrorEntrada, interpretar
from .limites import limite_con_pasos
from .pasos import Solucion

TIEMPO_MAXIMO = 20  # segundos

# Hilos de trabajo reutilizables para no bloquear la app con cálculos muy largos.
_EJECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def con_tiempo_limite(funcion, *args, segundos: float = TIEMPO_MAXIMO, **kwargs):
    """Ejecuta ``funcion`` y lanza ``ErrorEntrada`` si tarda demasiado."""
    futuro = _EJECUTOR.submit(funcion, *args, **kwargs)
    try:
        return futuro.result(timeout=segundos)
    except concurrent.futures.TimeoutError as error:
        raise ErrorEntrada(
            f"El cálculo tardó más de {int(segundos)} segundos y lo detuve. "
            "Prueba con una expresión más sencilla o revisa que esté bien escrita."
        ) from error


def _sin_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


# --------------------------------------------------------------------------
# Reconocimiento del tipo de problema
# --------------------------------------------------------------------------

_ORDINALES = {"primera": 1, "segunda": 2, "tercera": 3, "cuarta": 4, "quinta": 5}


def _punto_y_direccion(token: str):
    """Separa "0+" en (0, "+"), "2-" en (2, "-") y "-3" en (-3, "+-")."""
    t = token.strip().replace("^", "")
    direccion = "+-"
    if len(t) > 1 and t.endswith("+"):
        t, direccion = t[:-1], "+"
    elif len(t) > 1 and t.endswith("-"):
        t, direccion = t[:-1], "-"
    if t in ("+oo", "+inf", "+infinito"):
        t = "oo"
    if t in ("menos infinito", "-infinito"):
        t = "-oo"
    punto = interpretar(t)
    if punto.free_symbols:
        raise ErrorEntrada(f"El punto del límite debe ser un número, «oo» o «-oo», no «{token}».")
    return punto, direccion


def _limite(resto: str):
    t = resto.strip()
    # Formas de dirección en palabras.
    direccion_palabra = None
    if re.search(r"por la derecha", t):
        direccion_palabra = "+"
        t = re.sub(r"\s*por la derecha", "", t)
    elif re.search(r"por la izquierda", t):
        direccion_palabra = "-"
        t = re.sub(r"\s*por la izquierda", "", t)

    t = re.sub(r"^_?\s*[\{\(]?\s*(cuando\s+)?", "", t)
    m = re.match(
        r"([a-z])\s*(?:->|→|-->|=>|tiende\s+a(?:l)?|tiende\s+hacia)\s*"
        r"(menos\s+infinito|[+\-]?\s*(?:oo|infinito|inf|[0-9a-z./*()]+?))\s*(\^?[+\-](?![0-9a-z(]))?\s*[\}\)]?\s+(?:de\s+)?(.+)$",
        t,
    )
    if not m:
        raise ErrorEntrada(
            "No entendí el límite. Escríbelo así: «lim x->2 (x^2-4)/(x-2)» o «lim x->0+ 1/x»."
        )
    var, punto_txt, lado, cuerpo = m.groups()
    punto_txt = punto_txt.replace(" ", "")
    if punto_txt == "menosinfinito":
        punto_txt = "-oo"
    punto, direccion = _punto_y_direccion(punto_txt + (lado or "").replace("^", ""))
    if direccion_palabra:
        direccion = direccion_palabra
    x = sp.Symbol(var)
    expr = interpretar(cuerpo)
    return "limite", {"expr": expr, "variable": x, "punto": punto, "direccion": direccion}


def _derivada(resto: str, orden: int = 1):
    t = resto.strip()
    var = None
    m = re.search(r"(?:^|\s+)(?:respecto\s+(?:a|de)l?|con\s+respecto\s+a)\s+([a-z])\s*$", t)
    if m:
        var = m.group(1)
        t = t[: m.start()]
    t = re.sub(r"^de(\s+|$)", "", t)
    if not t.strip():
        raise ErrorEntrada("Falta la función que quieres derivar. Ejemplo: «derivada de x^2 sin x».")
    expr = interpretar(t)
    if var is None:
        libres = sorted(expr.free_symbols, key=str)
        var = str(libres[0]) if len(libres) == 1 else "x"
    return "derivada", {"expr": expr, "variable": sp.Symbol(var), "orden": orden}


def _integral(resto: str):
    t = resto.strip()
    a = b = None
    # Límites al estilo _a^b
    m = re.match(r"^_\s*\(?([^\s\^]+?)\)?\s*\^\s*\(?([^\s]+?)\)?\s+(.+)$", t)
    if m:
        a, b, t = m.groups()
    # "de A a B ..." / "desde A hasta B ..." / "entre A y B ..."
    patron_limites = r"(?:de|desde|entre)\s+(\S+)\s+(?:a|hasta|y)\s+(\S+)"
    if a is None:
        m = re.match(r"^" + patron_limites + r"\s+(?:de\s+)?(.+)$", t)
        if m:
            a, b, t = m.groups()
    if a is None:
        m = re.match(r"^(.+?)\s+" + patron_limites + r"$", t)
        if m:
            t, a, b = m.groups()
    t = re.sub(r"^de(\s+|$)", "", t.strip())
    # Diferencial final: dx, dt...
    var = None
    m = re.search(r"\s*\bd\s*([a-z])\s*$", t)
    if m:
        var = m.group(1)
        t = t[: m.start()]
    elif re.search(r"\)\s*d([a-z])$", t):
        m = re.search(r"d([a-z])$", t)
        var = m.group(1)
        t = t[: m.start()]
    if not t.strip():
        raise ErrorEntrada("Falta la función que quieres integrar.")
    expr = interpretar(t)
    if var is None:
        libres = sorted(expr.free_symbols, key=str)
        var = str(libres[0]) if len(libres) == 1 else "x"
    datos = {"expr": expr, "variable": sp.Symbol(var)}
    if a is not None:
        datos["a"] = interpretar(a)
        datos["b"] = interpretar(b)
        for limite in (datos["a"], datos["b"]):
            if limite.free_symbols:
                raise ErrorEntrada("Los límites de integración deben ser números (o oo).")
        return "integral_definida", datos
    return "integral", datos


def interpretar_problema(texto: str):
    """Devuelve ``(tipo, datos)`` a partir del texto del problema."""
    if not texto or not texto.strip():
        raise ErrorEntrada("Escribe un problema, por ejemplo «lim x->0 sin(x)/x», «d/dx x^2» o «integral x dx».")
    original = texto
    t = _sin_acentos(texto.strip()).lower()
    t = t.replace("∫", "integral ").replace("→", "->")
    t = re.sub(r"\s+", " ", t)

    m = re.match(r"^(?:limite|limit|lim)(?![a-z])\s*(.*)$", t)
    if m:
        return _limite(m.group(1))

    m = re.match(r"^d\s*(\d)?\s*/\s*d\s*([a-z])\s*(\d)?\s*(.*)$", t)
    if m:
        orden = int(m.group(1) or 1)
        var = m.group(2)
        cuerpo = m.group(4)
        tipo, datos = _derivada(cuerpo + f" respecto a {var}", orden)
        return tipo, datos

    m = re.match(r"^(?:la\s+)?(?:derivada|derivar|deriva|diff)(?![a-z])\s*(primera|segunda|tercera|cuarta|quinta)?\s*(.*)$", t)
    if m:
        orden = _ORDINALES.get(m.group(1) or "primera", 1)
        return _derivada(m.group(2), orden)

    m = re.match(r"^(?:la\s+)?(?:integrate|integral|integrar|integra|int)(?![a-z])\s*(.*)$", t)
    if m:
        return _integral(m.group(1))

    raise ErrorEntrada(
        f"No sé qué hacer con «{original.strip()}». Empieza con «lim», «derivada» (o «d/dx») o «integral». "
        "Ejemplos: «lim x->0 sin(x)/x», «d/dx x^2 sin x», «integral de 0 a 1 x^2 dx»."
    )


# --------------------------------------------------------------------------
# Resolución
# --------------------------------------------------------------------------

def resolver_datos(tipo: str, datos: dict) -> Solucion:
    """Resuelve a partir de datos ya interpretados (sin límite de tiempo)."""
    if tipo == "limite":
        return limite_con_pasos(datos["expr"], datos["variable"], datos["punto"], datos.get("direccion", "+-"))
    if tipo == "derivada":
        return derivar_con_pasos(datos["expr"], datos["variable"], datos.get("orden", 1))
    if tipo == "integral":
        return integral_con_pasos(datos["expr"], datos["variable"])
    if tipo == "integral_definida":
        return integral_con_pasos(datos["expr"], datos["variable"], datos["a"], datos["b"])
    raise ErrorEntrada(f"Tipo de problema desconocido: {tipo}")


def resolver(tipo: str, datos: dict, segundos: float = TIEMPO_MAXIMO) -> Solucion:
    """Resuelve con límite de tiempo y traduce cualquier fallo a ``ErrorEntrada``."""
    try:
        return con_tiempo_limite(resolver_datos, tipo, datos, segundos=segundos)
    except ErrorEntrada:
        raise
    except Exception as error:  # nunca mostramos un error técnico al estudiante
        raise ErrorEntrada(
            "No pude resolver este problema con los métodos disponibles. "
            "Revisa que esté bien escrito o prueba una versión más sencilla."
        ) from error


def resolver_texto(texto: str, segundos: float = TIEMPO_MAXIMO) -> Solucion:
    """Interpreta y resuelve un problema escrito en texto."""
    tipo, datos = interpretar_problema(texto)
    return resolver(tipo, datos, segundos)
