"""Página 3b: plan de estudio de 4 semanas."""

from __future__ import annotations

import streamlit as st

from calculo.plan import CONSEJOS, PLAN, SEMANAS, dias_de_semana
from calculo.progreso import Progreso
from calculo.temas import TEMAS
from interfaz.navegacion import ir_a


def _formato_minutos(minutos: int) -> str:
    h, m = divmod(minutos, 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"


def pagina():
    st.title("🗓️ Plan de estudio: 4 semanas")
    st.write("Pensado para estudiar **por la mañana, entre 1 y 2 horas al día**. Marca cada día cuando lo termines.")
    progreso = Progreso()
    hechos = sum(progreso.dia_hecho(d.numero) for d in PLAN)
    st.progress(hechos / len(PLAN), text=f"{hechos} de {len(PLAN)} días completados")

    siguiente = next((d for d in PLAN if not progreso.dia_hecho(d.numero)), None)
    if siguiente:
        st.info(f"**Hoy toca — Día {siguiente.numero}:** {siguiente.titulo} ({_formato_minutos(siguiente.minutos)})")
    else:
        st.success("¡Completaste el plan! Sigue con simulacros y repasa tus puntos débiles.")

    with st.expander("Consejos para seguir el plan"):
        for c in CONSEJOS:
            st.markdown(f"- {c}")

    pestañas = st.tabs([f"Semana {s}" for s in SEMANAS])
    for (semana, titulo), pestaña in zip(SEMANAS.items(), pestañas):
        with pestaña:
            st.markdown(f"**{titulo}**")
            for dia in dias_de_semana(semana):
                marca = "✅" if progreso.dia_hecho(dia.numero) else ("📝" if dia.simulacro else "📘")
                with st.expander(f"{marca} Día {dia.numero}: {dia.titulo} — {_formato_minutos(dia.minutos)}"):
                    if dia.temas:
                        st.markdown("**Temas:** " + ", ".join(TEMAS[t].nombre for t in dia.temas if t in TEMAS))
                    for minutos, actividad in dia.actividades:
                        st.markdown(f"- **{minutos} min** — {actividad}")
                    if dia.nota:
                        st.caption(dia.nota)
                    c1, c2 = st.columns(2)
                    hecho = c1.checkbox("Día terminado", value=progreso.dia_hecho(dia.numero), key=f"dia_{dia.numero}")
                    if hecho != progreso.dia_hecho(dia.numero):
                        progreso.marcar_dia(dia.numero, hecho)
                        st.rerun()
                    if dia.simulacro:
                        if c2.button("Ir al simulacro", key=f"sim_{dia.numero}"):
                            st.session_state["temas_simulacro"] = dia.temas
                            ir_a("simulacro")
                    elif dia.temas:
                        if c2.button("Estudiar el tema", key=f"est_{dia.numero}"):
                            ir_a("estudio", dia.temas[0])
