# Plan — TPI Primavera 2026: Comprensión visual de escenas

**Grupo:** 5 → notebook `TPI_IA_2026P_5`. Equipo de Kaggle "G5 - 5k2": Esmeralda Odar (líder), Joaquín Bustos, Guille Contigiani y Matus4.
**Objetivo:** promoción sólida.
**Meta interna:** lo que falta, hecho en 2 días (sáb 24 + dom 25/10); si no alcanza, se extiende a lun 26 y mar 27. Detalle en §6.
**Entrega oficial:** domingo 1/11/2026, 23:59.

---

## 0. Punto de partida (relevado el 24/10)

### Leaderboard
- Equipo: **0,6229**, puesto 36 de 50, con 1 envío válido (v2, de hace 7 días).
- Primero: 0,8298. La mitad de la tabla ronda 0,70.

### Ya hecho en la notebook de Esmeralda (`esmeraldaodar/tpi-ia-2026p-5`, v2, 5,6 min en T4)

| Fase | Contenido | Resultado en dev |
|---|---|---|
| 1. EDA | 10 preguntas, cada una con su decisión (tamaños, LVIS, solapes, grilla, preguntas) | — |
| 2. Detección | Métrica LVIS local con pruebas de cordura. OWLv2-base, prompt `"a photo of a {clase}"`, NMS por clase 0,5, umbral 0,20 por barrido. Experimento: 1 vs 2 vs 3 clases por caja → k = 2 | **F1 de cajas 0,660** (P 0,724, R 0,606) |
| 3. SAM2 | `facebook/sam2.1-hiera-small` (transformers). RLE con 3 tests. Experimento: caja rellena vs SAM2 | **F1 de máscaras 0,620** (caja rellena: 0,422) |
| 3. Propiedades | Centroide de la máscara, `area_ratio`, grilla 3×3, size con umbrales COCO 32² / 96², relaciones por centroide con margen del 5 %, `overlaps` con IoU de máscara > 0,01 | — |
| 4. SceneJSON | `procesar_imagen()` sin anotaciones, validación con jsonschema, cajas `xyxy`, topes de 300 objetos y 20000 relaciones, traza por módulo (`traza_envio.csv`), escena vacía si algo falla | 80 de 80 válidos |

Diagnósticos ya documentados: recall de 0,43 en objetos chicos contra 0,72 en grandes; `person` con recall 0,03 (confianza baja y pierde contra shirt/jacket); `book` sin caja en 26 de 43 casos.

### Falta (esto es lo que hay que hacer)
1. **Fase 5 — QA determinista** (`questions`). Hoy el 10 % de QA del puntaje está en 0.
2. **Fase 6 — Modo LLM** (`questions_llm` + descripciones). Requisito de promoción.
3. **Atributos útiles** consultables (color, oclusión, near) y manejo explícito de preguntas ambiguas, no soportadas o sin información.
4. **Tracing completo**: hoy hay traza por módulo; falta config_hash, artefactos, linaje por objeto y usar la traza para analizar la propagación de errores.
5. **Más experimentos** sobre la línea base actual y validación cruzada del umbral (hoy se eligió sobre todo dev).
6. **Evaluación de QA** (exactitud, fidelidad, interpretación del LLM) y análisis de casos correctos, ambiguos y fallidos.
7. **Reporte `.md`**.

---

## 1. Métrica oficial (pestaña Evaluation + Rules, leídas el 24/10)

- `PipelineScore = 0,40·F1_cajas + 0,35·F1_máscaras + 0,15·consistencia + 0,10·QA`.
- **QA:** por imagen, promedio entre la exactitud de `normalized_answer` en `questions` (preguntas cerradas) y un "proxy reproducible de cobertura factual y evidencia" para `questions_llm`. Por eso el `evidence` del modo LLM tiene que apuntar a objetos reales del JSON, y la descripción tiene que mencionar lo que está en el JSON.
- **Un JSON inválido, una RLE inconsistente o referencias a ids inexistentes invalidan la fila entera**, y con ella sus objetos y su QA. Hay que validar `evidence` y `relations` contra los ids antes de escribir.
- Leaderboard público: 40 % de las filas; privado: 60 %.
- **No se publican** los umbrales de small/medium/large ni la definición de las relaciones. Se mantienen las reglas de la notebook (COCO 32² / 96², centroide ± 5 %) y se documentan como decisión propia.
- Lectura del 0,6229: con F1 de dev de 0,66 y 0,62 (si en test se parecen), 0,40·0,66 + 0,35·0,62 ≈ 0,48. El resto (~0,14) es casi todo consistencia (≈ 0,95), y QA está en 0. **Completar QA puede sumar hasta +0,10**: es la mejora más barata.

