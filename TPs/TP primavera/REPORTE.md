# TPI IA 2026 – Comprensión visual de escenas

| | |
|---|---|
| **Grupo** | 5 (equipo de Kaggle "G5 - 5k2") |
| **Integrantes** | Esmeralda Odar, Joaquín Bustos, Guille Contigiani, Mateo Elias Maldonado |
| **Notebook** | `TPI_IA_2026P_5` (Kaggle, con todas las salidas guardadas) |
| **Envío final** | versión v6 (versión 4 de la notebook en Kaggle, `run_id` 20261025-211049-720181) · PipelineScore público **0,7049** (historial en §4.1) |
| **Fecha** | noviembre de 2026 |

Todos los números de este reporte salen de los archivos que guarda la notebook en `results/` (se indica el archivo en cada tabla) y corresponden a la corrida final, identificada por su `run_id` en `manifiesto_corrida.json`.

---

## 1. Resumen

La pipeline transforma una imagen en un **SceneJSON** observable y consultable, sin mirar anotaciones:

```
imagen ─► OWLv2 base (imagen completa + 4 ventanas, 120 clases + sinónimos, k = 3 clases por caja)
       ─► NMS por clase 0,5 + umbral 0,25 ─► SAM2.1 large (caja como prompt) ─► RLE column-major
       ─► propiedades derivadas (centroide, área, zona 3×3, tamaño, relaciones, color, oclusión, near)
       ─► SceneJSON validado (schema + RLE + ids) ─► preguntas:
            · modo determinista: campos estructurados ─► consulta JSON ─► motor
            · modo LLM: texto ─► Qwen2.5-3B ─► consulta JSON validada ─► el mismo motor ─► redacción con control
```

| Etapa | Métrica (desarrollo) | Valor | Archivo |
|---|---|---|---|
| Detección | F1 de cajas, IoU 0,5, reglas LVIS | **0,679** (P 0,716 · R 0,646) | `det_experimentos.csv` |
| Detección | F1 en validación cruzada de 5 particiones | **0,673 ± 0,023** | `det_validacion_cruzada.csv` |
| Segmentación | F1 de máscaras | **0,645** | `seg_experimentos.csv` |
| QA determinista | exactitud en preguntas cerradas · fidelidad al JSON | **0,775** · 100 % | `qa_det_exactitud.csv`, `qa_det_fidelidad.csv` |
| QA con LLM | clases escritas exactas por el LLM · interpretación correcta (con la normalización) · exactitud | 91,7 % · 100 % · **0,775** | `qa_llm_respuestas.csv` |
| Descripción con LLM | aceptadas por el control · clases alucinadas | 20 de 20 · 0 | `qa_llm_descripciones.csv` |
| Envío | filas válidas | 80 de 80 | `submission.csv` |

Los dos umbrales de F1 de detección (0,40 para aprobar y 0,50 para promocionar) se superan con margen también en validación cruzada.

---

## 2. Análisis del dataset

Cada observación del EDA (Fase 1 de la notebook) motivó una decisión:

| Observación | Decisión |
|---|---|
| 120 imágenes y 1790 objetos: 14,9 por imagen (mediana 10,5; máximo 66), entre 3 y 8 clases por imagen | El tope de 300 objetos del schema no limita; no se filtra por cantidad |
| **El 54 % de los objetos es chico** (< 32² px); la mediana ocupa el 0,29 % de la imagen | Detector fuerte en objetos chicos (OWLv2) y, después, ventanas ampliadas (E4) |
| 120 clases, ninguna domina: las 10 más frecuentes suman el 20 % | Vocabulario completo; no conviene descartar clases raras |
| **El 93,9 % de los pares imagen-clase no es evaluable** (LVIS federado): sólo 118 negativos verificados y 6 % de positivos no exhaustivos | Métrica local con las reglas LVIS y reporte de la **cobertura**; un FP de una clase no verificada no penaliza, pero los duplicados sí |
| Sólo el 0,5 % de los pares de objetos de la misma clase tiene IoU > 0,5 | NMS por clase con IoU 0,5: casi no borra objetos reales |
| Los centros se reparten en las 9 zonas (19 % en `center`, todas ≥ 7 %) | Grilla 3×3 por centroide sin correcciones |
| En las preguntas de posición, tamaño y relación la clase tiene **exactamente 1 instancia real**; en conteo, entre 2 y 4; la mitad de las de existencia son "no" | Ante varias instancias predichas se responde por la de mayor confianza y se marca `ambiguous`; en existencia importa la precisión |
| Las cajas de `annotations.json` están en `[x, y, ancho, alto]` | Internamente se usa ese formato; el SceneJSON exige `[xmin, ymin, xmax, ymax]` (lección del primer envío, rechazado) |

