"""Herramienta de estudio de Cálculo I — punto de entrada de Streamlit.

Ejecutar con:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="Cálculo I — estudio", page_icon="📘", layout="centered")

from interfaz import (  # noqa: E402  (después de set_page_config)
    pagina_ejercicios,
    pagina_estudio,
    pagina_plan,
    pagina_progreso,
    pagina_solucionador,
)
from interfaz.navegacion import PAGINAS, ir_a  # noqa: E402


def inicio():
    st.title("📘 Cálculo I: aprende, practica y verifica")
    st.markdown(
        """
Esta herramienta te acompaña para **aprobar Cálculo I** empezando desde las bases.

| Sección | Para qué sirve |
|---|---|
| 🧮 **Solucionador** | Escribe un límite, derivada o integral y mira cada paso explicado. En modo *verificar* revisa tu respuesta y te da pistas. |
| ✏️ **Ejercicios** | Problemas originales por tema y dificultad (básico, medio, parcial) con la solución oculta. |
| 📖 **Estudio** | Teoría corta, ejemplos resueltos y errores comunes de cada tema. |
| 🗓️ **Plan** | Plan de 4 semanas, 1–2 h por la mañana. |
| 📊 **Progreso** | Tus aciertos y fallos por tema, y qué repasar primero. |

Todas las respuestas matemáticas las calcula y comprueba **SymPy**: nada se inventa.
"""
    )
    c1, c2 = st.columns(2)
    if c1.button("🗓️ Ver qué toca hoy", width="stretch"):
        ir_a("plan")
    if c2.button("✏️ Practicar ahora", width="stretch"):
        ir_a("ejercicios")


PAGINAS.update({
    "inicio": st.Page(inicio, title="Inicio", icon="🏠", default=True),
    "solucionador": st.Page(pagina_solucionador.pagina, title="Solucionador", icon="🧮", url_path="solucionador"),
    "ejercicios": st.Page(pagina_ejercicios.pagina, title="Ejercicios", icon="✏️", url_path="ejercicios"),
    "estudio": st.Page(pagina_estudio.pagina, title="Estudio", icon="📖", url_path="estudio"),
    "plan": st.Page(pagina_plan.pagina, title="Plan de 4 semanas", icon="🗓️", url_path="plan"),
    "progreso": st.Page(pagina_progreso.pagina, title="Progreso", icon="📊", url_path="progreso"),
})

st.navigation(list(PAGINAS.values())).run()
