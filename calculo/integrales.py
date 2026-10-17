"""Integrales paso a paso (indefinidas y definidas).

Los pasos salen del "integrador manual" de SymPy
(``sympy.integrals.manualintegrate.integral_steps``), que imita cómo se
integra a mano: linealidad, potencia, sustitución, por partes, identidades...
Aquí cada regla se traduce a una explicación en español.

El resultado final se comprueba SIEMPRE derivándolo: si la derivada de la
primitiva no es el integrando, se descarta y se usa ``sympy.integrate``.
"""

from __future__ import annotations

import sympy as sp
from sympy.integrals import manualintegrate as mi

from .derivadas import simplificar_bonito
from .interprete import a_latex
from .pasos import Paso, Solucion, son_equivalentes

_ELEMENTALES = {
    "sin", "cos", "tan", "cot", "sec", "csc", "asin", "acos", "atan", "acot", "asec", "acsc",
    "sinh", "cosh", "tanh", "coth", "asinh", "acosh", "atanh", "exp", "log", "Abs", "sign",
}

# Letras para mostrar las variables auxiliares de sustitución (u, w, v...).
_LETRAS_SUSTITUCION = ["u", "w", "v", "s", "z"]

_FORMULAS_TRIG = {
    "SinRule": (r"\int \sin u\,du = -\cos u", "Integral del seno"),
    "CosRule": (r"\int \cos u\,du = \sin u", "Integral del coseno"),
    "Sec2Rule": (r"\int \sec^2 u\,du = \tan u", "Integral de la secante al cuadrado"),
    "Csc2Rule": (r"\int \csc^2 u\,du = -\cot u", "Integral de la cosecante al cuadrado"),
    "SecTanRule": (r"\int \sec u\tan u\,du = \sec u", "Integral de sec·tan"),
    "CscCotRule": (r"\int \csc u\cot u\,du = -\csc u", "Integral de csc·cot"),
    "SinhRule": (r"\int \sinh u\,du = \cosh u", "Integral del seno hiperbólico"),
    "CoshRule": (r"\int \cosh u\,du = \sinh u", "Integral del coseno hiperbólico"),
}


