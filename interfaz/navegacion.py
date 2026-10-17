"""Acceso a las páginas de la app para poder saltar entre ellas."""

from __future__ import annotations

import streamlit as st

PAGINAS: dict[str, "st.Page"] = {}  # lo llena app.py


def ir_a(nombre: str, tema_id: str | None = None) -> None:
    """Cambia de página (opcionalmente preseleccionando un tema)."""
    if tema_id is not None:
        st.session_state["tema_sugerido"] = tema_id
    if nombre in PAGINAS:
        st.switch_page(PAGINAS[nombre])
