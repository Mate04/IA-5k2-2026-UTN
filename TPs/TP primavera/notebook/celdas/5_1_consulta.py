import re
import unicodedata

name2id = dict(zip(cats.category_name, cats.category_id))
INTENCIONES = ["count", "existence", "position", "size", "relation", "attribute", "compare", "description", "unsupported"]
PREDICADOS = ["left_of", "right_of", "above", "below", "overlaps", "near"]
SALIDA_ESPERADA = dict(count="integer", existence="boolean", position="position_3x3", size="size_class", relation="boolean",
                       attribute="color", compare="boolean", description="free_text", unsupported="none")
N_CLASES = dict(count=1, existence=1, position=1, size=1, attribute=1, relation=2, compare=2, description=0, unsupported=0)

QUERY_SCHEMA = {
    "type": "object",
    "required": ["intent", "classes"],
    "additionalProperties": False,
    "properties": {
        "intent": {"enum": INTENCIONES},
        "classes": {"type": "array", "items": {"type": "string", "minLength": 1}, "maxItems": 2},
        "predicate": {"enum": PREDICADOS + [None]},
        "attribute": {"enum": ["color", None]},
        "comparator": {"enum": ["more", "fewer", "same", None]},
        "output": {"enum": sorted(set(SALIDA_ESPERADA.values()))},
        "reason": {"type": "string"},
    },
}
validador_query = jsonschema.Draft202012Validator(QUERY_SCHEMA)

def validar_query(query):
    """Valida forma y semántica. Devuelve (consulta normalizada, problemas). No mira la imagen ni la escena."""
    problemas = [e.message for e in validador_query.iter_errors(query)]
    if problemas:
        return None, problemas
    q = {**dict(predicate=None, attribute=None, comparator=None), **query}
    q["output"] = SALIDA_ESPERADA[q["intent"]]
    if q["intent"] == "unsupported":
        return q, [q.get("reason") or "consulta fuera de alcance"]
    if len(q["classes"]) != N_CLASES[q["intent"]]:
        problemas.append(f"'{q['intent']}' necesita {N_CLASES[q['intent']]} clase(s) y recibió {len(q['classes'])}")
    fuera = [c for c in q["classes"] if c not in name2id]
    if fuera:
        problemas.append(f"clase fuera del vocabulario: {', '.join(fuera)}")
    if q["intent"] == "relation" and q["predicate"] is None:
        problemas.append("no se reconoce la relación espacial")
    if q["intent"] == "attribute" and q["attribute"] is None:
        problemas.append("falta el atributo")
    if q["intent"] == "compare" and q["comparator"] is None:
        problemas.append("falta el tipo de comparación")
    return q, problemas

# Pruebas de la validación
for prueba in [dict(intent="count", classes=["doorknob"]),
               dict(intent="count", classes=["unicorn"]),
               dict(intent="relation", classes=["clock", "ring"]),
               dict(intent="size"),
               dict(intent="count", classes=["car"], color="red")]:
    q, prob = validar_query(prueba)
    print(f"{json.dumps(prueba, ensure_ascii=False):60s} -> {'OK' if not prob else prob}")
