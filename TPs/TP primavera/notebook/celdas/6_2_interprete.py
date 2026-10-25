PROMPT_INTERPRETE = f"""Sos el módulo de interpretación de un sistema que responde preguntas sobre una escena.
NO ves la imagen y NO respondés la pregunta: sólo la traducís a una consulta JSON que después ejecuta un motor determinista.

Devolvé un único objeto JSON, sin texto adicional, con estas claves:
- "intent": count, existence, position, size, relation, attribute, compare, description o unsupported.
- "classes": los objetos mencionados, en inglés y escritos EXACTAMENTE como en el vocabulario. count, existence, position, size y attribute llevan 1 clase; relation y compare llevan 2, en el orden de la pregunta; description y unsupported llevan [].
- "predicate": sólo en relation: left_of, right_of, above, below, overlaps o near.
- "attribute": sólo en attribute: "color".
- "comparator": sólo en compare: more, fewer o same.
- "reason": sólo en unsupported: por qué no se puede responder.

Qué significa cada intención:
- count: cuántas instancias hay de un objeto. existence: si hay al menos una.
- position: en qué zona de la imagen (grilla 3x3) está un objeto. size: qué tamaño relativo tiene (small, medium o large).
- relation: si un objeto está arriba (above), abajo (below), a la izquierda (left_of), a la derecha (right_of), superpuesto (overlaps) o cerca (near) de otro.
- attribute: el color de un objeto. compare: si hay más (more), menos (fewer) o la misma cantidad (same) de un objeto que de otro.
- description: describir la escena.
- unsupported: cualquier otra cosa (acciones, materiales, estados, texto escrito, emociones, intenciones, etc.).

Reglas:
- Traducí cada objeto al nombre del vocabulario que significa lo mismo y escribí en "classes" sólo el nombre en inglés. Si ninguno significa lo mismo, escribí el nombre en inglés tal cual: nunca lo reemplaces por otro objeto parecido.
- No inventes clases ni operaciones.

Vocabulario ({len(VOCAB)} clases, en inglés y con un nombre en español entre paréntesis):
{", ".join(f"{c} ({NOMBRES_ES_PROPIOS.get(c, c)})" for c in VOCAB)}"""

EJEMPLOS_INTERPRETE = [
    ('¿Cuántas instancias de la categoría "silla" aparecen en la imagen?', {"intent": "count", "classes": ["chair"]}),
    ('¿Hay al menos una instancia de la categoría "paraguas" en la imagen?', {"intent": "existence", "classes": ["umbrella"]}),
    ('¿En qué zona de la imagen está la instancia de "computadora portátil"?', {"intent": "position", "classes": ["laptop"]}),
    ('¿Qué tamaño relativo tiene la instancia de "perro"?', {"intent": "size", "classes": ["dog"]}),
    ('¿La instancia de "lámpara" está a la izquierda de la instancia de "sofá"?',
     {"intent": "relation", "classes": ["lamp", "sofa"], "predicate": "left_of"}),
    ("¿La taza está cerca del plato?", {"intent": "relation", "classes": ["cup", "plate"], "predicate": "near"}),
    ("¿De qué color es el auto?", {"intent": "attribute", "classes": ["car"], "attribute": "color"}),
    ("¿Hay más botellas que cuencos en la imagen?", {"intent": "compare", "classes": ["bottle", "bowl"], "comparator": "more"}),
    ("Contame qué hay en la foto.", {"intent": "description", "classes": []}),
    ("¿Qué está comiendo el gato?", {"intent": "unsupported", "classes": [], "reason": "pregunta por una acción"}),
    ('¿Hay al menos una instancia de la categoría "dragón" en la imagen?', {"intent": "existence", "classes": ["dragon"]}),
]
MENSAJES_INTERPRETE = [{"role": "system", "content": PROMPT_INTERPRETE}]
for pregunta, consulta in EJEMPLOS_INTERPRETE:
    MENSAJES_INTERPRETE += [{"role": "user", "content": pregunta},
                            {"role": "assistant", "content": json.dumps(consulta, ensure_ascii=False)}]