---

## 2. Decisiones

| Tema | Decisión | Por qué |
|---|---|---|
| Base de trabajo | **Seguir la notebook de Esmeralda**, agregando las fases 5 a 7 | Ya cumple la parte visual con F1 ≥ 0,50; rehacerla no tiene sentido |
| Detector | **OWLv2-base, k = 2, NMS 0,5, umbral 0,20** (línea base actual) | Medido y justificado en la Fase 2 |
| Mejoras de detector a probar | OWLv2-**large**; mayor resolución o **tiling** para objetos chicos; YOLO-World solo si sobra tiempo | El cuello de botella son los objetos chicos (recall 0,43) |
| Segmentación | SAM2.1 vía transformers (ya funciona). Experimento: **hiera-small vs hiera-large** | Contra el F1 de cajas se pierden solo 4 puntos: el margen es chico |
| Umbral | Validar el 0,20 con **5-fold** y reportar media ± desvío | Hoy se eligió y midió sobre los mismos datos |
| LLM | **Qwen2.5-3B-Instruct**, fp16, greedy | Buen español y JSON; reproducible |
| Ambigüedad | Varias instancias: usa la de mayor confianza, `status="ambiguous"`; `evidence` = la elegida, las demás en `alternatives`; la `confidence` se reparte | En el benchmark, la clase de posición/tamaño/relación tiene exactamente 1 instancia real (EDA 1.8); la evidencia apunta sólo a lo que sustenta la respuesta |
| Objeto no detectado | Conteo = 0 y existencia = `no`, con confianza baja; posición, tamaño y relación = `unknown` | No inventar respuestas |
| Atributos extra | Color dominante, oclusión estimada, `near` (en `extra_relations`) | El schema solo admite 5 predicados |
| Mapeo de clases (LLM) | El LLM elige una de las 120 clases (van en el prompt); el código valida, prueba coincidencia aproximada o responde `unsupported` | El LLM interpreta y el código decide |
| Trazas | Extender el `paso()` actual: run_id, config_hash, artefactos y linaje por objeto (score crudo, rango k, score de SAM) | Promoción pide reconstruir la ejecución y analizar la propagación |
| Relación (determinista) | El predicado ("por encima de"…) **se saca del texto con reglas** | No viene en los campos estructurados |
| Descripción | Plantilla determinista en `questions`; redacción por LLM en `questions_llm`, con control de alucinaciones | |

---

## 3. Arquitectura que se agrega (fases 5 y 6)

```
SceneJSON ─────────────────────────────────────────────┐
pregunta + campos estructurados ─► parser determinista ─┤
pregunta (solo texto) ─► Qwen ─► JSON validado ─────────┴► motor QA ─► answer, normalized_answer, evidence, confidence
                                                                  └► Qwen verbaliza (y describe la escena con un resumen del JSON)
```

**Query intermedio** (lo arma el parser o el LLM; lo ejecuta siempre el mismo motor):
```json
{"intent": "count|existence|position|size|relation|attribute|description",
 "classes": ["doorknob"], "predicate": "above|below|left_of|right_of|overlaps|near|null",
 "attribute": "color|null", "output": "integer|boolean|position_3x3|size_class|free_text"}
```

**Reglas del motor:** filtra los objetos por `category_id` y cuenta, compara o consulta con código. `evidence` = ids usados. `confidence` sale de las confianzas del detector (máximo para existencia, producto o mínimo para relaciones). Clase fuera del vocabulario → `unsupported`.

---

## 4. Métricas por etapa

| Etapa | Métricas |
|---|---|
| Detección | P / R / F1 @ IoU 0,5 (LVIS) + cobertura; por tamaño y por clase *(ya está)*; F1 con 5-fold |
| Segmentación | F1 de máscara *(ya está)*; mIoU de los pares emparejados; mIoU con cajas reales (oráculo) |
| Representación | % de JSON válidos *(ya está)*; consistencia de propiedades contra la máscara; referencias válidas |
| QA determinista | Exactitud contra respuestas GT calculadas desde las anotaciones (solo para evaluar); fidelidad (respuesta = consulta re-ejecutada sobre el JSON) |
| QA con LLM | Exactitud de interpretación (intención, clase y predicado contra los campos estructurados); % de JSON válidos; exactitud final; diferencia contra el modo determinista |
| Descripción | Tasa de alucinación (clases o números que no están en el JSON); cobertura de los objetos principales |
| Propagación | Objeto GT → no detectado / clase errónea / máscara IoU < 0,5 / OK. Error de QA → percepción / interpretación / motor |

