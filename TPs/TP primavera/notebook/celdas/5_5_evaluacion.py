stem2id = {Path(r.fname).stem: r.id for r in img_meta.values()}
anns_por_img = defaultdict(list)
for a in ann["annotations"]:
    anns_por_img[a["image_id"]].append(a)

def escena_gt(image_key):
    """SceneJSON armado con las ANOTACIONES. Sólo para evaluar: mismas reglas de propiedades, relaciones y atributos."""
    r = img_meta[stem2id[image_key]]
    objetos = []
    for a in anns_por_img[r.id]:
        m = mask_utils.decode(mask_utils.merge(mask_utils.frPyObjects(a["segmentation"], r.height, r.width))).astype(bool)
        if m.sum() == 0:
            continue
        x, y, w, h = a["bbox"]
        objetos.append(dict(id=f"gt_{a['id']}", category_id=a["category_id"], confidence=1.0, bbox=[x, y, x + w, y + h],
                            mask=rle_encode(m), **propiedades(m, r.width, r.height)))
    esc = dict(image=dict(id=image_key, width=r.width, height=r.height), objects=objetos,
               relations=relaciones_con_tope(objetos, r.width, r.height)[0])
    agregar_atributos(esc, Image.open(DEV / "images" / r.fname).convert("RGB"))
    return esc

escenas_gt = {k: escena_gt(k) for k in qs.image_key.unique()}

def iou_obj(o1, o2):
    return float(mask_utils.iou([a_rle_coco(o1["mask"])], [a_rle_coco(o2["mask"])], [0])[0][0])

def origen_error(p, q, esc, esc_gt, r_pred, r_gt):
    """Clasifica por qué una respuesta no coincide con la de la escena real."""
    n_pred = [len(instancias(esc, c)) for c in q["classes"]]
    n_gt = [len(instancias(esc_gt, c)) for c in q["classes"]]
    if p["type"] in ("count", "existence"):
        if n_pred[0] == 0:
            return "percepción: clase no detectada"
        return "percepción: sobran instancias (FP o duplicados)" if n_pred[0] > n_gt[0] else "percepción: faltan instancias"
    if r_pred["status"] == "insufficient_information":
        return "percepción: clase no detectada (unknown)"
    ids_pred = {o["id"]: o for o in esc["objects"]}
    ids_gt = {o["id"]: o for o in esc_gt["objects"]}
    for e_pred, e_gt in zip(r_pred["evidence"], r_gt["evidence"]):
        if iou_obj(ids_pred[e_pred], ids_gt[e_gt]) < 0.5:
            return "percepción: se eligió otra instancia (FP o mala localización)"
    return "borde de regla: misma instancia, valor distinto (zona, tamaño o margen)"

filas_ev = []
for p in qs[qs.type != "description"].to_dict("records"):
    q = query_determinista(p)
    item = next(x for x in preguntas_det[p["image_key"]] if x["question_id"] == p["question_id"])
    r_gt = ejecutar(q, escenas_gt[p["image_key"]])
    ok = item["normalized_answer"] == r_gt["normalized_answer"]
    filas_ev.append(dict(question_id=p["question_id"], type=p["type"], clases=", ".join(q["classes"]),
                         pred=item["normalized_answer"], ref=r_gt["normalized_answer"], correcta=ok, status=item["status"],
                         n_pred=len(instancias(escena_por_id[p["image_key"]], q["classes"][0])),
                         n_gt=len(instancias(escenas_gt[p["image_key"]], q["classes"][0])),
                         origen="" if ok else origen_error(p, q, escena_por_id[p["image_key"]], escenas_gt[p["image_key"]], item, r_gt)))
ev_det = pd.DataFrame(filas_ev)

def clases_nombradas(texto):
    """Clases del vocabulario que aparecen en un texto. Primero las más largas, para no leer 'glove' dentro de 'baseball glove'."""
    encontradas = set()
    for c in sorted(name2id, key=len, reverse=True):
        patron = rf"\b{re.escape(c)}\b"
        if re.search(patron, texto):
            encontradas.add(c)
            texto = re.sub(patron, " ", texto)
    return encontradas

def verificar_fidelidad(item, escena):
    """Verificador independiente del motor: ¿la respuesta se lee tal cual del SceneJSON predicho?"""
    q, objs = item["query"], {o["id"]: o for o in escena["objects"]}
    if not set(item["evidence"]) <= set(objs):
        return False                                       # evidencia que no existe en la escena
    if item["status"] in ("unsupported", "insufficient_information"):
        return item["evidence"] == [] and item["normalized_answer"] in ("unsupported", "unknown", "empty_scene")
    it = q["intent"]
    if it in ("count", "existence"):
        n = sum(o["category_id"] == name2id[q["classes"][0]] for o in escena["objects"])
        return item["normalized_answer"] == (n if it == "count" else ("yes" if n else "no"))
    if it in ("position", "size", "attribute"):
        o = objs[item["evidence"][0]]
        valor = o["attributes"][q["attribute"]] if it == "attribute" else o[it]
        return o["category_id"] == name2id[q["classes"][0]] and valor == item["normalized_answer"]
    if it == "relation":
        a, b = item["evidence"]
        trip = {(r["subject"], r["predicate"], r["object"]) for r in escena["relations"] + escena.get("extra_relations", [])}
        hay = (a, q["predicate"], b) in trip or (q["predicate"] in ("near", "overlaps") and (b, q["predicate"], a) in trip)
        return (item["normalized_answer"] == "yes") == hay
    if it == "compare":
        n, m = [sum(o["category_id"] == name2id[c] for o in escena["objects"]) for c in q["classes"]]
        return item["normalized_answer"] == ("yes" if {"more": n > m, "fewer": n < m, "same": n == m}[q["comparator"]] else "no")
    if it == "description":   # toda clase nombrada en el texto tiene que estar en la escena
        return clases_nombradas(item["answer"]) <= {id2name[o["category_id"]] for o in escena["objects"]}
    return False

fid = pd.DataFrame([dict(type=x["type"], fiel=verificar_fidelidad(x, escena_por_id[k]))
                    for k, lista in preguntas_det.items() for x in lista])

print("Exactitud contra la escena real (preguntas cerradas):")
resumen = ev_det.groupby("type").agg(preguntas=("correcta", "size"), exactitud=("correcta", "mean"))
resumen.loc["TOTAL"] = [len(ev_det), ev_det.correcta.mean()]
print(resumen.round(3).to_string())
print("\nFidelidad al SceneJSON (verificador independiente):")
print(fid.groupby("type").fiel.agg(["size", "mean"]).rename(columns={"size": "respuestas", "mean": "fieles"}).round(3).to_string())
print(f"Total: {fid.fiel.mean():.1%} de {len(fid)} respuestas")
print("\nRespuestas incorrectas y origen del error:")
print(ev_det[~ev_det.correcta][["question_id", "type", "clases", "pred", "ref", "n_pred", "n_gt", "origen"]].to_string(index=False))
print("\nOrigen de los errores:", ev_det[~ev_det.correcta].origen.value_counts().to_dict())