INV_ES = {sin_acentos(v): k for k, v in NOMBRES_ES_PROPIOS.items()}   # diccionario propio, no el de la cátedra

def normalizar_clase(c):
    """Lleva la clase que propone el LLM al vocabulario. Devuelve (clase, cómo se resolvió)."""
    c0 = " ".join(str(c).strip().lower().split())
    if c0 in name2id:
        return c0, "exacta"
    for sing in (c0[:-1] if c0.endswith("s") else None, c0[:-2] if c0.endswith("es") else None):
        if sing in name2id:
            return sing, "singular"
    if sin_acentos(c0) in INV_ES:
        return INV_ES[sin_acentos(c0)], "diccionario_es"
    cerca = difflib.get_close_matches(c0, VOCAB, n=1, cutoff=0.88)
    if cerca:
        return cerca[0], "aproximada"
    return c0, "sin_coincidencia"

def extraer_json(texto):
    """Primer objeto JSON de la salida del LLM (o None)."""
    if "{" not in texto:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(texto[texto.index("{"):])
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None

def preparar_query(salida):
    """Salida cruda del LLM -> (consulta limpia, problemas, normalizaciones). El código decide, no el LLM."""
    crudo = extraer_json(salida)
    if crudo is None:
        return None, ["la salida no contiene un objeto JSON válido"], []
    q = {k: crudo[k] for k in ("intent", "classes", "predicate", "attribute", "comparator", "reason") if crudo.get(k) is not None}
    if isinstance(q.get("classes"), str):
        q["classes"] = [q["classes"]]
    q.setdefault("classes", [])
    norm = []
    if isinstance(q["classes"], list) and all(isinstance(c, str) for c in q["classes"]):
        resueltas = [normalizar_clase(c) for c in q["classes"]]
        norm = [dict(llm=c, clase=r, como=como) for c, (r, como) in zip(q["classes"], resueltas)]
        q["classes"] = [r for r, _ in resueltas]
    _, problemas = validar_query(q)
    if q.get("intent") == "unsupported":
        problemas = []
    return q, problemas, norm

def hay_que_reintentar(q, problemas):
    """Se reintenta por errores de formato, no por una clase fuera del vocabulario (eso es una respuesta válida)."""
    return q is None or any(not p.startswith("clase fuera del vocabulario") for p in problemas)

def interpretar(preguntas):
    """Lista de textos -> lista de dicts con la consulta, los problemas y el registro de la interpretación."""
    t0 = time.time()
    convs = [MENSAJES_INTERPRETE + [{"role": "user", "content": t}] for t in preguntas]
    salidas = generar(convs, max_new_tokens=100)
    res = []
    for s in salidas:
        q, prob, norm = preparar_query(s)
        res.append(dict(query=q, problemas=prob, normalizacion=norm, salida_1=s, intentos=1, valida_1=not hay_que_reintentar(q, prob)))
    reintentar = [i for i, r in enumerate(res) if not r["valida_1"]]
    if reintentar:
        convs2 = [convs[i] + [{"role": "assistant", "content": res[i]["salida_1"]},
                              {"role": "user", "content": f"Esa consulta no es válida: {'; '.join(res[i]['problemas'])}. "
                                                          "Corregila y devolvé sólo el JSON."}] for i in reintentar]
        for i, s in zip(reintentar, generar(convs2, max_new_tokens=100)):
            q, prob, norm = preparar_query(s)
            res[i].update(query=q, problemas=prob, normalizacion=norm, salida_2=s, intentos=2)
    ms = (time.time() - t0) * 1000 / max(1, len(preguntas))
    for r in res:
        r["valida_final"] = not hay_que_reintentar(r["query"], r["problemas"])
        r["ms_por_pregunta"] = round(ms, 1)
    return res

# Prueba con preguntas que no están en el benchmark
for t, r in zip(pruebas := ["¿Cuántos inodoros hay?", "¿El reloj está a la derecha de la ventana?", "¿Qué hora marca el reloj?"],
                interpretar(pruebas)):
    print(f"{t:45s} -> {json.dumps(r['query'], ensure_ascii=False)} | problemas: {r['problemas'] or '-'} | intentos: {r['intentos']}")
