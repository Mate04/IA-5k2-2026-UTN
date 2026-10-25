ZONAS_ES = dict(top_left="arriba a la izquierda", top_center="arriba al centro", top_right="arriba a la derecha",
                middle_left="en el medio a la izquierda", center="en el centro", middle_right="en el medio a la derecha",
                bottom_left="abajo a la izquierda", bottom_center="abajo al centro", bottom_right="abajo a la derecha")
TAMANOS_ES = dict(small="chico", medium="mediano", large="grande")
COLORES_ES = dict(black="negro", white="blanco", gray="gris", red="rojo", orange="naranja", brown="marrón", yellow="amarillo",
                  green="verde", cyan="celeste", blue="azul", purple="violeta", pink="rosa")

PROMPT_VERBALIZAR = ("Redactás en español, en UNA oración completa, la respuesta de un sistema que analiza una imagen. "
                     "El resultado ya lo calculó un motor determinista: copiá su valor sin cambiarlo, no agregues datos y no expliques "
                     "el método. Escribí los números con dígitos. Si el valor es sí o no, empezá la oración con 'Sí,' o 'No,' según ese valor.")
SI_NO_ES = dict(yes="sí", no="no")

def valor_es(v):
    v = str(v)
    return ZONAS_ES.get(v) or TAMANOS_ES.get(v) or COLORES_ES.get(v) or SI_NO_ES.get(v) or v

def turno_verbalizar(pregunta, texto_motor, valor):
    return f"Pregunta: {pregunta}\nResultado del motor: {texto_motor}\nValor: {valor} ({valor_es(valor)})"

EJEMPLOS_VERBALIZAR = [
    (turno_verbalizar('¿Cuántas instancias de la categoría "silla" aparecen en la imagen?', "Hay 3 instancia(s) de 'chair' en la escena.", 3),
     "En la imagen aparecen 3 sillas."),
    (turno_verbalizar('¿Hay al menos una instancia de la categoría "perro" en la imagen?', "Sí, hay 1 instancia(s) de 'dog'.", "yes"),
     "Sí, en la imagen hay 1 perro."),
    (turno_verbalizar('¿La instancia de "lámpara" está a la izquierda de la instancia de "sofá"?',
                      "No: en la escena, 'lamp' (obj_4) no cumple left_of respecto de 'sofa' (obj_1).", "no"),
     "No, la lámpara no está a la izquierda del sofá."),
    (turno_verbalizar('¿En qué zona de la imagen está la instancia de "computadora portátil"?',
                      "La instancia de 'laptop' está en la zona bottom_left.", "bottom_left"),
     "La computadora portátil está abajo a la izquierda de la imagen."),
    (turno_verbalizar('¿Qué tamaño relativo tiene la instancia de "paraguas"?',
                      "No se detectó ninguna instancia de 'umbrella': no hay información suficiente para responder.", "unknown"),
     "No se detectó ningún paraguas, así que no hay información suficiente para responder."),
]
MENSAJES_VERBALIZAR = [{"role": "system", "content": PROMPT_VERBALIZAR}]
for u, a in EJEMPLOS_VERBALIZAR:
    MENSAJES_VERBALIZAR += [{"role": "user", "content": u}, {"role": "assistant", "content": a}]

def verbalizacion_fiel(texto, r, intent):
    """Control con código: el texto del LLM tiene que ser una oración y conservar el valor que calculó el motor."""
    t, v = sin_acentos(texto), r["normalized_answer"]
    if not texto or len(texto) < 12 or len(texto) > 400:
        return False
    if r["status"] in ("unsupported", "insufficient_information"):
        return bool(re.search(r"\bno\b", t))
    if intent == "count":
        return str(v) in re.findall(r"\d+", t) or (v == 0 and bool(re.search(r"\bningun|\bno hay\b", t)) and not re.search(r"\d", t))
    if v in ("yes", "no"):
        return t.startswith("si" if v == "yes" else "no")
    return sin_acentos(valor_es(v)) in t or str(v).lower() in t

def mensajes_verbalizar(pregunta, r):
    return MENSAJES_VERBALIZAR + [{"role": "user", "content": turno_verbalizar(pregunta, r["answer"], r["normalized_answer"])}]

def resumen_escena(escena, max_clases=8):
    """Resumen textual del SceneJSON predicho para el LLM: sólo conteos, zonas y tamaños (los calcula el código)."""
    por_clase = defaultdict(list)
    for o in escena["objects"]:
        por_clase[id2name[o["category_id"]]].append(o)
    orden = sorted(por_clase.items(), key=lambda kv: (-len(kv[1]), -kv[1][0]["confidence"]))[:max_clases]
    lineas = [f"Objetos detectados: {len(escena['objects'])}, de {len(por_clase)} clases."]
    for nombre, lista in orden:
        zona = Counter(o["position"] for o in lista).most_common(1)[0][0]
        mayor = max(lista, key=lambda o: o["area_ratio"])
        lineas.append(f"- {NOMBRES_ES_PROPIOS.get(nombre, nombre)} ({nombre}): {len(lista)}; zona más frecuente: {ZONAS_ES[zona]}; "
                      f"tamaño del más grande: {TAMANOS_ES[mayor['size']]}")
    if escena["objects"]:
        g = max(escena["objects"], key=lambda o: o["area_ratio"])
        nombre_g = id2name[g["category_id"]]
        lineas.append(f"El objeto que más área ocupa: {NOMBRES_ES_PROPIOS.get(nombre_g, nombre_g)} ({nombre_g}), "
                      f"{ZONAS_ES[g['position']]}.")
    numeros = {str(len(escena["objects"])), str(len(por_clase))} | {str(len(l)) for _, l in orden}
    return "\n".join(lineas), numeros

