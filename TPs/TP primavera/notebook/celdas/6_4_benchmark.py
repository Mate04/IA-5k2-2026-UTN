def responder_llm(preguntas, escenas_de):
    """Modo LLM completo. El LLM recibe SÓLO p['question']; image_key indica sobre qué SceneJSON ejecuta el motor."""
    interp = interpretar([p["question"] for p in preguntas])
    salida, a_verbalizar, a_describir = [None] * len(preguntas), [], []
    for i, (p, it) in enumerate(zip(preguntas, interp)):
        q = it["query"]
        if q and q.get("intent") == "description" and not it["problemas"]:
            a_describir.append(i)
        else:
            salida[i] = ejecutar(q or {}, escenas_de[p["image_key"]])
            a_verbalizar.append(i)
    for i, r in zip(a_describir, describir_llm([escenas_de[preguntas[i]["image_key"]] for i in a_describir])):
        salida[i] = r
    textos = generar([mensajes_verbalizar(preguntas[i]["question"], salida[i]) for i in a_verbalizar], max_new_tokens=80)
    for i, t in zip(a_verbalizar, textos):
        fiel = verbalizacion_fiel(t, salida[i], (interp[i]["query"] or {}).get("intent"))
        salida[i] = dict(salida[i], answer=t if fiel else salida[i]["answer"], redaccion="llm" if fiel else "plantilla", texto_llm=t)
    return interp, salida

def misma_consulta(q_llm, q_ref):
    """¿El LLM interpretó lo mismo que dicen los campos estructurados? (intención, clases en orden y predicado/comparador)"""
    q_llm = q_llm or {}
    if q_ref["intent"] != q_llm.get("intent"):
        return False
    if q_ref["intent"] in ("description", "unsupported"):
        return True
    return (list(q_llm.get("classes", [])) == q_ref["classes"] and q_llm.get("predicate") == q_ref.get("predicate")
            and q_llm.get("comparator") == q_ref.get("comparator"))

# --- Benchmark: 60 consignas sobre las 20 imágenes de desarrollo ---
t0 = time.time()
preg_bench = qs.to_dict("records")
interp_b, resp_b = responder_llm(preg_bench, escena_por_id)
print(f"Benchmark en modo LLM: {len(preg_bench)} consignas en {(time.time() - t0) / 60:.1f} min")

preguntas_llm, filas_llm, traza_llm = defaultdict(list), [], []
for p, it, r in zip(preg_bench, interp_b, resp_b):
    iq = it["query"] if it["query"] is not None else {"error": "; ".join(it["problemas"])}
    item = dict(question_id=p["question_id"], type=p["type"], question=p["question"], answer=r["answer"],
                normalized_answer=r["normalized_answer"], evidence=r["evidence"], confidence=r["confidence"], status=r["status"],
                interpreted_query=iq, llm=dict(modelo=LLM_ID, intentos=it["intentos"], normalizacion=it["normalizacion"],
                                               redaccion=r.get("redaccion")))
    if r.get("alternatives"):
        item["alternatives"] = r["alternatives"]
    preguntas_llm[p["image_key"]].append(item)

    q_det = query_determinista(p)
    item_det = next(x for x in preguntas_det[p["image_key"]] if x["question_id"] == p["question_id"])
    fila = dict(question_id=p["question_id"], type=p["type"], interpretacion_ok=misma_consulta(it["query"], q_det),
                json_valido_1=it["valida_1"], json_valido_final=it["valida_final"], intentos=it["intentos"],
                consulta_llm=json.dumps(it["query"], ensure_ascii=False), respuesta_llm=r["normalized_answer"],
                respuesta_det=item_det["normalized_answer"], redaccion=r.get("redaccion"), status=r["status"])
    if p["type"] != "description":
        ref = ejecutar(q_det, escenas_gt[p["image_key"]])["normalized_answer"]
        fila.update(ref=ref, correcta_llm=r["normalized_answer"] == ref, correcta_det=item_det["normalized_answer"] == ref,
                    igual_det=r["normalized_answer"] == item_det["normalized_answer"])
    filas_llm.append(fila)
    traza_llm.append(dict(image_id=p["image_key"], question_id=p["question_id"], params=json.dumps(LLM_CONFIG),
                          salida_interprete_1=it["salida_1"], salida_interprete_2=it.get("salida_2", ""), intentos=it["intentos"],
                          normalizacion=json.dumps(it["normalizacion"], ensure_ascii=False), ms_interprete=it["ms_por_pregunta"],
                          consulta=json.dumps(it["query"], ensure_ascii=False), status_motor=r["status"],
                          redaccion=r.get("redaccion"), texto_llm=r.get("texto_llm", r["answer"]), ok=it["valida_final"]))
