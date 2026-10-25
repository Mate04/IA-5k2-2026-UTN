### 6.4 Benchmark en modo LLM y evaluación

Las 60 consignas del benchmark y las preguntas extra de 5.6 pasan por el intérprete, el motor y la redacción. Medimos:

- **Interpretación:** ¿la consulta del LLM coincide con la que sale de los campos estructurados (intención, clases y predicado)? Es la exactitud del intérprete, aislada del resto de la pipeline.
- **JSON válido** al primer intento y después del reintento.
- **Exactitud final** contra la escena real (mismo criterio que 5.5) y **acuerdo** con el modo determinista. Si la interpretación es correcta, las dos respuestas tienen que ser idénticas, porque las ejecuta el mismo motor.
- **Descripciones:** cuántas pasaron el control de alucinaciones y qué parte de las clases principales de la escena nombran (cobertura).
- **Casos extra:** el mismo criterio de manejo de 5.6 (ambiguas, fuera de alcance, fuera del vocabulario, comparación y proximidad).

Cada paso queda en `traza_llm.csv`, con la salida cruda del LLM, los intentos, la normalización de clases y la redacción usada.
