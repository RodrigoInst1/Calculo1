"""Derivadas paso a paso.

Recorre la expresión desde afuera hacia adentro y, en cada nivel, decide qué
regla aplicar (suma, múltiplo constante, producto, cociente, potencia, cadena,
derivadas de funciones conocidas). Cada derivada parcial la calcula SymPy y el
resultado final se compara con ``sympy.diff`` para garantizar que es correcto.
"""

from __future__ import annotations

import sympy as sp

from .interprete import a_latex
from .pasos import Paso, Solucion, son_equivalentes

# Derivada de cada función elemental respecto de su argumento u, y cómo se
# llama la regla en clase.
_TABLA = {
    sp.sin: (lambda u: sp.cos(u), r"\frac{d}{du}\sin u = \cos u"),
    sp.cos: (lambda u: -sp.sin(u), r"\frac{d}{du}\cos u = -\sin u"),
    sp.tan: (lambda u: sp.sec(u) ** 2, r"\frac{d}{du}\tan u = \sec^2 u"),
    sp.cot: (lambda u: -sp.csc(u) ** 2, r"\frac{d}{du}\cot u = -\csc^2 u"),
    sp.sec: (lambda u: sp.sec(u) * sp.tan(u), r"\frac{d}{du}\sec u = \sec u \tan u"),
    sp.csc: (lambda u: -sp.csc(u) * sp.cot(u), r"\frac{d}{du}\csc u = -\csc u \cot u"),
    sp.exp: (lambda u: sp.exp(u), r"\frac{d}{du}e^{u} = e^{u}"),
    sp.log: (lambda u: 1 / u, r"\frac{d}{du}\ln u = \frac{1}{u}"),
    sp.asin: (lambda u: 1 / sp.sqrt(1 - u**2), r"\frac{d}{du}\arcsin u = \frac{1}{\sqrt{1-u^2}}"),
    sp.acos: (lambda u: -1 / sp.sqrt(1 - u**2), r"\frac{d}{du}\arccos u = -\frac{1}{\sqrt{1-u^2}}"),
    sp.atan: (lambda u: 1 / (1 + u**2), r"\frac{d}{du}\arctan u = \frac{1}{1+u^2}"),
    sp.sinh: (lambda u: sp.cosh(u), r"\frac{d}{du}\sinh u = \cosh u"),
    sp.cosh: (lambda u: sp.sinh(u), r"\frac{d}{du}\cosh u = \sinh u"),
    sp.tanh: (lambda u: 1 - sp.tanh(u) ** 2, r"\frac{d}{du}\tanh u = 1-\tanh^2 u"),
    sp.Abs: (lambda u: u / sp.Abs(u), r"\frac{d}{du}|u| = \frac{u}{|u|}\ (u \neq 0)"),
}

_NOMBRES = {
    sp.sin: "seno", sp.cos: "coseno", sp.tan: "tangente", sp.cot: "cotangente",
    sp.sec: "secante", sp.csc: "cosecante", sp.exp: "exponencial", sp.log: "logaritmo natural",
    sp.asin: "arcoseno", sp.acos: "arcocoseno", sp.atan: "arcotangente",
    sp.sinh: "seno hiperbólico", sp.cosh: "coseno hiperbólico", sp.tanh: "tangente hiperbólica",
    sp.Abs: "valor absoluto",
}


def _D(expr, x) -> str:
    """LaTeX de d/dx [expr]."""
    return rf"\frac{{d}}{{d{sp.latex(x)}}}\left[{a_latex(expr)}\right]"


