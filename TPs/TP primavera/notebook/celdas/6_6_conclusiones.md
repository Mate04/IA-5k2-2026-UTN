### 6.6 Conclusiones de la Fase 6

Los valores de esta corrida están en la tabla final de 6.5 (`results/resumen_corrida.csv`) y en `results/qa_llm_*.csv`. Comparación con la v5, la primera versión con el intérprete bilingüe:

| Medida | v5 | v6 |
|---|---|---|
| Clases escritas por el LLM exactamente como en el vocabulario | — | 55 de 60 |
| Interpretación correcta al primer intento (con la normalización del código) | 58 de 60 | 60 de 60 |
| JSON válido | 100 % | 100 % |
| Exactitud en preguntas cerradas | 0,725 | 0,775 (igual que el modo determinista) |
| Descripciones redactadas por el LLM, sin clases alucinadas | 20 de 20 | 20 de 20 |

**Lectura.**
- **El LLM interpreta casi todo bien por sí solo**, y el código cierra la brecha. En 5 de 60 consignas escribió la clase con otra forma (`wall_socket`, `baseball_cap`, `jeans`, `glasses`, `mango`) y la normalización la llevó al vocabulario, dejando registrado cómo (`traza_llm.csv`). Los dos errores de la v5 eran de este tipo y los corrigen el alias en inglés y el diccionario de sinónimos.
- **Esa mejora es optimista**, porque los dos arreglos se motivaron con estas mismas preguntas. La medida que no depende de ellos es la de clases exactas.
- **Con la interpretación correcta, los dos modos dan la misma respuesta:** las ejecuta el mismo motor. Por eso la exactitud del modo LLM queda igual a la determinista, y los errores restantes son de percepción (Fase 8).
- **El LLM nunca decide la respuesta.** Las redacciones que no conservan el valor del motor se reemplazan por la frase del motor, y las descripciones se aceptan sólo si nombran clases presentes con números sustentados en el resumen.
- **Casos extra:** ambiguas, atributos, fuera de alcance y fuera del vocabulario se manejan bien; comparación y proximidad heredan los errores de conteo de la percepción, igual que en el modo determinista.

**Límites.** El benchmark tiene sólo 60 consignas con redacciones muy regulares ("¿Cuántas instancias de la categoría...?"). Con preguntas más libres, la interpretación sería el eslabón más débil. El set extra de 5.6 lo prueba sólo en parte: agrega comparaciones, color y preguntas abiertas fuera de alcance, pero las demás también siguen plantillas.