class _Traductor:
    """Convierte el árbol de reglas de SymPy en una lista de ``Paso``."""

    def __init__(self, x):
        self.x = x
        self.pasos: list[Paso] = []
        self.mapa_mostrar: dict = {}  # variable auxiliar de SymPy -> letra bonita
        self.incompleto = False

    def paso(self, regla, explicacion, latex=None, nivel=0):
        self.pasos.append(Paso(regla, explicacion, latex, nivel))

    def M(self, e) -> str:
        """LaTeX de ``e`` mostrando u, w... en lugar de las variables internas."""
        if e is None:
            return ""
        e = sp.sympify(e)
        return a_latex(e.subs(self.mapa_mostrar)) if self.mapa_mostrar else a_latex(e)

    def I(self, f, var) -> str:
        return rf"\int {self.M(f)}\,d{self.M(var)}"

    def primitiva(self, regla) -> sp.Expr:
        try:
            return regla.eval()
        except Exception:
            return sp.integrate(regla.integrand, regla.variable)

    # ------------------------------------------------------------------
    def integrar(self, f, v, nivel=0):
        """Integra ``f`` respecto de ``v`` registrando pasos; devuelve la primitiva.

        Antes de usar el árbol de SymPy probamos una sustitución "de clase"
        (u = lo de adentro), porque SymPy a veces elige caminos menos naturales.
        """
        sustitucion = _buscar_sustitucion(f, v)
        if sustitucion is None:
            regla = mi.integral_steps(f, v)
            self.traducir(regla, nivel)
            return regla.eval()
        g, en_u, u = sustitucion
        letra = _LETRAS_SUSTITUCION[min(len(self.mapa_mostrar), len(_LETRAS_SUSTITUCION) - 1)]
        self.mapa_mostrar[u] = sp.Symbol(letra)
        dg = sp.diff(g, v)
        self.paso(
            "Sustitución (cambio de variable)",
            f"Elegimos ${letra} = {self.M(g)}$ (lo de adentro), porque su derivada "
            f"$d{letra} = {self.M(dg)}\\,d{self.M(v)}$ aparece en el integrando (salvo constantes). "
            f"Así la integral queda solo en ${letra}$.",
            rf"{self.I(f, v)} = {self.I(en_u, u)}",
            nivel,
        )
        G = self.integrar(en_u, u, nivel + 1)
        F = G.subs(u, g)
        self.paso("Volvemos a la variable original", f"Reemplazamos ${letra} = {self.M(g)}$.",
                  rf"{self.M(G)} \;\Rightarrow\; {self.M(F)}", nivel)
        return F

    def traducir(self, regla, nivel=0):
        nombre = type(regla).__name__
        f, v = regla.integrand, regla.variable
        metodo = getattr(self, "_" + nombre, None)
        if metodo is not None:
            return metodo(regla, f, v, nivel)
        if nombre in _FORMULAS_TRIG:
            formula, titulo = _FORMULAS_TRIG[nombre]
            self.paso(titulo, f"Fórmula básica: ${formula}$.", rf"{self.I(f, v)} = {self.M(self.primitiva(regla))}", nivel)
            return
        if nombre == "DontKnowRule":
            self.incompleto = True
            self.paso("Sin método elemental guiado",
                      "No encontré un método de clase para esta parte; SymPy usa métodos avanzados.",
                      rf"{self.I(f, v)}", nivel)
            return
        # Cualquier otra fórmula de tabla
        self.paso("Fórmula de integración", "Usamos una fórmula conocida de la tabla de integrales.",
                  rf"{self.I(f, v)} = {self.M(self.primitiva(regla))}", nivel)

    # Reglas -------------------------------------------------------------
    def _ConstantRule(self, r, f, v, nivel):
        self.paso("Integral de una constante", "La integral de una constante $k$ es $k$ por la variable: $\\int k\\,dx = kx$.",
                  rf"{self.I(f, v)} = {self.M(self.primitiva(r))}", nivel)

    def _ConstantTimesRule(self, r, f, v, nivel):
        self.paso(
            "Múltiplo constante",
            f"La constante ${self.M(r.constant)}$ sale fuera de la integral: $\\int k f = k\\int f$.",
            rf"{self.I(f, v)} = {self.M(r.constant)}\cdot {self.I(r.other, v)}",
            nivel,
        )
        self.traducir(r.substep, nivel + 1)
        self.paso("Multiplicamos por la constante", "",
                  rf"{self.M(r.constant)}\cdot\left({self.M(self.primitiva(r.substep))}\right) = {self.M(self.primitiva(r))}", nivel)

    def _AddRule(self, r, f, v, nivel):
        terminos = [s.integrand for s in r.substeps]
        self.paso(
            "Linealidad (integral de una suma)",
            "La integral de una suma es la suma de las integrales: integramos término a término.",
            rf"{self.I(f, v)} = " + " + ".join(self.I(t, v) for t in terminos),
            nivel,
        )
        for s in r.substeps:
            self.traducir(s, nivel + 1)
        self.paso("Juntamos los resultados", "", rf"{self.I(f, v)} = {self.M(self.primitiva(r))}", nivel)

    def _PowerRule(self, r, f, v, nivel):
        n = r.exp
        aviso = ""
        if n.is_Rational and not n.is_Integer:
            aviso = " Las raíces se escriben como potencias: $\\sqrt{x} = x^{1/2}$."
        elif n.is_negative:
            aviso = " Los cocientes $\\frac{1}{x^n}$ se escriben como $x^{-n}$."
        self.paso(
            "Regla de la potencia",
            f"Usamos $\\int x^n\\,dx = \\frac{{x^{{n+1}}}}{{n+1}}$ (válida si $n\\neq -1$), aquí $n = {self.M(n)}$: "
            f"sumamos 1 al exponente y dividimos entre el nuevo exponente.{aviso}",
            rf"{self.I(f, v)} = \frac{{{self.M(r.base)}^{{{self.M(n + 1)}}}}}{{{self.M(n + 1)}}} = {self.M(self.primitiva(r))}",
            nivel,
        )

    def _ReciprocalRule(self, r, f, v, nivel):
        self.paso(
            "Integral de 1/x",
            "Es el caso $n=-1$, donde no sirve la regla de la potencia: $\\int \\frac{1}{x}\\,dx = \\ln|x|$. "
            "(SymPy escribe $\\ln x$; en los reales recuerda poner valor absoluto.)",
            rf"{self.I(f, v)} = {self.M(self.primitiva(r))}",
            nivel,
        )

    def _ExpRule(self, r, f, v, nivel):
        if r.base == sp.E:
            texto = "La exponencial es su propia primitiva: $\\int e^u\\,du = e^u$."
        else:
            texto = "Para otra base: $\\int a^u\\,du = \\frac{a^u}{\\ln a}$."
        self.paso("Integral de la exponencial", texto, rf"{self.I(f, v)} = {self.M(self.primitiva(r))}", nivel)

    def _ArctanRule(self, r, f, v, nivel):
        self.paso("Fórmula del arcotangente",
                  "Usamos $\\int \\frac{du}{u^2 + a^2} = \\frac{1}{a}\\arctan\\frac{u}{a}$.",
                  rf"{self.I(f, v)} = {self.M(self.primitiva(r))}", nivel)

    def _ArcsinRule(self, r, f, v, nivel):
        self.paso("Fórmula del arcoseno", "Usamos $\\int \\frac{du}{\\sqrt{1-u^2}} = \\arcsin u$.",
                  rf"{self.I(f, v)} = {self.M(self.primitiva(r))}", nivel)

    def _URule(self, r, f, v, nivel):
        letra = _LETRAS_SUSTITUCION[min(len(self.mapa_mostrar), len(_LETRAS_SUSTITUCION) - 1)]
        u = sp.Symbol(letra)
        self.mapa_mostrar[r.u_var] = u
        du = sp.diff(r.u_func, v)
        self.paso(
            "Sustitución (cambio de variable)",
            f"Elegimos ${letra} = {self.M(r.u_func)}$ porque su derivada aparece (salvo constantes) en el integrando. "
            f"Entonces $d{letra} = {self.M(du)}\\,d{self.M(v)}$ y la integral queda solo en ${letra}$.",
            rf"{self.I(f, v)} = {self.I(r.substep.integrand, r.u_var)}",
            nivel,
        )
        self.traducir(r.substep, nivel + 1)
        en_u = self.primitiva(r.substep)
        self.paso(
            "Volvemos a la variable original",
            f"Reemplazamos ${letra} = {self.M(r.u_func)}$.",
            rf"{self.M(en_u)} \;\Rightarrow\; {self.M(self.primitiva(r))}",
            nivel,
        )

    def _PartsRule(self, r, f, v, nivel):
        du = sp.diff(r.u, v)
        vv = self.primitiva(r.v_step)
        self.paso(
            "Integración por partes",
            "Usamos $\\int u\\,dv = u\\,v - \\int v\\,du$. Una ayuda para elegir $u$ es el orden LIATE "
            "(Logaritmo, Inversa trig., Algebraica, Trigonométrica, Exponencial). "
            f"Tomamos $u = {self.M(r.u)}$ y $dv = {self.M(r.dv)}\\,d{self.M(v)}$, "
            f"así $du = {self.M(du)}\\,d{self.M(v)}$ y $v = {self.M(vv)}$.",
            rf"{self.I(f, v)} = \left({self.M(r.u)}\right)\left({self.M(vv)}\right) - {self.I(vv * du, v)}",
            nivel,
        )
        self.paso("Calculamos v", "Para obtener $v$ integramos $dv$.", None, nivel + 1)
        self.traducir(r.v_step, nivel + 1)
        if r.second_step is not None:
            self.paso("Integral que queda", "Ahora resolvemos la integral que quedó a la derecha.", None, nivel + 1)
            self.traducir(r.second_step, nivel + 1)
        self.paso("Juntamos", "", rf"{self.I(f, v)} = {self.M(self.primitiva(r))}", nivel)

    def _CyclicPartsRule(self, r, f, v, nivel):
        self.paso(
            "Integración por partes cíclica",
            "Al integrar por partes dos veces vuelve a aparecer la integral original. "
            "Llamándola $I$, queda una ecuación del tipo $I = (\\text{algo}) - I$ y se despeja $I$.",
            None,
            nivel,
        )
        for parte in r.parts_rules:
            self.paso("Por partes", f"$u = {self.M(parte.u)}$, $dv = {self.M(parte.dv)}\\,d{self.M(v)}$.", None, nivel + 1)
        self.paso("Despejamos la integral", "", rf"{self.I(f, v)} = {self.M(self.primitiva(r))}", nivel)

    def _RewriteRule(self, r, f, v, nivel):
        self.paso(
            "Reescribir el integrando",
            "Antes de integrar conviene reescribir la expresión (desarrollar, usar una identidad "
            "trigonométrica o separar en fracciones simples).",
            rf"{self.M(f)} = {self.M(r.rewritten)}",
            nivel,
        )
        self.traducir(r.substep, nivel + 1)

    _CompleteSquareRule = _RewriteRule

    def _AlternativeRule(self, r, f, v, nivel):
        # SymPy ofrece varios caminos válidos: tomamos el primero.
        self.traducir(r.alternatives[0], nivel)

    def _TrigSubstitutionRule(self, r, f, v, nivel):
        self.paso(
            "Sustitución trigonométrica",
            f"Hacemos ${self.M(v)} = {self.M(r.func)}$ para eliminar la raíz usando una identidad pitagórica.",
            rf"{self.I(f, v)} = {self.I(r.rewritten, r.theta)}",
            nivel,
        )
        self.traducir(r.substep, nivel + 1)
        self.paso("Volvemos a la variable original", "", rf"{self.I(f, v)} = {self.M(self.primitiva(r))}", nivel)


