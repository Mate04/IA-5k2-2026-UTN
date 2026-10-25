### 5.6 Preguntas extra: ambigüedad, atributos, comparación y fuera de alcance

El benchmark no tiene preguntas ambiguas, de color, de comparación ni fuera de alcance. Para probar esos casos armamos un set extra sobre las mismas 20 imágenes. Se genera **por código**, para que sea reproducible y sin etiquetado manual:

- **Ambigua (posición):** la clase con más instancias reales en la imagen.
- **Atributo (color):** una clase con una sola instancia real.
- **Comparación:** las dos clases más frecuentes ("¿hay más A que B?").
- **Proximidad (`near`):** el par formado por esas dos clases.
- **Fuera de alcance:** preguntas fijas sobre acciones, material o estado, más una clase que no está en el vocabulario.

Las anotaciones se usan sólo para **elegir** qué preguntar y para tener una referencia; el motor sigue leyendo únicamente el SceneJSON. Se evalúa si cada caso se maneja como corresponde: marcar la ambigüedad, responder `unsupported` cuando no hay forma de responder, y acertar las comparaciones y la proximidad. El set también se reutiliza en el modo LLM (Fase 6), así que cada pregunta trae su texto en español.
