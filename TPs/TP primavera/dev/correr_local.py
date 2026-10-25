"""Corre en CPU toda la notebook salvo lo que necesita GPU, para probar las celdas antes de subirlas a Kaggle.

Lo que en Kaggle hace la GPU (detector y SAM2) se reemplaza por el estado guardado de una corrida real
(por defecto kaggle_outputs/v5): detecciones crudas y finales, tablas de 2.9 y 3.3b y los SceneJSON del envío.
En la Fase 6 el LLM se simula con las salidas crudas guardadas de esa corrida (con --llm-real, Qwen2.5-0.5B en CPU).

Uso (desde la carpeta del TP):  .venv/Scripts/python -X utf8 dev/correr_local.py [carpeta_de_salidas_de_kaggle] [--llm-real]
Las salidas quedan en salidas_local/ (ignorada por git).
"""
import json
import os
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
plt.show = lambda *a, **k: plt.close("all")

BASE = Path(__file__).resolve().parents[1]
os.chdir(BASE)
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
KAGGLE = Path(ARGS[0]) if ARGS else BASE / "kaggle_outputs" / "v5"
nb = json.loads((BASE / "notebook" / "TPI_IA_2026P_5.ipynb").read_text(encoding="utf-8"))
codigo = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
ns = {"__name__": "__notebook__", "time": time, "torch": torch}


def correr(marca, hasta=None, titulo=None):
    """Ejecuta la celda que contiene `marca`, opcionalmente sólo hasta el texto `hasta`."""
    celdas = [c for c in codigo if marca in c]
    assert len(celdas) == 1, f"{marca!r}: {len(celdas)} celdas"
    src = celdas[0]
    if hasta:
        assert hasta in src, f"no está {hasta!r}"
        src = src[:src.index(hasta)]
    print(f"\n{'=' * 20} {titulo or marca} {'=' * 20}")
    t0 = time.time()
    exec(compile(src, marca, "exec"), ns)
    print(f"[{time.time() - t0:.1f} s]")


# --- Fases 0 a 3: sólo lo que no necesita GPU ---
correr("RUN_ID = time.strftime", titulo="0 corrida")
correr("ROOT = next(", titulo="1.0 datos")
correr('imgs = pd.DataFrame(ann["images"])', titulo="1.1 tablas")
correr('pos = objs.groupby("image_id").category_id.apply(set)', titulo="1.5 LVIS")
correr("def iou_xywh", titulo="1.6 IoU")
correr("def evaluar_cajas", titulo="2.1 métrica")
correr("def aplicar_nms", hasta="dets_nms = aplicar_nms(dets)", titulo="2.4 NMS (defs)")
correr("def gt_detectados", hasta="sel = dets_nms", titulo="2.5 (defs)")
pd, np, Image = ns["pd"], ns["np"], ns["Image"]
ns.update(device="cpu", VOCAB=ns["cats"].category_name.tolist(), CAT_IDS=ns["cats"].category_id.tolist())
correr("SINONIMOS = {", hasta="Q_TEXTOS, Q_CLASE, Q_BASE", titulo="2.9 sinónimos")

# Estado de 2.9 en la corrida de Kaggle: variante ganadora, sus detecciones crudas y la tabla de experimentos
tabla_det = pd.read_csv(KAGGLE / "results" / "det_experimentos.csv")
g = tabla_det.loc[tabla_det.F1.idxmax()]
var = "con_sinonimos" if g.sinonimos else "sin_sinonimos"
partes = [pd.read_pickle(KAGGLE / "dets_owlv2-base-patch16-ensemble_completa_dev.pkl")]
if g.ventanas:
    partes.append(pd.read_pickle(KAGGLE / "dets_owlv2-base-patch16-ensemble_ventanas_dev.pkl"))
dets_multi = pd.concat([p[p.variante == var] for p in partes], ignore_index=True)
DET_CONFIG = dict(modelo=g.modelo, prompt="a photo of a {clase}", sinonimos=bool(g.sinonimos), ventanas=bool(g.ventanas),
                  frac_ventana=0.6 if g.ventanas else None, ensamble_large=bool(g.ensamble_large),
                  k_max=int(g.k), nms_iou=0.5, umbral=float(g.umbral))
ns.update(tabla_det=tabla_det, g=g, dets_multi=dets_multi, DET_CONFIG=DET_CONFIG, K_MAX=int(g.k), UMBRAL=float(g.umbral),
          MODELO=g.modelo, RESULTADOS=BASE / "salidas_local" / "results")
