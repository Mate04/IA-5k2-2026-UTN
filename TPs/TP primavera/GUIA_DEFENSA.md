# Guía de defensa – Grupo 5

Para que los cuatro puedan explicar cualquier parte. Los números son los de la configuración final (ver `REPORTE.md`).

## Guion de 10 minutos

| Min | Tema | Qué mostrar |
|---|---|---|
| 0–1 | El problema y la arquitectura | Diagrama del §1 del reporte: imagen → OWLv2 → SAM2 → SceneJSON → preguntas en dos modos |
| 1–2 | EDA → decisiones | 54 % de objetos chicos, 94 % de pares imagen-clase no evaluables (LVIS), 1 instancia en las preguntas de posición |
| 2–4 | Percepción y experimentos | Tabla E1–E9: qué se probó, qué entró y qué no (large, ensamble, caja de la máscara, umbral por fuente) |
| 4–5 | Validación cruzada | 0,673 ± 0,023 contra 0,679: el F1 de desarrollo es confiable |
| 5–7 | Preguntas | Consulta intermedia común, motor único, políticas (ambigua, unknown, unsupported); el LLM sólo interpreta y redacta |
| 7–9 | Trazas y propagación | Tabla de 8.1 (dónde se pierde cada objeto) y la reconstrucción de 8.3 |
| 9–10 | Conclusión | El cuello de botella es la calibración del detector; trabajo futuro |

## Preguntas probables

### Datos y métrica
- **¿Por qué la precisión parece alta si hay tantos falsos positivos posibles?** Por LVIS federado: una predicción de una clase no verificada en esa imagen se ignora. Por eso reportamos la **cobertura** (≈ 0,42: sólo 42 % de las predicciones es evaluable).
- **¿Qué es una categoría no exhaustiva?** Está presente pero puede tener instancias sin anotar: una predicción que no empareja con ninguna anotada se ignora en lugar de contarse como FP.
- **¿El F1 es micro o macro?** Micro: sumamos TP, FP y FN de todas las imágenes y clases antes de calcularlo.
- **¿Cómo se empareja?** Por imagen y clase, de mayor a menor confianza, con la caja real de mayor IoU todavía libre; IoU ≥ 0,5 es TP.

### Detección
- **¿Por qué OWLv2 base y no large?** Lo medimos (E3): large dio 0,624 contra 0,666 con el mismo barrido, y el ensamble tampoco sumó (E8).
- **¿Qué hacen las ventanas?** Cuatro recortes de 60 % × 60 % en las esquinas, que se solapan en el centro. OWLv2 los reescala a 960 px, así que los objetos se ven 1,7 veces más grandes por lado (2,8 veces en área). Se descartan las cajas que tocan un borde interno (objeto cortado) y el NMS une duplicados con la imagen completa.
- **¿Qué es k?** Cuántas clases puede recibir cada caja (las de mayor puntaje). Con k = 1 una persona perdía contra "camisa"; con k > 1 la caja puede ser las dos cosas.
- **¿Cómo se eligió el umbral?** Máximo F1 en desarrollo con paso 0,01 y validado con 5 particiones: en todas el óptimo quedó entre 0,22 y 0,25.
- **¿Por qué NMS por clase a 0,5?** En el EDA, sólo el 0,5 % de los pares reales de la misma clase se solapa más que eso: casi no borra objetos reales (en 8.1, el NMS pierde 14 de 1790).

### Segmentación y representación
- **¿Qué recibe SAM2?** La imagen y la caja del detector como prompt. No sabe qué clase es.
- **¿Qué es RLE column-major?** Corridas alternadas de ceros y unos recorriendo la máscara por columnas (orden Fortran), empezando por ceros. Lo verificamos con el ejemplo oficial, con 200 máscaras al azar y con `pycocotools`.
- **¿Qué es observado y qué es derivado?** Observado: clase, confianza, caja y máscara (salen de modelos). Derivado: centroide, área, zona, tamaño, relaciones, color y oclusión (los calcula código desde la máscara). Desconocido: lo que se responde como `unknown` o `unsupported`.
- **¿De dónde salen los umbrales de tamaño?** De COCO (32² y 96² px), porque el dataset viene de COCO/LVIS. La cátedra no publica los suyos: es una decisión propia y documentada.

### Preguntas
- **¿Qué hace el LLM y qué no?** Recibe sólo el texto y devuelve una consulta JSON; redacta la respuesta y la descripción. No ve la imagen ni los campos estructurados, no cuenta ni filtra: eso lo hace el motor.
- **¿Cómo se evita que invente?** La consulta se valida contra un schema y el vocabulario; la redacción se acepta sólo si conserva el valor del motor; la descripción, sólo si las clases nombradas están en la escena y los números en el resumen. Si no, se usa la plantilla.
- **¿Qué pasa con una pregunta ambigua?** Se responde por la instancia de mayor confianza, `status = ambiguous`, las otras van en `alternatives` y la confianza se reparte.
- **¿Y si la clase no se detectó?** Conteo 0 y existencia "no" con confianza 0,5 (no detectar no prueba ausencia); para zona, tamaño, color y relación, `unknown`.
- **¿Cómo se midió la exactitud sin las respuestas de la cátedra?** Corriendo el mismo motor sobre una escena armada con las anotaciones. La fidelidad la mide un verificador independiente que recalcula cada respuesta desde el SceneJSON.
- **¿Por qué el conteo da 0,50?** Contar bien exige encontrar todas las instancias y ninguna de más. Los errores son de percepción: en 8.2 se ve la etapa de cada objeto que faltó.

### Trazas y errores
- **¿Cómo reconstruyen un resultado?** Con el `run_id` del SceneJSON se va al manifiesto (configuración y hash); `traza_envio.csv` tiene cada módulo de esa imagen; `traza_objetos.csv`, de qué detección sale cada objeto de la evidencia; `traza_llm.csv`, la salida cruda del LLM y la normalización. Demo en 8.3.
- **¿Dónde se pierden los objetos?** 60 % bien; 25 % tienen la caja correcta debajo del umbral; 7 % nadie los localiza (casi todos chicos); 5 % tienen mala máscara; NMS y emparejamiento, menos del 2 %.
- **Entonces, ¿por qué no bajan el umbral?** Porque entran más falsos positivos que objetos recuperados: con 0,18 el F1 cae a 0,650. Hace falta calibrar la confianza por clase.

### Reglas del TP
- **¿Usaron las anotaciones para inferir?** No. `procesar_imagen()` recibe sólo la imagen y el vocabulario; las anotaciones se usan en el EDA y para medir. Se puede probar con una foto nueva.
- **¿Es reproducible?** Semilla fija, decodificación greedy, versiones y configuración en el manifiesto, y todo corre en Kaggle sin archivos externos.
