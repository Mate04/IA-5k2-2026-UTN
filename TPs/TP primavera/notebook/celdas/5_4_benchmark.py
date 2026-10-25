escena_por_id = {e["image"]["id"]: e for e in escenas}
qs["image_key"] = qs.image_file.map(lambda f: Path(f).stem)
faltan = set(qs.image_key) - set(escena_por_id)
assert not faltan, f"preguntas sobre imágenes sin SceneJSON: {faltan}"

traza_qa, preguntas_det, filas_qa = [], defaultdict(list), []
for p in qs.to_dict("records"):
    escena = escena_por_id[p["image_key"]]
    q = query_determinista(p)
    r = paso(traza_qa, p["image_key"], "qa_determinista", dict(question_id=p["question_id"], query=q),
             lambda: ejecutar(q, escena))
    preguntas_det[p["image_key"]].append(dict(question_id=p["question_id"], type=p["type"], question=p["question"], **r, query=q))
    filas_qa.append(dict(question_id=p["question_id"], image_id=p["image_key"], type=p["type"], clases=", ".join(q["classes"]),
                         predicado=q.get("predicate"), respuesta=r["normalized_answer"], status=r["status"],
                         confianza=r["confidence"], n_evidencia=len(r["evidence"])))
qa_det = pd.DataFrame(filas_qa)

print("Consignas respondidas:", len(qa_det), "| por estado:", qa_det.status.value_counts().to_dict())
print(qa_det[qa_det.type != "description"].drop(columns="image_id").to_string(index=False))
ej = preguntas_det[qs.image_key.iloc[0]][0]
print("\nEjemplo de descripción por plantilla:\n", ej["answer"])
