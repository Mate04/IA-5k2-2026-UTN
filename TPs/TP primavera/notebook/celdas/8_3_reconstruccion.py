# --- 8.3 Reconstrucción de una respuesta leyendo sólo las trazas y el SceneJSON ---
traza_llm_df = pd.DataFrame(traza_llm)

def reconstruir(question_id):
    p = preg.loc[question_id]
    k, esc = p.image_key, escena_por_id[p.image_key]
    print(f"■ {question_id} ({p.type}) sobre {k}: {p.question}")
    print(f"  1. Corrida: run_id {esc['trace']['run_id']} | hash de la configuración de percepción {esc['trace']['config_percepcion']}")
    tr = traza[traza.image_id == k]
    print("  2. Percepción (traza_envio):", " → ".join(f"{m} {n} ({ms:.0f} ms)" for m, n, ms in zip(tr.modulo, tr.n_salidas, tr.duracion_ms)))
    det = next(x for x in esc["questions"] if x["question_id"] == question_id)
    print(f"  3. Determinista (traza_qa): consulta {json.dumps(det['query'], ensure_ascii=False)} → {det['normalized_answer']}"
          f" [{det['status']}], evidencia {det['evidence']}, confianza {det['confidence']}")
    llm = next(x for x in esc["questions_llm"] if x["question_id"] == question_id)
    t = traza_llm_df.set_index("question_id").loc[question_id]
    print(f"  4. LLM (traza_llm): salida cruda {t.salida_interprete_1!r}")
    if t.intentos > 1:
        print(f"     reintento por {t.motivo_reintento}: {t.salida_interprete_2!r}")
    print(f"     normalización {t.normalizacion} → consulta {t.consulta} → {llm['normalized_answer']} [{llm['status']}]")
    print(f"     redacción ({t.redaccion}): {llm['answer']}")
    for oid in dict.fromkeys(det["evidence"] + llm["evidence"]):
        l = lin_idx.loc[(k, oid)]
        print(f"  5. Evidencia {oid} (traza_objetos): {l.clase}, confianza {l.score:.3f}, clase n.º {l.rango_clase + 1} de su caja, "
              f"fuente {l.fuente}, caja del detector {l.bbox_detector}, máscara de {l.mascara_px} px con {l.segmentador.split('/')[-1]}")
    perdidos, falsos = detalle_percepcion(k, list(p.class_en))
    ref = ejecutar(query_determinista(p.to_dict()), escenas_gt[k])["normalized_answer"]
    print(f"  6. Contra las anotaciones (sólo evaluación): referencia {ref} | objetos reales perdidos: "
          f"{dict((f'{c}: {e}', n) for (c, e), n in perdidos.items()) or 'ninguno'} | predicciones sin objeto real: {falsos or 'ninguna'}\n")

# Un error de conteo del modo determinista y, del modo LLM, una consulta con reintento o donde el código tradujo la clase
# (alias en inglés o diccionario español); si no hay ninguna, la primera de relación
ej_det = next((q for q in prop_qa[prop_qa.modo == "determinista"].question_id if preg.loc[q].type == "count"), prop_qa.question_id.iloc[0])
con_reintento = ev_llm[(ev_llm.intentos > 1) & (ev_llm.type != "description")].question_id.tolist()
traducidas = [q for q, n in zip(traza_llm_df.question_id, traza_llm_df.normalizacion)
              if {x["como"] for x in json.loads(n)} & {"alias_en", "diccionario_es"}]
ej_llm = (con_reintento + traducidas + qs[qs.type == "relation"].question_id.tolist())[0]
for q in dict.fromkeys([ej_det, ej_llm]):
    reconstruir(q)
