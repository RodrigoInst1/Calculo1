"""Plan de estudio de 4 semanas (por la mañana, entre 1 y 2 horas al día).

Cada día tiene temas y una rutina con tiempos. Los días 7, 14, 21 y 28 son de
repaso con simulacro. El progreso del plan se marca en la app.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Dia:
    numero: int
    titulo: str
    temas: list[str]
    actividades: list[tuple[int, str]]  # (minutos, actividad)
    nota: str = ""
    simulacro: bool = False

    @property
    def semana(self) -> int:
        return (self.numero - 1) // 7 + 1

    @property
    def minutos(self) -> int:
        return sum(m for m, _ in self.actividades)


def _rutina(teoria: str, practica: str, minutos_practica: int = 50) -> list[tuple[int, str]]:
    """Rutina estándar de una mañana."""
    return [
        (10, "Calentamiento: repasa los «errores comunes» del tema anterior."),
        (25, f"Modo estudio: {teoria} Lee la teoría y sigue los ejemplos resueltos en papel."),
        (minutos_practica, f"Ejercicios: {practica} Resuelve en papel y verifica en la app."),
        (10, "Cierre: anota tus dudas y revisa en «Progreso» qué tema quedó débil."),
    ]


def _repaso(temas: list[str], numero: int, titulo: str) -> Dia:
    return Dia(numero, titulo, temas, [
        (15, "Mira tu «Progreso» y lee la teoría de tus puntos débiles."),
        (60, "Simulacro de parcial con los temas de la semana (en la página Simulacro)."),
        (25, "Corrige: para cada ejercicio fallado, mira la solución y rehaz uno parecido."),
    ], nota="Día de repaso: no veas temas nuevos.", simulacro=True)


PLAN: list[Dia] = [
    # ------------------------------------------------------------- semana 1
    Dia(1, "Álgebra que necesitas", ["repaso"],
        _rutina("Funciones y álgebra de repaso (potencias, factorización, ecuaciones).", "6 básicos y 4 medios.")),
    Dia(2, "Dominio, composición e inversa", ["repaso"],
        _rutina("Dominio, composición e inversa.", "4 medios y 4 de nivel parcial.")),
    Dia(3, "Límites: la idea y la sustitución", ["limites"],
        _rutina("Límites: definición intuitiva y sustitución directa.", "6 básicos y 3 medios (factorizar).")),
    Dia(4, "Límites: formas indeterminadas", ["limites"],
        _rutina("Factorizar, racionalizar y dividir entre la mayor potencia.", "6 medios.")),
    Dia(5, "Límites laterales, notables e infinitos", ["limites"],
        _rutina("Límites laterales, límites notables y límites al infinito.", "4 medios y 3 de nivel parcial."),
        nota="L'Hôpital aparece en algunos ejercicios de nivel parcial; si aún no sabes derivar, usa los límites notables."),
    Dia(6, "Continuidad", ["continuidad"],
        _rutina("Continuidad, tipos de discontinuidad y funciones a trozos.", "3 de cada dificultad.")),
    _repaso(["repaso", "limites", "continuidad"], 7, "Repaso de la semana 1 + simulacro"),
    # ------------------------------------------------------------- semana 2
    Dia(8, "Derivadas: definición y reglas básicas", ["derivadas_basicas"],
        _rutina("Derivadas: reglas básicas y tabla.", "8 básicos.")),
    Dia(9, "Recta tangente y derivada en un punto", ["derivadas_basicas"],
        _rutina("Interpretación geométrica: pendiente y recta tangente.", "4 medios y 3 de nivel parcial.")),
    Dia(10, "Producto y cociente", ["producto_cociente"],
        _rutina("Regla del producto y del cociente.", "4 de cada dificultad.")),
    Dia(11, "Regla de la cadena", ["regla_cadena"],
        _rutina("Regla de la cadena.", "5 básicos y 4 medios.")),
    Dia(12, "Cadena combinada", ["regla_cadena", "producto_cociente"],
        _rutina("Mezcla de cadena con producto y cociente.", "5 de nivel parcial.")),
    Dia(13, "Derivación implícita y L'Hôpital", ["implicita", "limites"],
        _rutina("Derivación implícita; después repasa L'Hôpital en Límites.", "4 de implícita y 3 límites de nivel parcial.")),
    _repaso(["derivadas_basicas", "producto_cociente", "regla_cadena", "implicita"], 14,
            "Repaso de la semana 2 + simulacro"),
    # ------------------------------------------------------------- semana 3
    Dia(15, "Puntos críticos y crecimiento", ["maximos_minimos"],
        _rutina("Puntos críticos, crecimiento y criterios de la primera y segunda derivada.", "3 básicos y 4 medios.")),
    Dia(16, "Extremos absolutos", ["maximos_minimos"],
        _rutina("Método del intervalo cerrado.", "4 de nivel parcial.")),
    Dia(17, "Razón de cambio", ["razon_cambio"],
        _rutina("Velocidad y razones relacionadas (dibuja siempre).", "2 básicos, 3 medios y 2 de nivel parcial.")),
    Dia(18, "Optimización", ["optimizacion"],
        _rutina("Método de optimización en 7 pasos.", "2 de cada dificultad, planteándolos en papel.")),
    Dia(19, "Integrales indefinidas: tabla y sustitución", ["integrales_indefinidas"],
        _rutina("Primitivas, tabla básica y sustitución.", "5 básicos y 4 medios.")),
    Dia(20, "Integración por partes", ["integrales_indefinidas"],
        _rutina("Integración por partes (LIATE).", "5 de nivel parcial.")),
    _repaso(["maximos_minimos", "razon_cambio", "optimizacion", "integrales_indefinidas"], 21,
            "Repaso de la semana 3 + simulacro"),
    # ------------------------------------------------------------- semana 4
    Dia(22, "Integrales definidas", ["integrales_definidas"],
        _rutina("Integral definida, propiedades e impropias sencillas.", "3 de cada dificultad.")),
    Dia(23, "Teorema Fundamental del Cálculo", ["tfc"],
        _rutina("TFC (primera y segunda parte) y regla de la cadena.", "3 de cada dificultad.")),
    Dia(24, "Áreas", ["areas"],
        _rutina("Área bajo la curva y entre curvas.", "3 de cada dificultad (dibuja cada región).")),
    Dia(25, "Puntos débiles (1)", [],
        [(10, "Abre «Progreso» y mira las recomendaciones."),
         (30, "Teoría y errores comunes de tu tema más débil."),
         (50, "Ejercicios de ese tema hasta acertar 3 seguidos."),
         (10, "Anota qué aprendiste.")],
        nota="Los temas del día los decide tu registro de progreso."),
    _repaso(["limites", "regla_cadena", "maximos_minimos", "integrales_indefinidas", "tfc", "areas"], 26,
            "Simulacro completo"),
    Dia(27, "Puntos débiles (2) y errores comunes", [],
        [(30, "Lee la sección «Errores comunes» de TODOS los temas."),
         (50, "Ejercicios de nivel parcial de tus 2 temas más débiles."),
         (10, "Prepara una hoja con las fórmulas clave (tabla de derivadas e integrales).")],
        nota="Los temas del día los decide tu registro de progreso."),
    _repaso(["repaso", "limites", "continuidad", "derivadas_basicas", "producto_cociente", "regla_cadena",
             "implicita", "maximos_minimos", "razon_cambio", "optimizacion", "integrales_indefinidas",
             "integrales_definidas", "tfc", "areas"], 28, "Simulacro final"),
]

SEMANAS = {
    1: "Bases, límites y continuidad",
    2: "Derivadas",
    3: "Aplicaciones de la derivada e integrales indefinidas",
    4: "Integral definida, TFC, áreas y preparación final",
}

CONSEJOS = [
    "Estudia por la mañana a la misma hora: la constancia vale más que las horas.",
    "Resuelve SIEMPRE en papel primero y usa la app para verificar.",
    "Si fallas un ejercicio, pide una pista antes de ver la solución.",
    "Un día de descanso a la semana también es parte del plan (puedes mover el día de repaso).",
]


def dias_de_semana(semana: int) -> list[Dia]:
    return [d for d in PLAN if d.semana == semana]