def _buscar_sustitucion(f, x):
    """Busca u = g(x) tal que f(x) dx = h(u) du. Devuelve (g, h(u), u) o None."""
    if isinstance(f, sp.Add) or not f.has(x):
        return None
    candidatos = []
    for sub in sp.preorder_traversal(f):
        if isinstance(sub, sp.Pow) and sub.base.has(x) and not sub.exp.has(x) and sub.base != x:
            candidatos.append(sub.base)
        elif isinstance(sub, sp.Function) and len(sub.args) == 1 and sub.args[0].has(x) and sub.args[0] != x:
            candidatos.append(sub.args[0])
    u = sp.Dummy("u")
    vistos = []
    for g in candidatos:
        if g in vistos:
            continue
        vistos.append(g)
        dg = sp.diff(g, x)
        if dg == 0:
            continue
        try:
            en_u = sp.simplify(sp.simplify(f / dg).subs(g, u))
        except Exception:
            continue
        if not en_u.has(x) and en_u.has(u):
            return g, en_u, u
    return None


def _variable(expr, x):
    if x is not None:
        return x
    libres = sorted(expr.free_symbols, key=str)
    return libres[0] if len(libres) == 1 else sp.Symbol("x")


def primitiva_con_pasos(expr, x):
    """Devuelve (primitiva verificada, pasos, advertencias, es_elemental)."""
    advertencias: list[str] = []
    traductor = _Traductor(x)
    primitiva = None
    try:
        candidata = traductor.integrar(expr, x)
        if not traductor.incompleto and not candidata.has(sp.Integral) \
                and son_equivalentes(sp.diff(candidata, x), expr, [x]):
            primitiva = candidata
    except Exception:
        traductor.pasos = []

    if primitiva is None:
        candidata = sp.integrate(expr, x)
        if candidata.has(sp.Integral):
            return None, [], ["Esta integral no tiene una primitiva expresable con funciones elementales."], False
        if not son_equivalentes(sp.diff(candidata, x), expr, [x]):
            advertencias.append("SymPy no pudo confirmar el resultado; revísalo derivando.")
        traductor.pasos.append(Paso(
            "Cálculo con SymPy",
            "Esta integral necesita un método que no tengo guiado paso a paso; SymPy la calcula directamente.",
            rf"\int {a_latex(expr)}\,d{sp.latex(x)} = {a_latex(candidata)}",
        ))
        advertencias.append("Procedimiento parcial: el resultado lo calculó SymPy directamente.")
        primitiva = candidata

    especiales = {type(f).__name__ for f in primitiva.atoms(sp.Function)} - _ELEMENTALES
    if especiales:
        advertencias.append(
            "La primitiva usa funciones especiales (" + ", ".join(sorted(especiales)) + "): "
            "esta integral no tiene primitiva elemental, en Cálculo I normalmente no se pide."
        )
    bonita = simplificar_bonito(primitiva)
    if bonita != primitiva and son_equivalentes(sp.diff(bonita, x), expr, [x]):
        traductor.pasos.append(Paso("Simplificamos", "", rf"{a_latex(primitiva)} = {a_latex(bonita)}"))
        primitiva = bonita
    return primitiva, traductor.pasos, advertencias, True


