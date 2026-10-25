CONF_AUSENCIA = 0.5   # no detectar no prueba ausencia (EDA 1.5): confianza media, decisión documentada

def instancias(escena, clase):
    cid = name2id[clase]
    return sorted((o for o in escena["objects"] if o["category_id"] == cid), key=lambda o: -o["confidence"])

def elegir(objs):
    """La instancia de mayor confianza. Si hay varias, se marca ambigua y se reparte la confianza."""
    top = objs[0]
    return top, len(objs) > 1, top["confidence"] / sum(o["confidence"] for o in objs)

def respuesta(texto, normalizada, evidencia, conf, estado, **extra):
    return dict(answer=texto, normalized_answer=normalizada, evidence=list(dict.fromkeys(evidencia)),
                confidence=round(float(np.clip(conf, 0, 1)), 4), status=estado, **extra)

def sin_info(motivo):
    return respuesta(f"{motivo}: no hay información suficiente para responder.", "unknown", [], 0.0, "insufficient_information")

def describir(escena, max_clases=6):
    """Descripción factual por plantilla: sólo cuenta y ubica lo que está en el SceneJSON."""
    objs = escena["objects"]
    if not objs:
        return respuesta("No se detectaron objetos en la escena.", "empty_scene", [], CONF_AUSENCIA, "insufficient_information")
    por_clase = defaultdict(list)
    for o in objs:
        por_clase[id2name[o["category_id"]]].append(o)
    orden = sorted(por_clase.items(), key=lambda kv: (-len(kv[1]), -kv[1][0]["confidence"]))
    partes, evid = [], []
    for nombre, lista in orden[:max_clases]:
        zona = Counter(o["position"] for o in lista).most_common(1)[0][0]
        partes.append(f"{len(lista)} {nombre} (sobre todo en {zona})" if len(lista) > 1 else f"1 {nombre} ({zona})")
        evid += [o["id"] for o in lista]
    grande = max(objs, key=lambda o: o["area_ratio"])
    evid.append(grande["id"])
    texto = (f"Se detectaron {len(objs)} objetos de {len(por_clase)} clases. Lo más frecuente: {', '.join(partes)}. "
             f"El objeto que más área ocupa es {id2name[grande['category_id']]} ({grande['position']}, {grande['size']}).")
    usados = {o["id"]: o["confidence"] for o in objs if o["id"] in set(evid)}
    return respuesta(texto, texto, evid, np.mean(list(usados.values())), "ok")

def ejecutar(query, escena):
    """Motor determinista: resuelve la consulta usando SÓLO el SceneJSON predicho."""
    q, problemas = validar_query(query)
    if problemas:
        return respuesta(f"No puedo responder con la información de la escena: {'; '.join(problemas)}.",
                         "unsupported", [], 0.0, "unsupported")
    it = q["intent"]
    if it == "description":
        return describir(escena)
    grupos = [instancias(escena, c) for c in q["classes"]]
    clase = q["classes"][0]

    if it in ("count", "existence", "compare"):
        todos = [o for g in grupos for o in g]
        ids, confs = [o["id"] for o in todos], [o["confidence"] for o in todos]
        conf = np.mean(confs) if confs else CONF_AUSENCIA
        n = len(grupos[0])
        if it == "count":
            return respuesta(f"Hay {n} instancia(s) de '{clase}' en la escena.", n, ids, conf, "ok")
        if it == "existence":
            return respuesta(f"Sí, hay {n} instancia(s) de '{clase}'." if n else f"No se detectó ninguna instancia de '{clase}'.",
                             "yes" if n else "no", ids, max(confs) if n else CONF_AUSENCIA, "ok")
        m = len(grupos[1])
        cumple = {"more": n > m, "fewer": n < m, "same": n == m}[q["comparator"]]
        return respuesta(f"{'Sí' if cumple else 'No'}: hay {n} '{clase}' y {m} '{q['classes'][1]}'.",
                         "yes" if cumple else "no", ids, conf, "ok")

    if it in ("position", "size", "attribute"):
        if not grupos[0]:
            return sin_info(f"No se detectó ninguna instancia de '{clase}'")
        o, ambigua, peso = elegir(grupos[0])
        valor = o.get("attributes", {}).get(q["attribute"]) if it == "attribute" else o[it]
        if valor is None:
            return respuesta(f"El atributo '{q['attribute']}' no está disponible en la escena.", "unsupported", [], 0.0, "unsupported")
        texto = {"position": f"La instancia de '{clase}' está en la zona {valor}.",
                 "size": f"La instancia de '{clase}' es de tamaño {valor}.",
                 "attribute": f"La instancia de '{clase}' es de color {valor}."}[it]
        if ambigua:
            texto += f" Hay {len(grupos[0])} instancias: respondo por la de mayor confianza ({o['id']})."
        return respuesta(texto, valor, [o["id"]], o["confidence"] * (peso if ambigua else 1),
                         "ambiguous" if ambigua else "ok", alternatives=[x["id"] for x in grupos[0][1:]])

    # relation
    a_objs, b_objs = grupos
    if q["classes"][0] == q["classes"][1]:
        b_objs = a_objs[1:]                     # misma clase: se comparan sus dos instancias más confiables
    if not a_objs or not b_objs:
        return sin_info(f"No se detectó ninguna instancia de '{q['classes'][0] if not a_objs else q['classes'][1]}'")
    a, amb_a, pa = elegir(a_objs)
    b, amb_b, pb = elegir(b_objs)
    fuente = escena.get("extra_relations", []) if q["predicate"] == "near" else escena["relations"]
    tripletas = {(r["subject"], r["predicate"], r["object"]) for r in fuente}
    hay = (a["id"], q["predicate"], b["id"]) in tripletas
    if q["predicate"] in ("near", "overlaps"):  # simétricas
        hay = hay or (b["id"], q["predicate"], a["id"]) in tripletas
    conf = min(a["confidence"], b["confidence"]) * (pa if amb_a else 1) * (pb if amb_b else 1)
    texto = (f"{'Sí' if hay else 'No'}: en la escena, '{q['classes'][0]}' ({a['id']}) {'' if hay else 'no '}cumple "
             f"{q['predicate']} respecto de '{q['classes'][1]}' ({b['id']}).")
    return respuesta(texto, "yes" if hay else "no", [a["id"], b["id"]], conf, "ambiguous" if (amb_a or amb_b) else "ok",
                     alternatives=[x["id"] for x in a_objs[1:] + b_objs[1:]])
