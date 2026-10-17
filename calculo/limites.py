"""Límites paso a paso.

Estrategia, como se enseña en clase:

1. Intentar **sustitución directa**.
2. Si aparece una **forma indeterminada** (0/0, ∞/∞, 0·∞, ∞−∞, 1^∞, 0^0, ∞^0),
   identificarla y transformarla: factorizar y simplificar, racionalizar,
   dividir entre la mayor potencia, aplicar **L'Hôpital** o usar logaritmos.
3. Si el denominador tiende a 0 y el numerador no, estudiar los **límites laterales**.

El valor correcto SIEMPRE lo da ``sympy.limit``. Si el camino guiado no llega al
mismo valor, se descarta y se muestra el resultado de SymPy con una advertencia.
"""

from __future__ import annotations

import sympy as sp

from .interprete import a_latex, a_latex_agrupado
from .pasos import Paso, Solucion

MAX_LHOPITAL = 4


class NoExiste:
    """Marca para un límite que no existe (laterales distintos u oscilación)."""

    def __init__(self, motivo: str, izquierdo=None, derecho=None):
        self.motivo = motivo
        self.izquierdo = izquierdo
        self.derecho = derecho

    def __repr__(self):
        return f"NoExiste({self.motivo!r})"

    def __eq__(self, otro):
        return isinstance(otro, NoExiste)

    def __hash__(self):
        return hash("NoExiste")


def _es_valor(v) -> bool:
    """¿Es ``v`` un valor de límite utilizable (número real o ±∞)?"""
    if v is None or isinstance(v, NoExiste):
        return False
    v = sp.sympify(v)
    if v.has(sp.nan, sp.zoo) or isinstance(v, sp.AccumBounds) or v.has(sp.AccumBounds):
        return False
    if v.has(sp.Limit):
        return False
    return v in (sp.oo, -sp.oo) or bool(v.is_real)


def limite_sympy(expr, x, a, direccion: str = "+-"):
    """Valor correcto del límite según SymPy.

    Devuelve un número, ``oo``/``-oo`` o un objeto ``NoExiste``.
    """
    a = sp.sympify(a)
    if a in (sp.oo, -sp.oo):
        v = sp.limit(expr, x, a)
        return v if _es_valor(v) else NoExiste("la función oscila o no se acerca a un valor")
    if direccion in ("+", "-"):
        v = sp.limit(expr, x, a, dir=direccion)
        return v if _es_valor(v) else NoExiste("la función oscila o no se acerca a un valor")
    derecho = sp.limit(expr, x, a, dir="+")
    izquierdo = sp.limit(expr, x, a, dir="-")
    if not (_es_valor(derecho) and _es_valor(izquierdo)):
        return NoExiste("la función oscila o no se acerca a un valor", izquierdo, derecho)
    if _iguales(derecho, izquierdo):
        return derecho
    return NoExiste("los límites laterales son distintos", izquierdo, derecho)


def _flecha(x, a, direccion):
    sup = {"+": "^{+}", "-": "^{-}"}.get(direccion, "")
    return rf"{sp.latex(x)} \to {a_latex(a)}{sup}"


def latex_limite(expr, x, a, direccion="+-"):
    cuerpo = a_latex_agrupado(expr)  # paréntesis si es suma, para que se vea qué abarca el límite
    return rf"\lim_{{{_flecha(x, a, direccion)}}} {cuerpo}"


def latex_valor(v) -> str:
    if isinstance(v, NoExiste):
        return r"\text{no existe}"
    return a_latex(v)


def _forma(v):
    """Clasifica un valor límite para describir formas: '0', 'oo', '-oo', 'k'."""
    if v == 0:
        return "0"
    if v == sp.oo:
        return "oo"
    if v == -sp.oo:
        return "-oo"
    return "k"


def _txt(v) -> str:
    return {sp.oo: r"\infty", -sp.oo: r"-\infty"}.get(v, a_latex(v)) if not isinstance(v, NoExiste) else "?"