def integral_con_pasos(expr, x: sp.Symbol | None = None, a=None, b=None) -> Solucion:
    """Integral indefinida (si ``a`` y ``b`` son None) o definida en [a, b]."""
    expr = sp.sympify(expr)
    x = _variable(expr, x)
    if (a is None) != (b is None):
        raise ValueError("Para una integral definida indica ambos límites, a y b.")
    if a is None:
        return _indefinida(expr, x)
    return _definida(expr, x, sp.sympify(a), sp.sympify(b))


def _indefinida(expr, x) -> Solucion:
    enunciado = rf"\int {a_latex(expr)}\,d{sp.latex(x)}"
    primitiva, pasos, advertencias, elemental = primitiva_con_pasos(expr, x)
    pasos.append(Paso(
        "Constante de integración",
        "Toda integral indefinida lleva $+C$: cualquier constante se anula al derivar.",
        None,
    ) if elemental else Paso("Sin primitiva elemental", advertencias[0]))
    if elemental:
        pasos.append(Paso(
            "Comprobación",
            "Derivamos el resultado y obtenemos de nuevo el integrando, así que la primitiva es correcta.",
            rf"\frac{{d}}{{d{sp.latex(x)}}}\left[{a_latex(primitiva)}\right] = {a_latex(expr)}",
        ))
    return Solucion(
        tipo="integral",
        enunciado_latex=enunciado,
        resultado=primitiva,
        resultado_latex=(rf"{enunciado} = {a_latex(primitiva)} + C" if elemental else r"\text{sin primitiva elemental}"),
        pasos=pasos,
        advertencias=advertencias,
        datos={"expr": expr, "variable": x},
    )