---

## 5. Experimentos (una variable por vez, sobre la línea base actual)

| # | Hipótesis | Variable | Estado |
|---|---|---|---|
| E1 | Varias clases por caja recuperan objetos tapados por clases que se solapan | k = 1/2/3 | ✅ hecho (+1,4 de F1) |
| E2 | SAM2 aporta sobre la caja rellena | Fuente de la máscara | ✅ hecho (+20 de F1) |
| E3 | OWLv2-large o mayor resolución sube el recall en objetos chicos | Modelo / resolución | Pendiente |
| E4 | El tiling (estilo SAHI) sube el recall en objetos chicos | Tiling | Pendiente (candidato a sobresaliente) |
| E5 | Con cajas perfectas, SAM2 casi no pierde calidad | Cajas GT vs predichas | Pendiente |
| E6 | SAM2 hiera-large mejora la máscara sobre small | Tamaño de SAM2 | Pendiente |
| E7 | Los sinónimos (fireplug → fire hydrant, jean → jeans…) ayudan a las clases con nombres raros | Prompts | Pendiente |
| E8 | El LLM interpreta casi tan bien como los campos estructurados | Modo de consulta | Pendiente (sale de la Fase 6) |

---

## 6. Plan de 2 días (sáb 24 + dom 25), con extensión a lun 26 y mar 27 si hace falta

**Reparto:** 🧑 = vos (Kaggle, decisiones, envíos) · 🤖 = Claude (código, tests locales, reporte).
Todo se escribe en el repo; vos importás la notebook a Kaggle, la corrés con GPU y bajás las salidas.

### Estructura final de la notebook
```
1 EDA (✅)  2 Detección (✅)  3 SAM2 + propiedades (+ atributos)  4 SceneJSON + traza (+ linaje)
5 QA determinista  6 Modo LLM  7 Experimentos (CV, oráculo, OWLv2-L, tiling)
8 Propagación de errores y casos  9 Envío final + resumen de resultados (results/*.csv)
```
Un flag `RUN_EXPERIMENTS` saltea la sección 7 en las corridas rápidas. La corrida final lo activa para que todas las salidas queden guardadas.

### SÁBADO 24 (hoy) — meta: envío v3 con `questions` deterministas
| # | Quién | Tarea | Listo cuando |
|---|---|---|---|
| S1 | 🧑 | Pedirle a Esmeralda permiso de edición en su notebook (Share → *Can edit*), o que suba ella las versiones | Podés importar una versión nueva |
| S2 ✅ | 🤖 | Bajar el `.ipynb` y `submission.csv` (v2) al repo; armar un venv local; hacer que `ROOT` también encuentre el caché local de `kagglehub` | Hecho: `notebook/`, `kaggle_outputs/v2/`, `dev/correr_local.py` |
| S3 ✅ | 🤖 | **Fase 5**: schema del query, motor (count, existence, position, size, relation, attribute, compare), parser determinista (campos estructurados + regex para el predicado), políticas de ambigüedad, `unknown` y `unsupported`, descripción por plantilla, validación de filas | Hecho: 60/60 consignas, 0 filas inválidas |
| S4 ✅ | 🤖 | Respuestas GT desde las anotaciones (solo para evaluar), exactitud por tipo, fidelidad y origen de cada error | Hecho: exactitud 0,75 · fidelidad 100 % · 9 de 10 errores son de percepción |
| S5 ✅ | 🤖 | **Atributos** (3.6): color dominante (HSV → nombre), oclusión, `near` en `extra_relations`, `touches_border` | Hecho; la plausibilidad del color es ≈ 0,55 (atributo aproximado, documentado) |
| S6 ✅ | 🤖 | Correr la v3 en Kaggle y **enviarla** | Hecho en `matus4/tpi-ia-2026p-5` (versión 1, 6 min 48 s en T4 x2): **0,6656** (+0,043 sobre la v2), puesto 37 de 50 |