class _Guia:
    """Construye el camino guiado. Cada método devuelve el valor o ``None``."""

    def __init__(self, x, a, direccion):
        self.x, self.a, self.dir = x, sp.sympify(a), direccion
        self.pasos: list[Paso] = []

    def paso(self, regla, explicacion, latex=None, nivel=0):
        self.pasos.append(Paso(regla, explicacion, latex, nivel))

    def lim(self, e):
        """Límite auxiliar (de numerador, denominador, factores...) calculado por SymPy."""
        r = limite_sympy(e, self.x, self.a, self.dir)
        return r

    def L(self, e):
        return latex_limite(e, self.x, self.a, self.dir)

    def L_cociente(self, n, d):
        """LaTeX de lim n/d sin que SymPy reordene la fracción."""
        return rf"\lim_{{{_flecha(self.x, self.a, self.dir)}}} \frac{{{a_latex(n)}}}{{{a_latex(d)}}}"

    # ------------------------------------------------------------------
    def resolver(self, e, nivel=0, profundidad=0):
        if profundidad > 6:
            return None
        x, a = self.x, self.a
        e = sp.sympify(e)

        if not e.has(x):
            self.paso("Límite de una constante", "La expresión no depende de la variable: el límite es la misma constante.",
                      rf"{self.L(e)} = {a_latex(e)}", nivel)
            return e

        finito = a not in (sp.oo, -sp.oo)
        if finito:
            v = self._sustitucion(e)
            if v is not None:
                self.paso(
                    "Sustitución directa",
                    f"La función es continua en ${sp.latex(x)} = {a_latex(a)}$, así que basta con sustituir.",
                    rf"{self.L(e)} = {a_latex(e.subs(x, a))} = {a_latex(v)}" if e.subs(x, a) != v
                    else rf"{self.L(e)} = {a_latex(v)}",
                    nivel,
                )
                return v

        # Primero la fracción tal como está escrita; si no hay, intentamos juntar fracciones.
        numerador, denominador = sp.fraction(e)
        if not denominador.has(x) and (not finito or _hay_fraccion(e)):
            numerador, denominador = sp.fraction(sp.together(e))
        if denominador.has(x):
            return self._cociente(e, numerador, denominador, nivel, profundidad)

        if isinstance(e, sp.Pow) and e.args[1].has(x) and e.args[0].has(x):
            return self._potencia_indeterminada(e, nivel, profundidad)

        if isinstance(e, sp.Mul):
            r = self._producto(e, nivel, profundidad)
            if r is not None:
                return r

        if isinstance(e, sp.Add):
            r = self._suma(e, nivel, profundidad)
            if r is not None:
                return r

        if not finito:
            return self._al_infinito_simple(e, nivel)
        return None

    # ------------------------------------------------------------------
    def _sustitucion(self, e):
        """Valor por sustitución directa, o None si no es válida."""
        try:
            v = sp.simplify(e.subs(self.x, self.a))
        except Exception:
            return None
        if not _es_valor(v) or v in (sp.oo, -sp.oo) or v.has(sp.oo, -sp.oo, sp.zoo, sp.nan):
            return None
        # 0^0 es indeterminado aunque SymPy lo evalúe como 1.
        for p in sp.preorder_traversal(e):
            if isinstance(p, sp.Pow) and p.args[0].has(self.x) and p.args[1].has(self.x):
                if p.args[0].subs(self.x, self.a) == 0:
                    return None
        # Comprobamos que realmente es el límite (la función es continua ahí).
        real = self.lim(e)
        if isinstance(real, NoExiste) or not _es_valor(real) or sp.simplify(real - v) != 0:
            return None
        return v

    def _cociente(self, e, n, d, nivel, profundidad):
        x, a = self.x, self.a
        ln, ld = self.lim(n), self.lim(d)
        if isinstance(ln, NoExiste) or isinstance(ld, NoExiste):
            return None
        fn, fd = _forma(ln), _forma(ld)

        if fn == "0" and fd == "0" or fn in ("oo", "-oo") and fd in ("oo", "-oo"):
            forma = r"\frac{0}{0}" if fn == "0" else r"\frac{\infty}{\infty}"
            self.paso(
                "Forma indeterminada",
                f"El numerador tiende a ${_txt(ln)}$ y el denominador a ${_txt(ld)}$: aparece la forma ${forma}$, "
                "que NO significa que el límite sea 1 ni 0. Hay que transformar la expresión.",
                rf"{self.L(e)} \;\to\; {forma}",
                nivel,
            )
            # 1) Factorizar y simplificar (funciones racionales con a finito)
            if a not in (sp.oo, -sp.oo) and e.is_rational_function(x):
                r = self._factorizar(e, n, d, nivel, profundidad)
                if r is not None:
                    return r
            # 2) Dividir entre la mayor potencia (racionales en el infinito)
            if a in (sp.oo, -sp.oo) and e.is_rational_function(x):
                r = self._mayor_potencia(e, n, d, nivel)
                if r is not None:
                    return r
            # 3) Racionalizar si hay raíces cuadradas
            if _tiene_raiz(e):
                r = self._racionalizar(e, n, d, nivel, profundidad)
                if r is not None:
                    return r
            # 4) L'Hôpital
            return self._lhopital(n, d, nivel, profundidad)

        if fd == "0" and fn != "0":
            return self._k_sobre_cero(e, ln, nivel)

        # Sin indeterminación: límite del cociente = cociente de límites
        if fd == "k" or fd in ("oo", "-oo") and fn == "k" or fn == "0" and fd in ("oo", "-oo"):
            valor = self.lim(e)
            self.paso(
                "Límite de un cociente",
                f"El numerador tiende a ${_txt(ln)}$ y el denominador a ${_txt(ld)}$. "
                "No hay indeterminación, así que el límite es el cociente de los límites"
                + (" (un número finito dividido entre algo que crece sin límite tiende a 0)." if fd in ("oo", "-oo") else "."),
                rf"{self.L(e)} = \frac{{{_txt(ln)}}}{{{_txt(ld)}}} = {latex_valor(valor)}",
                nivel,
            )
            return valor
        return None

    def _factorizar(self, e, n, d, nivel, profundidad):
        x = self.x
        nf, df = sp.factor(n), sp.factor(d)
        simplificada = sp.cancel(e)
        if simplificada == e or sp.fraction(simplificada)[1] == d:
            return None
        self.paso(
            "Factorizar y simplificar",
            "Factorizamos numerador y denominador. Como ambos se anulan en el punto, comparten el factor "
            f"$({sp.latex(x)} - {a_latex(self.a)})$, que se puede cancelar porque $x \\neq {a_latex(self.a)}$ dentro del límite.",
            rf"\frac{{{a_latex(n)}}}{{{a_latex(d)}}} = \frac{{{a_latex(nf)}}}{{{a_latex(df)}}} = {a_latex(simplificada)}",
            nivel,
        )
        return self.resolver(simplificada, nivel + 1, profundidad + 1)

    def _mayor_potencia(self, e, n, d, nivel):
        x = self.x
        gn = sp.degree(sp.Poly(n, x))
        gd = sp.degree(sp.Poly(d, x))
        k = gd
        cn = sp.LC(sp.Poly(n, x))
        cd = sp.LC(sp.Poly(d, x))
        valor = self.lim(e)
        if gn < gd:
            conclusion = "El grado del numerador es menor que el del denominador, así que el límite es 0."
        elif gn == gd:
            conclusion = (f"Los grados son iguales, así que el límite es el cociente de los coeficientes principales: "
                          f"${a_latex(cn)}/{a_latex(cd)}$.")
        else:
            conclusion = "El grado del numerador es mayor que el del denominador, así que el límite es infinito (con el signo que corresponda)."
        nueva_n = sp.expand(n / x**k)
        nueva_d = sp.expand(d / x**k)
        self.paso(
            "Dividir entre la mayor potencia",
            f"Dividimos numerador y denominador entre ${sp.latex(x**k)}$ (la mayor potencia del denominador). "
            f"Los términos de la forma $\\frac{{c}}{{x^m}}$ tienden a 0. {conclusion}",
            rf"{self.L(e)} = {self.L_cociente(nueva_n, nueva_d)} = {latex_valor(valor)}",
            nivel,
        )
        return valor

    def _racionalizar(self, e, n, d, nivel, profundidad):
        x = self.x
        for parte, es_num in ((n, True), (d, False)):
            if isinstance(parte, sp.Add) and len(parte.args) == 2 and _tiene_raiz(parte):
                t1, t2 = parte.args
                conj = t1 - t2
                nuevo_n = sp.expand(n * conj) if es_num else n * conj
                nuevo_d = d * conj if es_num else sp.expand(d * conj)
                nueva = sp.cancel(sp.simplify(nuevo_n / nuevo_d))
                donde = "el numerador" if es_num else "el denominador"
                self.paso(
                    "Racionalizar",
                    f"Hay una raíz en {donde}. Multiplicamos arriba y abajo por el conjugado "
                    f"${a_latex(conj)}$ y usamos $(A+B)(A-B) = A^2 - B^2$ para eliminar la raíz.",
                    rf"\frac{{{a_latex(n)}}}{{{a_latex(d)}}}\cdot\frac{{{a_latex(conj)}}}{{{a_latex(conj)}}}"
                    rf" = \frac{{{a_latex(nuevo_n)}}}{{{a_latex(nuevo_d)}}} = {a_latex(nueva)}",
                    nivel,
                )
                if nueva.subs(x, self.a).has(sp.nan, sp.zoo):
                    return None
                return self.resolver(nueva, nivel + 1, profundidad + 1)
        return None

    def _lhopital(self, n, d, nivel, profundidad, intento=1):
        x = self.x
        if intento > MAX_LHOPITAL:
            return None
        dn, dd = sp.diff(n, x), sp.diff(d, x)
        nueva = sp.simplify(dn / dd)
        self.paso(
            "Regla de L'Hôpital",
            "Como tenemos $\\frac{0}{0}$ o $\\frac{\\infty}{\\infty}$, podemos derivar el numerador y el denominador "
            "POR SEPARADO (no es la regla del cociente) y calcular el límite del nuevo cociente.",
            rf"{self.L_cociente(n, d)} = {self.L_cociente(dn, dd)}",
            nivel,
        )
        if dd != 1:
            self.paso("Simplificamos", "", rf"\frac{{{a_latex(dn)}}}{{{a_latex(dd)}}} = {a_latex(nueva)}", nivel)
        return self.resolver(nueva, nivel + 1, profundidad + 1)

    def _k_sobre_cero(self, e, ln, nivel):
        x, a = self.x, self.a
        valor = self.lim(e)
        if a in (sp.oo, -sp.oo) or self.dir in ("+", "-"):
            lado = {"+": "por la derecha", "-": "por la izquierda"}.get(self.dir, "")
            self.paso(
                "Numerador ≠ 0, denominador → 0",
                f"El numerador tiende a ${_txt(ln)}$ y el denominador a 0 {lado}: el cociente crece sin límite. "
                "El signo se decide mirando el signo del denominador muy cerca del punto.",
                rf"{self.L(e)} = {latex_valor(valor)}",
                nivel,
            )
            return valor
        izq = sp.limit(e, x, a, dir="-")
        der = sp.limit(e, x, a, dir="+")
        self.paso(
            "Numerador ≠ 0, denominador → 0: límites laterales",
            f"El numerador tiende a ${_txt(ln)}$ y el denominador a 0, así que el cociente se va a infinito. "
            "Para saber el signo calculamos los límites por la izquierda y por la derecha.",
            rf"\lim_{{{_flecha(x, a, '-')}}} {a_latex(e)} = {_txt(izq)}, \qquad \lim_{{{_flecha(x, a, '+')}}} {a_latex(e)} = {_txt(der)}",
            nivel,
        )
        if izq == der:
            self.paso("Conclusión", "Ambos laterales coinciden.", rf"{self.L(e)} = {_txt(der)}", nivel)
            return der
        self.paso("Conclusión", "Los límites laterales son distintos, por lo tanto el límite NO existe.",
                  rf"{self.L(e)}\ \text{{no existe}}", nivel)
        return NoExiste("los límites laterales son distintos", izq, der)

    def _producto(self, e, nivel, profundidad):
        """Forma 0·∞: se reescribe como cociente."""
        x = self.x
        constante, resto = e.as_independent(x, as_Add=False)
        factores = list(sp.Mul.make_args(resto))
        if len(factores) < 2:
            return None
        f = factores[0]
        g = sp.Mul(*factores[1:])
        lf, lg = self.lim(f), self.lim(g)
        formas = {_forma(lf), _forma(lg)}
        if not ("0" in formas and ({"oo", "-oo"} & formas)):
            return None
        cero, infinito = (f, g) if _forma(lf) == "0" else (g, f)
        self.paso(
            "Forma indeterminada 0·∞",
            f"Un factor tiende a 0 y el otro a infinito. Lo reescribimos como un cociente para poder usar L'Hôpital: "
            "$f\\cdot g = \\frac{f}{1/g}$.",
            rf"{self.L(e)} \;\to\; 0\cdot\infty",
            nivel,
        )
        # Probamos las dos formas de reescribir y nos quedamos con la más corta que funcione.
        exitosas = []
        for num, den in ((cero, 1 / infinito), (infinito, 1 / cero)):
            prueba = _Guia(x, self.a, self.dir)
            prueba.paso(
                "Reescribimos como cociente", "",
                rf"{a_latex(e)} = {a_latex(constante)}\cdot\frac{{{a_latex(num)}}}{{{a_latex(den)}}}" if constante != 1
                else rf"{a_latex(e)} = \frac{{{a_latex(num)}}}{{{a_latex(den)}}}",
                nivel,
            )
            r = prueba._lhopital(num, den, nivel, profundidad + 1)
            if r is not None and _es_valor(r):
                exitosas.append((len(prueba.pasos), r, prueba.pasos))
        if not exitosas:
            return None
        _, r, pasos = min(exitosas, key=lambda t: t[0])
        self.pasos.extend(pasos)
        if constante != 1:
            total = constante * r
            self.paso("Multiplicamos por la constante", "", rf"{a_latex(constante)}\cdot {_txt(r)} = {_txt(total)}", nivel)
            return total
        return r

    def _suma(self, e, nivel, profundidad):
        """Forma ∞ − ∞: combinar fracciones o racionalizar."""
        x = self.x
        terminos = e.args
        limites = [self.lim(t) for t in terminos]
        if any(isinstance(v, NoExiste) for v in limites):
            return None
        if sp.oo in limites and -sp.oo in limites:
            self.paso("Forma indeterminada ∞ − ∞",
                      "Hay términos que tienden a $+\\infty$ y otros a $-\\infty$: no se puede restar directamente.",
                      rf"{self.L(e)} \;\to\; \infty - \infty", nivel)
            if _tiene_raiz(e) and len(terminos) == 2:
                t1, t2 = terminos
                conj = t1 - t2
                nueva = sp.simplify(sp.expand(t1**2 - t2**2) / conj)
                self.paso(
                    "Racionalizar",
                    f"Multiplicamos y dividimos por el conjugado ${a_latex(conj)}$ para eliminar la raíz.",
                    rf"{a_latex(e)} = \frac{{{a_latex(sp.expand(t1**2 - t2**2))}}}{{{a_latex(conj)}}}",
                    nivel,
                )
                return self.resolver(nueva, nivel + 1, profundidad + 1)
            combinada = sp.together(e)
            if combinada != e and sp.fraction(combinada)[1].has(x):
                self.paso("Restar fracciones", "Escribimos todo con denominador común.",
                          rf"{a_latex(e)} = {a_latex(combinada)}", nivel)
                return self.resolver(combinada, nivel + 1, profundidad + 1)
            if self.a in (sp.oo, -sp.oo) and e.is_polynomial(x):
                return self._al_infinito_simple(e, nivel)
            return None
        if all(_es_valor(v) for v in limites):
            # Suma de límites sin indeterminación
            valor = self.lim(e)
            self.paso(
                "Límite de una suma",
                "Calculamos el límite de cada término y sumamos (no hay indeterminación).",
                rf"{self.L(e)} = " + " + ".join(_txt(v) for v in limites) + rf" = {latex_valor(valor)}",
                nivel,
            )
            return valor
        return None

    def _potencia_indeterminada(self, e, nivel, profundidad):
        """Formas 1^∞, 0^0, ∞^0: se usa logaritmo."""
        x = self.x
        base, exponente = e.args
        lb, le = self.lim(base), self.lim(exponente)
        nombre = None
        if lb == 1 and le in (sp.oo, -sp.oo):
            nombre = r"1^{\infty}"
        elif lb == 0 and le == 0:
            nombre = r"0^{0}"
        elif lb == sp.oo and le == 0:
            nombre = r"\infty^{0}"
        if nombre is None:
            return None
        self.paso(
            f"Forma indeterminada ${nombre}$",
            "Usamos logaritmos: si $y = f^g$, entonces $\\ln y = g\\cdot\\ln f$. "
            "Calculamos el límite de $g\\ln f$ y al final elevamos $e$ a ese resultado.",
            rf"{a_latex(e)} = e^{{{a_latex(exponente * sp.log(base))}}}",
            nivel,
        )
        interior = exponente * sp.log(base)
        r = self.resolver(interior, nivel + 1, profundidad + 1)
        if r is None or isinstance(r, NoExiste):
            return None
        valor = sp.exp(r) if r not in (sp.oo, -sp.oo) else (sp.oo if r == sp.oo else sp.Integer(0))
        self.paso("Volvemos a la exponencial", "El límite original es $e$ elevado al límite que acabamos de calcular.",
                  rf"{self.L(e)} = e^{{{_txt(r)}}} = {a_latex(valor)}", nivel)
        return valor

    def _al_infinito_simple(self, e, nivel):
        x = self.x
        valor = self.lim(e)
        if isinstance(valor, NoExiste):
            return None
        if e.is_polynomial(x):
            termino = sp.LT(sp.Poly(e, x)).as_expr()
            self.paso(
                "Polinomio en el infinito",
                f"En un polinomio, cuando ${sp.latex(x)}\\to\\pm\\infty$ manda el término de mayor grado, ${a_latex(termino)}$.",
                rf"{self.L(e)} = {self.L(termino)} = {latex_valor(valor)}",
                nivel,
            )
            return valor
        self.paso(
            "Comportamiento en el infinito",
            "Analizamos hacia dónde va cada parte de la expresión cuando la variable crece sin límite.",
            rf"{self.L(e)} = {latex_valor(valor)}",
            nivel,
        )
        return valor


