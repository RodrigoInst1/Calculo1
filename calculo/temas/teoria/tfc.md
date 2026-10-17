### Teorema Fundamental del Cálculo
Conecta derivadas e integrales: **son operaciones inversas**.

**Primera parte.** Si $f$ es continua y $F(x) = \displaystyle\int_a^x f(t)\,dt$, entonces
$$F'(x) = f(x).$$

**Segunda parte.** Si $F' = f$ en $[a, b]$, entonces $\displaystyle\int_a^b f(x)\,dx = F(b) - F(a)$.

### Con regla de la cadena
$$\frac{d}{dx}\int_a^{g(x)} f(t)\,dt = f(g(x))\cdot g'(x)$$
$$\frac{d}{dx}\int_{h(x)}^{g(x)} f(t)\,dt = f(g(x))\,g'(x) - f(h(x))\,h'(x)$$

### ¿Y la constante $a$?
El límite inferior constante no afecta la derivada (su derivada es 0).

### Errores comunes
- Intentar integrar primero: con la primera parte **no hace falta**.
- Olvidar multiplicar por $g'(x)$ cuando el límite superior no es solo $x$.
- Dejar la variable $t$ en la respuesta: hay que sustituir $t$ por el límite.
- Olvidar el signo menos del límite inferior cuando también depende de $x$.
