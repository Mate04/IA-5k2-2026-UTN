### 8.5 Conclusiones de la Fase 8

**Dónde se pierden los objetos reales (8.1, 1790 objetos de desarrollo).**

| Etapa | Objetos | % | De ellos, chicos |
|---|---|---|---|
| OK (caja y máscara correctas) | 1073 | 59,9 | 459 |
| Debajo del umbral | 453 | 25,3 | 299 |
| No localizado | 120 | 6,7 | 111 |
| Máscara mala (SAM2) | 83 | 4,6 | 64 |
| Localizado con otra clase | 31 | 1,7 | 14 |
| Caja usada por otro objeto | 16 | 0,9 | 10 |
| Eliminado por NMS | 14 | 0,8 | 10 |

- **La primera causa de pérdida es la confianza, no la localización.** Uno de cada cuatro objetos reales tiene una caja de su clase que lo cubre, pero con confianza menor que 0,25 (mediana 0,17). Bajar el umbral no sirve (7.1): entran más falsos positivos que objetos recuperados. Lo que falta es un puntaje mejor calibrado por clase; `car`, `book`, `shoe`, `chair` y `wheel` son las que más pierden así.
- **Los objetos chicos concentran las pérdidas que el umbral no explica:** 111 de los 120 no localizados y 64 de las 83 máscaras malas.
- **SAM2 casi no agrega error:** el 93 % de los objetos con caja correcta también tiene máscara correcta (IoU medio 0,80). El control de 8.1 cierra con la métrica: 1156 objetos con caja correcta, los mismos TP de 2.9.
- **NMS y emparejamiento son marginales** (30 objetos entre ambos), como anticipaba el EDA (1.6).

**De dónde vienen las respuestas incorrectas (8.2).** Los 9 errores del modo determinista vienen de la percepción, y en el modo LLM son los mismos 9, porque con la interpretación correcta el motor da la misma respuesta. Ninguno es del motor ni de una regla derivada:
- en 6 la causa principal es que objetos de la clase preguntada quedaron **debajo del umbral** (`doorknob`, `shoe`, `glove`, `strap`, `banner`, `elephant`);
- 1 es un **falso positivo**: 3 servilletas que la imagen tiene verificadas como ausentes, todas de las ventanas y con confianza apenas sobre el umbral (0,26 a 0,29);
- 2 conteos pierden objetos en dos etapas distintas (`trousers`: otra clase y umbral; `fork`: no localizado y NMS).

De los 11 objetos reales que faltan en esas respuestas, 8 quedaron debajo del umbral: la misma conclusión que a nivel de objetos. Para el QA, la palanca es la misma que para el F1.

**Las trazas alcanzan para reconstruir un resultado (8.3).** Desde el `run_id` de un SceneJSON se llega a la configuración, a los módulos de percepción de esa imagen, a la consulta ejecutada, a la salida cruda del LLM con su normalización (por ejemplo, `mango` → `handle` por el diccionario español) y al linaje de cada objeto de la evidencia: confianza, rango de clase, fuente y máscara. Las anotaciones sólo aparecen en el último paso, para explicar el error.

**Evaluación de las etapas con las trazas (8.4).** Ningún módulo falló en las 80 imágenes. El detector es el módulo más caro (≈ 2/3 del tiempo, por las 5 pasadas de OWLv2) y SAM2 le sigue (≈ 1/4). Del lado del intérprete, la normalización resolvió 6 clases que el LLM no escribió exactamente como en el vocabulario (3 por coincidencia aproximada, 1 por singular, 1 por alias en inglés y 1 por el diccionario español), sin necesidad de reintentos.
