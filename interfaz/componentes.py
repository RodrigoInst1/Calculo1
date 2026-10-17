"""Componentes visuales reutilizables (mostrar pasos, veredictos, etc.)."""

from __future__ import annotations

import streamlit as st

from calculo.ejercicios import NOMBRE_DIFICULTAD, Ejercicio
from calculo.pasos import Solucion
from calculo.verificador import Veredicto


def mostrar_pasos(solucion, titulo: str = "Procedimiento paso a paso") -> None:
    """Muestra los pasos con sangría según el nivel y la regla en negrita.

    ``solucion`` puede ser una ``Solucion`` o directamente una lista de pasos.
    """
    pasos = solucion.pasos if hasattr(solucion, "pasos") else solucion
    st.markdown(f"#### {titulo}")
    numero = 0
    for paso in pasos:
        numero += 1
        sangria = "&nbsp;" * 6 * paso.nivel
        marca = "↳ " if paso.nivel else ""
        texto = f"{sangria}{marca}**{numero}. {paso.regla}**"
        if paso.explicacion:
            texto += f" — {paso.explicacion}"
        st.markdown(texto, unsafe_allow_html=True)
        if paso.latex:
            if paso.nivel:
                columnas = st.columns([min(paso.nivel, 3), 12])
                with columnas[1]:
                    st.latex(paso.latex)
            else:
                st.latex(paso.latex)


def mostrar_resultado(solucion: Solucion) -> None:
    st.success("Resultado (calculado y verificado con SymPy):")
    st.latex(solucion.resultado_latex)
    for aviso in solucion.advertencias:
        st.warning(aviso)


def mostrar_solucion(solucion: Solucion) -> None:
    mostrar_resultado(solucion)
    mostrar_pasos(solucion)
    reglas = [r for r in solucion.reglas_usadas() if r not in ("Simplificamos", "Juntamos", "Juntamos los términos")]
    if reglas:
        st.caption("Reglas usadas: " + " · ".join(reglas))


def mostrar_veredicto(veredicto: Veredicto, clave: str, mostrar_todas: bool = False) -> None:
    """Muestra si la respuesta es correcta; si no, pistas de a una."""
    if veredicto.interpretado_latex:
        st.caption("Entendí tu respuesta como:")
        st.latex(veredicto.interpretado_latex)
    if veredicto.correcto:
        st.success(veredicto.mensaje)
        return
    st.error(veredicto.mensaje)
    if not veredicto.pistas:
        return
    if mostrar_todas:
        for i, pista in enumerate(veredicto.pistas, 1):
            st.info(f"Pista {i}: {pista}")
        return
    # Pistas graduales: se revelan una por una.
    estado = f"pistas_{clave}"
    cuantas = st.session_state.get(estado, 1)
    for i, pista in enumerate(veredicto.pistas[:cuantas], 1):
        st.info(f"Pista {i}: {pista}")
    if cuantas < len(veredicto.pistas):
        if st.button("Quiero otra pista", key=f"boton_{estado}"):
            st.session_state[estado] = cuantas + 1
            st.rerun()


def ayuda_escritura() -> None:
    with st.expander("¿Cómo escribo las expresiones?"):
        st.markdown(
            """
| Quiero escribir | Escribo |
|---|---|
| $x^2$ | `x^2` |
| $3x$ | `3x` o `3*x` |
| $\\sin x$, $\\cos x$, $\\tan x$ | `sin(x)`, `sen x`, `cos(x)`, `tan(x)` o `tg(x)` |
| $\\sin^2 x$ | `sin^2(x)` o `sin(x)^2` |
| $e^{2x}$ | `e^(2x)` o `exp(2x)` |
| $\\ln x$ | `ln(x)` (también `log(x)`, que es logaritmo natural) |
| $\\sqrt{x+1}$ | `sqrt(x+1)` o `raiz(x+1)` |
| $\\arctan x$ | `arctan(x)` o `atan(x)` |
| $\\lvert x \\rvert$ | `|x|` o `abs(x)` |
| $\\pi$, $\\infty$ | `pi`, `oo` (o `infinito`) |
| $\\frac{x+1}{x-1}$ | `(x+1)/(x-1)` ← ¡usa paréntesis! |
"""
        )


def mostrar_enunciado(ej: Ejercicio) -> None:
    st.markdown(f"**{NOMBRE_DIFICULTAD.get(ej.dificultad, ej.dificultad)}** · `{ej.id}`")
    st.markdown(ej.enunciado)


def mostrar_solucion_ejercicio(ej: Ejercicio) -> None:
    """Respuesta correcta y pasos (todo calculado con SymPy)."""
    if ej.solucion is not None:
        mostrar_solucion(ej.solucion)
        return
    st.success("Respuesta correcta (calculada con SymPy):")
    st.latex(ej.respuesta_latex)
    mostrar_pasos(ej.pasos)
