"""Registro de progreso: aciertos y fallos por tema, puntos débiles y qué repasar.

Se guarda en un archivo JSON (por defecto ``datos/progreso.json``; se puede
cambiar con la variable de entorno ``CALCULO_PROGRESO``).
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

RUTA_POR_DEFECTO = Path(__file__).resolve().parent.parent / "datos" / "progreso.json"
UMBRAL_DEBIL = 0.7  # menos de 70 % de aciertos = punto débil
MIN_INTENTOS = 3  # intentos mínimos para juzgar un tema
VENTANA_RECIENTE = 10  # se miran los últimos intentos (lo reciente pesa más)


def _vacio() -> dict:
    return {"intentos": [], "plan_completado": [], "simulacros": []}


class Progreso:
    def __init__(self, ruta: str | Path | None = None):
        self.ruta = Path(ruta or os.environ.get("CALCULO_PROGRESO") or RUTA_POR_DEFECTO)
        self.datos = self._cargar()

    # ------------------------------------------------------------ archivo
    def _cargar(self) -> dict:
        try:
            datos = json.loads(self.ruta.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return _vacio()
        base = _vacio()
        base.update({k: v for k, v in datos.items() if k in base and isinstance(v, list)})
        return base

    def guardar(self) -> None:
        """Escritura atómica: primero a un archivo temporal y luego se reemplaza."""
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        fd, temporal = tempfile.mkstemp(dir=self.ruta.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(self.datos, f, ensure_ascii=False, indent=1)
        os.replace(temporal, self.ruta)

    def exportar(self) -> str:
        return json.dumps(self.datos, ensure_ascii=False, indent=1)

    def importar(self, texto: str) -> None:
        datos = json.loads(texto)
        if not isinstance(datos, dict) or not isinstance(datos.get("intentos", []), list):
            raise ValueError("El archivo no tiene el formato de progreso esperado.")
        nuevo = _vacio()
        nuevo.update({k: v for k, v in datos.items() if k in nuevo and isinstance(v, list)})
        self.datos = nuevo
        self.guardar()

    def reiniciar(self) -> None:
        self.datos = _vacio()
        self.guardar()

    # ----------------------------------------------------------- registro
    def registrar(self, tema: str, dificultad: str, correcto: bool, origen: str = "ejercicio") -> None:
        self.datos["intentos"].append({
            "tema": tema, "dificultad": dificultad, "correcto": bool(correcto),
            "origen": origen, "fecha": datetime.now().isoformat(timespec="seconds"),
        })
        self.guardar()

    def registrar_simulacro(self, puntaje: float, total: float, detalle: list[dict]) -> None:
        self.datos["simulacros"].append({
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "puntaje": puntaje, "total": total, "detalle": detalle,
        })
        for item in detalle:
            self.datos["intentos"].append({
                "tema": item["tema"], "dificultad": item.get("dificultad", "parcial"),
                "correcto": bool(item["correcto"]), "origen": "simulacro",
                "fecha": datetime.now().isoformat(timespec="seconds"),
            })
        self.guardar()

    def marcar_dia(self, dia: int, hecho: bool) -> None:
        dias = set(self.datos["plan_completado"])
        if hecho:
            dias.add(dia)
        else:
            dias.discard(dia)
        self.datos["plan_completado"] = sorted(dias)
        self.guardar()

    def dia_hecho(self, dia: int) -> bool:
        return dia in self.datos["plan_completado"]

    # ------------------------------------------------------------ análisis
    def resumen_por_tema(self) -> dict[str, dict]:
        """Por tema: aciertos, fallos, total, porcentaje total y porcentaje reciente."""
        resumen: dict[str, dict] = {}
        for intento in self.datos["intentos"]:
            r = resumen.setdefault(intento["tema"], {"aciertos": 0, "fallos": 0, "historial": []})
            r["aciertos" if intento["correcto"] else "fallos"] += 1
            r["historial"].append(bool(intento["correcto"]))
        for r in resumen.values():
            r["total"] = r["aciertos"] + r["fallos"]
            r["porcentaje"] = r["aciertos"] / r["total"]
            recientes = r["historial"][-VENTANA_RECIENTE:]
            r["reciente"] = sum(recientes) / len(recientes)
        return resumen

    def puntos_debiles(self) -> list[tuple[str, dict]]:
        """Temas con suficientes intentos y bajo porcentaje reciente, del más débil al menos."""
        debiles = [(t, r) for t, r in self.resumen_por_tema().items()
                   if r["total"] >= MIN_INTENTOS and r["reciente"] < UMBRAL_DEBIL]
        return sorted(debiles, key=lambda par: par[1]["reciente"])

    def recomendaciones(self, temas_en_orden: list[str], cuantas: int = 3) -> list[tuple[str, str]]:
        """Qué repasar primero: ``[(tema_id, motivo), ...]``.

        Prioridad: 1) puntos débiles (agrupando por nivel de acierto y, a igual
        nivel, primero los temas más básicos, porque los siguientes dependen de
        ellos); 2) temas con pocos intentos, en el orden del curso; 3) el tema
        con menor porcentaje entre los demás.
        """
        resumen = self.resumen_por_tema()
        orden = {t: i for i, t in enumerate(temas_en_orden)}
        salida: list[tuple[str, str]] = []

        debiles = sorted(self.puntos_debiles(), key=lambda par: (int(par[1]["reciente"] / 0.2), orden.get(par[0], 99)))
        for tema, r in debiles:
            salida.append((tema, f"Punto débil: {r['reciente']:.0%} de aciertos en tus últimos intentos."))

        for tema in temas_en_orden:
            if len(salida) >= cuantas:
                break
            r = resumen.get(tema)
            if r is None or r["total"] < MIN_INTENTOS:
                hechos = 0 if r is None else r["total"]
                salida.append((tema, "Todavía no lo practicaste." if hechos == 0 else
                               f"Solo {hechos} intento(s): practica un poco más para evaluarlo."))

        restantes = sorted((r["reciente"], orden.get(t, 99), t) for t, r in resumen.items()
                           if t not in {s[0] for s in salida})
        for porcentaje, _, tema in restantes:
            if len(salida) >= cuantas:
                break
            salida.append((tema, f"Repaso de mantenimiento ({porcentaje:.0%} de aciertos)."))
        return salida[:cuantas]
