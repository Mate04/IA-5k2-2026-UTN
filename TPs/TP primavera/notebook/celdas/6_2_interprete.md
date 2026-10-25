### 6.2 Intérprete: del texto a la consulta intermedia

El prompt describe las operaciones del motor (las mismas de la Fase 5), incluye el vocabulario y trae ejemplos resueltos de cada intención. Los ejemplos usan **otras clases** que las del benchmark, para que el LLM aprenda el formato y no las respuestas.

Después, el **código** limpia la salida: toma el primer objeto JSON, se queda con las claves conocidas, normaliza las clases y valida con `validar_query()` (5.1). Si el JSON no se puede leer o no cumple el formato, se le muestra el error al LLM y tiene **un reintento**. Una clase fuera del vocabulario no se reintenta: es la respuesta correcta para una pregunta fuera de alcance, y pedirle otra clase invitaría a que la reemplace por una parecida.
