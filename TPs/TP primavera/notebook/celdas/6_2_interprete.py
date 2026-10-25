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

# v6: sinónimos y variantes regionales en español (diccionario propio). Motivo: en la v5 la pregunta decía "mango" y el
# diccionario sólo tenía "manija" para `handle`. Sólo palabras que no son el nombre de otra clase del vocabulario.
SINONIMOS_ES = {
    "handle": ["mango", "asa", "agarradera"], "spectacles": ["anteojos", "lentes"], "sunglasses": ["gafas de sol", "lentes de sol"],
    "doorknob": ["picaporte", "pomo"], "wall socket": ["enchufe"], "cell phone": ["celular", "telefono", "movil"],
    "car": ["coche", "automovil", "carro"], "bus": ["autobus", "omnibus"], "refrigerator": ["heladera", "nevera"],
    "television set": ["television", "tele"], "faucet": ["canilla"], "sink": ["lavabo", "lavamanos", "bacha"],
    "jacket": ["campera"], "kite": ["cometa"], "earring": ["arete"], "signboard": ["letrero"], "trash can": ["cesto de basura", "basurero", "papelera"],
    "baseball glove": ["manopla"], "flowerpot": ["matera"], "bowl": ["bol"], "skateboard": ["monopatin"], "motorcycle": ["motocicleta"],
    "bicycle": ["bici"], "streetlight": ["farol"], "license plate": ["matricula"], "headlight": ["faro"], "backpack": ["morral"],
    "suitcase": ["maleta"], "handbag": ["cartera"], "teddy bear": ["peluche"], "computer mouse": ["raton"], "laptop": ["notebook", "portatil"],
    "cabinet": ["armario", "alacena"], "jean": ["jeans", "vaqueros"], "short pants": ["shorts", "bermuda"], "baseball cap": ["gorra"],
    "blanket": ["frazada", "cobija"], "pillow": ["almohadon", "cojin"], "toilet": ["retrete"], "umbrella": ["sombrilla"],
    "boat": ["bote", "lancha"], "trousers": ["pantalon"], "fireplug": ["boca de incendio"], "vent": ["rejilla"],
}
assert set(SINONIMOS_ES) <= set(name2id)
assert not {s for l in SINONIMOS_ES.values() for s in l} & set(INV_ES), "un sinónimo coincide con el nombre propio de una clase"
INV_ES.update({s: c for c, l in SINONIMOS_ES.items() for s in l})

# v6: sinónimos en inglés que no son otra clase del vocabulario (los del detector de 2.9 más algunos comunes).
# Motivo: en la v5 el LLM tradujo "gafas" a "glasses", que no es el nombre LVIS ("spectacles").
ALIAS_EN = {s: c for c, sinonimos in SINONIMOS.items() for s in sinonimos}
ALIAS_EN.update({"glasses": "spectacles", "eyeglasses": "spectacles", "tv": "television set", "television": "television set",
                 "pants": "trousers", "jeans": "jean", "mobile phone": "cell phone", "smartphone": "cell phone", "phone": "cell phone",
                 "couch": "sofa", "door handle": "handle", "fire hydrant": "fireplug", "hydrant": "fireplug", "tie": "necktie",
                 "purse": "handbag", "mug": "cup", "outlet": "wall socket", "socket": "wall socket", "monitor": "computer monitor",
                 "keyboard": "computer keyboard", "mouse": "computer mouse", "bike": "bicycle", "motorbike": "motorcycle"})
assert set(ALIAS_EN.values()) <= set(name2id) and not set(ALIAS_EN) & set(name2id)

def normalizar_clase(c):
    """Lleva la clase que propone el LLM al vocabulario. Devuelve (clase, cómo se resolvió)."""
    c0 = " ".join(str(c).strip().lower().split())
    if c0 in name2id:
        return c0, "exacta"
    for sing in (c0[:-1] if c0.endswith("s") else None, c0[:-2] if c0.endswith("es") else None):
        if sing in name2id:
            return sing, "singular"
    for alias in (c0, c0[:-1] if c0.endswith("s") else None):
        if alias in ALIAS_EN:
            return ALIAS_EN[alias], "alias_en"
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
    propias = dict(predicate="relation", attribute="attribute", comparator="compare", reason="unsupported")
    q = {k: v for k, v in q.items() if k not in propias or q.get("intent") == propias[k]}   # cada clave sólo en su intención
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

