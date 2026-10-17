# Calculo1 — herramienta de estudio para Cálculo I

App en Python + Streamlit para **aprender, practicar y verificar** Cálculo I (temario estilo Stewart),
empezando desde lo más básico. Todo está en español y con tema oscuro, y se puede abrir desde el celular.

> **Regla de oro del proyecto:** ninguna respuesta matemática se inventa. Todos los resultados los calcula
> **SymPy** y se comprueban (por ejemplo, cada primitiva se deriva para confirmar que da el integrando).

## Qué hace

| Sección | Qué puedes hacer |
|---|---|
| 🧮 **Solucionador** | Escribes un límite, una derivada o una integral **en texto** y ves el resultado y **cada paso explicado**, con el nombre de la regla (suma, producto, cociente, cadena, L'Hôpital, sustitución, por partes, TFC...). |
| 🧮 **Modo verificar** | Escribes tu respuesta y la app te dice si es **equivalente** a la correcta (acepta formas distintas, como `sin(2x)` y `2 sin x cos x`). Si está mal, te da **pistas graduales** sin darte la solución: detecta errores típicos (olvidar la cadena, signo cambiado, factor constante, integrar en vez de derivar, restar al revés en el TFC...). |
| ✏️ **Ejercicios** | Problemas **originales** generados al azar para 14 temas y 3 dificultades (básico, medio, nivel parcial). La solución queda oculta hasta que la pidas. |
| 📖 **Estudio** | Resumen corto de teoría por tema, ejemplos resueltos paso a paso y **errores comunes**. |
| 🗓️ **Plan** | Plan de **4 semanas** para estudiar por la mañana (1–2 h al día), con días de repaso y simulacro. |
| 📊 **Progreso** | Aciertos y fallos por tema, **puntos débiles** y qué repasar primero. Copia de seguridad en JSON. |
| 📝 **Simulacro** | Examen de 5–6 ejercicios que mezcla temas, con **cuenta regresiva** y corrección final con puntaje sobre 100. |

### Temas (en este orden)
1. Funciones y álgebra de repaso · 2. Límites · 3. Continuidad · 4. Derivadas: reglas básicas ·
5. Producto y cociente · 6. Regla de la cadena · 7. Derivación implícita · 8. Máximos y mínimos ·
9. Razón de cambio · 10. Optimización · 11. Integrales indefinidas · 12. Integrales definidas ·
13. Teorema Fundamental del Cálculo · 14. Áreas

## Instalación

Necesitas **Python 3.11 o superior**.

```bash
git clone https://github.com/RodrigoInst1/Calculo1.git
cd Calculo1
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Cómo ejecutarla

```bash
streamlit run app.py
```

Se abre en el navegador en `http://localhost:8501`.

**Desde el celular** (en la misma red Wi-Fi que la computadora):

```bash
streamlit run app.py --server.address 0.0.0.0
```

y en el celular abre `http://IP-DE-TU-COMPUTADORA:8501` (la IP aparece en la terminal como *Network URL*).

### Pruebas automáticas

```bash
python -m pytest -q
```

Hay pruebas del intérprete, del solucionador (cada resultado se compara con SymPy), del verificador
(respuestas equivalentes y pistas), del generador (cada ejercicio generado acepta su propia respuesta
correcta y rechaza una incorrecta), del modo estudio y del simulacro.

## Cómo escribir las expresiones

| Quiero | Escribo |
|---|---|
| $x^2$, $3x$ | `x^2`, `3x` |
| $\sin x$, $\sin^2 x$ | `sin(x)` o `sen x`, `sin^2(x)` |
| $e^{2x}$, $\ln x$ | `e^(2x)`, `ln(x)` |
| $\sqrt{x+1}$, $\lvert x\rvert$ | `sqrt(x+1)` o `raiz(x+1)`, `|x|` |
| $\pi$, $\infty$ | `pi`, `oo` (o `infinito`) |

Problemas completos en el solucionador:

```
lim x->2 (x^2-4)/(x-2)
lim x->0+ 1/x
lim x->oo (3x^2+1)/(2x^2-x)
d/dx x^2 sin(x)
derivada segunda de x^4
integral x e^x dx
integral de 0 a 1 x^2 dx
```

Si algo no se entiende, la app muestra un mensaje explicando qué revisar (nunca un error técnico).

## Estructura del proyecto

```
app.py                      # punto de entrada de Streamlit (navegación)
.streamlit/config.toml      # tema oscuro
calculo/
  interprete.py             # texto -> SymPy, con mensajes de error útiles
  derivadas.py              # derivadas paso a paso
  limites.py                # límites paso a paso
  integrales.py             # integrales paso a paso (indefinidas, definidas, impropias)
  solucionador.py           # entiende "lim x->0 ...", "d/dx ...", "integral ..." y resuelve con tiempo límite
  verificador.py            # compara respuestas y genera pistas
  ejercicios.py             # modelo de ejercicio y comparadores de respuestas
  temas/                    # un archivo por tema (generadores) + teoria/<tema>.md
  progreso.py               # registro de aciertos/fallos y recomendaciones
  plan.py                   # plan de 4 semanas
  simulacro.py              # simulacro de parcial
interfaz/                   # páginas de Streamlit
tests/                      # pruebas con pytest
datos/progreso.json         # tu progreso (se crea al usar la app; no se sube a git)
```

El progreso se guarda en `datos/progreso.json`. Puedes cambiar la ubicación con la variable de entorno
`CALCULO_PROGRESO=/ruta/a/mi_progreso.json`. Desde la página **Progreso** puedes descargar una copia y restaurarla.

## Cómo agregar temas nuevos

Cada tema es **un archivo** en `calculo/temas/` y se detecta solo (no hay que registrarlo en otro lado).

1. **Crea el archivo** `calculo/temas/t15_mi_tema.py` (el número solo sirve para ordenar los archivos):

   ```python
   """Tema 15: Mi tema nuevo."""

   import sympy as sp

   from . import Tema
   from ._util import L, desde_solver, entero, nuevo, paso, x


   def derivada_de_seno(rng):
       """Ejercicio de derivada: el solucionador genera los pasos y la respuesta."""
       a = entero(rng, 2, 9)
       f = sp.sin(a * x)
       return desde_solver(f"Deriva $f(x) = {L(f)}$.", "derivada", {"expr": f, "variable": x, "orden": 1},
                           pistas=["Usa la regla de la cadena."])


   def valor_en_un_punto(rng):
       """Ejercicio con respuesta numérica: la respuesta la calcula SymPy."""
       a = entero(rng, 1, 5)
       f = x**2 + a
       valor = f.subs(x, 2)
       pasos = [paso("Sustituir", "Reemplazamos x por 2.", rf"f(2) = {L(valor)}")]
       return nuevo(f"Si $f(x) = {L(f)}$, calcula $f(2)$.", "numero", valor, pasos,
                    pistas=["Reemplaza cada x por 2."])


   TEMA = Tema(
       id="mi_tema",                   # identificador único, sin espacios
       nombre="Mi tema nuevo",
       orden=15,                       # posición en el curso
       descripcion="Qué se practica en este tema.",
       generadores={
           "basico": [valor_en_un_punto],
           "medio": [derivada_de_seno],
           "parcial": [derivada_de_seno],
       },
       ejemplos=[("basico", 1), ("medio", 1)],   # ejemplos resueltos del modo estudio (dificultad, semilla)
   )
   ```

   - Usa `desde_solver(...)` para límites (`"limite"`), derivadas (`"derivada"`) e integrales
     (`"integral"` / `"integral_definida"`): los pasos y la corrección salen del solucionador.
   - Usa `nuevo(enunciado, tipo_respuesta, respuesta, pasos, pistas)` para otros problemas.
     Tipos de respuesta: `expresion`, `factorizacion`, `simplificacion`, `numero`, `conjunto`,
     `recta`, `desigualdad` (ver `calculo/ejercicios.py`).
   - Calcula **siempre** la respuesta con SymPy, nunca a mano. Si los números al azar dan un caso feo,
     lanza `Reintentar` (de `calculo.temas`) y se generará otro.

2. **Escribe la teoría** en `calculo/temas/teoria/mi_tema.md` (Markdown con fórmulas entre `$...$`).
   Incluye una sección `### Errores comunes`.

3. *(Opcional)* Agrega el tema a un bloque de `BLOQUES` en `calculo/simulacro.py` para controlar con qué
   se mezcla en el simulacro (si no, igual puede salir), y a algún día de `calculo/plan.py`.

4. **Corre las pruebas**: `python -m pytest -q`. Las pruebas del generador recorren automáticamente
   todos los temas y comprueban que cada ejercicio acepta su propia respuesta correcta.

## Limitaciones conocidas

- Algunos límites e integrales poco comunes no tienen un camino guiado paso a paso; en ese caso la app lo
  avisa y muestra el resultado calculado directamente por SymPy.
- La primitiva de $\frac{1}{x}$ se muestra como $\ln x$ (así la escribe SymPy); la explicación recuerda
  que en los reales es $\ln\lvert x\rvert$.
- El progreso se guarda en un solo archivo local: está pensado para un estudiante por instalación.
- En el simulacro, las respuestas se guardan al pulsar Enter o salir del campo; escribe y confirma cada una.