def _hay_fraccion(e) -> bool:
    return sp.fraction(sp.together(e))[1] != 1


def _tiene_raiz(e) -> bool:
    return any(isinstance(p, sp.Pow) and p.args[1].is_Rational and p.args[1].q == 2 for p in sp.preorder_traversal(e))


def _iguales(v1, v2) -> bool:
    if isinstance(v1, NoExiste) or isinstance(v2, NoExiste):
        return isinstance(v1, NoExiste) and isinstance(v2, NoExiste)
    if v1 is None or v2 is None:
        return False
    if v1 in (sp.oo, -sp.oo) or v2 in (sp.oo, -sp.oo):
        return v1 == v2
    try:
        return sp.simplify(v1 - v2) == 0
    except Exception:
        return False


def limite_con_pasos(expr, x: sp.Symbol, a, direccion: str = "+-") -> Solucion:
    """Calcula ``lim_{x→a} expr`` con pasos explicados.

    ``direccion``: "+-" (bilateral), "+" (por la derecha) o "-" (por la izquierda).
    """
    expr = sp.sympify(expr)
    a = sp.sympify(a)
    if direccion not in ("+-", "+", "-"):
        raise ValueError("La dirección debe ser '+-', '+' o '-'.")
    if a in (sp.oo, -sp.oo):
        direccion = "+-"  # no tiene sentido lateral en el infinito

    correcto = limite_sympy(expr, x, a, direccion)
    guia = _Guia(x, a, direccion)
    try:
        obtenido = guia.resolver(expr)
    except Exception:  # cualquier fallo del camino guiado no debe romper la app
        obtenido = None

    advertencias = []
    pasos = guia.pasos
    if not _iguales(obtenido, correcto):
        # El camino guiado no llegó (o no coincidió): mostramos el valor de SymPy.
        pasos = [p for p in pasos if p.regla.startswith("Forma indeterminada")][:1]
        pasos.append(Paso(
            "Cálculo con SymPy",
            "Este límite necesita una técnica que no tengo guiada paso a paso (por ejemplo, series de Taylor o "
            "acotación). SymPy lo calcula con métodos más avanzados.",
            rf"{latex_limite(expr, x, a, direccion)} = {latex_valor(correcto)}",
        ))
        advertencias.append("Procedimiento parcial: el resultado lo calculó SymPy directamente.")

        if isinstance(correcto, NoExiste) and _es_valor(correcto.izquierdo) and _es_valor(correcto.derecho):
            pasos.append(Paso(
                "Límites laterales",
                "Calculamos el límite acercándonos por la izquierda y por la derecha.",
                rf"\lim_{{{_flecha(x, a, '-')}}} {a_latex(expr)} = {_txt(correcto.izquierdo)}, \qquad "
                rf"\lim_{{{_flecha(x, a, '+')}}} {a_latex(expr)} = {_txt(correcto.derecho)}",
            ))

    if isinstance(correcto, NoExiste):
        detalle = f"El límite no existe: {correcto.motivo}."
        if correcto.izquierdo is not None and _es_valor(correcto.izquierdo):
            detalle += f" Por la izquierda: ${_txt(correcto.izquierdo)}$; por la derecha: ${_txt(correcto.derecho)}$."
        if not any(p.regla == "Conclusión" for p in pasos):
            pasos.append(Paso("Conclusión", detalle))
    elif sp.sympify(correcto).has(sp.I):
        advertencias.append("El resultado no es un número real: la función no está definida en los reales cerca del punto.")

    return Solucion(
        tipo="limite",
        enunciado_latex=latex_limite(expr, x, a, direccion),
        resultado=correcto,
        resultado_latex=rf"{latex_limite(expr, x, a, direccion)} = {latex_valor(correcto)}",
        pasos=pasos,
        advertencias=advertencias,
        datos={"expr": expr, "variable": x, "punto": a, "direccion": direccion},
    )
