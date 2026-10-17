"""Página 3c: registro de progreso, puntos débiles y recomendaciones."""

from __future__ import annotations

import streamlit as st

from calculo.progreso import MIN_INTENTOS, UMBRAL_DEBIL, Progreso
from calculo.temas import TEMAS
from interfaz.navegacion import ir_a


def pagina():
    st.title("📊 Mi progreso")
    progreso = Progreso()
    resumen = progreso.resumen_por_tema()
    total = sum(r["total"] for r in resumen.values())
    aciertos = sum(r["aciertos"] for r in resumen.values())

    c1, c2, c3 = st.columns(3)
    c1.metric("Ejercicios hechos", total)
    c2.metric("Aciertos", f"{aciertos / total:.0%}" if total else "—")
    c3.metric("Simulacros", len(progreso.datos["simulacros"]))

    st.markdown("### ¿Qué repaso primero?")
    for i, (tema_id, motivo) in enumerate(progreso.recomendaciones(list(TEMAS), cuantas=3), 1):
        nombre = TEMAS[tema_id].nombre if tema_id in TEMAS else tema_id
        col_a, col_b, col_c = st.columns([5, 1.3, 1.3])
        col_a.markdown(f"**{i}. {nombre}** — {motivo}")
        if col_b.button("Estudiar", key=f"rec_est_{tema_id}"):
            ir_a("estudio", tema_id)
        if col_c.button("Practicar", key=f"rec_pra_{tema_id}"):
            ir_a("ejercicios", tema_id)

    st.markdown("### Aciertos y fallos por tema")
    st.caption(f"Un tema se marca como **débil** si tienes al menos {MIN_INTENTOS} intentos y menos de "
               f"{UMBRAL_DEBIL:.0%} de aciertos en los últimos.")
    filas = []
    for tema in TEMAS.values():
        r = resumen.get(tema.id)
        if r is None:
            filas.append({"Tema": tema.nombre, "Aciertos": 0, "Fallos": 0, "% total": None, "% reciente": None, "Estado": "Sin practicar"})
            continue
        if r["total"] < MIN_INTENTOS:
            estado = "Pocos intentos"
        elif r["reciente"] < UMBRAL_DEBIL:
            estado = "⚠️ Débil"
        else:
            estado = "✅ Bien"
        filas.append({"Tema": tema.nombre, "Aciertos": r["aciertos"], "Fallos": r["fallos"],
                      "% total": 100 * r["porcentaje"], "% reciente": 100 * r["reciente"], "Estado": estado})
    st.dataframe(
        filas, hide_index=True, width="stretch",
        column_config={
            "% total": st.column_config.ProgressColumn("% total", min_value=0, max_value=100, format="%.0f%%"),
            "% reciente": st.column_config.ProgressColumn("% reciente", min_value=0, max_value=100, format="%.0f%%"),
        },
    )

    if progreso.datos["simulacros"]:
        st.markdown("### Simulacros")
        for s in reversed(progreso.datos["simulacros"][-10:]):
            st.markdown(f"- {s['fecha'].replace('T', ' ')}: **{s['puntaje']:.0f} / {s['total']:.0f}** puntos")

    with st.expander("Copia de seguridad y reinicio"):
        st.caption(f"El progreso se guarda en `{progreso.ruta}`.")
        st.download_button("Descargar mi progreso (.json)", progreso.exportar(), file_name="progreso_calculo.json",
                           mime="application/json")
        archivo = st.file_uploader("Restaurar desde un archivo .json", type="json")
        if archivo is not None and st.button("Restaurar"):
            try:
                progreso.importar(archivo.getvalue().decode("utf-8"))
                st.success("Progreso restaurado.")
                st.rerun()
            except (ValueError, UnicodeDecodeError) as error:
                st.error(f"No pude leer el archivo: {error}")
        confirmar = st.checkbox("Quiero borrar todo mi progreso")
        if st.button("Borrar progreso", disabled=not confirmar):
            progreso.reiniciar()
            st.rerun()
