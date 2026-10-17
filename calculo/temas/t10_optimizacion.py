"""Tema 10: Optimización."""

import sympy as sp

from . import Tema
from ._util import L, entero, nuevo, paso, x


def _optimizar(funcion, intervalo):
    """Máximo de ``funcion`` en ``intervalo`` (abierto) usando derivada; todo con SymPy."""
    df = sp.diff(funcion, x)
    criticos = [c for c in sp.solve(df, x) if c.is_real and intervalo[0] < c < intervalo[1]]
    mejor = max(criticos, key=lambda c: funcion.subs(x, c))
    return df, criticos, mejor, sp.simplify(funcion.subs(x, mejor))


def suma_producto(rng):
    S = 2 * entero(rng, 5, 30)
    P = x * (S - x)
    df, criticos, mejor, valor = _optimizar(P, (0, S))
    pasos = [
        paso("Variables", f"Si un número es $x$, el otro es ${S} - x$ (suman ${S}$)."),
        paso("Función a maximizar", "", rf"P(x) = x({S} - x) = {L(sp.expand(P))}"),
        paso("Derivar e igualar a cero", "", rf"P'(x) = {L(df)} = 0 \;\Rightarrow\; x = {L(mejor)}"),
        paso("Comprobar que es máximo", "", rf"P''(x) = {L(sp.diff(P, x, 2))} < 0 \;\Rightarrow\; \text{{máximo}}"),
        paso("Producto máximo", "", rf"P({L(mejor)}) = {L(valor)}"),
    ]
    return nuevo(f"Dos números positivos suman ${S}$. ¿Cuál es el **mayor producto** posible entre ellos?", "numero", valor, pasos,
                 ["Llama $x$ a un número y escribe el otro en función de $x$.", "Maximiza $P(x) = x(S - x)$ derivando."])


def corral_rio(rng):
    P = 4 * entero(rng, 10, 80)
    # Se cercan 3 lados: 2x + y = P  ->  y = P - 2x ;  A = x (P - 2x)
    A = x * (P - 2 * x)
    df, criticos, mejor, valor = _optimizar(A, (0, sp.Rational(P, 2)))
    pasos = [
        paso("Dibujo", "Llamamos $x$ a los dos lados perpendiculares al río e $y$ al lado paralelo (el río no se cerca)."),
        paso("Restricción", f"Se usan ${P}$ m de cerca en tres lados.", rf"2x + y = {P} \;\Rightarrow\; y = {P} - 2x"),
        paso("Función a maximizar", "", rf"A(x) = x\,y = x({P} - 2x) = {L(sp.expand(A))}"),
        paso("Derivar e igualar a cero", "", rf"A'(x) = {L(df)} = 0 \;\Rightarrow\; x = {L(mejor)}"),
        paso("Comprobar máximo", "", rf"A''(x) = {L(sp.diff(A, x, 2))} < 0"),
        paso("Área máxima", "", rf"A({L(mejor)}) = {L(valor)}\ \text{{m}}^2"),
    ]
    return nuevo(f"Con ${P}$ m de cerca se quiere cercar un terreno rectangular junto a un río (el lado del río no se cerca). "
                 "¿Cuál es el **área máxima** (en m²)?", "numero", valor, pasos,
                 ["Escribe la restricción de la cerca: $2x + y = P$.", "Despeja $y$, sustitúyelo en el área y deriva."],
                 respuesta_latex=f"{L(valor)}\\ \\text{{m}}^2")


def caja_abierta(rng):
    lado = 6 * entero(rng, 1, 8)
    V = x * (lado - 2 * x) ** 2
    df, criticos, mejor, valor = _optimizar(V, (0, sp.Rational(lado, 2)))
    pasos = [
        paso("Modelo", f"Se cortan cuadrados de lado $x$ en las esquinas de una lámina de ${lado}\\times{lado}$ y se doblan los bordes. "
             f"La base mide $({lado} - 2x)$ por lado y la altura es $x$, con $0 < x < {lado // 2}$."),
        paso("Volumen", "", rf"V(x) = x({lado} - 2x)^2"),
        paso("Derivar e igualar a cero", "", rf"V'(x) = {L(sp.factor(df))} = 0 \;\Rightarrow\; x = " +
             r" \text{ o } x = ".join(L(c) for c in sorted(sp.solve(df, x)))),
        paso("Elegir la solución válida", f"Solo sirve la que está en $(0, {lado // 2})$ y no anula el volumen.", rf"x = {L(mejor)}"),
    ]
    return nuevo(f"De una lámina cuadrada de ${lado}$ cm de lado se cortan cuadrados iguales en las esquinas para hacer una caja "
                 "sin tapa. ¿De qué lado $x$ (en cm) deben ser los cuadrados para que el **volumen sea máximo**?",
                 "numero", mejor, pasos, ["El volumen es $V(x) = x(L - 2x)^2$.", "Descarta la solución que da volumen cero."],
                 respuesta_latex=f"x = {L(mejor)}\\ \\text{{cm}}")


TEMA = Tema(
    id="optimizacion",
    nombre="Optimización",
    orden=10,
    descripcion="Plantear y resolver problemas de máximos y mínimos con derivadas.",
    generadores={
        "basico": [suma_producto],
        "medio": [corral_rio],
        "parcial": [caja_abierta, corral_rio],
    },
    ejemplos=[("basico", 1), ("medio", 1), ("parcial", 1)],
)
