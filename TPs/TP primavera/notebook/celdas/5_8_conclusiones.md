### 5.8 Conclusiones de la Fase 5

*Números de la configuración final (v5 y v6: OWLv2 base con ventanas y sinónimos, SAM2 large). Entre paréntesis, los de la v3 (OWLv2 base sola, SAM2 small).*

| Medida | Resultado |
|---|---|
| Consignas respondidas | 60 de 60: 51 `ok`, 6 `ambiguous`, 3 `insufficient_information` |
| Exactitud en preguntas cerradas (contra la escena real) | **0,775** (31 de 40) (v3: 0,75) |
| Exactitud por tipo | conteo 0,50 · existencia 0,90 · posición 1,00 (v3: 0,80) · relación 0,80 · tamaño 0,80 |
| Fidelidad al SceneJSON (verificador independiente) | **100 %** (60 de 60) |
| Casos extra bien manejados (105 preguntas) | ambiguas, atributo, fuera de alcance y fuera del vocabulario: 100 % · comparación 0,50 · proximidad 0,55 |
| Filas inválidas en el envío | 0 de 80 |

**Lectura.**
- **El motor no agrega errores.** La fidelidad es del 100 %: cada respuesta se puede leer tal cual del SceneJSON. Los 9 errores vienen de la percepción:
  - en 4 conteos faltan instancias;
  - en 3 preguntas (dos relaciones y un tamaño) la clase no se detectó y se respondió `unknown`;
  - en 1 conteo la clase no se detectó (`doorknob`: 0 contra 2);
  - en 1 existencia sobran instancias (`napkin`: el detector ve servilletas que no están anotadas).
- **El conteo es la operación más débil (0,50).** Para contar bien, el detector tiene que encontrar todas las instancias y ninguna de más. Es coherente con el recall de 0,65 de 2.9. Las comparaciones (0,50) heredan el mismo problema, porque comparan dos conteos, y la proximidad (0,55) falla sobre todo cuando una de las dos clases no se detectó.
- **No se inventa.** Las 3 respuestas `unknown` corresponden a clases que no se detectaron. Cuentan como error en la exactitud, pero el sistema declara que no tiene información en lugar de adivinar.
- **La mejora del detector se ve en QA:** con la configuración final la posición pasa de 0,80 a 1,00 (el banco del borde de zona ahora cae en la zona correcta) y la exactitud total sube de 0,75 a 0,775.
- **Límite del método de evaluación.** La referencia se calcula con nuestras reglas de tamaño y relaciones, porque la cátedra no publica las suyas. El puntaje oficial de QA puede diferir en las preguntas de tamaño y de relación.

La Fase 8 lleva cada uno de estos errores hasta la etapa exacta de la percepción donde se originó (umbral, detector, NMS o SAM2). Lo que sigue (Fase 6): la misma consulta intermedia, pero armada por un LLM a partir del texto solo, y ejecutada por este mismo motor.