---

## 3. Metodología

### 3.1 Percepción

| Decisión | Elección | Justificación |
|---|---|---|
| Detector | `google/owlv2-base-patch16-ensemble` | Open-vocabulary, las 120 clases en una pasada, bueno en objetos chicos. Large rindió peor (E3) |
| Vocabulario | las 120 clases de `categories.csv`, prompt `"a photo of a {clase}"`, más sinónimos para 22 clases (`person` → man / woman / child, `fireplug` → fire hydrant…) | El puntaje de una clase es el máximo entre sus consultas (E7) |
| Resolución | 960 px (la de OWLv2 base) en la imagen completa + 4 ventanas de 60 % × 60 % que se solapan | Cada ventana se reescala a la entrada de OWLv2: los objetos se ven 1,7 veces más grandes por lado (E4); se descartan las cajas cortadas por el borde interno de la ventana |
| Clases por caja | k = 3 | Una caja puede ser "persona" y "camisa" a la vez (E1) |
| Duplicados | NMS por clase con IoU 0,5 sobre imagen + ventanas | EDA 1.6 |
| Umbral | 0,25, elegido por máximo F1 y validado con 5 particiones (§4.3) | — |
| Segmentación | `facebook/sam2.1-hiera-large`, la caja del detector como prompt | +20 puntos de F1 sobre la caja rellena (E2) y +0,8 sobre small (E6) |
| Máscara en el JSON | RLE no comprimido, column-major, verificado con 3 tests (ejemplo oficial, 200 máscaras al azar y `pycocotools`) | Requisito del schema |

### 3.2 Representación: observado, derivado y desconocido

| Tipo | Campos | Origen |
|---|---|---|
| **Observado** (salida de un modelo) | `category_id`, `confidence`, `bbox`, `mask` | OWLv2 y SAM2 |
| **Derivado** (calculado con código desde la máscara) | `centroid`, `area_ratio`, `position` (zona del centroide), `size` (COCO: < 32², < 96², ≥ 96²), `relations` (centroides con margen del 5 %; `overlaps` con IoU de máscara > 0,01), `attributes.color` (HSV en 12 nombres dentro de la máscara erosionada), `attributes.occlusion` (fracción de la caja tapada por otras máscaras), `attributes.touches_border`, `extra_relations` (`near`: separación ≤ 2 % de la diagonal) | Reglas propias, documentadas en 3.4 y 3.6 |
| **Desconocido** | respuestas `unknown` (`insufficient_information`) y `unsupported` | Clase no detectada, clase fuera del vocabulario u operación no soportada |

Los umbrales de tamaño y la definición de las relaciones no están publicados por la cátedra: son decisiones propias. El color es un **atributo aproximado** (sin ground truth; plausibilidad ≈ 0,55 en clases de color esperable) y su respuesta va acompañada de `color_ratio`.

Cada SceneJSON se valida antes de escribirse: schema, RLE consistente (los `counts` suman alto × ancho), cajas con `0 ≤ xmin < xmax`, y que todo id usado en `relations`, `extra_relations` y `evidence` exista. Si algo falla, la fila sale como escena vacía válida en lugar de invalidar el envío. Hay topes de 300 objetos y 20 000 relaciones (la imagen más cargada llegó a 17 206).

### 3.3 Preguntas

**Contrato común.** Los dos modos producen la misma **consulta intermedia** (`intent`, `classes`, `predicate`, `attribute`, `comparator`), validada con JSON Schema y con reglas semánticas (cantidad de clases por intención, clases del vocabulario). La ejecuta un único **motor determinista** que lee sólo el SceneJSON predicho y devuelve `answer`, `normalized_answer`, `evidence` (ids de la misma escena), `confidence` (derivada de las confianzas del detector), `status` y `alternatives`.

Operaciones: `count`, `existence`, `position`, `size`, `relation` (6 predicados), `attribute` (color), `compare` (más / menos / igual) y `description`.

