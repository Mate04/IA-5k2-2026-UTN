### 3.3b Experimentos de segmentación (agregado en la v4)

Tres preguntas, con las mismas detecciones finales y la misma métrica de 3.3:

| # | Pregunta | Cómo se mide |
|---|---|---|
| E6 | ¿Un SAM2 más grande da mejores máscaras con las mismas cajas? | F1 de máscaras con `sam2.1-hiera-small` vs `sam2.1-hiera-large` |
| E5 | ¿Cuánto pierde SAM2 por sí solo, con cajas perfectas? (oráculo) | SAM2 recibe las **cajas reales** y se mide el IoU de cada máscara contra su máscara real. Separa los errores del detector de los del segmentador |
| — | ¿Conviene reemplazar la caja del detector por la caja que encierra la máscara? | F1 de cajas con una y otra caja |

El segmentador con mayor F1 de máscaras pasa a ser el de la pipeline. Las anotaciones se usan sólo para medir: en el oráculo, las cajas reales nunca llegan al envío.
