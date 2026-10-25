### 6.2 Intérprete: del texto a la consulta intermedia

El prompt describe las operaciones del motor (las mismas de la Fase 5), incluye el vocabulario y trae ejemplos resueltos de cada intención. Los ejemplos usan **otras clases** que las del benchmark, para que el LLM aprenda el formato y no las respuestas.

Después, el **código** limpia la salida: toma el primer objeto JSON, se queda con las claves conocidas (cada una sólo en su intención: `predicate` sólo en `relation`, etc.), normaliza las clases y valida con `validar_query()` (5.1). La normalización prueba, en orden: nombre exacto, singular, **alias en inglés** (sinónimos que no son otra clase, por ejemplo `glasses` → `spectacles`), el **diccionario español → inglés propio** (con sinónimos y variantes regionales: `mango` y `manija` → `handle`, `heladera` → `refrigerator`…) y una coincidencia aproximada. Cada paso queda registrado en la traza.

**Reintentos (uno como máximo):**
- **Formato:** si el JSON no se puede leer o no cumple el formato, se le muestra el error al LLM.
- **Vocabulario (v6):** si el LLM propone una clase fuera del vocabulario pero la pregunta **nombra** un objeto que sí está (según el diccionario propio), es un posible error de traducción. Se le avisa cuáles objetos del vocabulario nombra la pregunta y el LLM decide. Si la segunda respuesta no es válida, se conserva la primera.

Una clase fuera del vocabulario **sin** ninguna mención en el texto (por ejemplo "unicornio") no se reintenta: `unsupported` es la respuesta correcta, y pedirle otra clase invitaría a que la reemplace por una parecida.

**Por qué se agregaron en la v6:** en la v5 hubo dos errores de interpretación, los dos por el nombre de la clase. En "gafas" el LLM escribió `glasses` (en el vocabulario, `spectacles`). En una pregunta sobre "mango" copió la palabra tal cual: es el nombre que usa la cátedra para `handle`, pero nuestro diccionario sólo tenía "manija". Las dos correcciones se motivaron con estas mismas preguntas, así que la interpretación final de la v6 es optimista. Por eso 6.4 mide tres cosas: si el LLM escribió las clases **exactamente** como en el vocabulario (sin ayuda del código), la interpretación al **primer intento** (con la normalización) y la **final** (con el reintento).
