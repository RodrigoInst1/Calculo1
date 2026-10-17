### ¿Qué es la derivada?
$$f'(x) = \lim_{h\to 0}\frac{f(x+h) - f(x)}{h}$$
Es la **pendiente de la recta tangente** y la **razón de cambio instantánea** de $f$.

### Reglas básicas
- Constante: $(c)' = 0$.
- Potencia: $(x^n)' = n\,x^{n-1}$ (vale para cualquier exponente real: $\sqrt{x}=x^{1/2}$, $\frac1x = x^{-1}$).
- Múltiplo constante: $(c\,f)' = c\,f'$.
- Suma/resta: $(f \pm g)' = f' \pm g'$.

### Tabla de derivadas
| $f(x)$ | $f'(x)$ |
|---|---|
| $\sin x$ | $\cos x$ |
| $\cos x$ | $-\sin x$ |
| $\tan x$ | $\sec^2 x$ |
| $e^x$ | $e^x$ |
| $a^x$ | $a^x\ln a$ |
| $\ln x$ | $\frac{1}{x}$ |
| $\arctan x$ | $\frac{1}{1+x^2}$ |

### Recta tangente en $x = a$
$y = f(a) + f'(a)(x - a)$.

### Errores comunes
- $(x^n)' = n x^{n+1}$ ✗ — se **resta** 1 al exponente.
- Derivar una constante y obtener la misma constante (es **0**).
- $(\cos x)' = \sin x$ ✗ — falta el signo menos.
- Evaluar en el punto **antes** de derivar (por ejemplo, $f(2)$ es un número y su derivada es 0).
- No reescribir raíces y fracciones como potencias antes de derivar.
