### 2.9 Experimentos de mejora del detector (agregado en la v4)

El análisis de 2.5 deja dos cuellos de botella: **objetos chicos** (recall 0,43) y **confianzas bajas** en clases como `person`. Probamos cada cambio **por separado** y sobre las mismas 120 imágenes, con la misma métrica (2.1), el mismo NMS por clase 0,5 y el mismo barrido de umbral y de clases por caja (k):

| # | Hipótesis | Variable que cambia |
|---|---|---|
| E3 | Un backbone más grande separa mejor clases parecidas y ve mejor los objetos chicos | `owlv2-base-patch16` → `owlv2-large-patch14` (entrada 960 → 1008 px) |
| E7 | Para nombres raros de LVIS (`fireplug`, `jean`, `spectacles`…) y para `person`, sumar sinónimos sube la confianza correcta | Cada clase puede tener varias consultas de texto; el puntaje de la clase es el **máximo** entre sus consultas |
| E4 | Mirar la imagen por partes (estilo SAHI) agranda los objetos chicos: cada ventana se reescala a la entrada de OWLv2, así que los objetos se ven 1,7 veces más grandes por lado (2,8 veces en área) | Además de la imagen completa, 4 ventanas de 60 % × 60 % que se solapan. Se descartan las cajas que tocan un borde interno de la ventana (objeto cortado) y el NMS une los duplicados |
| E8 (v5) | Large solo rinde menos que base, pero puede encontrar objetos distintos: el ensamble suma recall | Se agregan las detecciones de large (imagen completa) a las de base y el NMS une los duplicados |

**Cómo se elige la configuración final:** la de mayor F1 de cajas en desarrollo. Cada variante se mide con su mejor umbral y su mejor k, así ninguna sale perjudicada por un umbral elegido para otra. El umbral se elige con un paso de 0,01 alrededor del óptimo grueso.

**Detalle de implementación (E7):** en OWLv2 el puntaje de una caja para una consulta de texto no depende de las otras consultas. Por eso una sola pasada con todas las consultas permite medir "con" y "sin sinónimos" sin volver a usar la GPU.

La configuración ganadora reemplaza a la de la Fase 2: las Fases 3 y 4 usan `detectar_multi`, `UMBRAL` y `K_MAX` tal como quedan al final de esta celda.
