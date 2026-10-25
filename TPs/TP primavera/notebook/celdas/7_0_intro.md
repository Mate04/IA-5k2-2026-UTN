## 7. Validación cruzada de la configuración del detector (agregado en la v6)

**Problema.** En 2.9 el umbral y la cantidad de clases por caja (k) se eligieron sobre las mismas 120 imágenes en las que después se mide el F1. Ese F1 es optimista: parte de la mejora puede ser ajuste al azar de estas imágenes.

**7.1 Validación cruzada.** Partimos las 120 imágenes en 5 grupos de 24 (al azar, con semilla fija). En cada vuelta elegimos k y umbral sobre 4 grupos (96 imágenes), con el mismo criterio de 2.9 (máximo F1, paso 0,01), y medimos el F1 en el grupo que quedó afuera. La media de esas 5 mediciones estima el F1 esperable en imágenes nuevas. También mostramos qué tan sensible es el F1 al umbral.

**7.2 Experimento E9: ¿un umbral por fuente?** Las cajas de las ventanas (E4) salen de recortes ampliados, así que su confianza podría no ser comparable con la de la imagen completa. Hipótesis: un umbral distinto para cada fuente sube el F1. Se valida con las mismas 5 particiones, comparando contra un umbral único elegido de la misma forma.

Todo corre en CPU sobre las detecciones crudas que ya están en memoria (`dets_multi`, la variante ganadora de 2.9). Las anotaciones se usan sólo para medir.