ev_llm = pd.DataFrame(filas_llm)

print("\nInterpretación (consulta del LLM = consulta de los campos estructurados), por tipo:")
print(ev_llm.groupby("type").agg(consignas=("interpretacion_ok", "size"), interpretacion=("interpretacion_ok", "mean"),
                                 json_1er_intento=("json_valido_1", "mean"), json_final=("json_valido_final", "mean")).round(3).to_string())
cerr = ev_llm[ev_llm.type != "description"]
print(f"\nPreguntas cerradas ({len(cerr)}): exactitud LLM {cerr.correcta_llm.astype(bool).mean():.3f} | determinista {cerr.correcta_det.astype(bool).mean():.3f} | "
      f"misma respuesta que el determinista: {cerr.igual_det.astype(bool).mean():.1%}")
print("Redacción aceptada por el control (cerradas):", f"{(cerr.redaccion == 'llm').mean():.1%}")
mal = ev_llm[~ev_llm.interpretacion_ok]
if len(mal):
    print("\nConsignas mal interpretadas:")
    print(mal[["question_id", "type", "consulta_llm"]].to_string(index=False))

# Descripciones: control de alucinaciones y cobertura de las clases principales
filas_desc = []
for p, r in zip(preg_bench, resp_b):
    if p["type"] != "description":
        continue
    esc = escena_por_id[p["image_key"]]
    principales = [c for c, _ in Counter(id2name[o["category_id"]] for o in esc["objects"]).most_common(3)]
    nombradas = clases_nombradas(r["answer"].lower())
    filas_desc.append(dict(question_id=p["question_id"], redaccion=r.get("redaccion"), intentos=r.get("intentos"),
                           clases_nombradas=len(nombradas), alucinadas=len(nombradas - {id2name[o["category_id"]] for o in esc["objects"]}),
                           cobertura_top3=np.mean([c in nombradas for c in principales]) if principales else np.nan,
                           n_evidencia=len(r["evidence"]), texto=r["answer"]))
ev_desc = pd.DataFrame(filas_desc)
print(f"\nDescripciones: {(ev_desc.redaccion == 'llm').sum()} de {len(ev_desc)} redactadas por el LLM "
      f"({(ev_desc.intentos == 1).sum()} al primer intento) | clases alucinadas en las aceptadas: "
      f"{ev_desc[ev_desc.redaccion == 'llm'].alucinadas.sum()} | cobertura de las 3 clases principales: {ev_desc.cobertura_top3.mean():.2f}")
print("Ejemplo:", ev_desc.texto.iloc[0])

# --- Casos extra de 5.6 en modo LLM ---
interp_x, resp_x = responder_llm(preguntas_extra, escena_por_id)
filas_x = []
for p, it, r in zip(preguntas_extra, interp_x, resp_x):
    q_ref = query_determinista(p)
    if p["caso"] == "fuera de alcance":
        q_ref = dict(intent="unsupported", classes=[])
    r_ref = ejecutar(query_determinista(p), escenas_gt[p["image_key"]])
    filas_x.append(dict(question_id=p["question_id"], caso=p["caso"], pregunta=p["question"][:70],
                        interpretacion_ok=misma_consulta(it["query"], q_ref), respuesta=r["normalized_answer"], status=r["status"],
                        correcto=manejo_correcto(p, r, r_ref), consulta_llm=json.dumps(it["query"], ensure_ascii=False)))
ev_extra_llm = pd.DataFrame(filas_x)
print(f"\nCasos extra en modo LLM ({len(ev_extra_llm)} preguntas):")
print(ev_extra_llm.groupby("caso").agg(preguntas=("correcto", "size"), interpretacion=("interpretacion_ok", "mean"),
                                       manejo_correcto=("correcto", "mean")).round(3).to_string())
