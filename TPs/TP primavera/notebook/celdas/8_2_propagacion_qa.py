# --- 8.2 ¿De dónde viene cada respuesta incorrecta? (benchmark, los dos modos) ---
lin_idx = linaje.set_index(["image_id", "obj_id"])
prop_idx = prop.set_index("ann_id")
preg = qs.set_index("question_id")

def detalle_percepcion(image_key, clases):
    """Para las clases de la pregunta compara el SceneJSON con las anotaciones: objetos reales que faltan (con la etapa
    de 8.1 donde se perdieron) y objetos predichos que no corresponden a ninguno real (con su linaje)."""
    esc, img_id = escena_por_id[image_key], stem2id[image_key]
    perdidos, falsos = Counter(), []
    for clase in clases:
        gts = [a for a in anns_por_img[img_id] if a["category_id"] == name2id[clase]]
        usado = [False] * len(gts)
        for o in instancias(esc, clase):
            b = [o["bbox"][0], o["bbox"][1], o["bbox"][2] - o["bbox"][0], o["bbox"][3] - o["bbox"][1]]
            ious = [-1 if usado[j] else iou_xywh(b, g["bbox"]) for j, g in enumerate(gts)]
            j = int(np.argmax(ious)) if gts else -1
            if j >= 0 and ious[j] >= 0.5:
                usado[j] = True
            else:
                l = lin_idx.loc[(image_key, o["id"])]
                falsos.append(f"{clase} {o['id']} ({l.fuente}, confianza {l.score:.2f})")
        for g, u in zip(gts, usado):
            if not u:
                perdidos[(clase, prop_idx.loc[g["id"], "etapa"])] += 1
    return perdidos, falsos

def etapa_del_error(p, fila_llm=None):
    """Etapa que explica una respuesta incorrecta, en el orden de la pipeline inversa: interpretación -> percepción -> regla."""
    if fila_llm is not None and not fila_llm.interpretacion_ok:
        return "interpretación (LLM)", f"consulta del LLM: {fila_llm.consulta_llm}"
    clases = list(p.class_en)
    perdidos, falsos = detalle_percepcion(p.image_key, clases)
    texto = "; ".join([f"{n} {c} perdido(s): {e}" for (c, e), n in perdidos.items()] + [f"sobra {f}" for f in falsos])
    if perdidos:   # la etapa que explica más objetos perdidos; si empatan, la más temprana de la pipeline
        por_etapa = Counter()
        for (_, e), n in perdidos.items():
            por_etapa[e] += n
        temprana = {e: i for i, e in enumerate(reversed(ETAPAS))}
        return f"percepción: {max(por_etapa, key=lambda e: (por_etapa[e], -temprana[e]))}", texto
    if falsos:
        return "percepción: falso positivo del detector", texto
    etapas_gt = {prop_idx.loc[a["id"], "etapa"] for c in clases for a in anns_por_img[stem2id[p.image_key]]
                 if a["category_id"] == name2id[c]}
    if "máscara mala (SAM2)" in etapas_gt:
        return "segmentación: máscara mala", "la instancia es la correcta, pero su máscara (y su centroide) no"
    return "regla derivada (zona, tamaño o relación)", "misma instancia y buena máscara; el valor cae del otro lado de un límite de la regla"

filas_eq = []
for f in ev_det[~ev_det.correcta].itertuples():
    etapa, det = etapa_del_error(preg.loc[f.question_id])
    filas_eq.append(dict(modo="determinista", question_id=f.question_id, type=f.type, clases=f.clases, pred=f.pred, ref=f.ref,
                         etapa=etapa, detalle=det))
cerr_llm = ev_llm[(ev_llm.type != "description") & ~ev_llm.correcta_llm.astype(bool)]
for f in cerr_llm.itertuples():
    p = preg.loc[f.question_id]
    etapa, det = etapa_del_error(p, f)
    filas_eq.append(dict(modo="LLM", question_id=f.question_id, type=f.type, clases=", ".join(p.class_en), pred=f.respuesta_llm,
                         ref=f.ref, etapa=etapa, detalle=det))
prop_qa = pd.DataFrame(filas_eq)
prop_qa.to_csv(RESULTADOS / "propagacion_qa.csv", index=False)
print("Respuestas incorrectas por etapa de origen (preguntas cerradas):")
print(pd.crosstab(prop_qa.etapa, prop_qa.modo, margins=True, margins_name="total").to_string())
print()
with pd.option_context("display.max_colwidth", 110):
    print(prop_qa[["modo", "question_id", "type", "pred", "ref", "etapa", "detalle"]].to_string(index=False))
