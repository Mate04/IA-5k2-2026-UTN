"""Corre en CPU las partes de la notebook que no necesitan GPU, para probar las celdas nuevas antes de subirlas a Kaggle.

Los SceneJSON de la Fase 4 se toman del submission.csv de una corrida de Kaggle (por defecto kaggle_outputs/v2).
Uso (desde la carpeta del TP):  .venv/Scripts/python -X utf8 dev/correr_local.py [carpeta_de_salidas_de_kaggle]
"""
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
SALIDAS_KAGGLE = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "kaggle_outputs" / "v2"
nb = json.loads((BASE / "notebook" / "TPI_IA_2026P_5.ipynb").read_text(encoding="utf-8"))
codigo = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
ns = {"__name__": "__notebook__", "time": time}


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


# Fases 1 a 4: sólo lo que no necesita GPU (datos, métricas, RLE, propiedades, procesar_imagen sin ejecutarla)
correr("ROOT = next(", titulo="1.0 datos")
correr('imgs = pd.DataFrame(ann["images"])', titulo="1.1 tablas")
correr('pos = objs.groupby("image_id").category_id.apply(set)', titulo="1.5 LVIS")
correr("def iou_xywh", titulo="1.6 IoU")
correr("def evaluar_cajas", titulo="2.1 métrica")
correr("def rle_encode", hasta="# Test 3", titulo="3.2 RLE")
correr("gt_rle = defaultdict(list)", hasta="rle_sam, rle_caja, vacias", titulo="3.3 métrica de máscaras")
correr("def propiedades", hasta="# Calculamos todo sobre", titulo="3.4 propiedades")
correr("def agregar_atributos", hasta="# --- Demostración", titulo="3.6 atributos (defs)")
correr("def procesar_imagen", hasta="# Prueba con una imagen de desarrollo", titulo="4.1 pipeline (defs)")

# Reemplazo local de lo que en Kaggle hace la GPU: escenas de una corrida real + atributos calculados en CPU
pd, np, Image = ns["pd"], ns["np"], ns["Image"]
envio = pd.read_csv(SALIDAS_KAGGLE / "submission.csv")
escenas = [json.loads(s) for s in envio.SceneJSON]
rutas = {p.stem: p for p in ns["ROOT"].rglob("*.jpg")}
t0 = time.time()
for e in escenas:
    if "extra_relations" not in e:        # la v2 no tenía atributos: se calculan acá con la misma función
        ns["agregar_atributos"](e, Image.open(rutas[e["image"]["id"]]).convert("RGB"))
print(f"\nAtributos agregados a {len(escenas)} escenas de {SALIDAS_KAGGLE.name} en {time.time() - t0:.0f} s")
stem2id = {Path(r.fname).stem: r.id for r in ns["img_meta"].values()}
filas = [dict(image_id=stem2id[e["image"]["id"]], category_id=o["category_id"], score=o["confidence"],
              bbox=[o["bbox"][0], o["bbox"][1], o["bbox"][2] - o["bbox"][0], o["bbox"][3] - o["bbox"][1]], rle_sam=o["mask"])
         for e in escenas if e["image"]["id"] in stem2id for o in e["objects"]]
SALIDA = BASE / "salidas_local"
SALIDA.mkdir(exist_ok=True)
ns.update(envio=envio, escenas=escenas, dets_final=pd.DataFrame(filas), SALIDA=SALIDA)

correr("# --- Demostración", titulo="3.6 atributos (demo sobre las 20 imágenes de dev de la corrida)")

# Prueba de integración de procesar_imagen() (parcheada en la v3) con detector y SAM2 falsos que devuelven lo de la corrida
print(f"\n{'=' * 20} 4.1 procesar_imagen() con detector y segmentador simulados {'=' * 20}")
def simular(escena):
    objs = escena["objects"]
    ns["detectar_multi"] = lambda path, umbral=0.05, k_max=2: [
        dict(category_id=o["category_id"], score=o["confidence"], rango=0,
             bbox=[o["bbox"][0], o["bbox"][1], o["bbox"][2] - o["bbox"][0], o["bbox"][3] - o["bbox"][1]]) for o in objs]
    ns["segmentar"] = lambda im, cajas: [ns["rle_decode"](o["mask"]) for o in objs][:len(cajas)]
ns.update(aplicar_nms=lambda d: d, MODELO="simulado", SAM_ID="simulado", UMBRAL=0.2,
          caja_a_mascara=lambda b, H, W: np.zeros((H, W), bool))
for e in escenas[:2] + escenas[-2:]:
    simular(e)
    traza_sim = []
    nueva = ns["procesar_imagen"](rutas[e["image"]["id"]], e["image"]["id"], traza_sim)
    iguales = [o1["mask"] == o2["mask"] and o1["bbox"] == o2["bbox"] for o1, o2 in zip(nueva["objects"], e["objects"])]
    print(f"{e['image']['id']}: {len(nueva['objects'])} objetos (antes {len(e['objects'])}) | mismas cajas y máscaras: {all(iguales)}"
          f" | con atributos: {all('attributes' in o for o in nueva['objects'])} | near: {len(nueva['extra_relations'])}"
          f" | válida: {ns['validador'].is_valid(nueva)} | módulos: {[t['modulo'] for t in traza_sim]}")

# Fase 5 completa
for marca, titulo in [("QUERY_SCHEMA = {", "5.1"), ("def query_determinista", "5.2"), ("def ejecutar(query, escena)", "5.3"),
                      ("escena_por_id = {", "5.4"), ("def escena_gt", "5.5"), ("NOMBRES_ES = {", "5.6"),
                      ("def problemas_de_fila", "5.7")]:
    correr(marca, titulo=titulo)
