### 5.4 Respuestas del benchmark (20 imágenes de desarrollo)

Cada consigna de `questions_dev.jsonl` pasa por el parser y el motor, sobre el SceneJSON que produjo la pipeline en la Fase 4. Cada respuesta queda en la traza, con su consulta, su tiempo y su estado. El ítem conserva `question_id`, `type` y `question` tal como los publica la cátedra, y agrega `query` para que se pueda auditar.
