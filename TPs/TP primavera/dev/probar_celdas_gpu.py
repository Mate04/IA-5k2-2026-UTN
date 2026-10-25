"""Prueba en CPU, con pocas imágenes, las celdas nuevas que en Kaggle usan GPU (2.9 detector y 3.3b SAM2).

No mide nada: sólo verifica que el código corre y que las cajas de OWLv2-large caen donde corresponde.
Uso (desde la carpeta del TP):  .venv/Scripts/python -X utf8 dev/probar_celdas_gpu.py [n_imagenes]
"""
import contextlib
import io
import json
import os
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.show = lambda *a, **k: plt.close("all")

BASE = Path(__file__).resolve().parents[1]
os.chdir(BASE)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
nb = json.loads((BASE / "notebook" / "TPI_IA_2026P_5.ipynb").read_text(encoding="utf-8"))
codigo = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
ns = {"__name__": "__notebook__", "time": time}


def correr(marca, hasta=None, desde=None, titulo=None, silencio=False):
    celdas = [c for c in codigo if marca in c]
    assert len(celdas) == 1, f"{marca!r}: {len(celdas)} celdas"
    src = celdas[0]
    if desde:
        src = src[src.index(desde):]
    if hasta:
        src = src[:src.index(hasta)]
    print(f"\n{'=' * 20} {titulo or marca} {'=' * 20}")
    t0 = time.time()
    with (contextlib.redirect_stdout(io.StringIO()) if silencio else contextlib.nullcontext()):
        exec(compile(src, marca, "exec"), ns)
    print(f"[{time.time() - t0:.1f} s]")


for marca in ["ROOT = next(", 'imgs = pd.DataFrame(ann["images"])', 'pos = objs.groupby("image_id").category_id.apply(set)',
              "def iou_xywh", "def evaluar_cajas"]:
    correr(marca, silencio=True)
correr("MODELO = \"google/owlv2-base-patch16-ensemble\"", titulo="2.2 OWLv2 base")
correr("def aplicar_nms", hasta="dets_nms = aplicar_nms(dets)", titulo="2.4 NMS (defs)")
correr("def gt_detectados", hasta="sel = dets_nms", titulo="2.5 (defs)")
correr("def detectar_multi(img_path, umbral=0.05, k_max=3)", hasta="filas = []", titulo="2.7 (defs)")

pd, np = ns["pd"], ns["np"]
ns["SALIDA"] = BASE / "salidas_local"
ns["SALIDA"].mkdir(exist_ok=True)
ns["dets_multi"] = pd.read_pickle(BASE / "notebook" / "salidas_local" / "dets_owlv2_base_dev_top3.pkl")
todas = ns["imgs"]
correr("SINONIMOS = {", hasta="# Línea base: las mismas", titulo="2.9 definiciones")

# Chequeo de coordenadas de OWLv2-large en las N imágenes: TP a IoU 0,5 con umbral 0,2, contra base
sub = todas.head(N)
for nombre in (ns["MODELO_BASE"], ns["MODELO_LARGE"]):
    t0, tp, n_pred, n_gt = time.time(), 0, 0, 0
    for img_id, fname in sub[["id", "fname"]].itertuples(index=False):
        im = ns["Image"].open(ns["DEV"] / "images" / fname).convert("RGB")
        filas = [f for f in ns["owl_pasada"](im, nombre)["con_sinonimos"] if f["score"] >= 0.2 and f["rango"] == 0]
        n_pred += len(filas)
        for (i, c), gts in ns["gt_by"].items():
            if i != img_id:
                continue
            n_gt += len(gts)
            tp += sum(any(ns["iou_xywh"](f["bbox"], g) >= 0.5 for f in filas if f["category_id"] == c) for g in gts)
    print(f"{nombre.split('/')[-1]}: {n_pred} predicciones, {tp} de {n_gt} objetos reales encontrados ({time.time() - t0:.0f} s)")
im = ns["Image"].open(ns["DEV"] / "images" / sub.fname.iloc[0]).convert("RGB")
v = ns["owl_ventanas"](im, ns["MODELO_LARGE"])
print("ventanas:", ns["ventanas"](*im.size), "| filas por variante:", {k: len(x) for k, x in v.items()})

# Resto de 2.9 con sólo N imágenes (las F1 salen bajas: es una prueba de plomería)
ns["imgs"] = sub
correr("SINONIMOS = {", desde="# Línea base: las mismas", titulo="2.9 experimentos (N imágenes)")
ns["imgs"] = todas
print("detectar_multi final:", len(ns["detectar_multi"](ns["DEV"] / "images" / sub.fname.iloc[0])), "filas")

# 3.3b con las detecciones finales de N imágenes
correr('SAM_ID = "facebook/sam2.1-hiera-small"', hasta="# Prueba con la imagen", titulo="3.1 SAM2 (defs y dets_final)")
correr("def rle_encode", hasta="# Test 3", titulo="3.2 RLE", silencio=True)
correr("gt_rle = defaultdict(list)", hasta="rle_sam, rle_caja, vacias", titulo="3.3 métrica (defs)", silencio=True)
ids = set(sub.id)
df = pd.read_pickle(BASE / "notebook" / "salidas_local" / "dets_final_dev_con_mascaras.pkl")
ns["dets_final"] = df[df.image_id.isin(ids)].copy()
objs_todos = ns["objs"]
ns["objs"] = objs_todos[objs_todos.image_id.isin(ids)]
correr("def segmentar_con", titulo="3.3b SAM2 large + oráculo (N imágenes)")
ns["objs"] = objs_todos
print("\nOK: celdas 2.9 y 3.3b corren de punta a punta.")
