"""Arma notebook/TPI_IA_2026P_5.ipynb a partir de la v2 de Esmeralda, con los parches y las celdas de notebook/celdas/.

Uso: python notebook/construir_notebook.py
El resultado es el archivo que se importa en Kaggle (File -> Import Notebook).
"""
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ORIGINAL = AQUI / "TPI_IA_2026P_5_v2_original.ipynb"
DESTINO = AQUI / "TPI_IA_2026P_5.ipynb"
CELDAS = AQUI / "celdas"

# Parches puntuales sobre celdas existentes: (texto que identifica la celda, texto viejo, texto nuevo)
PARCHES = [
    ("# TPI IA 2026 – Grupo 5",
     "# TPI IA 2026 – Grupo 5\n",
     "# TPI IA 2026 – Grupo 5\n\n"
     "| Versión | Cambios | PipelineScore (público) |\n"
     "|---|---|---|\n"
     "| v1 | Fases 1 a 4 con cajas en `[x, y, w, h]` | rechazada por formato |\n"
     "| v2 | Cajas en `[xmin, ymin, xmax, ymax]` | 0,6229 |\n"
     "| v3 | Atributos y proximidad (3.6), preguntas en modo determinista (Fase 5), validación de filas antes del envío | 0,6656 |\n"
     "| v4 | Experimentos de detector (2.9: OWLv2-large, sinónimos, ventanas) y de SAM2 (3.3b), modo LLM con Qwen2.5-3B (Fase 6) | 0,7022 |\n"
     "| v5 | Ensamble base + large (E8), vocabulario bilingüe para el intérprete, ejemplos resueltos en la redacción y control de conteos en la descripción | 0,7028 |\n"
     "| v6 | Traza completa (RUN_ID, hash de configuración, linaje por objeto, manifiesto), alias y reintento por vocabulario en el intérprete, validación cruzada (Fase 7), propagación de errores (Fase 8) y resumen final (Fase 9) | 0,7049 |\n\n"),
    # v6: 4.3 con los números de la configuración final (los de la v2 quedan como referencia)
    ('### 4.3 Conclusiones de la Fase 4',
     '| Verificación | Resultado |\n'
     '|---|---|\n'
     '| Filas y orden iguales a `sample_submission.csv` | 80 de 80, mismo orden |\n'
     '| SceneJSON válidos según `scene_schema.json` | 80 de 80 |\n'
     '| Imágenes que fallaron (escena vacía) | 0 |\n'
     '| Máximo de objetos / relaciones por imagen | 81 / 11 258 (límites 300 / 20 000) |\n'
     '| Imágenes donde se aplicó el tope de relaciones | 0 (el tope queda como protección) |\n'
     '| Serialización: métrica antes y después de escribir el CSV | idéntica en cajas y máscaras |\n'
     '| Tamaño de `submission.csv` | 11,5 MB |\n'
     '| Tiempo total | 1,2 min para 80 imágenes (≈ 0,9 s por imagen) |\n'
     '\n'
     '**Traza.** Los módulos que más tardan son el detector (≈ 0,46 s por imagen) y SAM2 (≈ 0,31 s). Ninguno falló. La traza completa queda en `traza_envio.csv`, una fila por imagen y módulo.',
     '| Verificación | v2 (OWLv2 base, SAM2 small) | v5 y v6 (configuración final: ventanas + sinónimos, SAM2 large) |\n'
     '|---|---|---|\n'
     '| Filas y orden iguales a `sample_submission.csv` | 80 de 80, mismo orden | 80 de 80, mismo orden |\n'
     '| SceneJSON válidos según `scene_schema.json` | 80 de 80 | 80 de 80 |\n'
     '| Imágenes que fallaron (escena vacía) | 0 | 0 |\n'
     '| Objetos por imagen: media / máximo (límite 300) | — / 81 | 30,3 / 112 |\n'
     '| Relaciones por imagen: máximo (límite 20 000) | 11 258 | 17 206 |\n'
     '| Imágenes donde se aplicó el tope de relaciones | 0 | 0 (el tope queda como protección) |\n'
     '| Serialización: métrica antes y después de escribir el CSV | idéntica en cajas y máscaras | idéntica |\n'
     '| Tamaño de `submission.csv` | 11,5 MB | 14,8 MB |\n'
     '| Tiempo total de la pipeline | 1,2 min para 80 imágenes (≈ 0,9 s por imagen) | 4,9 min (≈ 3,7 s por imagen) |\n'
     '\n'
     '**Traza.** En la configuración final el detector es el módulo más caro: 2,4 s por imagen, porque hace 5 pasadas de OWLv2 (la imagen completa y 4 ventanas). Le sigue SAM2 large, con 1,0 s. Ningún módulo falló. La imagen con más relaciones llegó a 17 206, cerca del límite del schema: el tope de 4.1 no se activó, pero es la protección que evita perder la fila en una imagen más cargada. La traza completa queda en `traza_envio.csv`, una fila por imagen y módulo; desde la v6 cada fila lleva el `RUN_ID` y se complementa con el linaje por objeto (`traza_objetos.csv`, Fase 8).'),
    # v6: el título de la Fase 1 pasa a su propia celda, después de la identificación de la corrida (sección 0)
    ('# TPI IA 2026 – Grupo 5',
     '\n\n## 1. Análisis exploratorio (EDA)',
     ''),
    ('img_meta = {r.id: r for r in imgs.itertuples()}',
     'img_meta = {r.id: r for r in imgs.itertuples()}\n',
     'marcar_fase("1 EDA")\n'
     'img_meta = {r.id: r for r in imgs.itertuples()}\n'),
    ('ROOT = next(Path("/kaggle/input")',
     '# Ubicar la raíz sin adivinar la ruta de montaje\nROOT = next(Path("/kaggle/input").rglob("scene_schema.json")).parent',
     '# Ubicar la raíz sin adivinar la ruta de montaje (en Kaggle: /kaggle/input; en una PC: el caché de kagglehub)\n'
     'BASES = [Path("/kaggle/input"), Path.home() / ".cache" / "kagglehub" / "competitions"]\n'
     'ROOT = next(p.parent for b in BASES if b.exists() for p in b.rglob("scene_schema.json"))'),
    ('SALIDA = Path("/kaggle/working")',
     'SALIDA = Path("/kaggle/working")',
     'SALIDA = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path("salidas_local")\n'
     'SALIDA.mkdir(exist_ok=True)'),
    ('def procesar_imagen',
     '        escena = dict(image=dict(id=image_id, width=W, height=H), objects=objetos, relations=rels, questions=[], questions_llm=[])\n',
     '        escena = dict(image=dict(id=image_id, width=W, height=H), objects=objetos, relations=rels, questions=[], questions_llm=[])\n'
     '        paso(traza, image_id, "atributos", PARAMS_ATRIBUTOS, lambda: agregar_atributos(escena, im))   # v3: 3.6\n'),
    # v4: el detector, k y la caja salen de los experimentos 2.9 y 3.3b
    ('def procesar_imagen',
     'dict(modelo=MODELO, prompt="a photo of a {clase}", k_max=2, umbral_crudo=0.05)',
     'dict(DET_CONFIG, umbral_crudo=0.05)'),
    ('def procesar_imagen',
     'detectar_multi(path, umbral=0.05, k_max=2)',
     'detectar_multi(path, umbral=0.05, k_max=K_MAX)'),
    ('def procesar_imagen',
     '                caja = caja_xyxy(d.bbox, W, H)\n'
     '                if not caja_valida(caja):\n'
     '                    continue                           # caja degenerada (ancho o alto 0 tras recortar al borde)\n'
     '                if m.sum() == 0:\n'
     '                    m = caja_a_mascara(d.bbox, H, W)   # respaldo: la caja como máscara\n'
     '                if m.sum() == 0:\n'
     '                    continue\n',
     '                if m.sum() == 0:\n'
     '                    m = caja_a_mascara(d.bbox, H, W)   # respaldo: la caja como máscara\n'
     '                if m.sum() == 0:\n'
     '                    continue\n'
     '                caja = caja_xyxy(caja_de_mascara(m) if CAJA_DESDE_MASCARA else d.bbox, W, H)   # v4: decisión de 3.3b\n'
     '                if not caja_valida(caja):\n'
     '                    continue                           # caja degenerada (ancho o alto 0 tras recortar al borde)\n'),
    # v6: la métrica de cajas puede evaluarse sobre un subconjunto de imágenes (validación cruzada, Fase 7)
    ('def evaluar_cajas',
     'def evaluar_cajas(preds, iou_thr=0.5, detalle=False):\n'
     '    """preds: DataFrame con image_id, category_id, score y bbox [x, y, w, h]. Aplica las reglas LVIS."""',
     'def evaluar_cajas(preds, iou_thr=0.5, detalle=False, imagenes=None):\n'
     '    """preds: DataFrame con image_id, category_id, score y bbox [x, y, w, h]. Aplica las reglas LVIS.\n'
     '    imagenes: si se indica, evalúa sólo esas imágenes (los objetos reales de las demás no cuentan como FN)."""'),
    ('def evaluar_cajas',
     '    for img_id, r in img_meta.items():\n'
     '        neg, noexh = set(r.neg_category_ids), set(r.not_exhaustive_category_ids)\n'
     '        for c in pos.get(img_id, set()) | cats_pred[img_id]:\n'
     '            pb, gts = grupos.get((img_id, c), []), gt_by.get((img_id, c), [])',
     '    for img_id, r in img_meta.items():\n'
     '        if imagenes is not None and img_id not in imagenes:\n'
     '            continue\n'
     '        neg, noexh = set(r.neg_category_ids), set(r.not_exhaustive_category_ids)\n'
     '        for c in pos.get(img_id, set()) | cats_pred[img_id]:\n'
     '            pb, gts = grupos.get((img_id, c), []), gt_by.get((img_id, c), [])'),
    # v6: traza completa. Cada fila de la traza lleva el RUN_ID; cada SceneJSON, el hash de la configuración de percepción;
    # cada objeto, su linaje (de qué detección sale y qué le pasó en cada paso)
    ('def procesar_imagen',
     '    fila = dict(image_id=image_id, modulo=modulo, params=json.dumps(params, ensure_ascii=False), inicio=inicio)',
     '    fila = dict(run_id=RUN_ID, image_id=image_id, modulo=modulo, params=json.dumps(params, ensure_ascii=False), inicio=inicio)'),
    ('def procesar_imagen',
     'print("Topes del schema:", MAX_OBJ, "objetos y", MAX_REL, "relaciones")\n',
     'print("Topes del schema:", MAX_OBJ, "objetos y", MAX_REL, "relaciones")\n\n'
     '# v6: configuración de percepción y su hash. Va en el campo `trace` de cada SceneJSON, junto con el RUN_ID\n'
     'CONFIG_PERCEPCION = dict(detector=DET_CONFIG, segmentador=SAM_ID, caja_desde_mascara=bool(CAJA_DESDE_MASCARA),\n'
     '                         propiedades=dict(bbox="xyxy", size="COCO 32^2 / 96^2", grilla="3x3 por centroide"),\n'
     '                         relaciones=dict(margen=0.05, iou_overlaps=0.01, max_rel=MAX_REL), atributos=PARAMS_ATRIBUTOS)\n'
     'TRAZA_ESCENA = dict(run_id=RUN_ID, config_percepcion=huella(CONFIG_PERCEPCION))\n'
     'print("Traza de cada escena:", TRAZA_ESCENA)\n'),
    ('def procesar_imagen',
     '    return dict(image=dict(id=image_id, width=W, height=H), objects=[], relations=[], questions=[], questions_llm=[])',
     '    return dict(image=dict(id=image_id, width=W, height=H), objects=[], relations=[], questions=[], questions_llm=[],\n'
     '                trace=TRAZA_ESCENA)'),
    ('def procesar_imagen',
     'def procesar_imagen(path, image_id, traza):',
     'def procesar_imagen(path, image_id, traza, linaje=None):'),
    ('def procesar_imagen',
     '            for d, m in zip(finales.itertuples(), masks):\n'
     '                if m.sum() == 0:\n'
     '                    m = caja_a_mascara(d.bbox, H, W)   # respaldo: la caja como máscara\n',
     '            for d, m in zip(finales.itertuples(), masks):\n'
     '                respaldo = m.sum() == 0\n'
     '                if respaldo:\n'
     '                    m = caja_a_mascara(d.bbox, H, W)   # respaldo: la caja como máscara\n'),
    ('def procesar_imagen',
     '                                    bbox=caja, mask=rle_encode(m), **propiedades(m, W, H)))\n'
     '            return objetos\n',
     '                                    bbox=caja, mask=rle_encode(m), **propiedades(m, W, H)))\n'
     '                if linaje is not None:   # v6: de qué detección sale cada objeto y qué pasó en cada paso\n'
     '                    linaje.append(dict(run_id=RUN_ID, image_id=image_id, obj_id=objetos[-1]["id"], clase=id2name[d.category_id],\n'
     '                                       score=round(float(d.score), 4), rango_clase=int(d.rango), fuente=getattr(d, "fuente", "imagen"),\n'
     '                                       bbox_detector=[round(float(v), 1) for v in d.bbox], segmentador=SAM_ID,\n'
     '                                       mascara_px=int(m.sum()), mascara_respaldo=bool(respaldo),\n'
     '                                       relleno_caja=round(float(m.sum()) / max(1.0, d.bbox[2] * d.bbox[3]), 3)))\n'
     '            return objetos\n'),
    ('def procesar_imagen',
     '        print(f"[{image_id}] falló, se envía una escena vacía válida: {repr(e)[:150]}")\n',
     '        print(f"[{image_id}] falló, se envía una escena vacía válida: {repr(e)[:150]}")\n'
     '        if linaje is not None:   # la escena sale vacía: su linaje también\n'
     '            linaje[:] = [fila for fila in linaje if fila["image_id"] != image_id]\n'),
    ('def procesar_imagen',
     'objects=objetos, relations=rels, questions=[], questions_llm=[])',
     'objects=objetos, relations=rels, questions=[], questions_llm=[],\n'
     '                      trace=TRAZA_ESCENA)'),
    ('rutas = {p.stem: p for p in ROOT.rglob("*.jpg")}',
     'traza, filas_env = [], []',
     'traza, filas_env, linaje = [], [], []'),
    ('rutas = {p.stem: p for p in ROOT.rglob("*.jpg")}',
     '    esc = procesar_imagen(rutas[iid], iid, traza)',
     '    esc = procesar_imagen(rutas[iid], iid, traza, linaje)'),
    ('rutas = {p.stem: p for p in ROOT.rglob("*.jpg")}',
     'traza.to_csv(SALIDA / "traza_envio.csv", index=False)\n',
     'traza.to_csv(SALIDA / "traza_envio.csv", index=False)\n'
     'linaje = pd.DataFrame(linaje)                        # v6: una fila por objeto de cada SceneJSON\n'
     'linaje.to_csv(SALIDA / "traza_objetos.csv", index=False)\n'
     'print(f"Linaje: {len(linaje)} objetos en traza_objetos.csv | por fuente: {linaje.fuente.value_counts().to_dict()}")\n'
     'marcar_fase("4 SceneJSON y envío")\n'),
    ('SAM_ID = "facebook/sam2.1-hiera-small"',
     '# Detecciones finales de la Fase 2: hasta 2 clases por caja, NMS 0,5, umbral 0,20\ndk = aplicar_nms(dets_multi[dets_multi.rango < 2])',
     '# Detecciones finales: configuración elegida en 2.9 (hasta K_MAX clases por caja, NMS 0,5, umbral UMBRAL)\n'
     'dk = aplicar_nms(dets_multi[dets_multi.rango < K_MAX])'),
]