**Cómo correr la v3 en Kaggle (S6):**
1. Abrir la notebook de Esmeralda → **Edit** (si sólo aparece *Copy & Edit*, falta el permiso de S1).
2. **File → Import Notebook** → subir `notebook/TPI_IA_2026P_5.ipynb` → confirmar que reemplaza el contenido.
3. Panel derecho: **Accelerator: GPU T4** · **Internet: On** · en *Input* tiene que figurar la competencia.
4. **Save Version → Save & Run All (Commit)**, con el nombre "v3 – QA determinista + atributos". Tarda ~8 min.
5. Cuando termine: **Output → submission.csv → Submit**, con la descripción "TPI_IA_2026P_5 - v3 - QA determinista + atributos".
6. Pasarme el puntaje. Las salidas (`results/`, `traza_*.csv`) las bajo yo con Chrome.

**Cómo se regenera la notebook:** `.venv/Scripts/python -X utf8 notebook/construir_notebook.py` (v2 de Esmeralda + parches + `notebook/celdas/`). Para probar sin GPU: `.venv/Scripts/python -X utf8 dev/correr_local.py`.

### DOMINGO 25 — meta: envío v4 con `questions_llm`, experimentos y borrador del reporte
| # | Quién | Tarea | Listo cuando |
|---|---|---|---|
| D1 | 🤖 | **Fase 6**: Qwen2.5-3B intérprete (las 120 clases + few-shot en el prompt) → validación con JSON Schema + 1 reintento → mismo motor → verbalización con control → descripción desde un resumen del JSON con control de alucinaciones | Plomería probada localmente con Qwen2.5-0.5B en CPU |
| D2 | 🤖 | Evaluación del LLM: exactitud de interpretación contra los campos estructurados, % de JSON válidos, exactitud final y alucinación en descripciones | `results/qa_llm.csv` |
| D3 | 🤖 | **Traza completa**: run_id, config_hash, versiones, artefactos y linaje por objeto. **Fase 8**: cada objeto GT → no detectado / clase errónea / máscara mala / OK; cada error de QA → percepción / interpretación / motor | `results/propagacion.csv` + figuras |
| D4 | 🤖 | **Fase 7**: umbral con 5-fold (CPU), SAM2 con cajas reales (oráculo), OWLv2-large y tiling (cada uno detrás de una función con la misma interfaz) | Celdas listas con `RUN_EXPERIMENTS` |
| D5 | 🧑 | Correr con `RUN_EXPERIMENTS=True` (~30-40 min de GPU) → bajar `results/` y `traza*` al repo → **enviar v4** | Puntaje de la v4 + salidas en el repo |
| D6 | 🤖 | Si OWLv2-large o el tiling mejoran el F1 en dev, pasan a ser la configuración del envío (otra corrida, v5) | Decisión documentada con números |
| D7 | 🤖 | Borrador de `REPORTE.md`: cada número leído de `results/*.csv`, con figuras exportadas | Borrador completo para revisar |

### Extensión — lun 26 y mar 27 (solo lo que no haya entrado)
- Lo pendiente de D4 a D7, en este orden de prioridad: oráculo y CV → OWLv2-large → tiling.
- Pulir el reporte: casos correctos, ambiguos y fallidos con imágenes, limitaciones y trabajo futuro.
- Guía de defensa para los 4 (preguntas probables + respuestas), y probar la pipeline con una foto fuera del dataset.
- Corrida final limpia → elegir los 2 envíos finales en *Submissions* → compartir la notebook con **martingra** → subir reporte + notebook + csv a la UV (vence el **1/11 a las 23:59**).

### Prioridad si el tiempo aprieta
1. **Checklist de promoción** (nunca se recorta): QA determinista, modo LLM, atributos, manejo de ambiguas, traza con propagación y reporte.
2. Experimentos baratos: CV del umbral y SAM2 con cajas reales.
3. Experimentos de mejora: OWLv2-large, después tiling. Si no entran el sábado y el domingo, pasan al lunes y martes.

---

## 7. Operación y coordinación

- **Leer la competencia:** el conector MCP de Kaggle no tiene tu cuenta, así que se usa Claude in Chrome (tu Edge, con la sesión iniciada).
- **Correr en Kaggle:** lo hacés vos a mano (sin token de la API). Ciclo: importar el `.ipynb` del repo → *Save & Run All* → enviar desde *Output* → bajar las salidas a `kaggle_outputs/vN/`.
- **Notebook entregable:** la de Esmeralda (`TPI_IA_2026P_5`). Las versiones nuevas se suben ahí; avisale al equipo para que nadie la edite en paralelo.
- **Envíos:** los hacés vos. Al final se eligen 2 en *Submissions*.
- **Equipo:** vos y Claude hacen todo; al final se pasa la guía de defensa a los otros tres.

