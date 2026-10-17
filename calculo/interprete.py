"""Intérprete de expresiones matemáticas escritas en texto.

Convierte lo que escribe el estudiante (por ejemplo ``x^2 sen x`` o ``e^(2x)``)
en una expresión de SymPy. Acepta notación habitual en clase:

- ``^`` para potencias (``x^2``) y multiplicación implícita (``2x``, ``x sin x``).
- Nombres en español: ``sen``, ``tg``, ``arcsen``, ``raiz``, ``ln``.
- ``e`` es el número de Euler, ``pi`` es π y ``oo`` / ``inf`` / ``infinito`` es ∞.
- ``|x|`` es el valor absoluto.

Si algo no se puede interpretar se lanza ``ErrorEntrada`` con un mensaje
claro en español (nunca un error técnico de Python).
"""

from __future__ import annotations

import re
from tokenize import TokenError

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


class ErrorEntrada(ValueError):
    """Error con un mensaje pensado para el estudiante."""


# Transformaciones del analizador de SymPy: las estándar, más
# multiplicación implícita ("2x" -> 2*x) y "^" como potencia.
_TRANSFORMACIONES = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

# Nombres permitidos y a qué objeto de SymPy corresponden.
FUNCIONES: dict[str, object] = {
    "sin": sp.sin, "sen": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan, "tg": sp.tan,
    "cot": sp.cot, "cotg": sp.cot, "ctg": sp.cot,
    "sec": sp.sec,
    "csc": sp.csc, "cosec": sp.csc,
    "asin": sp.asin, "arcsin": sp.asin, "arcsen": sp.asin,
    "acos": sp.acos, "arccos": sp.acos,
    "atan": sp.atan, "arctan": sp.atan, "arctg": sp.atan,
    "sinh": sp.sinh, "senh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "exp": sp.exp,
    "log": sp.log, "ln": sp.log,
    "sqrt": sp.sqrt, "raiz": sp.sqrt,
    "abs": sp.Abs, "Abs": sp.Abs,
}

CONSTANTES: dict[str, object] = {
    "e": sp.E,
    "E": sp.E,
    "pi": sp.pi,
    "oo": sp.oo,
    "inf": sp.oo,
    "infinito": sp.oo,
}

# Ordenados de mayor a menor longitud para que "sinh" se detecte antes que "sin".
_NOMBRES_FUNCIONES = sorted(FUNCIONES, key=len, reverse=True)
_NOMBRES_RESERVADOS = sorted(list(FUNCIONES) + list(CONSTANTES), key=len, reverse=True)

_CARACTERES_PERMITIDOS = re.compile(r"^[0-9a-zA-Z+\-*/^().,\s|<>=]*$")
LONGITUD_MAXIMA = 300


def _normalizar(texto: str) -> str:
    """Limpia el texto y traduce notaciones comunes a algo que SymPy entienda."""
    t = texto.strip()
    # Símbolos tipográficos frecuentes al copiar y pegar.
    reemplazos = {
        "−": "-", "–": "-", "·": "*", "×": "*", "÷": "/", "²": "^2", "³": "^3",
        "√": "sqrt", "π": "pi", "∞": "oo", "**": "^", "≥": ">=", "≤": "<=",
        "{": "(", "}": ")", "[": "(", "]": ")",
    }
    for viejo, nuevo in reemplazos.items():
        t = t.replace(viejo, nuevo)
    # La coma decimal (3,5) se convierte en punto, solo entre dígitos.
    t = re.sub(r"(?<=\d),(?=\d)", ".", t)
    # |x| -> Abs(x) (sin anidar).
    t = re.sub(r"\|([^|]+)\|", r"Abs(\1)", t)
    # sin^2(x) o sin^2 x  ->  (sin(x))^2  (notación usual de clase).
    patron_pot = r"\b(" + "|".join(_NOMBRES_FUNCIONES) + r")\s*\^\s*(\d+)\s*"
    t = re.sub(patron_pot + r"\(([^()]*)\)", r"(\1(\3))^\2", t)
    t = re.sub(patron_pot + r"([a-zA-Z0-9]+)", r"(\1(\3))^\2", t)
    # "sinx" -> "sin x": separa el nombre de función pegado a su argumento.
    t = _separar_funciones(t)
    nombres = "|".join(_NOMBRES_FUNCIONES)
    # "sin2x" -> "sin 2x"
    t = re.sub(r"(?<![a-zA-Z])(" + nombres + r")(?=\d)", r"\1 ", t)
    # "sin 2x" -> "sin(2x)", "ln x^2" -> "ln(x^2)": el argumento sin paréntesis
    # es el término inmediato (número y una letra, con potencia opcional).
    argumento = r"(\d*\.?\d*[a-zA-Z](?![a-zA-Z(])(?:\^\d+)?|\d+(?:\.\d+)?(?![\d.a-zA-Z(]))"
    t = re.sub(r"(?<![a-zA-Z])(" + nombres + r")\s+" + argumento, r"\1(\2)", t)
    return t


def _separar_funciones(t: str) -> str:
    """Inserta un espacio entre un nombre de función y su argumento pegado.

    Se recorre cada palabra para no romper nombres más largos
    (por ejemplo "sinh" no debe convertirse en "sin h").
    """

    def separar(palabra: str) -> str:
        if palabra in FUNCIONES or palabra in CONSTANTES:
            return palabra
        # Busca el primer nombre de función dentro de la palabra (el más largo
        # si hay varios en la misma posición): "xsinx" -> "x sin x".
        for i in range(len(palabra)):
            for nombre in _NOMBRES_FUNCIONES:
                if palabra.startswith(nombre, i):
                    antes, despues = palabra[:i], palabra[i + len(nombre):]
                    partes = [antes, nombre, separar(despues) if despues else ""]
                    return " ".join(p for p in partes if p)
        return palabra

    return re.sub(r"[a-zA-Z]+", lambda m: separar(m.group(0)), t)


