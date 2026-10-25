# Nombres en español para redactar las preguntas extra (los del benchmark se toman tal cual de questions_dev)
NOMBRES_ES = {
    "sofa": "sofá", "laptop": "computadora portátil", "pillow": "almohada", "bench": "banco", "jacket": "chaqueta",
    "signboard": "cartel", "backpack": "mochila", "traffic light": "semáforo", "umbrella": "paraguas", "horse": "caballo",
    "handle": "manija", "chair": "silla", "clock": "reloj", "napkin": "servilleta", "pizza": "pizza", "flag": "bandera",
    "person": "persona", "trousers": "pantalones", "trash can": "tacho de basura", "sock": "calcetín", "vase": "jarrón",
    "bicycle": "bicicleta", "tennis racket": "raqueta de tenis", "necklace": "collar", "cell phone": "teléfono celular",
    "book": "libro", "sunglasses": "anteojos de sol", "lamp": "lámpara", "bottle": "botella", "glove": "guante",
    "shoe": "zapato", "blanket": "manta", "computer keyboard": "teclado de computadora", "dog": "perro", "jean": "jean",
    "short pants": "pantalones cortos", "flower arrangement": "arreglo floral", "ski": "esquí", "cat": "gato",
    "wheel": "rueda", "faucet": "grifo", "helmet": "casco", "table": "mesa", "drinking glass": "vaso",
    "headlight": "faro delantero", "streetlight": "farola", "television set": "televisor", "belt": "cinturón",
    "bird": "pájaro", "knife": "cuchillo", "watch": "reloj de pulsera", "handbag": "bolso", "street sign": "señal de tránsito",
    "bowl": "cuenco", "ski pole": "bastón de esquí", "hat": "sombrero", "plate": "plato", "car": "auto", "curtain": "cortina",
    "elephant": "elefante", "bed": "cama", "drawer": "cajón", "earring": "aro", "boat": "barco", "necktie": "corbata",
    "skateboard": "patineta", "wall socket": "tomacorriente", "fork": "tenedor", "bus": "colectivo", "giraffe": "jirafa",
    "toilet": "inodoro", "surfboard": "tabla de surf", "motorcycle": "moto", "cabinet": "gabinete", "taillight": "luz trasera",
    "train": "tren", "baseball cap": "gorra de béisbol", "airplane": "avión", "jersey": "camiseta deportiva", "pole": "poste",
    "doorknob": "pomo de puerta", "baseball bat": "bate de béisbol", "shirt": "camisa", "license plate": "patente",
    "banana": "banana", "mirror": "espejo", "kite": "barrilete", "frisbee": "frisbee", "sink": "pileta", "spectacles": "gafas",
    "button": "botón", "goggles": "antiparras", "zebra": "cebra", "suitcase": "valija", "baseball glove": "guante de béisbol",
    "basket": "canasta", "refrigerator": "refrigerador", "ski boot": "bota de esquí", "tablecloth": "mantel",
    "bracelet": "pulsera", "teddy bear": "oso de peluche", "windshield wiper": "limpiaparabrisas",
    "computer mouse": "mouse de computadora", "box": "caja", "cup": "taza", "dress": "vestido", "computer monitor": "monitor",
    "broccoli": "brócoli", "strap": "correa", "knob": "perilla", "plastic bag": "bolsa de plástico", "ring": "anillo",
    "awning": "toldo", "vent": "rejilla de ventilación", "banner": "pancarta", "cow": "vaca", "flowerpot": "maceta",
    "tag": "etiqueta", "fireplug": "hidrante", "boot": "bota",
}
for p in qs[qs.class_en.str.len() > 0].to_dict("records"):   # mismos nombres que usa la cátedra
    NOMBRES_ES.update(zip(p["class_en"], p["class_es"]))
assert set(NOMBRES_ES) == set(name2id), set(name2id) ^ set(NOMBRES_ES)

FUERA_DE_ALCANCE = [("action", "¿Qué está haciendo la persona en la imagen?"),
                    ("material", "¿De qué material está hecha la mesa?"),
                    ("state", "¿El televisor está encendido?"),
                    ("text", "¿Qué dice el cartel?"),
                    ("emotion", "¿La persona parece contenta?")]