| Caso | Política |
|---|---|
| Varias instancias (ambigua) | Se responde por la de mayor confianza, `status = ambiguous`, las demás en `alternatives`, y la confianza se reparte |
| Clase no detectada | Conteo 0 y existencia "no" con confianza 0,5 (no detectar no prueba ausencia); en posición, tamaño, atributo y relación, `unknown` |
| Fuera de alcance o del vocabulario | `unsupported`, con el motivo |

**Modo determinista.** La consulta sale de los campos `type` y `class_en`; el predicado o el comparador se leen del texto con expresiones regulares. La descripción es una plantilla con conteos, zonas y el objeto más grande.

**Modo LLM (Qwen2.5-3B-Instruct, fp16, greedy).** El intérprete recibe **sólo el texto** de la pregunta, más la lista de operaciones y el vocabulario (en inglés, con un nombre en español de un diccionario propio, no de los campos de la cátedra). El código toma el primer JSON, normaliza las clases (exacta → singular → alias en inglés → diccionario español → coincidencia aproximada) y valida. Hay un reintento como máximo, por formato inválido o cuando la clase propuesta no está en el vocabulario pero la pregunta nombra una que sí (posible error de traducción). El motor es el mismo de la Fase 5. El LLM redacta la respuesta, y un control con código la acepta sólo si conserva el valor del motor; si no, se usa la frase del motor. Para describir, el LLM recibe un resumen textual del SceneJSON y un control de alucinaciones exige que toda clase nombrada esté en la escena y que todo número esté en el resumen; si falla dos veces, se usa la plantilla.

### 3.4 Trazabilidad

| Artefacto | Contenido |
|---|---|
| `manifiesto_corrida.json` | `run_id`, `config_hash` (SHA-256 de toda la configuración: percepción, LLM, prompts y semilla), versiones del entorno, tiempos por fase y lista de artefactos con tamaño y SHA-256 |
| Campo `trace` de cada SceneJSON | `run_id` y hash de la configuración de percepción: cada fila del envío queda atada a su corrida |
| `traza_envio.csv` | imagen × módulo: parámetros, inicio, duración, estado, salidas y error |
| `traza_objetos.csv` | linaje de cada objeto: confianza, rango de la clase en su caja, fuente (imagen o ventana), caja del detector, segmentador, píxeles de la máscara y uso de la caja de respaldo |
| `traza_qa.csv`, `traza_llm.csv` | consulta ejecutada; en el modo LLM, salida cruda, reintentos y motivo, normalización de clases y redacción usada |

En 8.3 la notebook reconstruye una respuesta completa leyendo sólo estos archivos: pregunta → consulta → evidencia → linaje de cada objeto → módulos de percepción → configuración.

---

## 4. Resultados

### 4.1 Historial de envíos

| Versión | Cambio principal | PipelineScore público |
|---|---|---|
| v1 | Fases 1 a 4 | rechazada: cajas en `[x, y, w, h]` |
| v2 | Cajas en `[xmin, ymin, xmax, ymax]` | 0,6229 |
| v3 | Atributos, `questions` determinista, validación de filas | 0,6656 |
| v4 | Ventanas + sinónimos, SAM2 large, `questions_llm` con Qwen2.5-3B | 0,7022 |
| v5 | Vocabulario bilingüe en el intérprete, ejemplos en la redacción | 0,7028 |
| v6 | Traza completa, alias y sinónimos en el intérprete, validación cruzada y propagación | **0,7049** |

QA aporta el 10 % del puntaje: el salto de la v2 a la v3 (+0,043) es casi todo `questions`; el de la v3 a la v4 (+0,037), la mejora del detector y `questions_llm`. La v6 deja la percepción igual que la v5 y suma +0,002 por el modo LLM: con la interpretación corregida, sus respuestas pasan de 0,725 a 0,775 de exactitud en desarrollo.

### 4.2 Experimentos controlados (una variable por vez, mismas 120 imágenes y misma métrica)

