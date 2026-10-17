"""Página 3a: modo estudio (teoría, ejemplos resueltos y errores comunes)."""

from __future__ import annotations

import streamlit as st

from calculo.ejercicios import NOMBRE_DIFICULTAD
from calculo.temas import TEMAS, generar
from interfaz.componentes import mostrar_solucion_ejercicio
from interfaz.navegacion import ir_a


@st.cache_resource(show_spinner=False)
def _ejemplo(tema_id: str, dificultad: str, semilla: int):
    """Los ejemplos resueltos se generan con semilla fija y se resuelven con SymPy (se guardan en caché)."""
    return generar(tema_id, dificultad, semilla)


def pagina():
    st.title("📖 Modo estudio")
    st.write("Resumen corto de teoría, ejemplos resueltos paso a paso y los errores más comunes de cada tema.")
    nombres = {f"{t.orden}. {t.nombre}": t.id for t in TEMAS.values()}
    lista = list(nombres)
    sugerido = st.session_state.get("tema_sugerido")
    indice = next((i for i, n in enumerate(lista) if nombres[n] == sugerido), 0)
    elegido = st.selectbox("Tema", lista, index=indice)
    tema = TEMAS[nombres[elegido]]

    st.caption(tema.descripcion)
    st.markdown(tema.teoria)

    st.markdown("### Ejemplos resueltos")
    st.caption("Generados y resueltos con SymPy. Intenta resolverlos tú primero y luego abre la solución.")
    for i, (dificultad, semilla) in enumerate(tema.ejemplos, 1):
        ej = _ejemplo(tema.id, dificultad, semilla)
        st.markdown(f"**Ejemplo {i}** ({NOMBRE_DIFICULTAD[dificultad]})")
        st.markdown(ej.enunciado)
        with st.expander("Ver solución"):
            mostrar_solucion_ejercicio(ej)

    st.divider()
    if st.button(f"✏️ Practicar «{tema.nombre}»", type="primary"):
        ir_a("ejercicios", tema.id)
