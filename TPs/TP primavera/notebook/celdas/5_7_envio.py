def problemas_de_fila(e):
    """Lo que según la métrica oficial invalida una fila: JSON fuera del schema, RLE inconsistente o referencias rotas."""
    errores = [x.message[:120] for x in validador.iter_errors(e)]
    ids = {o["id"] for o in e["objects"]}
    if len(ids) != len(e["objects"]):
        errores.append("ids de objetos repetidos")
    for o in e["objects"]:
        h, w = o["mask"]["size"]
        if sum(o["mask"]["counts"]) != h * w or [h, w] != [e["image"]["height"], e["image"]["width"]]:
            errores.append(f"RLE inconsistente en {o['id']}")
    for r in e["relations"] + e.get("extra_relations", []):
        if r["subject"] not in ids or r["object"] not in ids:
            errores.append(f"relación con id inexistente: {r}")
    for x in e.get("questions", []) + e.get("questions_llm", []):
        errores += [f"evidencia inexistente {i} en {x['question_id']}" for i in x["evidence"] if i not in ids]
    return errores

for e in escenas:
    e["questions"] = preguntas_det.get(e["image"]["id"], [])
    e.setdefault("questions_llm", [])

problemas = {e["image"]["id"]: problemas_de_fila(e) for e in escenas}
malas = {k: v for k, v in problemas.items() if v}
print("Filas con problemas:", len(malas), "de", len(escenas))
assert not malas, list(malas.items())[:3]
con_preguntas = sum(len(e["questions"]) > 0 for e in escenas)
print("Filas con questions:", con_preguntas, "| preguntas:", sum(len(e["questions"]) for e in escenas))
assert con_preguntas == qs.image_key.nunique()

envio = pd.DataFrame(dict(image_id=[e["image"]["id"] for e in escenas],
                          SceneJSON=[json.dumps(e, separators=(",", ":"), ensure_ascii=False) for e in escenas]))
assert list(envio.image_id) == list(sub.image_id), "filas u orden distintos al sample"
envio.to_csv(SALIDA / "submission.csv", index=False)
envio.to_csv(SALIDA / "solution.csv", index=False)

RESULTADOS = SALIDA / "results"
RESULTADOS.mkdir(exist_ok=True)
qa_det.to_csv(RESULTADOS / "qa_det_respuestas.csv", index=False)
ev_det.to_csv(RESULTADOS / "qa_det_exactitud.csv", index=False)
fid.to_csv(RESULTADOS / "qa_det_fidelidad.csv", index=False)
ev_extra.to_csv(RESULTADOS / "qa_extra_manejo.csv", index=False)
pd.DataFrame(traza_qa).to_csv(SALIDA / "traza_qa.csv", index=False)
print(f"submission.csv: {(SALIDA / 'submission.csv').stat().st_size / 1e6:.1f} MB | resultados en {RESULTADOS}")
marcar_fase("5 QA determinista")
