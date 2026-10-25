### 5.8 Conclusiones de la Fase 5

| Medida | Resultado |
|---|---|
| Consignas respondidas | 60 de 60: 51 `ok`, 6 `ambiguous`, 3 `insufficient_information` |
| Exactitud en preguntas cerradas (contra la escena real) | **0,75** (30 de 40) |
| Exactitud por tipo | conteo 0,50 · existencia 0,90 · posición 0,80 · relación 0,80 · tamaño 0,80 |
| Fidelidad al SceneJSON (verificador independiente) | **100 %** (60 de 60) |
| Casos extra bien manejados | ambiguas, fuera de alcance y fuera del vocabulario: 100 % · comparación 0,40 · proximidad 0,60 |
| Filas inválidas en el envío | 0 de 80 |

**Lectura.**
- **El motor no agrega errores.** La fidelidad es del 100 %: cada respuesta se puede leer tal cual del SceneJSON. Los 10 errores vienen de antes:
  - 9 son de percepción: en 3 faltan instancias, en 3 la clase no se detectó y se respondió `unknown`, en 2 sobran instancias y en 1 la clase no se detectó en un conteo;
  - 1 es un borde de regla: el banco tiene el centroide sobre el límite entre `middle_left` y `center`.
- **El conteo es la operación más débil (0,50).** Para contar bien, el detector tiene que encontrar todas las instancias y ninguna de más. Es coherente con el recall de 0,61 de la Fase 2. Las comparaciones (0,40) heredan el mismo problema, porque comparan dos conteos.
- **No se inventa.** Las 3 respuestas `unknown` corresponden a clases que no se detectaron. Cuentan como error en la exactitud, pero el sistema declara que no tiene información en lugar de adivinar.
- **Límite del método de evaluación.** La referencia se calcula con nuestras reglas de tamaño y relaciones, porque la cátedra no publica las suyas. El puntaje oficial de QA puede diferir en las preguntas de tamaño y de relación.

Lo que sigue (Fase 6): la misma consulta intermedia, pero armada por un LLM a partir del texto solo, y ejecutada por este mismo motor.
