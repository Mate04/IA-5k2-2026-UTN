### 5.3 Motor de ejecución

`ejecutar(consulta, escena)` resuelve la consulta con código sobre el SceneJSON y devuelve los campos que pide el schema:

- `answer`: frase legible.
- `normalized_answer`: el valor que se evalúa.
- `evidence`: los `id` de los objetos de **esa misma escena** que sustentan la respuesta.
- `confidence`: sale de las confianzas del detector, no de un modelo de lenguaje:
  - conteo: el promedio;
  - existencia: el máximo;
  - relación: el mínimo de los dos objetos;
  - si la pregunta es ambigua, se multiplica por la parte de la confianza total que se lleva la instancia elegida;
  - "no se detectó": 0,5, porque no detectar un objeto no prueba que no esté (EDA 1.5).

Además se agregan `status` (`ok`, `ambiguous`, `insufficient_information` o `unsupported`) y `alternatives` (las otras instancias candidatas). El schema permite campos adicionales.
