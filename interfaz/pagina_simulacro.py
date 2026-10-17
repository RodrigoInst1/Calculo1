"""Página 4: simulacro de parcial con tiempo límite y corrección final."""

from __future__ import annotations

import time

import streamlit as st

from calculo.ejercicios import NOMBRE_DIFICULTAD
from calculo.progreso import Progreso
from calculo.simulacro import MINUTOS, NOTA_APROBACION, crear_simulacro
from calculo.temas import TEMAS
from interfaz.componentes import mostrar_solucion_ejercicio, mostrar_veredicto


def _reloj(segundos: float) -> str:
    m, s = divmod(int(segundos), 60)
    return f"{m:02d}:{s:02d}"


def _configurar():
    st.write("Un examen de práctica de **5 a 6 ejercicios** que mezcla temas, con **tiempo límite**. "
             "Al final se corrige todo y obtienes tu puntaje sobre 100.")
    nombres = {t.nombre: t.id for t in TEMAS.values()}
    sugeridos = st.session_state.get("temas_simulacro") or list(TEMAS)
    por_defecto = [n for n, i in nombres.items() if i in sugeridos]
    elegidos = st.multiselect("Temas que entran", list(nombres), default=por_defecto)
    c1, c2 = st.columns(2)
    cuantos = c1.radio("Número de ejercicios", [5, 6], index=1, horizontal=True)
    sugerido = round(cuantos * (MINUTOS["medio"] + MINUTOS["parcial"]) / 2)
    minutos = c2.number_input("Tiempo límite (minutos)", min_value=10, max_value=180, value=sugerido, step=5)
    nota = st.number_input("Nota mínima para aprobar (ajústala a tu universidad)", 1, 100, NOTA_APROBACION)
    st.caption("Consejo: hazlo con papel y lápiz, sin mirar apuntes, como si fuera el parcial real.")
    if st.button("▶️ Comenzar simulacro", type="primary", disabled=not elegidos):
        st.session_state["simulacro"] = crear_simulacro([nombres[n] for n in elegidos], cuantos, int(minutos))
        st.session_state["simulacro_nota"] = nota
        st.session_state.pop("simulacro_correccion", None)
        for i in range(6):
            st.session_state.pop(f"sim_resp_{i}", None)
        st.rerun()


@st.fragment(run_every=1)
def _cuenta_regresiva():
    """Se actualiza cada segundo; al llegar a 0 entrega el examen automáticamente."""
    sim = st.session_state.get("simulacro")
    if sim is None or "simulacro_correccion" in st.session_state:
        return
    restante = sim.segundos_restantes()
    if restante <= 0:
        st.session_state["simulacro_entregar"] = True
        st.rerun(scope="app")
    texto = f"⏱️ Tiempo restante: **{_reloj(restante)}**"
    if restante < 300:
        st.warning(texto + " — ¡quedan menos de 5 minutos!")
    else:
        st.info(texto)


def _corregir(sim):
    respuestas = [st.session_state.get(f"sim_resp_{i}", "") for i in range(len(sim.ejercicios))]
    correccion = sim.corregir(respuestas)
    st.session_state["simulacro_correccion"] = correccion
    Progreso().registrar_simulacro(
        correccion.puntaje, correccion.total,
        [{"tema": r.ejercicio.tema, "dificultad": r.ejercicio.dificultad, "correcto": r.veredicto.correcto,
          "puntos": r.puntos} for r in correccion.detalle],
    )


def _examen(sim):
    _cuenta_regresiva()
    st.caption(f"Duración: {sim.minutos} min · Empezó a las {time.strftime('%H:%M', time.localtime(sim.inicio))}. "
               "Escribe cada respuesta y pulsa Enter; al terminar pulsa «Entregar».")
    for i, (ej, puntos) in enumerate(zip(sim.ejercicios, sim.puntos)):
        st.markdown(f"#### Ejercicio {i + 1} · {puntos:g} puntos")
        st.caption(f"{TEMAS[ej.tema].nombre} · {NOMBRE_DIFICULTAD[ej.dificultad]}")
        st.markdown(ej.enunciado)
        st.text_input("Respuesta", key=f"sim_resp_{i}", help=ej.ayuda_formato, placeholder=ej.ayuda_formato)
    st.divider()
    if st.button("📤 Entregar y corregir", type="primary"):
        st.session_state["simulacro_entregar"] = True
        st.rerun()


def _resultados(correccion, nota_minima):
    aprobado = correccion.aprobado(nota_minima)
    st.markdown(f"## Puntaje: {correccion.puntaje:g} / {correccion.total:g}")
    st.progress(min(1.0, correccion.puntaje / correccion.total))
    if aprobado:
        st.success(f"¡Aprobado! (nota mínima {nota_minima}). Tiempo usado: {correccion.minutos_usados} min.")
    else:
        st.error(f"No aprobado esta vez (nota mínima {nota_minima}). Revisa los ejercicios fallados abajo.")
    if correccion.fuera_de_tiempo:
        st.warning("Se entregó después del tiempo límite.")
    st.caption("El resultado se guardó en tu progreso (cuenta para detectar puntos débiles).")

    for i, r in enumerate(correccion.detalle, 1):
        icono = "✅" if r.veredicto.correcto else "❌"
        with st.expander(f"{icono} Ejercicio {i} — {TEMAS[r.ejercicio.tema].nombre}: {r.puntos:g}/{r.puntos_maximos:g}",
                         expanded=not r.veredicto.correcto):
            st.markdown(r.ejercicio.enunciado)
            st.markdown(f"**Tu respuesta:** `{r.respuesta or '(vacía)'}`")
            mostrar_veredicto(r.veredicto, f"sim_{i}", mostrar_todas=True)
            if not r.veredicto.correcto:
                st.markdown("---")
                mostrar_solucion_ejercicio(r.ejercicio)

    fallados = sorted({r.ejercicio.tema for r in correccion.detalle if not r.veredicto.correcto})
    if fallados:
        st.info("Para repasar: " + ", ".join(TEMAS[t].nombre for t in fallados))
    if st.button("🔁 Hacer otro simulacro"):
        for clave in ("simulacro", "simulacro_correccion", "simulacro_entregar"):
            st.session_state.pop(clave, None)
        st.rerun()


def pagina():
    st.title("📝 Simulacro de parcial")
    sim = st.session_state.get("simulacro")
    if sim is None:
        _configurar()
        return
    if st.session_state.pop("simulacro_entregar", False) and "simulacro_correccion" not in st.session_state:
        _corregir(sim)
    correccion = st.session_state.get("simulacro_correccion")
    if correccion is None:
        _examen(sim)
    else:
        _resultados(correccion, st.session_state.get("simulacro_nota", NOTA_APROBACION))
