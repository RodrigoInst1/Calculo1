"""Página 2: generador de ejercicios por tema y dificultad."""

from __future__ import annotations

import random

import streamlit as st

from calculo.ejercicios import DIFICULTADES, NOMBRE_DIFICULTAD
from calculo.temas import TEMAS, generar
from interfaz.componentes import ayuda_escritura, mostrar_enunciado, mostrar_solucion_ejercicio, mostrar_veredicto


def _nuevo(tema_id: str, dificultad: str) -> None:
    st.session_state["ej_actual"] = generar(tema_id, dificultad, random.randrange(10**6))
    st.session_state["ej_veredicto"] = None
    st.session_state["ej_ver_solucion"] = False
    st.session_state.pop("pistas_ejercicio", None)
    st.session_state["ej_respuesta"] = ""


def pagina():
    st.title("✏️ Ejercicios")
    st.write("Ejercicios **originales**, generados al azar por tema y dificultad. La solución queda oculta hasta que la pidas.")

    nombres = {t.nombre: t.id for t in TEMAS.values()}
    preseleccion = st.session_state.get("tema_sugerido")
    lista = list(nombres)
    indice = lista.index(TEMAS[preseleccion].nombre) if preseleccion in TEMAS else 0
    c1, c2 = st.columns([3, 2])
    tema_nombre = c1.selectbox("Tema", lista, index=indice)
    dificultad = c2.selectbox("Dificultad", DIFICULTADES, format_func=lambda d: NOMBRE_DIFICULTAD[d])
    tema_id = nombres[tema_nombre]

    actual = st.session_state.get("ej_actual")
    if st.button("🎲 Nuevo ejercicio", type="primary") or actual is None or \
            (actual.tema, actual.dificultad) != (tema_id, dificultad):
        _nuevo(tema_id, dificultad)
    ej = st.session_state["ej_actual"]

    st.divider()
    mostrar_enunciado(ej)
    with st.form("form_respuesta", clear_on_submit=False):
        respuesta = st.text_input("Tu respuesta", key="ej_respuesta", help=ej.ayuda_formato)
        st.caption(ej.ayuda_formato)
        enviado = st.form_submit_button("Comprobar")
    if enviado:
        st.session_state.pop("pistas_ejercicio", None)
        veredicto = ej.verificar(respuesta)
        st.session_state["ej_veredicto"] = veredicto
        registrar = st.session_state.get("registrar_intento")
        if registrar is not None and veredicto.mensaje and "No pude leer" not in veredicto.mensaje:
            registrar(ej, veredicto.correcto)
    if st.session_state.get("ej_veredicto") is not None:
        mostrar_veredicto(st.session_state["ej_veredicto"], "ejercicio")

    if st.button("👀 Ver la solución completa"):
        st.session_state["ej_ver_solucion"] = True
    if st.session_state.get("ej_ver_solucion"):
        mostrar_solucion_ejercicio(ej)
    ayuda_escritura()
