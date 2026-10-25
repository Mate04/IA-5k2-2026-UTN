### 9.3 Dónde se cumple cada criterio de la consigna

| Criterio | Dónde está |
|---|---|
| EDA que fundamenta decisiones | 1.1 a 1.10 (tabla observación → decisión) |
| Detector open-vocabulary justificado (modelo, vocabulario, umbral, resolución, supresión de duplicados) | 2.2 a 2.9, con validación cruzada en la Fase 7 |
| F1 de detección ≥ 0,50 en desarrollo (IoU 0,5, reglas LVIS) | 2.9 (0,679) y 7.1 (0,673 ± 0,023 fuera de la muestra) |
| SAM2 con las cajas como prompt, RLE column-major | 3.1 a 3.3b |
| Propiedades, atributos y relaciones derivados de las máscaras | 3.4 y 3.6 |
| SceneJSON válido y consistente | 4.1, 4.2, 5.7 y 6.5 (schema, RLE e ids validados antes de escribir) |
| `questions` en modo determinista, con fidelidad medida | Fase 5 (5.5: exactitud y fidelidad) |
| `questions_llm`: el LLM sólo recibe el texto y arma la consulta; el motor determinista la ejecuta | Fase 6 |
| Ubicación, comparación, atributos y relaciones en los dos modos | 5.3, 5.6 y 6.4 |
| Manejo de ambiguas, no soportadas y sin información | 5.3, 5.6 y 6.4 (casos extra) |
| Traza que reconstruye la ejecución (parámetros, artefactos, errores) | 0, 4.1, 4.2, 8.3 y 9.2 (`manifiesto_corrida.json`) |
| Trazas usadas para evaluar las etapas y la propagación de errores | 8.1, 8.2 y 8.4 |
| Mejora contra una línea base con experimentos controlados | 2.7, 2.9, 3.3, 3.3b y 7.2 (E1 a E9, incluidos los que no mejoraron) |
| Casos correctos, ambiguos y fallidos | 5.5, 5.6, 6.4, 8.2 y 8.3 |
| Resultados en formatos auditables | `results/*.csv`, trazas y manifiesto; resumen en `results/resumen_final.csv` |
