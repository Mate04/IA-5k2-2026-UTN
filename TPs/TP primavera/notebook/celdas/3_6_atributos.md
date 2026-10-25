### 3.6 Atributos derivados y proximidad (agregado en la v3)

Además de las propiedades del schema, cada objeto lleva atributos que se calculan con código a partir de su máscara y de los píxeles de la imagen. Son **derivados**: no los predice un modelo y LVIS no trae ground truth para ellos.

| Campo | Regla |
|---|---|
| `attributes.color` | el color con más píxeles dentro de la máscara (erosionada 1 px para no tomar el fondo), clasificado por reglas HSV en 12 nombres |
| `attributes.color_ratio` | fracción de los píxeles de la máscara que tienen ese color: indica qué tan dominante es |
| `attributes.occlusion` | fracción de la caja del objeto tapada por máscaras de **otros** objetos (estimación de oclusión) |
| `attributes.touches_border` | la caja toca el borde de la imagen, así que el objeto puede estar cortado |
| `extra_relations` (`near`) | separación entre cajas ≤ 2 % de la diagonal de la imagen. Va en un campo aparte porque el schema sólo admite 5 predicados en `relations` |

Las reglas y los umbrales son decisiones propias. Quedan en `PARAMS_ATRIBUTOS`, que también se guarda en la traza de cada imagen.

**Cómo se eligieron los umbrales de color:** no hay ground truth de color, así que usamos como aproximación las clases con un color esperable (brócoli verde, cebra blanca, negra o gris, elefante gris o marrón…). Con las máscaras reales de desarrollo, subir el umbral de saturación de "gris" de 0,15 a 0,25 llevó el promedio de aciertos plausibles de 0,48 a 0,55. Más que eso no se logra con reglas HSV simples: las bananas con luz cálida caen en naranja y el brócoli amarillento en amarillo. Por eso el color es un **atributo aproximado**, y la confianza de una respuesta de color viene acompañada de `color_ratio`.
