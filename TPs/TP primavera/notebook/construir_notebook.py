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
     "| v3 | Atributos y proximidad (3.6), preguntas en modo determinista (Fase 5), validación de filas antes del envío | pendiente |\n\n"),
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
]

# Celdas nuevas: (texto que identifica la celda de referencia, "despues" o "reemplazar", archivos en orden)
INSERCIONES = [
    ("### 3.5 Conclusiones de la Fase 3", "despues", ["3_6_atributos.md", "3_6_atributos.py"]),
    (None, "reemplazar_ultima_vacia", ["5_0_intro.md", "5_1_consulta.md", "5_1_consulta.py", "5_2_parser.md", "5_2_parser.py",
                                       "5_3_motor.md", "5_3_motor.py", "5_4_benchmark.md", "5_4_benchmark.py",
                                       "5_5_evaluacion.md", "5_5_evaluacion.py", "5_6_extra.md", "5_6_extra.py",
                                       "5_7_envio.md", "5_7_envio.py", "5_8_conclusiones.md"]),
]


def fuente(celda):
    return "".join(celda["source"])


def nueva_celda(archivo):
    texto = (CELDAS / archivo).read_text(encoding="utf-8").rstrip("\n")
    lineas = texto.splitlines(keepends=True)
    id_celda = "v3-" + archivo.replace(".", "-").replace("_", "-")
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
        if modo == "despues":
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