# Celdas nuevas: (texto que identifica la celda de referencia, "despues" o "reemplazar", archivos en orden)
INSERCIONES = [
    (None, "inicio", ["0_instalacion.py"]),
    ("### 2.8 Conclusiones de la Fase 2", "despues", ["2_9_detector.md", "2_9_detector.py"]),
    ("rle_sam, rle_caja, vacias = {}, {}, 0", "despues", ["3_3b_sam.md", "3_3b_sam.py"]),
    ("### 3.5 Conclusiones de la Fase 3", "despues", ["3_6_atributos.md", "3_6_atributos.py"]),
    (None, "reemplazar_ultima_vacia", ["5_0_intro.md", "5_1_consulta.md", "5_1_consulta.py", "5_2_parser.md", "5_2_parser.py",
                                       "5_3_motor.md", "5_3_motor.py", "5_4_benchmark.md", "5_4_benchmark.py",
                                       "5_5_evaluacion.md", "5_5_evaluacion.py", "5_6_extra.md", "5_6_extra.py",
                                       "5_7_envio.md", "5_7_envio.py", "5_8_conclusiones.md",
                                       "6_0_intro.md", "6_1_llm.md", "6_1_llm.py", "6_2_interprete.md", "6_2_interprete.py",
                                       "6_3_redaccion.md", "6_3_redaccion.py", "6_4_benchmark.md", "6_4_benchmark.py",
                                       "6_5_envio.md", "6_5_envio.py", "6_6_conclusiones.md",
                                       "7_0_intro.md", "7_1_validacion_cruzada.py", "7_2_umbral_fuente.py", "7_3_conclusiones.md",
                                       "8_0_intro.md", "8_1_propagacion_objetos.py", "8_2_propagacion_qa.py", "8_3_reconstruccion.py",
                                       "8_4_evaluacion_trazas.py", "8_5_conclusiones.md", "9_0_intro.md", "9_1_manifiesto.py",
                                       "9_2_conclusiones.md"]),
    ("# TPI IA 2026 – Grupo 5", "despues", ["0_corrida.md", "0_corrida.py", "1_titulo.md"]),
]


