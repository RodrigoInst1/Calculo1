"""Herramienta de estudio de Cálculo I — punto de entrada de Streamlit.

Ejecutar con:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="Cálculo I — estudio", page_icon="📘", layout="centered")

from interfaz import pagina_ejercicios, pagina_solucionador  # noqa: E402  (después de set_page_config)


def inicio():
    st.title("📘 Cálculo I: aprende, practica y verifica")
    st.markdown(
        """
Bienvenido. Esta herramienta te acompaña para **aprobar Cálculo I** empezando desde las bases.

- **🧮 Solucionador**: escribe un límite, derivada o integral y mira cada paso explicado.
  En modo *verificar* te dice si tu respuesta está bien y te da pistas.
- **✏️ Ejercicios**: problemas originales por tema y dificultad (básico, medio, parcial),
  con la solución oculta hasta que la pidas.

Todas las respuestas matemáticas las calcula y comprueba **SymPy**: nada se inventa.
"""
    )


paginas = [
    st.Page(inicio, title="Inicio", icon="🏠", default=True),
    st.Page(pagina_solucionador.pagina, title="Solucionador", icon="🧮", url_path="solucionador"),
    st.Page(pagina_ejercicios.pagina, title="Ejercicios", icon="✏️", url_path="ejercicios"),
]

st.navigation(paginas).run()