PROMPT_DESCRIBIR = ("Escribís descripciones breves de escenas a partir de datos de un detector de objetos. Usá SOLO los datos que te pasan: "
                    "no agregues objetos, colores, acciones, lugares ni relaciones que no estén. Escribí un párrafo de 2 o 3 oraciones "
                    "en español (no una lista), con los números en dígitos, y nombrá cada objeto en español seguido de su nombre EN INGLÉS "
                    "entre paréntesis, tal como aparece en los datos, por ejemplo: 2 sillas (chair).")
EJEMPLO_DESCRIBIR = (
    "Datos de la escena:\nObjetos detectados: 9, de 3 clases.\n"
    "- silla (chair): 4; zona más frecuente: abajo al centro; tamaño del más grande: mediano\n"
    "- persona (person): 4; zona más frecuente: en el centro; tamaño del más grande: grande\n"
    "- mesa (table): 1; zona más frecuente: en el centro; tamaño del más grande: grande\n"
    "El objeto que más área ocupa: mesa (table), en el centro.",
    "La escena tiene 9 objetos detectados de 3 clases. Se ven 4 sillas (chair), sobre todo abajo al centro, y 4 personas (person) "
    "en el centro. La mesa (table) es el objeto que más área ocupa y está en el centro de la imagen.")

def control_descripcion(texto, escena, numeros):
    """Control de alucinaciones: clases nombradas ⊆ clases de la escena, al menos una, y números sustentados."""
    presentes = {id2name[o["category_id"]] for o in escena["objects"]}
    nombradas = clases_nombradas(texto.lower())
    problemas = []
    if not nombradas:
        problemas.append("no nombra ninguna clase del vocabulario")
    if nombradas - presentes:
        problemas.append(f"nombra clases que no están en la escena: {sorted(nombradas - presentes)}")
    sobran = set(re.findall(r"\d+", texto)) - numeros
    if sobran:
        problemas.append(f"números sin sustento: {sorted(sobran)}")
    conteo = Counter(id2name[o["category_id"]] for o in escena["objects"])
    for n, clase in re.findall(r"(\d+)\s+[^\d()]{0,40}?\(([a-z ]+)\)", texto.lower()):   # "2 sillas (chair)"
        if clase.strip() in conteo and int(n) != conteo[clase.strip()]:
            problemas.append(f"dice {n} {clase.strip()} y la escena tiene {conteo[clase.strip()]}")
    return nombradas, problemas

def describir_llm(escenas_a_describir):
    """Descripción redactada por el LLM con control de alucinaciones; si falla dos veces, plantilla de la Fase 5."""
    resumenes = [resumen_escena(e) for e in escenas_a_describir]
    convs = [[{"role": "system", "content": PROMPT_DESCRIBIR}, {"role": "user", "content": EJEMPLO_DESCRIBIR[0]},
              {"role": "assistant", "content": EJEMPLO_DESCRIBIR[1]}, {"role": "user", "content": f"Datos de la escena:\n{res}"}]
             for res, _ in resumenes]
    salidas = generar(convs, max_new_tokens=160)
    controles = [control_descripcion(s, e, n) for s, e, (_, n) in zip(salidas, escenas_a_describir, resumenes)]
    reintentar = [i for i, (_, p) in enumerate(controles) if p]
    intentos = [1] * len(salidas)
    if reintentar:
        convs2 = [convs[i] + [{"role": "assistant", "content": salidas[i]},
                              {"role": "user", "content": f"La descripción tiene problemas: {'; '.join(controles[i][1])}. "
                                                          "Reescribila usando sólo los datos."}] for i in reintentar]
        for i, s in zip(reintentar, generar(convs2, max_new_tokens=160)):
            salidas[i], controles[i], intentos[i] = s, control_descripcion(s, escenas_a_describir[i], resumenes[i][1]), 2
    respuestas = []
    for e, s, (nombradas, prob), n_int in zip(escenas_a_describir, salidas, controles, intentos):
        if prob or not e["objects"]:
            r = describir(e)
            respuestas.append(dict(r, redaccion="plantilla", intentos=n_int, problemas_redaccion=prob))
            continue
        evid = [o["id"] for o in e["objects"] if id2name[o["category_id"]] in nombradas]
        conf = np.mean([o["confidence"] for o in e["objects"] if o["id"] in set(evid)])
        respuestas.append(dict(respuesta(s, s, evid, conf, "ok"), redaccion="llm", intentos=n_int, problemas_redaccion=[]))
    return respuestas

# Prueba sobre la primera escena del benchmark
esc_prueba = escena_por_id[qs.image_key.iloc[0]]
print(resumen_escena(esc_prueba)[0])
r_prueba = describir_llm([esc_prueba])[0]
print(f"\n[{r_prueba['redaccion']}] {r_prueba['answer']}\nevidencia: {len(r_prueba['evidence'])} objetos")
