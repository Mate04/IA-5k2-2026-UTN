"""Prueba rápida en CPU de las celdas del modo LLM (6.1 a 6.3) con un modelo chico y las escenas de una corrida guardada.

Uso (desde la carpeta del TP):  .venv/Scripts/python -X utf8 dev/probar_llm.py [carpeta_de_salidas_de_kaggle]
"""
import ast
import contextlib
import io
import json
import os
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
os.chdir(BASE)
os.environ.setdefault("TPI_LLM_ID", "Qwen/Qwen2.5-0.5B-Instruct")
SALIDAS_KAGGLE = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "kaggle_outputs" / "v2"
nb = json.loads((BASE / "notebook" / "TPI_IA_2026P_5.ipynb").read_text(encoding="utf-8"))
codigo = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
ns = {"__name__": "__notebook__", "time": time}


def celda(marca):
    c = [x for x in codigo if marca in x]
    assert len(c) == 1, marca
    return c[0]


def correr(marca, hasta=None, silencio=True):
    src = celda(marca)
    if hasta:
        src = src[:src.index(hasta)]
    with (contextlib.redirect_stdout(io.StringIO()) if silencio else contextlib.nullcontext()):
        exec(compile(src, marca, "exec"), ns)


def definir(marca, nombre):
    """Ejecuta sólo la función `nombre` de la celda que contiene `marca`."""
    arbol = ast.parse(celda(marca))
    fn = next(n for n in arbol.body if isinstance(n, ast.FunctionDef) and n.name == nombre)
    exec(compile(ast.Module(body=[fn], type_ignores=[]), nombre, "exec"), ns)


import torch
correr("ROOT = next(")
correr('imgs = pd.DataFrame(ann["images"])')
correr("def rle_encode", hasta="# Test 1")
ns.update(torch=torch, device="cpu", VOCAB=ns["cats"].category_name.tolist(), Counter=__import__("collections").Counter,
          defaultdict=__import__("collections").defaultdict, jsonschema=__import__("jsonschema"))
correr("QUERY_SCHEMA = {", hasta="# Pruebas de la validación")
correr("def query_determinista", hasta="# Las 10 preguntas")
correr("CONF_AUSENCIA = 0.5")
definir("def escena_gt", "clases_nombradas")
correr("NOMBRES_ES = {", hasta="FUERA_DE_ALCANCE")
pd = ns["pd"]
escenas = [json.loads(s) for s in pd.read_csv(SALIDAS_KAGGLE / "submission.csv").SceneJSON]
qs = ns["qs"]
qs["image_key"] = qs.image_file.map(lambda f: Path(f).stem)
ns["escena_por_id"] = {e["image"]["id"]: e for e in escenas}

t0 = time.time()
for marca, titulo in [("LLM_ID = os.environ", "6.1"), ("PROMPT_INTERPRETE = f", "6.2"), ("ZONAS_ES = dict(", "6.3")]:
    print(f"\n===== {titulo} =====")
    correr(marca, silencio=False)

print("\n===== verbalización de 6 respuestas del motor =====")
muestras = qs[qs.type != "description"].head(6).to_dict("records")
rs = [ns["ejecutar"](ns["query_determinista"](p), ns["escena_por_id"][p["image_key"]]) for p in muestras]
textos = ns["generar"]([ns["mensajes_verbalizar"](p["question"], r) for p, r in zip(muestras, rs)], max_new_tokens=80)
for p, r, t in zip(muestras, rs, textos):
    print(f"[{'OK' if ns['verbalizacion_fiel'](t, r, p['type']) else 'RECHAZADA'}] {r['normalized_answer']} -> {t}")
print(f"\nOK en {time.time() - t0:.0f} s")