print(f"\n2.9 (de {KAGGLE.name}): {g.variante} | k = {int(g.k)} | umbral {g.umbral} | {len(dets_multi)} detecciones crudas")

correr("def rle_encode", hasta="# Test 3", titulo="3.2 RLE")
correr("gt_rle = defaultdict(list)", hasta="rle_sam, rle_caja, vacias", titulo="3.3 métrica de máscaras")
tabla_seg = pd.read_csv(KAGGLE / "results" / "seg_experimentos.csv")
ns.update(dets_final=pd.read_pickle(KAGGLE / "dets_final_dev_con_mascaras.pkl"), tabla_seg=tabla_seg,
          SAM_ID=tabla_seg.loc[tabla_seg.F1.idxmax(), "segmentador"], oraculo=pd.read_csv(KAGGLE / "results" / "seg_oraculo.csv"),
          CAJA_DESDE_MASCARA=False)
correr("def propiedades", hasta="# Calculamos todo sobre", titulo="3.4 propiedades")
correr("def agregar_atributos", hasta="# --- Demostración", titulo="3.6 atributos (defs)")
SALIDA = BASE / "salidas_local"
(SALIDA / "results").mkdir(parents=True, exist_ok=True)
ns["SALIDA"] = SALIDA
correr("def procesar_imagen", hasta="# Prueba con una imagen de desarrollo", titulo="4.1 pipeline (defs)")
correr("# --- Demostración", titulo="3.6 atributos (demo)")

# --- 4.2 con detector y segmentador simulados: devuelven los objetos de la corrida de Kaggle ---
envio_k = pd.read_csv(KAGGLE / "submission.csv")
escenas_k = [json.loads(s) for s in envio_k.SceneJSON]
rutas = {p.stem: p for p in ns["ROOT"].rglob("*.jpg")}
stem2id = {Path(r.fname).stem: r.id for r in ns["img_meta"].values()}
df = ns["dets_final"]
aplicar_nms_real = ns["aplicar_nms"]


def linaje_de(escena):
    """Para las imágenes de desarrollo recupera fuente y rango desde dets_final (misma caja); en test no se guardaron."""
    d = df[df.image_id == stem2id.get(escena["image"]["id"], -1)]
    claves = {(int(r.category_id), round(float(r.score), 4)): r for r in d.itertuples()}
    return [claves.get((o["category_id"], o["confidence"])) for o in escena["objects"]]


def simular(escena):
    objs, lin = escena["objects"], linaje_de(escena)
    ns["detectar_multi"] = lambda path, umbral=0.05, k_max=None: [
        dict(category_id=o["category_id"], score=o["confidence"], rango=int(l.rango) if l is not None else 0,
             fuente=l.fuente if l is not None else "imagen",
             bbox=[o["bbox"][0], o["bbox"][1], o["bbox"][2] - o["bbox"][0], o["bbox"][3] - o["bbox"][1]])
        for o, l in zip(objs, lin)]
    ns["segmentar"] = lambda im, cajas: [ns["rle_decode"](o["mask"]) for o in objs][:len(cajas)]


ns["aplicar_nms"] = lambda d: d
print(f"\n{'=' * 20} 4.2 envío con detector y segmentador simulados ({len(escenas_k)} imágenes) {'=' * 20}")
t0 = time.time()
traza, linaje, escenas, iguales = [], [], [], 0
for e in escenas_k:
    simular(e)
    nueva = ns["procesar_imagen"](rutas[e["image"]["id"]], e["image"]["id"], traza, linaje)
    iguales += [o["mask"] for o in nueva["objects"]] == [o["mask"] for o in e["objects"]] and \
               [o["bbox"] for o in nueva["objects"]] == [o["bbox"] for o in e["objects"]]
    escenas.append(nueva)
ns["aplicar_nms"] = aplicar_nms_real
traza, linaje = pd.DataFrame(traza), pd.DataFrame(linaje)
envio = pd.DataFrame(dict(image_id=[e["image"]["id"] for e in escenas],
                          SceneJSON=[json.dumps(e, separators=(",", ":"), ensure_ascii=False) for e in escenas]))
ns.update(traza=traza, linaje=linaje, escenas=escenas, envio=envio)
print(f"{time.time() - t0:.0f} s | escenas idénticas a las de Kaggle (cajas y máscaras): {iguales} de {len(escenas)} | "
      f"válidas: {sum(ns['validador'].is_valid(e) for e in escenas)} | con trace: {sum('trace' in e for e in escenas)} | "
      f"linaje: {len(linaje)} objetos, fuentes {linaje.fuente.value_counts().to_dict()}")

