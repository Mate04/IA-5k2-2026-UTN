## 8. Trazas y propagación de errores (agregado en la v6)

La traza tiene tres niveles, todos con el mismo `RUN_ID`:

| Archivo | Una fila por | Qué registra |
|---|---|---|
| `traza_envio.csv` | imagen × módulo | parámetros, inicio, duración, estado, cantidad de salidas y error (detector, NMS + umbral, segmentador, propiedades, relaciones, atributos, validación) |
| `traza_objetos.csv` | objeto de cada SceneJSON | **linaje**: confianza, rango de la clase en su caja (k), fuente (imagen completa o ventana), caja del detector, segmentador, píxeles de la máscara, si se usó la caja de respaldo |
| `traza_qa.csv`, `traza_llm.csv` | pregunta | consulta ejecutada; en el modo LLM, la salida cruda del intérprete, los reintentos y su motivo, la normalización de clases y la redacción usada |

Con eso respondemos dos preguntas:

1. **¿En qué etapa se pierde cada objeto real?** (8.1) Para los 1790 objetos de desarrollo seguimos la cadena *detector → umbral → NMS → emparejamiento → SAM2* y asignamos cada objeto a la **primera** etapa donde se pierde:
   - **no localizado:** ninguna caja cruda (de ninguna clase, confianza ≥ 0,05) tiene IoU ≥ 0,5 con él;
   - **localizado con otra clase:** hay cajas que lo cubren, pero ninguna de su clase entre las k clases candidatas;
   - **debajo del umbral:** hay una caja de su clase, pero con confianza menor que el umbral final;
   - **eliminado por NMS:** había una caja de su clase sobre el umbral y el NMS la borró;
   - **caja usada por otro objeto:** la caja sobrevivió, pero el emparejamiento uno a uno la asignó a otro objeto real;
   - **máscara mala (SAM2):** la caja es correcta, pero la máscara tiene IoU < 0,5 con la real;
   - **OK:** caja y máscara correctas.
2. **¿De dónde viene cada respuesta incorrecta?** (8.2) Cada error de QA se lleva hasta la etapa que lo causó: interpretación del LLM, una regla derivada (zona, tamaño, relación) o la percepción, y en ese caso hasta la etapa de 8.1 de los objetos involucrados. Si los objetos que faltan se perdieron en etapas distintas, se informa la que explica más objetos y, si empatan, la más temprana de la pipeline; la columna `detalle` muestra todas.

En 8.3 reconstruimos una respuesta completa leyendo sólo las trazas, y en 8.4 usamos las trazas para evaluar las etapas (tiempos, fallas, reintentos y normalizaciones). Las anotaciones se usan sólo para medir.