---

## 8. Checklist de promoción

| Criterio | Estado |
|---|---|
| EDA que fundamenta decisiones | ✅ |
| Pipeline: detección + SAM2 + JSON | ✅ |
| F1 de detección ≥ 0,50 (dev, IoU 0,5, LVIS) | ✅ 0,660 (falta validarlo con CV) |
| Máscaras usadas + JSON válido | ✅ |
| `questions` determinista (existencia y conteo como mínimo) | ✅ Fase 5 (falta correrla en Kaggle) |
| Atributos y relaciones consultables | ✅ color, oclusión, borde, `near` + 5 predicados |
| `questions_llm` con LLM liviano que solo recibe el texto | ❌ Fase 6 |
| Ubicación, comparación, atributos y relaciones en los dos modos | 🟡 determinista sí; falta el modo LLM |
| Manejo de ambiguas, no soportadas e insuficientes | ✅ 5.6 (100 % en los tres casos) |
| Tracing completo usado para analizar la propagación | 🟡 traza básica |
| Mejora contra la línea base con experimento controlado | ✅ E1 y E2 (sumar E3 a E7) |
| Reporte `.md` consistente con la notebook | ❌ |

---

## 9. Riesgos

| Riesgo | Mitigación |
|---|---|
| Pisar el trabajo de un compañero | Acordar quién toca qué fase antes de editar |
| Una fila inválida (JSON, RLE o referencia rota) anula esa fila | Validar ids y RLE antes de escribir; `assert` en el CSV final |
| Conflictos de versiones en Kaggle (transformers / SAM2) | Fijar versiones; la notebook ya tiene un fallback a SAM v1 |
| LLM no reproducible | Greedy + semilla + salidas guardadas |
| Reporte que no coincide con la notebook | El reporte cita solo números leídos de archivos de resultados |
| Archivos pesados en git (GitHub rechaza > 100 MB) | `*.mp4` ya está en `.gitignore`; ignorar también pesos de modelos y salidas de Kaggle |

---

## 10. Plan para subir el puntaje (sáb 24/10 a la noche, ejecutado por Claude)

### Dónde estamos
- **0,6656**, puesto 37 de 52. El primero tiene 0,8298 y los de 5K1 están entre 0,70 y 0,80.
- Despeje de la fórmula: con F1 de cajas 0,66 y de máscaras 0,62 (dev), la percepción aporta ≈ 0,48 de los 0,75 posibles; la consistencia, ≈ 0,14 de 0,15; y QA, ≈ 0,043 de 0,10, porque `questions_llm` va vacía.
- **Conclusión:** el 75 % del puntaje es percepción, y ahí está casi toda la distancia con los primeros (que deben andar en F1 ≈ 0,78). La segunda palanca es el modo LLM (+0,03 a +0,05, y además es requisito de promoción).
- Probado en CPU sobre las detecciones guardadas: afinar el umbral (0,20 → 0,18), el NMS o un umbral por rango suma como mucho +0,005 de F1, y la caja sacada de la máscara empeora (0,651). **No alcanza con post-procesar: hay que cambiar el detector.**

### Qué se hace (v4), en una sola corrida de Kaggle (~45 min de GPU)
| # | Cambio | Dónde | Por qué |
|---|---|---|---|
| E3 | OWLv2 **large** (patch14, 1008 px) contra base | 2.9 | Mejor backbone; es lo que suele usar quien tiene F1 ≈ 0,75+ |
| E7 | **Sinónimos** por clase (`fireplug` → fire hydrant, `person` → man / woman / child…), con el máximo entre consultas | 2.9 | `person` tenía recall 0,03 por confianza baja; nombres raros de LVIS |
| E4 | **Ventanas** 2×2 (60 %) además de la imagen completa, estilo SAHI | 2.9 | 54 % de objetos chicos con recall 0,43 |
| E6 | SAM2.1 **large** contra small | 3.3b | Máscaras más finas con las mismas cajas |
| E5 | Oráculo: SAM2 con cajas reales | 3.3b | Separa errores del detector y del segmentador (promoción) |
| F6 | **Modo LLM** con Qwen2.5-3B: intérprete → mismo motor → redacción con control; descripción con control de alucinaciones | Fase 6 | +QA y requisito de promoción |