class _Derivador:
    def __init__(self, x: sp.Symbol):
        self.x = x
        self.pasos: list[Paso] = []

    def paso(self, regla, explicacion, latex=None, nivel=0):
        self.pasos.append(Paso(regla, explicacion, latex, nivel))

    # ------------------------------------------------------------------
    def d(self, expr, nivel=0):
        """Deriva ``expr`` registrando los pasos y devuelve la derivada."""
        x = self.x
        L = a_latex

        if not expr.has(x):
            self.paso(
                "Regla de la constante",
                f"${L(expr)}$ no depende de ${sp.latex(x)}$, es una constante: su derivada es 0.",
                rf"{_D(expr, x)} = 0",
                nivel,
            )
            return sp.Integer(0)

        if expr == x:
            self.paso("Derivada de x", f"La derivada de ${sp.latex(x)}$ respecto de sí misma es 1.",
                      rf"{_D(x, x)} = 1", nivel)
            return sp.Integer(1)

        if isinstance(expr, sp.Add):
            return self._suma(expr, nivel)

        if isinstance(expr, sp.Mul):
            constante, resto = expr.as_independent(x, as_Add=False)
            if constante != 1:
                return self._multiplo_constante(constante, resto, nivel)
            numerador, denominador = sp.fraction(expr)
            if denominador.has(x) and numerador != 1:
                return self._cociente(numerador, denominador, nivel)
            if denominador.has(x) and numerador == 1:
                # 1/g(x): lo tratamos como g(x)^(-1) (potencia + cadena)
                return self.d(sp.Pow(denominador, -1, evaluate=False), nivel)
            return self._producto(expr, nivel)

        if isinstance(expr, sp.Pow):
            return self._potencia(expr, nivel)

        if isinstance(expr, sp.Function) and expr.func in _TABLA and len(expr.args) == 1:
            return self._funcion(expr, nivel)

        if isinstance(expr, sp.log) and len(expr.args) == 2:
            # log(u, b) = ln(u)/ln(b)
            u, b = expr.args
            self.paso("Cambio de base", "Escribimos el logaritmo en base natural.",
                      rf"\log_{{{L(b)}}}{L(u)} = \frac{{\ln {L(u)}}}{{\ln {L(b)}}}", nivel)
            return self.d(sp.log(u) / sp.log(b), nivel)

        # Caso no previsto: SymPy deriva directamente.
        derivada = sp.diff(expr, x)
        self.paso("Cálculo directo", "Para esta expresión no tengo una regla guiada; SymPy la deriva directamente.",
                  rf"{_D(expr, x)} = {L(derivada)}", nivel)
        return derivada

    # ------------------------------------------------------------------
    def _suma(self, expr, nivel):
        x, L = self.x, a_latex
        terminos = list(expr.as_ordered_terms())
        self.paso(
            "Regla de la suma",
            "La derivada de una suma (o resta) es la suma de las derivadas: derivamos término a término.",
            rf"{_D(expr, x)} = " + " + ".join(_D(t, x) for t in terminos),
            nivel,
        )
        derivadas = [self.d(t, nivel + 1) for t in terminos]
        resultado = sp.Add(*derivadas)
        self.paso("Juntamos los términos", "Sumamos las derivadas de cada término.",
                  rf"{_D(expr, x)} = {L(resultado)}", nivel)
        return resultado

    def _multiplo_constante(self, c, f, nivel):
        x, L = self.x, a_latex
        self.paso(
            "Regla del múltiplo constante",
            f"La constante ${L(c)}$ multiplica a la función, así que sale de la derivada: $(c\\cdot f)' = c\\cdot f'$.",
            rf"{_D(c * f, x)} = {L(c)}\cdot {_D(f, x)}",
            nivel,
        )
        df = self.d(f, nivel + 1)
        resultado = c * df
        if df.has(x) or df != 0:
            self.paso("Multiplicamos por la constante", "", rf"{L(c)}\cdot\left({L(df)}\right) = {L(resultado)}", nivel)
        return resultado

    def _producto(self, expr, nivel):
        x, L = self.x, a_latex
        factores = list(expr.args)
        f = factores[0]
        g = sp.Mul(*factores[1:])
        self.paso(
            "Regla del producto",
            f"Es un producto de dos funciones, $f = {L(f)}$ y $g = {L(g)}$. "
            "Usamos $(f\\cdot g)' = f'\\cdot g + f\\cdot g'$. Primero calculamos $f'$ y $g'$.",
            rf"{_D(expr, x)} = {_D(f, x)}\cdot {L(g)} + {L(f)}\cdot {_D(g, x)}",
            nivel,
        )
        df = self.d(f, nivel + 1)
        dg = self.d(g, nivel + 1)
        resultado = df * g + f * dg
        self.paso(
            "Aplicamos la regla del producto",
            f"Sustituimos $f' = {L(df)}$ y $g' = {L(dg)}$.",
            rf"\left({L(df)}\right)\left({L(g)}\right) + \left({L(f)}\right)\left({L(dg)}\right) = {L(resultado)}",
            nivel,
        )
        return resultado

    def _cociente(self, f, g, nivel):
        x, L = self.x, a_latex
        self.paso(
            "Regla del cociente",
            f"Es un cociente: numerador $f = {L(f)}$ y denominador $g = {L(g)}$. "
            "Usamos $\\left(\\frac{f}{g}\\right)' = \\frac{f'\\,g - f\\,g'}{g^2}$ "
            "(ojo con el orden: primero $f'g$, después se resta $fg'$).",
            rf"{_D(f / g, x)} = \frac{{{_D(f, x)}\cdot {L(g)} - {L(f)}\cdot {_D(g, x)}}}{{\left({L(g)}\right)^2}}",
            nivel,
        )
        df = self.d(f, nivel + 1)
        dg = self.d(g, nivel + 1)
        numerador = df * g - f * dg
        resultado = numerador / g**2
        self.paso(
            "Aplicamos la regla del cociente",
            f"Sustituimos $f' = {L(df)}$ y $g' = {L(dg)}$.",
            rf"\frac{{\left({L(df)}\right)\left({L(g)}\right) - \left({L(f)}\right)\left({L(dg)}\right)}}{{\left({L(g)}\right)^2}}"
            rf" = {L(sp.expand(numerador))}\Big/\left({L(g)}\right)^2",
            nivel,
        )
        return resultado

    def _potencia(self, expr, nivel):
        x, L = self.x, a_latex
        base, exponente = expr.args

        if base.has(x) and not exponente.has(x):
            n = exponente
            if base == x:
                aviso = ""
                if n.is_Rational and not n.is_Integer:
                    aviso = " Recuerda que las raíces son potencias fraccionarias, por ejemplo $\\sqrt{x} = x^{1/2}$."
                elif n.is_negative:
                    aviso = " Recuerda que $\\frac{1}{x^n} = x^{-n}$, así que también vale la regla de la potencia."
                resultado = n * x ** (n - 1)
                self.paso(
                    "Regla de la potencia",
                    f"Usamos $(x^n)' = n\\,x^{{n-1}}$ con $n = {L(n)}$: bajamos el exponente y le restamos 1.{aviso}",
                    rf"{_D(expr, x)} = {L(n)}\,{sp.latex(x)}^{{{L(n - 1)}}} = {L(resultado)}",
                    nivel,
                )
                return resultado
            # (u)^n con u función de x: regla de la cadena
            self.paso(
                "Regla de la cadena (con potencia)",
                f"Es una potencia de una función: $u^n$ con $u = {L(base)}$ y $n = {L(n)}$. "
                "Usamos $(u^n)' = n\\,u^{n-1}\\cdot u'$: derivamos la potencia y multiplicamos por la derivada de lo de adentro.",
                rf"{_D(expr, x)} = {L(n)}\left({L(base)}\right)^{{{L(n - 1)}}}\cdot {_D(base, x)}",
                nivel,
            )
            du = self.d(base, nivel + 1)
            resultado = n * base ** (n - 1) * du
            self.paso("Aplicamos la regla de la cadena", f"Multiplicamos por $u' = {L(du)}$.",
                      rf"{_D(expr, x)} = {L(resultado)}", nivel)
            return resultado

        if not base.has(x) and exponente.has(x):
            # a^u  (e^u lo maneja la tabla porque SymPy lo guarda como exp)
            a, u = base, exponente
            if u == x:
                resultado = a**x * sp.log(a)
                self.paso("Derivada de la exponencial $a^x$", "Usamos $(a^x)' = a^x \\ln a$.",
                          rf"{_D(expr, x)} = {L(resultado)}", nivel)
                return resultado
            self.paso(
                "Regla de la cadena (exponencial)",
                f"Es $a^u$ con $a = {L(a)}$ y $u = {L(u)}$. Usamos $(a^u)' = a^u \\ln a \\cdot u'$.",
                rf"{_D(expr, x)} = {L(expr)}\,\ln {L(a)}\cdot {_D(u, x)}",
                nivel,
            )
            du = self.d(u, nivel + 1)
            resultado = expr * sp.log(a) * du
            self.paso("Aplicamos la regla de la cadena", f"Multiplicamos por $u' = {L(du)}$.",
                      rf"{_D(expr, x)} = {L(resultado)}", nivel)
            return resultado

        # u^v con variable en base y exponente: derivación logarítmica
        u, v = base, exponente
        self.paso(
            "Derivación logarítmica",
            "La variable está en la base y en el exponente, así que no sirve la regla de la potencia "
            "ni la de la exponencial. Tomamos logaritmo: si $y = u^v$, entonces $\\ln y = v\\ln u$ "
            "y derivando: $\\frac{y'}{y} = (v \\ln u)'$, es decir $y' = u^v\\,(v\\ln u)'$.",
            rf"{_D(expr, x)} = {L(expr)}\cdot {_D(v * sp.log(u), x)}",
            nivel,
        )
        dlog = self.d(v * sp.log(u), nivel + 1)
        resultado = expr * dlog
        self.paso("Multiplicamos por $y = u^v$", "", rf"{_D(expr, x)} = {L(resultado)}", nivel)
        return resultado

    def _funcion(self, expr, nivel):
        x, L = self.x, a_latex
        f = expr.func
        u = expr.args[0]
        derivada_externa, formula = _TABLA[f]
        nombre = _NOMBRES.get(f, str(f))
        if u == x:
            resultado = derivada_externa(x)
            self.paso(
                f"Derivada del {nombre}",
                f"Usamos la fórmula conocida ${formula}$ con $u = {sp.latex(x)}$.",
                rf"{_D(expr, x)} = {L(resultado)}",
                nivel,
            )
            return resultado
        externa = derivada_externa(u)
        self.paso(
            "Regla de la cadena",
            f"Es una composición: función externa {nombre}, función interna $u = {L(u)}$. "
            f"Derivamos la externa dejando $u$ igual (${formula}$) y multiplicamos por $u'$.",
            rf"{_D(expr, x)} = {L(externa)}\cdot {_D(u, x)}",
            nivel,
        )
        du = self.d(u, nivel + 1)
        resultado = externa * du
        self.paso("Aplicamos la regla de la cadena", f"Multiplicamos por $u' = {L(du)}$.",
                  rf"{_D(expr, x)} = {L(resultado)}", nivel)
        return resultado


