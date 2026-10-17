"""Modo «verificar»: compara la respuesta del estudiante con la correcta.

La respuesta correcta SIEMPRE sale del solucionador (SymPy). Si la respuesta
del estudiante no es equivalente, se intenta diagnosticar el error típico
(signo, factor constante, olvidar la regla de la cadena, integrar en vez de
derivar, restar al revés en el TFC...) y se dan pistas graduales que NO revelan
la solución completa.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import sympy as sp

from .derivadas import _Derivador
from .interprete import ErrorEntrada, a_latex, interpretar
from .limites import NoExiste
from .pasos import Solucion, son_equivalentes

_PALABRAS_NO_EXISTE = {"no existe", "noexiste", "ne", "dne", "no", "no hay", "nexiste", "∄"}


@dataclass
class Veredicto:
    correcto: bool
    mensaje: str
    pistas: list[str] = field(default_factory=list)
    interpretado_latex: str = ""  # cómo se entendió la respuesta del estudiante


# --------------------------------------------------------------------------
# Lectura de la respuesta del estudiante
# --------------------------------------------------------------------------

def _quitar_lado_izquierdo(texto: str) -> str:
    """Quita «y' =», «f'(x) =», «F(x) =», «L =», etc."""
    t = texto.strip()
    if "=" in t and not re.search(r"[<>]=", t):
        izquierda, derecha = t.split("=", 1)
        if len(izquierda.strip()) <= 12:
            return derecha.strip()
    return t


def leer_expresion(texto: str, variables=("x",)) -> sp.Expr:
    texto = _quitar_lado_izquierdo(texto)
    return interpretar(texto)


def leer_valor_limite(texto: str):
    t = _quitar_lado_izquierdo(texto).strip().lower()
    if t in _PALABRAS_NO_EXISTE:
        return NoExiste("indicado por el estudiante")
    t = t.replace("menos infinito", "-oo").replace("+infinito", "oo").replace("+oo", "oo")
    valor = interpretar(t)
    if valor.free_symbols:
        raise ErrorEntrada("El valor de un límite es un número (o «oo», «-oo», «no existe»), no puede tener variables.")
    return valor


def leer_primitiva(texto: str, x: sp.Symbol) -> sp.Expr:
    """Lee una primitiva quitando la constante de integración (+C, +K...)."""
    expr = leer_expresion(texto)
    constantes = [s for s in expr.free_symbols if s != x and str(s) in ("C", "c", "K", "k", "C1")]
    return expr.subs({c: 0 for c in constantes}), bool(constantes)


# --------------------------------------------------------------------------
# Verificación según el tipo de problema
# --------------------------------------------------------------------------

def verificar(solucion: Solucion, respuesta: str) -> Veredicto:
    """Compara ``respuesta`` (texto) con la ``solucion`` calculada por SymPy."""
    if respuesta is None or not str(respuesta).strip():
        return Veredicto(False, "Escribe tu respuesta para poder revisarla.")
    try:
        if solucion.tipo == "derivada":
            return _verificar_derivada(solucion, respuesta)
        if solucion.tipo == "integral":
            return _verificar_integral(solucion, respuesta)
        if solucion.tipo == "integral_definida":
            return _verificar_definida(solucion, respuesta)
        if solucion.tipo == "limite":
            return _verificar_limite(solucion, respuesta)
    except ErrorEntrada as error:
        return Veredicto(False, f"No pude leer tu respuesta: {error}")
    except Exception:  # red de seguridad: nunca mostrar un error técnico
        return Veredicto(False, "No pude comparar tu respuesta. Revisa cómo está escrita e inténtalo otra vez.")
    return Veredicto(False, "Este tipo de problema todavía no se puede verificar.")


def _variables_extra(expr, x):
    return [s for s in expr.free_symbols if s != x]


def _verificar_derivada(sol: Solucion, texto: str) -> Veredicto:
    x = sol.datos["variable"]
    f = sol.datos["expr"]
    correcta = sol.resultado
    usuario = leer_expresion(texto)
    interpretado = a_latex(usuario)
    extra = _variables_extra(usuario, x)
    if extra:
        return Veredicto(False, f"Tu respuesta usa letras que no aparecen en el problema: "
                         f"{', '.join(map(str, extra))}. Usa solo ${sp.latex(x)}$.", [], interpretado)
    if son_equivalentes(usuario, correcta, [x]):
        return Veredicto(True, "¡Correcto! Tu derivada es equivalente a la de SymPy.", [], interpretado)

    pistas = []
    diagnostico = _diagnostico_comun(usuario, correcta, x)
    if diagnostico:
        pistas.append(diagnostico)
    if sol.datos.get("orden", 1) == 1:
        if son_equivalentes(usuario, f, [x]):
            pistas.insert(0, "Escribiste la misma función: todavía falta derivarla.")
        else:
            try:
                integral = sp.integrate(f, x)
                if not integral.has(sp.Integral) and son_equivalentes(usuario, integral, [x]):
                    pistas.insert(0, "¡Ojo! Parece que integraste en lugar de derivar.")
            except Exception:
                pass
        sin_cadena = _derivada_olvidando_cadena(f, x)
        if sin_cadena is not None and son_equivalentes(usuario, sin_cadena, [x]):
            pistas.insert(0, "Parece que olvidaste la regla de la cadena: después de derivar la función de afuera "
                             "hay que multiplicar por la derivada de lo de adentro.")
        error_producto = _producto_mal_aplicado(f, x)
        if error_producto is not None and son_equivalentes(usuario, error_producto, [x]):
            pistas.insert(0, "La derivada de un producto NO es el producto de las derivadas: "
                             "$(f g)' = f' g + f g'$.")
        error_cociente = _cociente_mal_aplicado(f, x)
        if error_cociente is not None and son_equivalentes(usuario, error_cociente, [x]):
            pistas.insert(0, "La derivada de un cociente NO es el cociente de las derivadas: "
                             "$\\left(\\frac{f}{g}\\right)' = \\frac{f'g - fg'}{g^2}$.")
        pistas.append(_regla_principal_derivada(f, x))
    pistas.append(_pista_primer_paso(sol))
    return Veredicto(False, "Todavía no es correcto.", _sin_repetir(pistas), interpretado)


def _verificar_integral(sol: Solucion, texto: str) -> Veredicto:
    x = sol.datos["variable"]
    f = sol.datos["expr"]
    if sol.resultado is None:
        return Veredicto(False, "Esta integral no tiene primitiva elemental, así que no hay una respuesta que comparar.")
    usuario, tenia_c = leer_primitiva(texto, x)
    interpretado = a_latex(usuario) + (" + C" if tenia_c else "")
    extra = _variables_extra(usuario, x)
    if extra:
        return Veredicto(False, f"Tu respuesta usa letras que no esperaba: {', '.join(map(str, extra))}. "
                         "Para la constante de integración usa «+ C».", [], interpretado)
    derivada_usuario = sp.diff(usuario, x)
    if son_equivalentes(derivada_usuario, f, [x]):
        mensaje = "¡Correcto! Al derivar tu resultado se obtiene el integrando."
        if not tenia_c:
            mensaje += " Solo te faltó escribir la constante de integración «+ C»."
        return Veredicto(True, mensaje, [], interpretado)

    pistas = []
    if son_equivalentes(usuario, sp.diff(f, x), [x]):
        pistas.append("¡Ojo! Parece que derivaste en lugar de integrar.")
    diagnostico = _diagnostico_comun(derivada_usuario, f, x, contexto="integral")
    if diagnostico:
        pistas.append(diagnostico)
    pistas.append("Truco para revisarte tú mismo: deriva tu resultado. Si no obtienes el integrando, hay un error. "
                  f"La derivada de lo que escribiste es ${a_latex(sp.simplify(derivada_usuario))}$.")
    pistas.extend(_pistas_metodo_integral(sol))
    return Veredicto(False, "Todavía no es correcto.", _sin_repetir(pistas), interpretado)


def _verificar_definida(sol: Solucion, texto: str) -> Veredicto:
    try:
        usuario = leer_valor_limite(texto)
    except ErrorEntrada as error:
        return Veredicto(False, f"No pude leer tu respuesta: {error}")
    if isinstance(usuario, NoExiste):
        if sol.resultado in (sp.oo, -sp.oo):
            return Veredicto(True, "Correcto: la integral diverge (no es un número finito).")
        return Veredicto(False, "La integral sí da un número. Vuelve a intentarlo.", _pistas_metodo_integral(sol))
    interpretado = a_latex(usuario)
    correcta = sol.resultado
    if _mismo_numero(usuario, correcta):
        aprox = f" (≈ {sp.N(correcta, 6)})" if not correcta.is_Rational and correcta.is_finite else ""
        return Veredicto(True, f"¡Correcto!{aprox}", [], interpretado)
    if _aproximacion_valida(texto, usuario, correcta):
        return Veredicto(True, f"¡Correcto! (aproximación bien redondeada; el valor exacto es ${a_latex(correcta)}$)",
                         [], interpretado)

    pistas = []
    F = sol.datos.get("primitiva")
    a, b, x = sol.datos["a"], sol.datos["b"], sol.datos["variable"]
    if F is not None and correcta.is_finite:
        try:
            Fa, Fb = sp.limit(F, x, a, "+"), sp.limit(F, x, b, "-")
            if _mismo_numero(usuario, Fa - Fb):
                pistas.append("Restaste al revés: el TFC dice $F(b) - F(a)$ (extremo de arriba menos el de abajo).")
            elif _mismo_numero(usuario, Fb):
                pistas.append("Calculaste solo $F(b)$: falta restar $F(a)$.")
            elif _mismo_numero(usuario, -correcta):
                pistas.append("Tu resultado tiene el signo cambiado.")
        except Exception:
            pass
    if correcta in (sp.oo, -sp.oo):
        pistas.append("Revisa si el integrando es continuo en todo el intervalo: esta integral es impropia.")
    pistas.append("Primero encuentra una primitiva $F$ y luego calcula $F(b) - F(a)$. "
                  "Puedes revisar tu primitiva derivándola.")
    pistas.extend(_pistas_metodo_integral(sol))
    return Veredicto(False, "Todavía no es correcto.", _sin_repetir(pistas), interpretado)


def _verificar_limite(sol: Solucion, texto: str) -> Veredicto:
    usuario = leer_valor_limite(texto)
    correcta = sol.resultado
    interpretado = r"\text{no existe}" if isinstance(usuario, NoExiste) else a_latex(usuario)
    if isinstance(correcta, NoExiste):
        if isinstance(usuario, NoExiste):
            return Veredicto(True, f"¡Correcto! El límite no existe ({correcta.motivo}).", [], interpretado)
        pistas = ["Calcula los límites laterales (por la izquierda y por la derecha) y compáralos."]
        return Veredicto(False, "Todavía no es correcto.", pistas + _pistas_limite(sol), interpretado)
    if isinstance(usuario, NoExiste):
        pistas = ["Este límite sí existe. Si te salió una forma como 0/0, eso no significa que no exista: "
                  "hay que transformar la expresión."]
        return Veredicto(False, "Todavía no es correcto.", pistas + _pistas_limite(sol), interpretado)
    if _mismo_numero(usuario, correcta):
        return Veredicto(True, "¡Correcto!", [], interpretado)
    if _aproximacion_valida(texto, usuario, correcta):
        return Veredicto(True, f"¡Correcto! (aproximación bien redondeada; el valor exacto es ${a_latex(correcta)}$)",
                         [], interpretado)

    pistas = []
    if correcta in (sp.oo, -sp.oo) and usuario in (sp.oo, -sp.oo):
        pistas.append("Vas bien: el límite es infinito, pero revisa el signo.")
    elif usuario.is_finite and correcta.is_finite and _mismo_numero(usuario, -correcta):
        pistas.append("Revisa los signos: tu resultado tiene el signo cambiado.")
    formas = [p for p in sol.pasos if p.regla.startswith("Forma indeterminada")]
    if formas and usuario in (0, 1, sp.oo):
        pistas.append("Recuerda: $\\frac{0}{0}$, $\\frac{\\infty}{\\infty}$ y $1^\\infty$ son formas indeterminadas, "
                      "no valen automáticamente 0, 1 ni ∞.")
    pistas.extend(_pistas_limite(sol))
    return Veredicto(False, "Todavía no es correcto.", _sin_repetir(pistas), interpretado)


# --------------------------------------------------------------------------
# Diagnósticos y pistas
# --------------------------------------------------------------------------

def _decimales(texto: str) -> int | None:
    """Cantidad de decimales escritos por el estudiante (None si no usó decimales)."""
    m = re.findall(r"\d[.,](\d+)", texto)
    return max(len(d) for d in m) if m else None


def _aproximacion_valida(texto: str, usuario, correcta) -> bool | None:
    """Si el estudiante escribió un decimal, lo aceptamos si está bien redondeado.

    Devuelve True/False, o None si no aplica (no escribió decimales).
    """
    d = _decimales(texto)
    if d is None or correcta in (sp.oo, -sp.oo) or isinstance(correcta, NoExiste):
        return None
    try:
        diferencia = abs(float(sp.N(usuario)) - float(sp.N(correcta)))
    except (TypeError, ValueError):
        return None
    return d >= 2 and diferencia <= 0.51 * 10 ** (-d) + 1e-12


def _mismo_numero(u, c) -> bool:
    if u in (sp.oo, -sp.oo) or c in (sp.oo, -sp.oo):
        return u == c
    try:
        return son_equivalentes(sp.sympify(u), sp.sympify(c))
    except Exception:
        return False


def _diagnostico_comun(usuario, correcta, x, contexto="derivada"):
    """Detecta signo cambiado o un factor constante de diferencia."""
    try:
        if son_equivalentes(usuario, -correcta, [x]):
            return "Revisa los signos: tu resultado es exactamente el correcto con el signo cambiado."
        cociente = sp.simplify(usuario / correcta)
        if cociente.is_number and cociente not in (0, 1) and cociente.is_finite:
            if contexto == "integral":
                return (f"Tu resultado difiere del correcto en un factor constante (${a_latex(cociente)}$). "
                        "Revisa la división entre el nuevo exponente o la constante de la sustitución ($du$).")
            return (f"Tu resultado difiere del correcto en un factor constante (${a_latex(cociente)}$). "
                    "Revisa los coeficientes y los exponentes que bajaste.")
    except Exception:
        return None
    return None


class _DerivadorSinCadena(_Derivador):
    """Deriva «olvidando» multiplicar por la derivada interna (error típico)."""

    def _funcion(self, expr, nivel):
        f = expr.func
        from .derivadas import _TABLA

        return _TABLA[f][0](expr.args[0])

    def _potencia(self, expr, nivel):
        base, exponente = expr.args
        if base.has(self.x) and not exponente.has(self.x) and base != self.x:
            return exponente * base ** (exponente - 1)
        return super()._potencia(expr, nivel)


def _derivada_olvidando_cadena(f, x):
    try:
        resultado = _DerivadorSinCadena(x).d(f)
    except Exception:
        return None
    if son_equivalentes(resultado, sp.diff(f, x), [x]):
        return None  # en esta función no hay cadena que olvidar
    return resultado


def _producto_mal_aplicado(f, x):
    if isinstance(f, sp.Mul):
        c, resto = f.as_independent(x, as_Add=False)
        factores = [g for g in sp.Mul.make_args(resto)]
        if len(factores) == 2 and sp.fraction(resto)[1] == 1:
            return c * sp.diff(factores[0], x) * sp.diff(factores[1], x)
    return None


def _cociente_mal_aplicado(f, x):
    n, d = sp.fraction(f)
    if d.has(x) and n.has(x):
        dd = sp.diff(d, x)
        if dd != 0:
            return sp.diff(n, x) / dd
    return None


def _regla_principal_derivada(f, x) -> str:
    """Describe la regla que hay que usar primero (sin resolver)."""
    c, resto = f.as_independent(x, as_Add=False) if isinstance(f, sp.Mul) else (1, f)
    if isinstance(f, sp.Add):
        return "Es una suma: deriva cada término por separado y luego súmalos."
    if isinstance(resto, sp.Mul):
        n, d = sp.fraction(resto)
        if d.has(x) and n != 1:
            return "La función es un cociente: usa la regla del cociente $\\left(\\frac{f}{g}\\right)' = \\frac{f'g - fg'}{g^2}$."
        return "La función es un producto: usa la regla del producto $(fg)' = f'g + fg'$."
    if isinstance(resto, sp.Pow):
        base, exponente = resto.args
        if base.has(x) and exponente.has(x):
            return "La variable está en la base y en el exponente: usa derivación logarítmica."
        if base != x and base.has(x):
            return "Es una potencia de una función: usa la regla de la cadena $(u^n)' = n u^{n-1} u'$."
        if base == x:
            return "Usa la regla de la potencia $(x^n)' = n x^{n-1}$."
        return "Es una exponencial $a^u$: $(a^u)' = a^u \\ln a \\cdot u'$."
    if isinstance(resto, sp.Function) and resto.args and resto.args[0] != x:
        return "Hay una función compuesta: usa la regla de la cadena (deriva la de afuera y multiplica por la derivada de la de adentro)."
    return "Usa la tabla de derivadas básicas."


def _pista_primer_paso(sol: Solucion) -> str:
    if not sol.pasos:
        return "Repasa la teoría del tema y vuelve a intentarlo."
    p = sol.pasos[0]
    return f"Pista más concreta — primer paso: **{p.regla}**. {p.explicacion}"


def _pistas_metodo_integral(sol: Solucion) -> list[str]:
    pistas = []
    reglas = sol.reglas_usadas()
    if any(r.startswith("Sustitución (") for r in reglas):
        pistas.append("Prueba con una **sustitución** $u = g(x)$: busca una función cuya derivada también aparezca en el integrando.")
        paso = next(p for p in sol.pasos if p.regla.startswith("Sustitución ("))
        m = re.search(r"Elegimos \$(.+?)\$", paso.explicacion)
        if m:
            pistas.append(f"Pista más concreta: usa ${m.group(1)}$.")
    elif "Integración por partes" in reglas or "Integración por partes cíclica" in reglas:
        pistas.append("Prueba **integración por partes**: $\\int u\\,dv = uv - \\int v\\,du$. Elige $u$ con el orden LIATE.")
        paso = next(p for p in sol.pasos if p.regla.startswith("Integración por partes") or p.regla == "Por partes")
        m = re.search(r"Tomamos (\$u = .+?\$)", paso.explicacion) or re.search(r"(\$u = .+?\$)", paso.explicacion)
        if m:
            pistas.append(f"Pista más concreta: toma {m.group(1)}.")
    elif "Reescribir el integrando" in reglas:
        pistas.append("Antes de integrar, **reescribe** el integrando (desarrolla, usa una identidad o separa en fracciones).")
    elif "Linealidad (integral de una suma)" in reglas:
        pistas.append("Separa la integral en una suma de integrales más sencillas y usa la regla de la potencia en cada una.")
    elif "Regla de la potencia" in reglas:
        pistas.append("Usa la **regla de la potencia**: $\\int x^n\\,dx = \\frac{x^{n+1}}{n+1}$ (suma 1 al exponente y divide).")
    else:
        pistas.append("Busca en la tabla de integrales básicas una fórmula que encaje con el integrando.")
    return pistas


def _pistas_limite(sol: Solucion) -> list[str]:
    reglas = sol.reglas_usadas()
    pistas = []
    if reglas and reglas[0] == "Sustitución directa":
        pistas.append("Prueba primero sustituir directamente el valor en la función.")
        return pistas
    forma = next((p for p in sol.pasos if p.regla.startswith("Forma indeterminada")), None)
    if forma:
        m = re.search(r"\\;\\to\\;\s*(.+)$", forma.latex or "")
        texto_forma = f" ${m.group(1)}$" if m else ""
        pistas.append(f"Al sustituir aparece una forma indeterminada{texto_forma}. Hay que transformar la expresión antes.")
    sugerencias = {
        "Factorizar y simplificar": "Intenta **factorizar** numerador y denominador y cancelar el factor común.",
        "Racionalizar": "Hay una raíz: intenta **multiplicar por el conjugado**.",
        "Dividir entre la mayor potencia": "Divide numerador y denominador entre la **mayor potencia** de $x$.",
        "Regla de L'Hôpital": "Puedes usar **L'Hôpital**: deriva numerador y denominador por separado.",
        "Numerador ≠ 0, denominador → 0: límites laterales": "El denominador tiende a 0 y el numerador no: estudia los **límites laterales**.",
        "Numerador ≠ 0, denominador → 0": "El denominador tiende a 0 y el numerador no: el resultado es infinito; mira el **signo**.",
        "Polinomio en el infinito": "En un polinomio, en el infinito manda el **término de mayor grado**.",
    }
    for regla in reglas:
        if regla.startswith("Forma indeterminada $"):
            pistas.append("Con potencias indeterminadas usa logaritmos: $f^g = e^{g \\ln f}$.")
            break
    for regla in reglas:
        if regla in sugerencias:
            pistas.append(sugerencias[regla])
            break
    if not pistas:
        pistas.append("Analiza qué pasa con cada parte de la expresión cuando la variable se acerca al punto.")
    return pistas


def _sin_repetir(lista):
    vistos = []
    for elemento in lista:
        if elemento and elemento not in vistos:
            vistos.append(elemento)
    return vistos