| # | Hipótesis | Línea base → alternativa | Resultado | Decisión |
|---|---|---|---|---|
| E1 | Varias clases por caja recuperan objetos tapados por clases que se solapan | k = 1 → k = 2 | F1 0,646 → 0,660 (+49 TP, +35 FP) | ✅ k > 1 |
| E2 | SAM2 aporta sobre la caja rellena | caja → SAM2 small | F1 de máscaras 0,422 → 0,620 | ✅ SAM2 |
| E3 | Un backbone más grande ve mejor | OWLv2 base → large | F1 0,666 → 0,624 | ❌ queda base |
| E7 | Sinónimos para nombres raros de LVIS y para `person` | sin → con sinónimos | F1 0,666 → 0,673 | ✅ |
| E4 | Ventanas estilo SAHI suben el recall en chicos | sin → con 4 ventanas | F1 0,666 → 0,674; con sinónimos, **0,679**; recall en chicos 0,487 → 0,519 | ✅ |
| E8 | Ensamble con large suma objetos distintos | ventanas + sinónimos → + large | F1 0,679 → 0,676 | ❌ |
| E6 | SAM2 más grande da mejores máscaras | SAM2.1 small → large | F1 de máscaras 0,637 → 0,645 | ✅ large |
| — | La caja de la máscara es más ajustada que la del detector | caja del detector → caja de la máscara | F1 de cajas 0,679 → 0,672 | ❌ |
| E5 | Con cajas perfectas SAM2 casi no pierde (oráculo) | cajas reales como prompt | IoU medio 0,789; 90,3 % con IoU ≥ 0,5 (chicos 84,7 %, medianos 97,0 %, grandes 96,9 %) | Diagnóstico: el cuello de botella es el detector |
| E9 | Un umbral distinto para las cajas de las ventanas | umbral único → umbral por fuente, ambos elegidos por validación cruzada | F1 de prueba 0,674 → 0,674 (+0,001; mejora en 2 particiones, empeora en 1) | ❌ no justifica el parámetro extra |

Archivos: `det_experimentos.csv`, `seg_experimentos.csv`, `seg_oraculo.csv`, `det_umbral_por_fuente.csv`. Cada variante de detector se mide con su mejor k y umbral, para que ninguna salga perjudicada por un umbral elegido para otra.

### 4.3 Validación cruzada de la configuración del detector

El umbral y k se eligieron sobre las mismas imágenes en las que se mide el F1. Para estimar cuánto de eso es ajuste al azar, se repitió la elección en 5 particiones por imagen (96 para elegir, 24 para medir):

| Medida | Valor |
|---|---|
| F1 en las particiones de prueba (media ± desvío) | **0,673 ± 0,023** |
| F1 dentro de la muestra (configuración final) | 0,679 → optimismo ≈ 0,006 |
| Umbral elegido en cada partición | entre 0,22 y 0,25 (k = 3 en 4 de 5) |
| F1 con umbrales a ±0,03 del final | entre 0,671 y 0,679 |

La configuración es estable: el óptimo casi no se mueve entre particiones y el F1 cae poco cerca del umbral elegido. El desvío entre particiones (0,023) es cuatro veces mayor que el optimismo, así que diferencias de menos de ~0,01 entre variantes (E7, E4, E8) no son concluyentes por sí solas (`det_validacion_cruzada.csv`, `det_curva_umbral.csv`).

### 4.4 Preguntas en modo determinista

| Medida | Resultado |
|---|---|
| Exactitud en preguntas cerradas (contra la escena armada con las anotaciones) | **0,775** (31 de 40): conteo 0,50 · existencia 0,90 · posición 1,00 · relación 0,80 · tamaño 0,80 |
| Fidelidad al SceneJSON (verificador independiente del motor) | **100 %** (60 de 60) |
| Estados | 51 `ok`, 6 `ambiguous`, 3 `insufficient_information` |
| Casos extra (105 preguntas generadas por código) | ambigua, atributo, fuera de alcance y fuera del vocabulario: 100 % · comparación 0,50 · proximidad 0,55 |

La referencia se calcula corriendo **el mismo motor** sobre una escena armada con las anotaciones (máscaras reales y nuestras reglas de propiedades). Como la cátedra no publica sus reglas de tamaño y relaciones, el QA oficial puede diferir en esos tipos.

### 4.5 Preguntas y descripción con LLM