Cada experimento elige solo, con el F1 de desarrollo, si entra en la configuración final; las Fases 3 y 4 usan lo que gana. Todo queda en `results/*.csv`.

### Próximos pasos después de la v4
1. Leer `results/det_experimentos.csv`: si las ventanas o los sinónimos no ayudaron, documentarlo como intento fallido (también suma en la nota).
2. Validación cruzada del umbral (5-fold, CPU) sobre las detecciones crudas que guarda la v4.
3. Traza completa (run_id, config_hash, linaje por objeto) y Fase 8 de propagación de errores.
4. Actualizar los markdown con números fijos (4.3 y 5.8 todavía muestran los de la v2 y la v3) y escribir `REPORTE.md`.

### Resultado de la v4 (dom 25/10, ~04:00) — **0,7022** en el público (+0,037 sobre la v3)
Corrida: versión 2 de `matus4/tpi-ia-2026p-5` (28 min en T4 x2). Envío "TPI_IA_2026P_5 - v4 - …".

| Etapa | v3 | v4 | Detalle |
|---|---|---|---|
| F1 cajas (dev) | 0,660 | **0,679** | base + ventanas 2×2 + sinónimos, k = 3, umbral 0,25. Recall en chicos 0,487 → 0,519 |
| F1 máscaras (dev) | 0,620 | **0,645** | SAM2.1 **large** (small: 0,637 con las mismas cajas) |
| QA determinista | 0,75 | **0,775** | posición 1,0 |
| QA LLM (Qwen2.5-3B) | — | 0,725 | interpretación correcta 88 %, misma respuesta que el determinista 95 %, JSON válido 100 % |
| Descripciones LLM | — | 19/20 | 0 clases alucinadas, cobertura de las 3 clases principales 0,78 |

**Experimentos que no mejoraron (documentar):** OWLv2-**large** dio F1 0,624, peor que base (0,666) con el mismo barrido; caja sacada de la máscara 0,672 vs 0,679. Oráculo SAM2 con cajas reales: IoU medio 0,79 y 90 % de máscaras con IoU ≥ 0,5 (chicos 85 %) → el cuello de botella sigue siendo el detector.

**Problemas vistos en la traza del LLM:** la redacción pasó el control sólo en 30 % (el 3B contestaba "No" a secas); las descripciones salieron como lista y con el nombre en español entre paréntesis; errores de traducción de clase ("calcetín" → shoe, "pantalones" → short pants).

### v5 — **0,7028** en el público, puesto 24 de 52 (versión 3 de la copia, 32 min)
- Intérprete con vocabulario bilingüe (inglés + nombre en español propio).
- Ejemplos resueltos en los prompts de redacción y de descripción; control de "N objetos (clase)" contra el conteo.
- Candidato extra de detector: ensamble base (ventanas + sinónimos) + large, elegido sólo si sube el F1 de dev.

**Resultado de la v5:** el ensamble con large no mejoró (F1 0,676 contra 0,679), así que la percepción quedó igual que en la v4. Lo que cambió fue el modo LLM:
- Interpretación correcta: 88 % → **97 %** (58 de 60). Quedan dos errores: "manija" → `mango` y "gafas" → `glasses` (en el vocabulario, `spectacles`).
- Redacción aceptada por el control: 30 % → **80 %**.
- Descripciones: **20 de 20** redactadas por el LLM, sin clases alucinadas, con cobertura de las 3 clases principales de 0,98 (antes 0,78).

### Próximos pasos (para retomar)
1. **QA LLM:** agregar al normalizador un mapa de alias en inglés (`glasses` → spectacles, `tv` → television set, etc.) y un ejemplo con "manija". Suma 2 preguntas.
2. **Detector:** la mejora que queda es chica (+0,019 de F1 en la v4). Ideas sin probar: ventanas de 3×3, umbral distinto para las cajas de las ventanas y validación cruzada del umbral (5-fold, en CPU con `dets_*_dev.pkl`).
3. **Promoción:** traza completa (run_id, config_hash, linaje por objeto) y propagación de errores (Fase 8). Además, actualizar los markdown con números fijos (4.3 y 5.8) y escribir `REPORTE.md` con los CSV de `results/` de la versión 3.
4. **Entrega:** elegir 2 envíos finales en *Submissions* (hoy, v5 = 0,7028 y v4 = 0,7022), compartir la notebook con **martingra** y acordar con Esmeralda cuál notebook es la oficial.