def _evaluar_en(F, x, punto, direccion):
    """F(punto); si el punto es infinito (o F no está definida ahí) se usa un límite lateral."""
    if punto in (sp.oo, -sp.oo):
        return sp.limit(F, x, punto), True
    valor = F.subs(x, punto)
    if valor.has(sp.nan, sp.zoo, sp.oo, -sp.oo):
        return sp.limit(F, x, punto, dir=direccion), True
    return sp.simplify(valor), False


def _definida(expr, x, a, b) -> Solucion:
    enunciado = rf"\int_{{{a_latex(a)}}}^{{{a_latex(b)}}} {a_latex(expr)}\,d{sp.latex(x)}"
    correcto = sp.integrate(expr, (x, a, b))
    advertencias: list[str] = []
    pasos: list[Paso] = []

    impropia = a in (sp.oo, -sp.oo) or b in (sp.oo, -sp.oo)
    problema = None
    if not impropia:
        izq, der = (a, b) if (a <= b) == sp.true else (b, a)
        try:
            dominio = sp.calculus.util.continuous_domain(expr, x, sp.Interval(izq, der))
            if dominio != sp.Interval(izq, der):
                problema = sp.Interval(izq, der) - dominio
                impropia = True
        except Exception:
            pass

    en_extremo = problema is not None and problema.is_subset(sp.FiniteSet(a, b))
    if en_extremo:
        pasos.append(Paso(
            "Integral impropia en un extremo",
            f"El integrando no está definido en ${a_latex(problema)}$, que es un extremo del intervalo. "
            "Buscamos la primitiva y en ese extremo, en vez de sustituir, calculamos un límite lateral.",
        ))
        problema = None
    elif problema is not None:
        pasos.append(Paso(
            "Revisamos la continuidad",
            f"El integrando no es continuo en todo el intervalo: falla en ${a_latex(problema)}$. "
            "El Teorema Fundamental del Cálculo no se puede aplicar directamente; es una integral impropia "
            "y se calcula con límites.",
        ))
    elif not en_extremo:
        pasos.append(Paso(
            "Teorema Fundamental del Cálculo",
            "Si $F$ es una primitiva de $f$ y $f$ es continua en el intervalo, entonces "
            "$\\int_a^b f(x)\\,dx = F(b) - F(a)$. Primero buscamos la primitiva $F$.",
        ))

    primitiva, pasos_F, adv_F, elemental = primitiva_con_pasos(expr, x)
    advertencias.extend(adv_F)
    if elemental and (problema is None):
        pasos.extend(Paso(p.regla, p.explicacion, p.latex, p.nivel + 1) for p in pasos_F)
        creciente = (a <= b) == sp.true or a == -sp.oo or b == sp.oo
        Fb, lim_b = _evaluar_en(primitiva, x, b, "-" if creciente else "+")
        Fa, lim_a = _evaluar_en(primitiva, x, a, "+" if creciente else "-")
        valor = sp.simplify(Fb - Fa) if not (Fb.has(sp.oo) or Fa.has(sp.oo)) else Fb - Fa
        texto_lim = " (donde no se puede sustituir directamente usamos límites)" if (lim_a or lim_b) else ""
        pasos.append(Paso(
            "Evaluamos F(b) − F(a)",
            f"Con $F({sp.latex(x)}) = {a_latex(primitiva)}$ evaluamos en los extremos{texto_lim}.",
            rf"F({a_latex(b)}) - F({a_latex(a)}) = \left({a_latex(Fb)}\right) - \left({a_latex(Fa)}\right) = {a_latex(valor)}",
        ))
        if not _mismo_valor(valor, correcto):
            advertencias.append("El cálculo con la primitiva no coincidió con SymPy; se muestra el valor de SymPy.")
    else:
        pasos.append(Paso(
            "Cálculo con SymPy",
            "SymPy calcula la integral (con límites en los puntos problemáticos).",
            rf"{enunciado} = {a_latex(correcto)}",
        ))

    if correcto in (sp.oo, -sp.oo) or correcto.has(sp.nan, sp.zoo):
        pasos.append(Paso("Conclusión", "La integral diverge (no da un número finito)."))
    elif impropia and not correcto.has(sp.Integral):
        pasos.append(Paso("Conclusión", "La integral impropia converge."))
    if correcto.has(sp.Integral):
        advertencias.append("SymPy no pudo calcular el valor exacto; se muestra una aproximación numérica.")
        correcto = sp.N(correcto)

    return Solucion(
        tipo="integral_definida",
        enunciado_latex=enunciado,
        resultado=correcto,
        resultado_latex=rf"{enunciado} = {a_latex(correcto)}" + (
            rf" \approx {sp.N(correcto, 6)}" if correcto.is_number and not correcto.is_Rational and correcto.is_finite else ""),
        pasos=pasos,
        advertencias=advertencias,
        datos={"expr": expr, "variable": x, "a": a, "b": b, "primitiva": primitiva},
    )


def _mismo_valor(v1, v2) -> bool:
    if v1 in (sp.oo, -sp.oo) or v2 in (sp.oo, -sp.oo):
        return v1 == v2
    return son_equivalentes(v1, v2)