| Medida | v5 | v6 (final) |
|---|---|---|
| Clases escritas por el LLM exactamente como en el vocabulario | — | 91,7 % (55 de 60) |
| Interpretación correcta (consulta del LLM, normalizada por el código = consulta de los campos estructurados) | 96,7 % (58 de 60) | 100 % al primer intento, sin reintentos |
| JSON válido | 100 % | 100 % |
| Exactitud en preguntas cerradas | 0,725 | 0,775 |
| Misma respuesta que el modo determinista | 95 % | 100 % |
| Redacción aceptada por el control | 80 % | 82,5 % |
| Descripciones redactadas por el LLM · clases alucinadas · cobertura de las 3 clases principales | 20 de 20 · 0 · 0,98 | 20 de 20 · 0 · 0,98 |
| Casos extra bien manejados | ambigua 0,95 · atributo 1,00 · fuera de alcance 1,00 · fuera del vocabulario 1,00 · comparación 0,45 · proximidad 0,55 | ambigua 1,00 · atributo 1,00 · fuera de alcance 1,00 · fuera del vocabulario 1,00 · comparación 0,50 · proximidad 0,55 |

Cuando la interpretación es correcta, la respuesta del modo LLM es idéntica a la determinista, porque la ejecuta el mismo motor. Los dos errores de interpretación de la v5 fueron por el nombre de la clase: en "gafas" el LLM escribió `glasses` (en el vocabulario, `spectacles`), y en una pregunta sobre "mango" copió la palabra, que es el nombre de la cátedra para `handle` pero no estaba en nuestro diccionario (tenía "manija"). La v6 agrega alias en inglés y sinónimos en español, y los dos se resuelven en la normalización, sin reintento. Como las correcciones se motivaron con estas mismas preguntas, el 100 % es optimista: la medida que no depende de ellas es el 91,7 % de clases que el LLM escribió exactamente como en el vocabulario.

---

## 5. Discusión y análisis de errores

### 5.1 ¿Dónde se pierde cada objeto real?

La traza permite seguir cada uno de los 1790 objetos reales de desarrollo por la cadena detector → umbral → NMS → emparejamiento → SAM2, y asignarlo a la primera etapa donde se pierde (`propagacion_objetos.csv`):

| Etapa | Objetos | % | Chicos | Medianos | Grandes |
|---|---|---|---|---|---|
| **OK** (caja y máscara correctas) | 1073 | 59,9 | 459 | 440 | 174 |
| Máscara mala (SAM2, IoU < 0,5) | 83 | 4,6 | 64 | 12 | 7 |
| Caja usada por otro objeto | 16 | 0,9 | 10 | 4 | 2 |
| Eliminado por NMS | 14 | 0,8 | 10 | 1 | 3 |
| **Debajo del umbral** (su clase tiene caja, con confianza < 0,25) | 453 | 25,3 | 299 | 117 | 37 |
| Localizado con otra clase | 31 | 1,7 | 14 | 14 | 3 |
| No localizado (ninguna caja con IoU ≥ 0,5) | 120 | 6,7 | 111 | 9 | 0 |

Lectura:
- **El principal problema es de calibración, no de localización.** Un cuarto de los objetos tiene una caja correcta de su clase, pero con confianza menor que el umbral (mediana 0,17). Bajar el umbral no lo arregla: el F1 cae (0,650 con umbral 0,18, `det_curva_umbral.csv`) porque entran más falsos positivos que objetos recuperados. Haría falta un puntaje mejor calibrado por clase: `car`, `book`, `shoe`, `chair` y `wheel` son las que más pierden así, y `book` y `shoe` siguen con recall de cajas de 0,07 y 0,19. En cambio, `person` pasó de 0,03 en la línea base de la Fase 2 a 0,55 con la configuración final (sinónimos, ventanas y varias clases por caja).
- **Los objetos chicos concentran casi todas las pérdidas:** 111 de los 120 no localizados y 64 de las 83 máscaras malas. Coincide con el oráculo de SAM2 (E5): con cajas reales, el 84,7 % de las máscaras de objetos chicos tiene IoU ≥ 0,5, contra el 97 % en medianos y grandes.
- **SAM2 pierde poco:** de los 1156 objetos con caja correcta, el 93 % tiene también máscara correcta (IoU medio 0,80). La diferencia entre F1 de cajas (0,679) y de máscaras (0,645) es chica y está en los objetos chicos.
- **NMS y emparejamiento son marginales** (1,7 % entre ambos): el NMS por clase a 0,5 es seguro, como anticipaba el EDA.

### 5.2 ¿De dónde viene cada respuesta incorrecta?

Cada error de QA se lleva hasta la etapa que lo causó (`propagacion_qa.csv`):

