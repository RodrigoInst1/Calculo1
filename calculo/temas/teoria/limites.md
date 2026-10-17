### Idea
$\displaystyle\lim_{x\to a} f(x) = L$ significa que $f(x)$ se acerca a $L$ cuando $x$ se acerca a $a$
(sin importar lo que pase **exactamente** en $a$).

### Método paso a paso
1. **Sustituye** directamente. Si da un número, ese es el límite (polinomios, racionales con denominador $\neq 0$, $\sin$, $\cos$, $e^x$... son continuas).
2. Si aparece una **forma indeterminada** ($\frac{0}{0}$, $\frac{\infty}{\infty}$, $0\cdot\infty$, $\infty-\infty$, $1^\infty$, $0^0$, $\infty^0$), transforma:
   - **Factorizar y cancelar** (racionales con $\frac{0}{0}$).
   - **Racionalizar**: multiplicar por el conjugado si hay raíces.
   - **Dividir entre la mayor potencia** cuando $x \to \pm\infty$.
   - **L'Hôpital**: si es $\frac{0}{0}$ o $\frac{\infty}{\infty}$, $\displaystyle\lim \frac{f}{g} = \lim \frac{f'}{g'}$.
   - **Logaritmos** para $1^\infty$, $0^0$, $\infty^0$: $f^g = e^{g\ln f}$.
3. Si queda $\frac{k}{0}$ con $k \neq 0$: el límite es infinito; estudia los **límites laterales** para el signo.

### Límites laterales
El límite existe solo si $\displaystyle\lim_{x\to a^-} f(x) = \lim_{x\to a^+} f(x)$.

### Límites notables
$\displaystyle\lim_{u\to 0}\frac{\sin u}{u} = 1,\quad \lim_{u\to 0}\frac{1-\cos u}{u^2} = \frac12,\quad \lim_{u\to 0}\frac{e^u - 1}{u} = 1,\quad \lim_{x\to\infty}\left(1 + \frac{1}{x}\right)^x = e.$

### Racionales en el infinito (grados $n$ arriba y $m$ abajo)
- $n < m$: el límite es $0$. $\;n = m$: cociente de coeficientes principales. $\;n > m$: $\pm\infty$.

### Errores comunes
- Creer que $\frac{0}{0} = 0$ o $= 1$: es **indeterminado**, hay que trabajar más.
- Usar L'Hôpital como si fuera la regla del cociente: se derivan numerador y denominador **por separado**.
- Aplicar L'Hôpital cuando NO hay $\frac{0}{0}$ ni $\frac{\infty}{\infty}$ (da resultados falsos).
- Olvidar revisar los dos lados cuando el denominador tiende a 0.
- Cancelar antes de factorizar: $\frac{x^2-4}{x-2}$ se simplifica factorizando $x^2 - 4 = (x-2)(x+2)$.
