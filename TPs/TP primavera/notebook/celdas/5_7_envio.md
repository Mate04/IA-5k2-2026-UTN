### 5.7 Envío con `questions` (v3)

Las respuestas se agregan a las 20 filas de desarrollo. `questions_llm` sigue vacía hasta la Fase 6. Antes de escribir el CSV se valida todo lo que, según la página de evaluación, anula una fila:

- el schema;
- RLE consistente (los `counts` suman alto × ancho);
- referencias: todo `id` usado en `relations`, `extra_relations` o `evidence` existe en la misma escena.

Las tablas de resultados se guardan en `results/` para que el reporte cite los números desde archivos.
