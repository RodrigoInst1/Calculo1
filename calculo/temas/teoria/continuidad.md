### Definición
$f$ es **continua en $x = a$** si se cumplen tres cosas:
1. $f(a)$ existe,
2. $\displaystyle\lim_{x\to a} f(x)$ existe,
3. $\displaystyle\lim_{x\to a} f(x) = f(a)$.

Intuición: se puede dibujar la gráfica cerca de $a$ **sin levantar el lápiz**.

### Funciones que ya sabemos continuas
Polinomios (en todo $\mathbb{R}$), racionales (donde el denominador $\neq 0$), $\sin$, $\cos$, $e^x$, $\ln x$ (para $x>0$), $\sqrt{x}$ (para $x\ge 0$), y sumas, productos, cocientes y composiciones de ellas en su dominio.

### Tipos de discontinuidad
- **Evitable**: el límite existe pero no coincide con $f(a)$ (o $f(a)$ no está definido). Se arregla redefiniendo $f(a)$.
- **De salto**: los límites laterales existen pero son distintos.
- **Infinita**: algún límite lateral es $\pm\infty$ (asíntota vertical).

### Funciones a trozos
Para que sea continua en el punto donde cambia la fórmula, **iguala los límites laterales** (y el valor de la función).

### Teorema del valor intermedio
Si $f$ es continua en $[a, b]$ y $k$ está entre $f(a)$ y $f(b)$, existe $c \in (a, b)$ con $f(c) = k$.
(Sirve para probar que una ecuación tiene solución.)

### Errores comunes
- Revisar solo que $f(a)$ exista y olvidar comparar con el límite.
- En funciones a trozos, usar la fórmula equivocada para cada lado.
- Creer que si $f(a)$ no está definido no hay nada que hacer: puede ser una discontinuidad **evitable**.