# --- Fase 5 completa ---
for marca, titulo in [("QUERY_SCHEMA = {", "5.1"), ("def query_determinista", "5.2"), ("def ejecutar(query, escena)", "5.3"),
                      ("escena_por_id = {", "5.4"), ("def escena_gt", "5.5"), ("NOMBRES_ES = {", "5.6"),
                      ("def problemas_de_fila", "5.7")]:
    correr(marca, titulo=titulo)

# --- Fase 6 ---
# Por defecto el LLM se simula con las salidas crudas de la corrida de Kaggle (rápido y, para la interpretación,
# idéntico a la primera pasada del modelo de 3B). Con --llm-real corre Qwen2.5-0.5B en CPU (lento: más de una hora).
import re
if "--llm-real" in sys.argv:
    os.environ.setdefault("TPI_LLM_ID", "Qwen/Qwen2.5-0.5B-Instruct")
    correr("LLM_ID = os.environ", titulo="6.1")
else:
    t_llm = pd.read_csv(KAGGLE / "traza_llm.csv").fillna("")
    qs_k = ns["qs"].set_index("question_id")
    INTERP = {qs_k.loc[r.question_id, "question"]: r.salida_interprete_1 for r in t_llm.itertuples()}
    extra_k = pd.read_csv(KAGGLE / "results" / "qa_llm_extra.csv").set_index("question_id")
    INTERP.update({p["question"]: extra_k.loc[p["question_id"], "consulta_llm"] for p in ns["preguntas_extra"]
                   if p["question_id"] in extra_k.index})
    VERB = {qs_k.loc[r.question_id, "question"]: r.texto_llm for r in t_llm.itertuples() if r.redaccion == "llm"}
    desc_k = pd.read_csv(KAGGLE / "results" / "qa_llm_descripciones.csv").set_index("question_id").texto
    DESC = {}

    def generar_simulado(conversaciones, max_new_tokens=160, lote=8):
        salidas = []
        for c in conversaciones:
            sistema, ultimo = c[0]["content"], c[-1]["content"]
            if sistema.startswith("Sos el módulo de interpretación"):
                reintento = len(c) > len(ns["MENSAJES_INTERPRETE"]) + 1
                salidas.append(c[-2]["content"] if reintento else
                               INTERP.get(ultimo, '{"intent": "unsupported", "classes": [], "reason": "sin salida guardada"}'))
            elif sistema.startswith("Redactás"):
                pregunta = re.search(r"Pregunta: (.*)\n", ultimo).group(1)
                salidas.append(VERB.get(pregunta) or re.search(r"Resultado del motor: (.*)\n", ultimo).group(1))
            elif sistema.startswith("Escribís descripciones"):
                if not DESC:   # resumen de cada escena del benchmark -> descripción de la corrida de Kaggle
                    for p in ns["qs"][ns["qs"].type == "description"].itertuples():
                        res = ns["resumen_escena"](ns["escena_por_id"][p.image_key])[0]
                        DESC[f"Datos de la escena:\n{res}"] = desc_k.get(p.question_id, "")
                salidas.append(DESC.get(ultimo, c[-2]["content"]))
            else:
                salidas.append("listo")
        return salidas
    ns.update(difflib=__import__("difflib"), generar=generar_simulado, LLM_ID=f"simulado con las salidas de {KAGGLE.name}",
              LLM_CONFIG=dict(modelo=f"simulado con las salidas de {KAGGLE.name}", decodificacion="greedy", dispositivo="cpu"))
    print(f"\n6.1: LLM simulado con las salidas crudas de {KAGGLE.name} ({len(INTERP)} interpretaciones, {len(VERB)} redacciones)")
for marca, titulo in [("PROMPT_INTERPRETE = f", "6.2"), ("ZONAS_ES = dict(", "6.3"),
                      ("def responder_llm", "6.4"), ('e["questions_llm"] = preguntas_llm', "6.5")]:
    correr(marca, titulo=titulo)

# --- Fases 7 a 9 ---
for marca, titulo in [("PARTICIONES = [set(p)", "7.1"), ("def f1_por_fuente", "7.2"), ("ETAPAS = [", "8.1"),
                      ("def detalle_percepcion", "8.2"), ("def reconstruir", "8.3"), ("modulos = traza.groupby", "8.4"),
                      ("resumen_final = pd.DataFrame", "9")]:
    correr(marca, titulo=titulo)