def _validar_identificadores(t: str) -> None:
    """Rechaza nombres raros para evitar que se ejecute código inesperado."""
    for palabra in re.findall(r"[a-zA-Z_]+", t):
        if palabra in FUNCIONES or palabra in CONSTANTES:
            continue
        # Palabras de solo letras se interpretan como producto de variables
        # (por ejemplo "xy" = x*y). Bloqueamos nombres de Python peligrosos.
        if "_" in palabra or palabra.lower() in {"lambda", "import", "eval", "exec", "open"}:
            raise ErrorEntrada(f"No reconozco «{palabra}» como parte de una expresión matemática.")


def _revisar_parentesis(t: str) -> None:
    nivel = 0
    for c in t:
        if c == "(":
            nivel += 1
        elif c == ")":
            nivel -= 1
            if nivel < 0:
                raise ErrorEntrada("Hay un paréntesis «)» de más. Revisa que cada «(» tenga su pareja.")
    if nivel > 0:
        raise ErrorEntrada("Falta cerrar un paréntesis: hay más «(» que «)».")


def interpretar(texto: str, variables: tuple[str, ...] = ()) -> sp.Expr:
    """Convierte ``texto`` en una expresión de SymPy.

    ``variables`` es opcional: si se indica, la expresión solo puede usar esas
    letras como variables (útil para detectar errores de escritura).
    """
    if texto is None or not str(texto).strip():
        raise ErrorEntrada("La expresión está vacía. Escribe algo como «x^2 + 3x».")
    texto = str(texto)
    if len(texto) > LONGITUD_MAXIMA:
        raise ErrorEntrada(f"La expresión es demasiado larga (máximo {LONGITUD_MAXIMA} caracteres).")

    t = _normalizar(texto)
    if not _CARACTERES_PERMITIDOS.match(t):
        raro = sorted({c for c in t if not _CARACTERES_PERMITIDOS.match(c)})
        raise ErrorEntrada(
            "Hay caracteres que no entiendo: " + " ".join(f"«{c}»" for c in raro)
            + ". Usa + - * / ^ ( ) y letras o números."
        )
    _validar_identificadores(t)
    _revisar_parentesis(t)
    # Evita cálculos gigantes como 9^9^9 que congelarían la app.
    if re.search(r"(?<![.\d])\d{7,}", t) or re.search(r"\d+\s*\^\s*\(?\s*\d+\s*\^", t):
        raise ErrorEntrada("Los números son demasiado grandes para trabajar con ellos aquí.")

    diccionario = dict(FUNCIONES)
    diccionario.update(CONSTANTES)
    try:
        expr = parse_expr(t, local_dict=diccionario, transformations=_TRANSFORMACIONES)
    except (SyntaxError, TypeError, ValueError, AttributeError, TokenError) as error:
        raise ErrorEntrada(_mensaje_sintaxis(texto)) from error
    except Exception as error:  # cualquier otro fallo de SymPy se traduce
        raise ErrorEntrada(_mensaje_sintaxis(texto)) from error

    if not isinstance(expr, (sp.Basic,)):
        # Por ejemplo, "3" se convierte en entero de Python en algunos casos.
        try:
            expr = sp.sympify(expr)
        except sp.SympifyError as error:
            raise ErrorEntrada(_mensaje_sintaxis(texto)) from error
    if isinstance(expr, tuple) or isinstance(expr, sp.Tuple):
        raise ErrorEntrada("Escribiste varias expresiones separadas por comas; escribe solo una.")
    if isinstance(expr, sp.FunctionClass) or (isinstance(expr, type)):
        raise ErrorEntrada("Falta el argumento de la función. Escribe, por ejemplo, «sin(x)».")

    if variables:
        permitidas = {sp.Symbol(v) for v in variables}
        sobrantes = expr.free_symbols - permitidas
        if sobrantes:
            nombres = ", ".join(sorted(str(s) for s in sobrantes))
            raise ErrorEntrada(
                f"La expresión usa letras que no esperaba: {nombres}. "
                f"Solo puedes usar: {', '.join(variables)}."
            )
    return expr


def _mensaje_sintaxis(texto: str) -> str:
    consejos = []
    if re.search(r"[+\-*/^]\s*$", texto.strip()):
        consejos.append("la expresión termina en un operador")
    if re.search(r"[+\-*/^]\s*[*/^]", texto):
        consejos.append("hay dos operadores seguidos")
    if "=" in texto and not re.search(r"[<>]=", texto):
        consejos.append("hay un «=» (escribe solo la expresión, sin igualarla a nada)")
    detalle = (" Revisa: " + "; ".join(consejos) + ".") if consejos else ""
    return (
        f"No pude entender «{texto.strip()}».{detalle} "
        "Ejemplos válidos: «x^2 + 3x - 1», «sin(2x)/x», «e^(x^2)», «sqrt(x+1)», «ln(x)»."
    )


def a_latex(expr) -> str:
    """LaTeX de una expresión, usando ``\\ln`` y ``\\arctan`` como en clase."""
    return sp.latex(expr, ln_notation=True, inv_trig_style="full")


def a_latex_agrupado(expr) -> str:
    """Como ``a_latex`` pero con paréntesis si es una suma (para integrales y límites)."""
    texto = a_latex(expr)
    return rf"\left({texto}\right)" if isinstance(expr, sp.Add) else texto


def simbolo(nombre: str = "x") -> sp.Symbol:
    """Devuelve el símbolo de SymPy con ese nombre (igual al del intérprete)."""
    return sp.Symbol(nombre)
