### ¿Cuándo se usa?
Cuando $x$ e $y$ están mezcladas en una ecuación (por ejemplo $x^2 + y^2 = 25$) y es difícil o imposible despejar $y$.

### Método
1. Deriva **ambos lados** respecto de $x$.
2. Cada vez que derives algo con $y$, multiplica por $y'$ (regla de la cadena, porque $y = y(x)$):
   $(y^2)' = 2y\,y'$, $\;(\sin y)' = \cos y\cdot y'$, $\;(xy)' = y + x\,y'$ (regla del producto).
3. Junta todos los términos con $y'$ en un lado, saca factor común $y'$ y **despeja**.

### Ejemplo rápido
$x^2 + y^2 = 25 \Rightarrow 2x + 2y\,y' = 0 \Rightarrow y' = -\dfrac{x}{y}$.

### Errores comunes
- Olvidar el $y'$ al derivar términos con $y$.
- Derivar $xy$ como $y'$ o como $1\cdot y'$: es un **producto**, $(xy)' = y + xy'$.
- Derivar el número del lado derecho y no ponerlo en 0.
- Despejar mal: hay que sacar $y'$ como factor común antes de dividir.
