## 6. Modo con LLM (agregado en la v4)

Objetivo de la fase: que un **LLM liviano de texto** interprete la pregunta, sin los campos estructurados, y que el **mismo motor determinista** de la Fase 5 la resuelva sobre el SceneJSON predicho.

```
texto de la pregunta ─► Qwen2.5-3B ─► consulta JSON ─► normalización y validación (código) ─► motor ejecutar() ─► respuesta normalizada + evidencia
                                         └─ 1 reintento si el JSON no es válido                    └─► Qwen redacta la respuesta ─► control de fidelidad
resumen del SceneJSON (código) ─► Qwen redacta la descripción ─► control de alucinaciones ─► descripción + evidencia
```

**Qué recibe el LLM y qué no:**
- Recibe el **texto** de la pregunta, la lista de operaciones soportadas y el **vocabulario de 120 clases**, en inglés y con un nombre en español de un diccionario propio (`NOMBRES_ES_PROPIOS`, 5.6), que no se arma con los campos `class_es` de las preguntas. Es la configuración del sistema, no un dato de la pregunta.
- **No** recibe la imagen, las anotaciones ni los campos `type`, `class_en` y `class_es`. `type` se copia en la salida sólo porque el contrato del envío lo exige, y se usa después para **medir** la interpretación.
- Para describir la escena recibe un **resumen textual del SceneJSON predicho** que arma el código: conteos, zonas y tamaños.

**Qué decide el código, no el LLM:**
- Conteos, filtros, relaciones, comparaciones, `evidence` y `confidence` salen del motor de la Fase 5.
- La clase que propone el LLM se valida contra el vocabulario. Si no coincide exacto, el código prueba el singular, un diccionario español → inglés propio y una coincidencia aproximada, y registra cuál usó. Si nada coincide, la consulta queda `unsupported`: el código nunca reemplaza un objeto por otro parecido.
- La redacción del LLM se acepta sólo si conserva el valor del motor, y la descripción sólo si nombra clases que están en la escena. Si no, se usa la plantilla y la traza lo registra.

**Modelo:** `Qwen/Qwen2.5-3B-Instruct` en fp16 con decodificación greedy, así la corrida es reproducible. Es liviano (3 000 millones de parámetros), entra en una T4 junto con la percepción y maneja bien español y JSON.
