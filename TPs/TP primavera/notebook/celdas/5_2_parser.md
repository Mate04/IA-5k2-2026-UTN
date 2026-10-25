### 5.2 Parser determinista

En modo determinista la cátedra entrega `type` y `class_en` junto con la pregunta, así que la consulta sale casi directa de esos campos. Hay un dato que **no viene estructurado**: en las preguntas de relación, cuál es la relación ("por encima de", "a la derecha de"…). Ese predicado se lee del texto con expresiones regulares, sin LLM. Lo mismo vale para el comparador de las preguntas `compare` ("más", "menos").
