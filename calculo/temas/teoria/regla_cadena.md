### Regla de la cadena
Si $y = f(g(x))$ (una función **dentro** de otra):
$$\big(f(g(x))\big)' = f'(g(x))\cdot g'(x)$$
"Deriva la función de afuera dejando igual lo de adentro, y **multiplica por la derivada de lo de adentro**."

### Formas que más se usan (con $u = u(x)$)
- $(u^n)' = n\,u^{n-1}\,u'$
- $(\sqrt{u})' = \dfrac{u'}{2\sqrt{u}}$
- $(e^u)' = e^u\,u'$
- $(\ln u)' = \dfrac{u'}{u}$
- $(\sin u)' = \cos u\cdot u'$, $\;(\cos u)' = -\sin u\cdot u'$

### Cadenas largas
$\sin^3(x^2) = \big(\sin(x^2)\big)^3$: potencia → seno → $x^2$. Se deriva de afuera hacia adentro, multiplicando cada derivada:
$3\sin^2(x^2)\cdot\cos(x^2)\cdot 2x$.

### Errores comunes
- **Olvidar multiplicar por la derivada de lo de adentro** (el error más frecuente del parcial).
- Cambiar lo de adentro al derivar la función externa: $(\sin(x^2))' = \cos(x^2)\cdot 2x$, no $\cos(2x)$.
- Confundir $\sin^2 x = (\sin x)^2$ con $\sin(x^2)$.