preguntas_extra = []
for i, k in enumerate(sorted(qs.image_key.unique())):
    frec = Counter(id2name[o["category_id"]] for o in escenas_gt[k]["objects"]).most_common()
    a, b = frec[0][0], frec[1][0]
    unicas = [c for c, n in frec if n == 1]
    base = dict(image_key=k)
    if frec[0][1] > 1:
        preguntas_extra.append(dict(base, caso="ambigua", type="position", class_en=[a],
                                    question=f"¿En qué zona de la imagen está la instancia de \"{NOMBRES_ES[a]}\"?"))
    if unicas:
        preguntas_extra.append(dict(base, caso="atributo", type="attribute", class_en=[unicas[0]], attribute="color",
                                    question=f"¿De qué color es la instancia de \"{NOMBRES_ES[unicas[0]]}\"?"))
    preguntas_extra.append(dict(base, caso="comparación", type="compare", class_en=[a, b], comparator="more",
                                question=f"¿Hay más instancias de \"{NOMBRES_ES[a]}\" que de \"{NOMBRES_ES[b]}\" en la imagen?"))
    preguntas_extra.append(dict(base, caso="proximidad", type="relation", class_en=[a, b], predicate="near",
                                question=f"¿La instancia de \"{NOMBRES_ES[a]}\" está cerca de la instancia de \"{NOMBRES_ES[b]}\"?"))
    tipo, texto = FUERA_DE_ALCANCE[i % len(FUERA_DE_ALCANCE)]
    preguntas_extra.append(dict(base, caso="fuera de alcance", type=tipo, class_en=[], question=texto))
    if i % 4 == 0:
        preguntas_extra.append(dict(base, caso="fuera del vocabulario", type="existence", class_en=["unicorn"],
                                    question="¿Hay al menos una instancia de la categoría \"unicornio\" en la imagen?"))
for j, p in enumerate(preguntas_extra, 1):
    p["question_id"] = f"EXTRA-{j:03d}"

def manejo_correcto(p, r, r_ref):
    """¿Se manejó el caso como corresponde?"""
    if p["caso"] in ("fuera de alcance", "fuera del vocabulario"):
        return r["normalized_answer"] == "unsupported"
    if p["caso"] == "ambigua":   # si hay varias instancias predichas, tiene que avisarlo
        n = len(instancias(escena_por_id[p["image_key"]], p["class_en"][0]))
        return r["status"] == ("ambiguous" if n > 1 else "ok") or (n == 0 and r["status"] == "insufficient_information")
    if p["caso"] == "atributo":   # sin ground truth de color: tiene que dar un color o declarar que no hay información
        return r["status"] in ("ok", "ambiguous", "insufficient_information")
    return r["normalized_answer"] == r_ref["normalized_answer"]   # comparación y proximidad: contra la escena real

filas_extra, respuestas_extra = [], {}
for p in preguntas_extra:
    q = query_determinista(p)
    r = ejecutar(q, escena_por_id[p["image_key"]])
    r_ref = ejecutar(q, escenas_gt[p["image_key"]])
    respuestas_extra[p["question_id"]] = r
    filas_extra.append(dict(question_id=p["question_id"], caso=p["caso"], pregunta=p["question"][:70],
                            respuesta=r["normalized_answer"], status=r["status"], ref=r_ref["normalized_answer"],
                            correcto=manejo_correcto(p, r, r_ref)))
ev_extra = pd.DataFrame(filas_extra)
print(f"{len(ev_extra)} preguntas extra sobre {len({p['image_key'] for p in preguntas_extra})} imágenes")
print(ev_extra.groupby("caso").agg(preguntas=("correcto", "size"), manejo_correcto=("correcto", "mean")).round(3).to_string())
print("\nEjemplos:")
for caso in ev_extra.caso.unique():
    p = next(x for x in preguntas_extra if x["caso"] == caso)
    print(f"[{caso}] {p['question']}\n   -> {respuestas_extra[p['question_id']]['answer']}")