| Etapa de origen | Determinista | LLM |
|---|---|---|
| Interpretación del LLM | — | 0 |
| Percepción: debajo del umbral | 6 | 6 |
| Percepción: localizado con otra clase | 1 | 1 |
| Percepción: no localizado | 1 | 1 |
| Percepción: falso positivo del detector | 1 | 1 |
| Segmentación o regla derivada | 0 | 0 |
| **Total** | **9** | **9** |

Si los objetos que faltan en una respuesta se perdieron en etapas distintas, se cuenta la que explica más objetos (y, si empatan, la más temprana). De los 11 objetos reales que faltan en estas respuestas, 8 quedaron debajo del umbral, y el único falso positivo son 3 servilletas en una imagen que las tiene verificadas como ausentes, todas de las ventanas y con confianza de 0,26 a 0,29. Para el QA, la palanca es la misma que para el F1: la calibración del detector.

Ningún error es del motor: la fidelidad es del 100 % y, cuando la interpretación es correcta, los dos modos coinciden.

### 5.3 Casos correctos, ambiguos y fallidos

| Caso | Pregunta | Qué pasó |
|---|---|---|
| Correcto | DEV-11-Q2: ¿en qué zona está el teléfono celular? | Una sola instancia detectada, centroide en `bottom_left`: coincide con la referencia en los dos modos |
| Correcto con ambigüedad | DEV-20-Q2: zona de la tabla de surf | Hay 2 tablas predichas y 1 real: se responde por la de mayor confianza (`middle_right`, correcta), `status = ambiguous`, la otra en `alternatives` y la confianza repartida |
| Declarado como desconocido | DEV-25-Q2: tamaño del elefante | El elefante no se detectó: el sistema responde `unknown` en lugar de inventar un tamaño. Cuenta como error, pero es una respuesta sustentada |
| Fallido por percepción | DEV-4-Q1: ¿cuántos pantalones? | Responde 2, hay 4: uno de los que faltan se detectó con otra clase y el otro quedó debajo del umbral (8.2) |
| Fallido por falso positivo | DEV-23-Q1: ¿hay servilletas? | Responde "sí": el detector ve 3 servilletas, y la imagen tiene `napkin` verificada como ausente |
| Fuera de alcance | "¿Qué está haciendo la persona?" | El intérprete devuelve `unsupported` (acción) y no se ejecuta nada |
| Interpretación corregida por el código | DEV-10-Q1: ¿cuántas instancias de "mango"? | El LLM devuelve `mango`; en la v5 quedaba `unsupported`. En la v6 el diccionario de sinónimos lo lleva a `handle` y la respuesta (2) es correcta. 8.3 reconstruye esta cadena desde las trazas |

### 5.4 Intentos que no mejoraron

- **OWLv2 large** (E3): peor que base con el mismo barrido (0,624 contra 0,666), y el ensamble con base tampoco suma (E8). No es lo que esperábamos de un backbone más grande; no investigamos la causa y queda como resultado negativo documentado.
- **Caja sacada de la máscara**: empeora el F1 de cajas (0,672 contra 0,679), así que la caja del SceneJSON sigue siendo la del detector.
- **Umbral por fuente** (E9): +0,001 en validación cruzada, con resultados mezclados entre particiones; no compensa el parámetro extra.
- En conjunto, lo que mejoró el F1 fue cambiar **lo que ve** el detector (ventanas, sinónimos, varias clases por caja), no filtrar distinto sus salidas.

### 5.5 Extensión principal: aporte y costo de las ventanas y los sinónimos

| | Línea base (OWLv2 base, imagen completa) | Final (+ 4 ventanas + sinónimos) |
|---|---|---|
| F1 de cajas en desarrollo | 0,666 | 0,679 (+0,013) |
| Recall en objetos chicos / medianos / grandes | 0,487 / 0,710 / 0,805 | 0,519 / 0,707 / 0,787 |
| Precisión | 0,697 | 0,716 |
| Tiempo del detector por imagen (`traza_envio.csv`) | ≈ 0,46 s (v2) | ≈ 2,4 s (5 pasadas de OWLv2) |
| Pipeline completa para las 80 imágenes del envío | 1,2 min (v2, con SAM2 small) | 4,9 min (con SAM2 large) |

