### 5.5 Evaluación: exactitud y fidelidad

Las respuestas de referencia de la cátedra son privadas. Para medir localmente armamos la **escena de ground truth** de cada imagen a partir de las anotaciones: máscaras reales con las mismas reglas de propiedades, relaciones y atributos. Después corremos **el mismo motor** sobre esa escena. Las anotaciones se usan sólo acá, para evaluar.

Se miden tres cosas distintas:
- **Exactitud:** ¿la respuesta coincide con la que da la escena real? Mide la pipeline completa (percepción + motor). Supuesto: la cátedra no publica cómo define tamaño y relaciones, así que la referencia usa nuestras reglas (3.4).
- **Fidelidad:** ¿la respuesta se puede leer tal cual del SceneJSON predicho? Un verificador independiente del motor recalcula cada respuesta desde el JSON y chequea que la evidencia exista. Mide que el motor no invente.
- **Origen del error:** cuando una respuesta falla, ¿el problema está en la percepción (objeto no detectado, conteo distinto, otra instancia) o en el motor?