def fuente(celda):
    return "".join(celda["source"])


def nueva_celda(archivo):
    texto = (CELDAS / archivo).read_text(encoding="utf-8").rstrip("\n")
    lineas = texto.splitlines(keepends=True)
    id_celda = "tpi-" + archivo.replace(".", "-").replace("_", "-")
    if archivo.endswith(".md"):
        return {"cell_type": "markdown", "id": id_celda, "metadata": {}, "source": lineas}
    return {"cell_type": "code", "id": id_celda, "metadata": {}, "execution_count": None, "outputs": [], "source": lineas}


def buscar(celdas, marca):
    encontradas = [i for i, c in enumerate(celdas) if marca in fuente(c)]
    assert len(encontradas) == 1, f"la marca {marca!r} aparece en {len(encontradas)} celdas"
    return encontradas[0]


def construir():
    nb = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    celdas = nb["cells"]

    for marca, viejo, nuevo in PARCHES:
        i = buscar(celdas, marca)
        src = fuente(celdas[i])
        assert src.count(viejo) == 1, f"el texto a parchear no aparece una sola vez en la celda {i}"
        celdas[i]["source"] = src.replace(viejo, nuevo).splitlines(keepends=True)

    for marca, modo, archivos in INSERCIONES:
        nuevas = [nueva_celda(a) for a in archivos]
        if modo == "inicio":
            celdas[0:0] = nuevas
        elif modo == "despues":
            i = buscar(celdas, marca)
            celdas[i + 1:i + 1] = nuevas
        else:
            assert not fuente(celdas[-1]).strip(), "la última celda no está vacía"
            celdas[-1:] = nuevas

    for c in celdas:          # Kaggle regenera las salidas al correr: se guardan limpias
        if c["cell_type"] == "code":
            c["outputs"], c["execution_count"] = [], None
        c.get("metadata", {}).pop("papermill", None)
        c.get("metadata", {}).pop("execution", None)
    nb["metadata"].pop("papermill", None)
    nb["metadata"].pop("widgets", None)

    DESTINO.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{DESTINO.name}: {len(celdas)} celdas ({sum(c['cell_type'] == 'code' for c in celdas)} de código)")


if __name__ == "__main__":
    construir()