- **Qué mejora:** el recall en objetos chicos (+0,032), que era el cuello de botella del EDA, y la precisión (0,697 → 0,716). Las cajas de las ventanas salen con más confianza que las de la imagen completa (son el 79 % de las detecciones que sobreviven al NMS), y el umbral óptimo sube de 0,185 a 0,25, que deja afuera falsos positivos.
- **Qué no mejora:** medianos y grandes (0,710 → 0,707 y 0,805 → 0,787), y 111 objetos chicos siguen sin ninguna caja.
- **Costo:** el detector pasa a ser 5 veces más caro y es el 66 % del tiempo de la pipeline. Con 3,7 s por imagen sigue siendo viable en Kaggle, pero 9 ventanas en lugar de 4 duplicarían las pasadas.
- **Cautela:** +0,013 de F1 está dentro del desvío entre particiones (0,023, §4.3). El leaderboard sí subió al adoptarla (v3 → v4, +0,037), aunque esa versión también agregó `questions_llm`, así que no se puede atribuir toda la suba al detector.

### 5.6 Limitaciones

- Todo se ajusta y se mide sobre 120 imágenes: las diferencias de menos de ~0,01 de F1 están dentro del ruido entre particiones.
- La referencia de QA usa nuestras reglas de tamaño y relaciones; el benchmark tiene sólo 40 preguntas cerradas (cada una vale 2,5 puntos de exactitud).
- El color es aproximado (reglas HSV, sin ground truth) y la oclusión es una estimación por cajas.
- La redacción del LLM sólo se acepta si pasa un control con código; cuando lo falla se usa la frase del motor, que es correcta pero menos natural.

---

## 6. Conclusiones y trabajo futuro

- La pipeline cumple los requisitos de promoción: F1 de detección 0,679 (0,673 en validación cruzada), máscaras de SAM2 usadas para todas las propiedades, SceneJSON válido en 80 de 80 filas, modo determinista con fidelidad del 100 %, modo LLM que interpreta y redacta sin reemplazar al motor, manejo explícito de ambigüedad y de lo no soportado, y traza completa usada para analizar la propagación de errores.
- **La percepción explica casi todos los errores**, y dentro de ella la **calibración** del detector: el 25 % de los objetos reales tiene la caja correcta debajo del umbral.
- **Trabajo futuro**, en orden de impacto esperado:
  1. Calibrar la confianza por clase (por ejemplo, regresión isotónica por clase con validación cruzada) o reentrenar la cabeza de clasificación de OWLv2 con las imágenes de desarrollo, evaluando en particiones separadas.
  2. Ventanas de 3×3 o a mayor resolución para los objetos chicos no localizados (111 de 120).
  3. Probar otros detectores open-vocabulary (Grounding DINO, YOLO-World) y ensambles con fusión de cajas (WBF) en lugar de NMS.
  4. Pedirle al LLM una redacción más libre con un control semántico en lugar de léxico.

---

## Anexo A. Modelos, recursos y código reutilizado

| Recurso | Uso | Origen |
|---|---|---|
| `google/owlv2-base-patch16-ensemble` (y `-large-patch14-ensemble` en E3/E8) | Detección open-vocabulary | Hugging Face, vía `transformers` |
| `facebook/sam2.1-hiera-large` (y `-small` en E6) | Segmentación con caja como prompt | Hugging Face, vía `transformers` |
| `Qwen/Qwen2.5-3B-Instruct` | Intérprete, redacción y descripción (sólo texto) | Hugging Face, vía `transformers` |
| `pycocotools` | Rasterizar polígonos y calcular IoU de máscaras (sólo evaluación y tests de RLE) | PyPI |
| `jsonschema` | Validación del SceneJSON y de la consulta intermedia | PyPI |
| `torchvision.ops.batched_nms` | NMS por clase | PyPI |

No se reutilizó código de terceros más allá de estas librerías. La notebook parte de la versión v2 del grupo (Fases 1 a 4); las fases 5 a 9 y los experimentos se agregaron en las versiones siguientes.

## Anexo B. Reproducibilidad

- La notebook corre de punta a punta en Kaggle (GPU T4 x2, Internet activado para bajar los modelos) en unos 40 minutos, sin archivos externos al dataset de la competencia.
- Semilla fija (0) para Python, NumPy y PyTorch; decodificación greedy en el LLM.
- `manifiesto_corrida.json` registra la configuración completa y su hash, las versiones y el SHA-256 de cada archivo generado.
- Las anotaciones se usan sólo para el EDA y para medir: `procesar_imagen()` y los dos modos de preguntas reciben únicamente la imagen o el SceneJSON predicho.