def menciones_vocab(texto):
    """Clases del vocabulario que el texto nombra, en español (diccionario propio) o en inglés. Primero los nombres más largos."""
    t = sin_acentos(texto.lower())
    nombres = {**INV_ES, **{c: c for c in name2id}}
    encontradas = []
    for n in sorted(nombres, key=len, reverse=True):
        patron = rf"\b{re.escape(n)}(s|es)?\b"
        if re.search(patron, t):
            encontradas.append(nombres[n])
            t = re.sub(patron, " ", t)
    return list(dict.fromkeys(encontradas))

def pista_vocabulario(texto, r):
    """v6: si el LLM propuso una clase fuera del vocabulario pero la pregunta nombra objetos que sí están, arma la pista del
    reintento. Es un posible error de traducción de la clase. Elige el LLM; el código sólo avisa.
    No se usa si la intención es unsupported o description: ahí las clases no se ejecutan, y un reintento podría
    convertir una pregunta fuera de alcance en una soportada."""
    if (r["query"] or {}).get("intent") in (None, "unsupported", "description"):
        return None
    fuera = [n["llm"] for n in r["normalizacion"] if n["como"] == "sin_coincidencia"]
    candidatas = [c for c in menciones_vocab(texto) if c not in (r["query"] or {}).get("classes", [])]
    if not fuera or not candidatas:
        return None
    return (f"Las clases {', '.join(fuera)} no están en el vocabulario. La pregunta nombra estos objetos que sí están: "
            f"{', '.join(f'{c} ({NOMBRES_ES_PROPIOS.get(c, c)})' for c in candidatas)}. Si alguno es el objeto por el que "
            "se pregunta, usá su nombre en inglés; si no, dejá la clase como estaba. Devolvé sólo el JSON.")

def interpretar(preguntas):
    """Lista de textos -> lista de dicts con la consulta, los problemas y el registro de la interpretación."""
    t0 = time.time()
    convs = [MENSAJES_INTERPRETE + [{"role": "user", "content": t}] for t in preguntas]
    salidas = generar(convs, max_new_tokens=100)
    res = []
    for s in salidas:
        q, prob, norm = preparar_query(s)
        res.append(dict(query=q, query_1=q, problemas=prob, normalizacion=norm, normalizacion_1=norm, salida_1=s, intentos=1,
                        motivo_reintento="", valida_1=not hay_que_reintentar(q, prob)))
    # Dos motivos de reintento: formato inválido, o clase fuera del vocabulario cuando la pregunta nombra una que sí está
    reintentar = {}
    for i, (t, r) in enumerate(zip(preguntas, res)):
        if not r["valida_1"]:
            reintentar[i] = ("formato", f"Esa consulta no es válida: {'; '.join(r['problemas'])}. Corregila y devolvé sólo el JSON.")
        elif pista := pista_vocabulario(t, r):
            reintentar[i] = ("vocabulario", pista)
    if reintentar:
        idx = list(reintentar)
        convs2 = [convs[i] + [{"role": "assistant", "content": res[i]["salida_1"]}, {"role": "user", "content": reintentar[i][1]}]
                  for i in idx]
        for i, s in zip(idx, generar(convs2, max_new_tokens=100)):
            q, prob, norm = preparar_query(s)
            res[i].update(salida_2=s, intentos=2, motivo_reintento=reintentar[i][0])
            if reintentar[i][0] == "formato" or not hay_que_reintentar(q, prob):   # una pista nunca empeora una consulta válida
                res[i].update(query=q, problemas=prob, normalizacion=norm)
    ms = (time.time() - t0) * 1000 / max(1, len(preguntas))
    for r in res:
        r["valida_final"] = not hay_que_reintentar(r["query"], r["problemas"])
        r["ms_por_pregunta"] = round(ms, 1)
    return res

# Prueba con preguntas que no están en el benchmark
print("Menciones del vocabulario en un texto de prueba:", menciones_vocab('¿El "reloj de pulsera" está cerca de las sillas?'))
for t, r in zip(pruebas := ["¿Cuántos inodoros hay?", "¿El reloj está a la derecha de la ventana?", "¿Qué hora marca el reloj?"],
                interpretar(pruebas)):
    print(f"{t:45s} -> {json.dumps(r['query'], ensure_ascii=False)} | problemas: {r['problemas'] or '-'} | intentos: {r['intentos']}")
