### Primitiva
$F$ es primitiva de $f$ si $F'(x) = f(x)$. Escribimos $\displaystyle\int f(x)\,dx = F(x) + C$.
**Truco de oro:** siempre puedes revisar tu resultado **derivándolo**.

### Tabla básica
| $\int f\,dx$ | resultado |
|---|---|
| $\int x^n\,dx$ $(n\neq-1)$ | $\frac{x^{n+1}}{n+1} + C$ |
| $\int \frac1x\,dx$ | $\ln\lvert x\rvert + C$ |
| $\int e^x\,dx$ | $e^x + C$ |
| $\int \sin x\,dx$ | $-\cos x + C$ |
| $\int \cos x\,dx$ | $\sin x + C$ |
| $\int \sec^2 x\,dx$ | $\tan x + C$ |
| $\int \frac{dx}{1+x^2}$ | $\arctan x + C$ |

### Sustitución ($u = g(x)$)
Busca una función "de adentro" cuya derivada aparezca multiplicando. Con $du = g'(x)\,dx$ todo queda en $u$; integra y **vuelve a $x$**.

### Por partes
$$\int u\,dv = uv - \int v\,du$$
Elige $u$ con el orden **LIATE**: Logarítmica, Inversa trigonométrica, Algebraica, Trigonométrica, Exponencial.

### Errores comunes
- Olvidar el $+C$.
- $\int x^n dx = \frac{x^{n+1}}{n}$ ✗ — se divide entre el **nuevo** exponente $n+1$.
- Usar la regla de la potencia con $n = -1$ (ahí da $\ln|x|$).
- En sustitución, no ajustar la constante: $\int \cos(3x)\,dx = \frac13\sin(3x) + C$.
- $\int f g\,dx = \int f\,dx \cdot \int g\,dx$ ✗ — la integral de un producto **no** es el producto de integrales.
