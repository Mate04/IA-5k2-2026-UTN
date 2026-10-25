def sin_acentos(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")

PATRONES_PREDICADO = [(r"por encima d|arriba d|encima d", "above"), (r"por debajo d|debajo d|abajo d", "below"),
                      (r"a la izquierda d", "left_of"), (r"a la derecha d", "right_of"),
                      (r"superpone|solapa", "overlaps"), (r"cerca d|junto a|al lado d", "near")]
PATRONES_COMPARADOR = [(r"\bmas\b", "more"), (r"\bmenos\b", "fewer"), (r"misma cantidad|igual cantidad|tant[oa]s", "same")]

def buscar_patron(texto, patrones):
    t = sin_acentos(texto)
    return next((valor for patron, valor in patrones if re.search(patron, t)), None)

def query_determinista(p):
    """Consulta a partir de los campos estructurados (type, class_en). Del texto sólo se lee el predicado o el comparador."""
    intent = p["type"] if p["type"] in INTENCIONES else "unsupported"
    q = dict(intent=intent, classes=list(p.get("class_en") or []))
    if intent == "relation":
        q["predicate"] = p.get("predicate") or buscar_patron(p["question"], PATRONES_PREDICADO)
    elif intent == "attribute":
        q["attribute"] = p.get("attribute") or "color"
    elif intent == "compare":
        q["comparator"] = p.get("comparator") or buscar_patron(p["question"], PATRONES_COMPARADOR)
    elif intent == "unsupported":
        q["classes"] = []
        q["reason"] = p.get("reason") or f"tipo de pregunta no soportado: {p['type']}"
    return q

# Las 10 preguntas de relación del benchmark: el predicado tiene que salir del texto en todas
rel = qs[qs.type == "relation"]
predicados = rel.question.map(lambda t: buscar_patron(t, PATRONES_PREDICADO))
print("Predicados reconocidos:", predicados.notna().sum(), "de", len(rel))
print(pd.DataFrame({"pregunta": rel.question.str.slice(0, 75), "predicado": predicados}).to_string(index=False))