def simplificar_bonito(expr):
    """Simplifica solo si el resultado queda claramente más corto.

    Así se respeta la forma "natural" que sale de aplicar las reglas
    (por ejemplo ``x^2 cos x + 2x sin x``) en lugar de factorizar sin necesidad.
    """
    try:
        candidatos = [sp.simplify(expr), sp.factor(expr), sp.cancel(expr)]
    except Exception:
        return expr
    mejor = min(candidatos, key=lambda e: (sp.count_ops(e), len(str(e))))
    if sp.count_ops(mejor) <= sp.count_ops(expr) - 2:
        return mejor
    return expr


def derivar_con_pasos(expr, x: sp.Symbol | None = None, orden: int = 1) -> Solucion:
    """Calcula la derivada de ``expr`` respecto de ``x`` con todos los pasos.

    ``orden`` permite derivadas de orden superior (se deriva varias veces).
    """
    expr = sp.sympify(expr)
    if x is None:
        libres = sorted(expr.free_symbols, key=str)
        x = libres[0] if len(libres) == 1 else sp.Symbol("x")
    if orden < 1:
        raise ValueError("El orden de la derivada debe ser al menos 1.")

    pasos: list[Paso] = []
    actual = expr
    for k in range(1, orden + 1):
        if orden > 1:
            pasos.append(Paso(f"Derivada número {k}", f"Derivamos ${a_latex(actual)}$.", None, 0))
        derivador = _Derivador(x)
        obtenida = derivador.d(actual)
        pasos.extend(derivador.pasos)
        simplificada = simplificar_bonito(obtenida)
        if simplificada != obtenida:
            pasos.append(Paso("Simplificamos", "Ordenamos y simplificamos el resultado.",
                              rf"{a_latex(obtenida)} = {a_latex(simplificada)}", 0))
        actual = simplificada

    # Verificación obligatoria contra SymPy: nunca mostramos un resultado sin comprobar.
    correcta = sp.diff(expr, x, orden)
    advertencias = []
    if not son_equivalentes(actual, correcta, [x]):
        advertencias.append("Los pasos guiados no coincidieron con SymPy; se muestra el resultado de SymPy.")
        actual = simplificar_bonito(correcta)

    simbolo_orden = "'" * orden if orden <= 3 else f"^{{({orden})}}"
    if orden == 1:
        enunciado = rf"\frac{{d}}{{d{sp.latex(x)}}}\left[{a_latex(expr)}\right]"
    else:
        enunciado = rf"\frac{{d^{{{orden}}}}}{{d{sp.latex(x)}^{{{orden}}}}}\left[{a_latex(expr)}\right]"
    return Solucion(
        tipo="derivada",
        enunciado_latex=enunciado,
        resultado=actual,
        resultado_latex=rf"f{simbolo_orden}({sp.latex(x)}) = {a_latex(actual)}",
        pasos=pasos,
        advertencias=advertencias,
        datos={"expr": expr, "variable": x, "orden": orden},
    )
