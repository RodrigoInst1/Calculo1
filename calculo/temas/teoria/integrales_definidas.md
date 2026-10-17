### Idea
$\displaystyle\int_a^b f(x)\,dx$ es el **área con signo** entre la gráfica y el eje $x$ (lo que está debajo del eje cuenta negativo).
Es el límite de las **sumas de Riemann** $\sum f(x_i^*)\Delta x$.

### Cómo se calcula (TFC, segunda parte)
Si $f$ es continua en $[a, b]$ y $F' = f$:
$$\int_a^b f(x)\,dx = F(b) - F(a) = \Big[F(x)\Big]_a^b$$

### Propiedades
- $\int_a^a f = 0$, $\;\int_b^a f = -\int_a^b f$.
- $\int_a^b (f + g) = \int_a^b f + \int_a^b g$, $\;\int_a^b c f = c\int_a^b f$.
- $\int_a^b f = \int_a^c f + \int_c^b f$.

### Sustitución en definidas
Si cambias a $u = g(x)$, **cambia también los límites**: $x = a \to u = g(a)$, $x = b \to u = g(b)$. Así no hace falta volver a $x$.

### Integrales impropias
Si un límite es infinito (o $f$ explota en un extremo) se calcula con un límite:
$\displaystyle\int_1^\infty f(x)\,dx = \lim_{t\to\infty}\int_1^t f(x)\,dx$. Ejemplo clave: $\int_1^\infty \frac{dx}{x^p}$ converge solo si $p > 1$.

### Errores comunes
- Restar al revés: es $F(b) - F(a)$ (arriba menos abajo).
- Cambiar a $u$ y usar los límites viejos de $x$.
- Aplicar el TFC cuando la función **no es continua** en el intervalo (por ejemplo $\int_{-1}^{1}\frac{1}{x^2}dx$ no vale $-2$: diverge).
- Poner $+C$ en una integral definida (no hace falta: se cancela).
