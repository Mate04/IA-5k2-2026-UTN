### 6.6 Conclusiones de la v4

Los valores de esta versión están en la tabla final de 6.5 (`results/resumen_v4.csv`) y en los CSV de `results/`. Lo que muestra cada experimento:

- **Detector (2.9):** la tabla `det_experimentos.csv` compara la línea base con OWLv2-large (E3), los sinónimos (E7) y las ventanas (E4), cada uno con su mejor k y umbral. La configuración elegida es la de mayor F1 en desarrollo, y el recall por tamaño muestra si la mejora vino de los objetos chicos, como decía la hipótesis.
- **Segmentación (3.3b):** `seg_experimentos.csv` compara SAM2 small y large con las mismas cajas. El oráculo (`seg_oraculo.csv`) mide cuánto pierde SAM2 por sí solo con cajas perfectas, y así separa los errores del detector de los del segmentador.
- **Modo LLM (Fase 6):** la interpretación se mide contra los campos estructurados, y la exactitud final contra la escena real. Las dos respuestas salen del mismo motor, así que cuando la interpretación es correcta, la respuesta del modo LLM es idéntica a la determinista: los errores restantes son de percepción, no del LLM.
- **Control del LLM:** ninguna redacción se acepta sin pasar el control con código. Las que fallan quedan registradas en `traza_llm.csv` con la salida cruda, y se reemplazan por la plantilla.

**Límites.** El umbral y la configuración se eligen sobre las mismas 120 imágenes en las que se miden, así que el F1 de desarrollo es algo optimista. La validación cruzada del umbral queda para la próxima versión.
