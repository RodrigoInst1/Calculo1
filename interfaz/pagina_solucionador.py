"""Página 1: solucionador con pasos y modo verificar."""

from __future__ import annotations

import streamlit as st

from calculo.interprete import ErrorEntrada, interpretar
from calculo.solucionador import interpretar_problema, resolver
from calculo.verificador import verificar
from interfaz.componentes import ayuda_escritura, mostrar_solucion, mostrar_veredicto

EJEMPLOS = [
    "lim x->2 (x^2-4)/(x-2)",
    "lim x->0 sin(3x)/x",
    "lim x->oo (3x^2+1)/(2x^2-x)",
    "d/dx x^2 sin(x)",
    "derivada de e^(x^2) / (x+1)",
    "integral x e^x dx",
    "integral x cos(x^2) dx",
    "integral de 0 a 1 x^2 dx",
]


def _leer_formulario():
    """Formulario guiado: el estudiante elige el tipo y llena los campos."""
    tipo = st.selectbox("Tipo de problema", ["Límite", "Derivada", "Integral indefinida", "Integral definida"])
    var = st.text_input("Variable", value="x", max_chars=1)
    expr_txt = st.text_input("Función", placeholder="por ejemplo: (x^2-4)/(x-2)")
    datos = {}
    if tipo == "Límite":
        c1, c2 = st.columns(2)
        punto = c1.text_input("Tiende a", value="0", help="Un número, pi, oo o -oo")
        lado = c2.selectbox("Dirección", ["Ambos lados", "Por la derecha (+)", "Por la izquierda (−)"])
        datos["punto_txt"] = punto
        datos["direccion"] = {"Ambos lados": "+-", "Por la derecha (+)": "+", "Por la izquierda (−)": "-"}[lado]
    elif tipo == "Derivada":
        datos["orden"] = st.number_input("Orden de la derivada", 1, 5, 1)
    elif tipo == "Integral definida":
        c1, c2 = st.columns(2)
        datos["a_txt"] = c1.text_input("Desde (a)", value="0")
        datos["b_txt"] = c2.text_input("Hasta (b)", value="1")
    return tipo, var, expr_txt, datos


def _armar_problema(tipo, var, expr_txt, extra):
    import sympy as sp

    if not var or not var.isalpha():
        raise ErrorEntrada("La variable debe ser una letra, por ejemplo x o t.")
    x = sp.Symbol(var)
    expr = interpretar(expr_txt)
    if tipo == "Límite":
        punto = interpretar(extra["punto_txt"])
        if punto.free_symbols:
            raise ErrorEntrada("El punto del límite debe ser un número (o oo / -oo).")
        return "limite", {"expr": expr, "variable": x, "punto": punto, "direccion": extra["direccion"]}
    if tipo == "Derivada":
        return "derivada", {"expr": expr, "variable": x, "orden": int(extra["orden"])}
    if tipo == "Integral indefinida":
        return "integral", {"expr": expr, "variable": x}
    a, b = interpretar(extra["a_txt"]), interpretar(extra["b_txt"])
    if a.free_symbols or b.free_symbols:
        raise ErrorEntrada("Los límites de integración deben ser números.")
    return "integral_definida", {"expr": expr, "variable": x, "a": a, "b": b}


def pagina():
    st.title("🧮 Solucionador y verificador")
    st.write(
        "Escribe un límite, una derivada o una integral. Te muestro el resultado y **cada paso explicado**, "
        "o, en modo verificar, te digo si tu respuesta es correcta y te doy pistas sin revelar la solución."
    )
    modo = st.radio("Modo", ["Resolver con pasos", "Verificar mi respuesta"], horizontal=True)
    forma = st.radio("¿Cómo quieres escribir el problema?", ["En texto", "Con formulario"], horizontal=True)

    problema = None
    texto = ""
    if forma == "En texto":
        ejemplo = st.selectbox("Ejemplos (opcional)", ["—"] + EJEMPLOS)
        texto = st.text_input(
            "Problema",
            value="" if ejemplo == "—" else ejemplo,
            placeholder="lim x->0 sin(x)/x   ·   d/dx x^2 sin x   ·   integral de 0 a 1 x^2 dx",
        )
    else:
        tipo_f, var_f, expr_f, extra_f = _leer_formulario()
    ayuda_escritura()

    respuesta = ""
    if modo == "Verificar mi respuesta":
        respuesta = st.text_input(
            "Tu respuesta",
            placeholder="Ej.: 2x cos(x^2)  ·  x e^x - e^x + C  ·  1/3  ·  oo  ·  no existe",
        )

    boton = st.button("Resolver" if modo == "Resolver con pasos" else "Verificar", type="primary")
    if not boton and "ultima_solucion" not in st.session_state:
        return

    if boton:
        st.session_state.pop("pistas_verificador", None)
        try:
            if forma == "En texto":
                tipo, datos = interpretar_problema(texto)
            else:
                tipo, datos = _armar_problema(tipo_f, var_f, expr_f, extra_f)
            with st.spinner("Calculando con SymPy..."):
                problema = resolver(tipo, datos)
        except ErrorEntrada as error:
            st.error(str(error))
            st.session_state.pop("ultima_solucion", None)
            return
        st.session_state["ultima_solucion"] = problema
        st.session_state["ultima_respuesta"] = respuesta
        st.session_state["ultimo_modo"] = modo
    problema = st.session_state["ultima_solucion"]
    modo_guardado = st.session_state.get("ultimo_modo", modo)

    st.markdown("### Problema")
    st.latex(problema.enunciado_latex)
    if modo_guardado == "Resolver con pasos":
        mostrar_solucion(problema)
        return

    veredicto = verificar(problema, st.session_state.get("ultima_respuesta", ""))
    mostrar_veredicto(veredicto, "verificador")
    if not veredicto.correcto:
        with st.expander("Me rindo: ver la solución completa"):
            mostrar_solucion(problema)
