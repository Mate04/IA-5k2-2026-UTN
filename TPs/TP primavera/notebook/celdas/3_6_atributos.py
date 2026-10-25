PARAMS_ATRIBUTOS = dict(color="HSV, 12 nombres, gris si S < 0.25, máscara erosionada 1 px, hasta 4000 píxeles",
                        near_max_frac_diag=0.02, oclusion="caja cubierta por máscaras de otros objetos", borde_px=2)
COLORES = ["black", "white", "gray", "red", "orange", "brown", "yellow", "green", "cyan", "blue", "purple", "pink"]
C = {c: i for i, c in enumerate(COLORES)}

def nombres_de_color(hsv):
    """hsv: (N, 3) con H, S, V en 0-255 (formato de PIL). Devuelve el índice en COLORES de cada píxel."""
    h, s, v = hsv[:, 0] * (360 / 255), hsv[:, 1] / 255, hsv[:, 2] / 255
    tono = np.select([(h < 12) | (h >= 345), h < 40, h < 70, h < 165, h < 195, h < 255, h < 290],
                     [C["red"], C["orange"], C["yellow"], C["green"], C["cyan"], C["blue"], C["purple"]], default=C["pink"])
    tono = np.where((h >= 10) & (h < 45) & (v < 0.6), C["brown"], tono)   # naranja oscuro = marrón
    gris = s < 0.25                                                       # poca saturación = acromático
    return np.where(v < 0.2, C["black"], np.where(gris & (v > 0.8), C["white"], np.where(gris, C["gray"], tono)))

def erosionar(m):
    """Erosión de 1 píxel (vecindad en cruz). Si la máscara desaparece, devuelve la original."""
    e = m.copy()
    e[1:, :] &= m[:-1, :]; e[:-1, :] &= m[1:, :]; e[:, 1:] &= m[:, :-1]; e[:, :-1] &= m[:, 1:]
    return e if e.any() else m

def color_dominante(hsv_img, m, max_px=4000):
    ys, xs = np.nonzero(erosionar(m))
    if len(ys) > max_px:                                   # submuestreo determinista
        idx = np.linspace(0, len(ys) - 1, max_px).astype(int)
        ys, xs = ys[idx], xs[idx]
    cuenta = np.bincount(nombres_de_color(hsv_img[ys, xs].astype(float)), minlength=len(COLORES))
    k = int(cuenta.argmax())
    return COLORES[k], round(float(cuenta[k] / cuenta.sum()), 3)

def relaciones_near(objetos, W, H):
    """Pares cuya separación entre cajas es ≤ 2 % de la diagonal. Simétrica: se guarda una vez por par."""
    diag = (W ** 2 + H ** 2) ** 0.5
    rels = []
    for i, a in enumerate(objetos):
        for b in objetos[i + 1:]:
            dx = max(0.0, b["bbox"][0] - a["bbox"][2], a["bbox"][0] - b["bbox"][2])
            dy = max(0.0, b["bbox"][1] - a["bbox"][3], a["bbox"][1] - b["bbox"][3])
            d = (dx ** 2 + dy ** 2) ** 0.5 / diag
            if d <= PARAMS_ATRIBUTOS["near_max_frac_diag"]:
                rels.append(dict(subject=a["id"], predicate="near", object=b["id"], distance=round(d, 4)))
    return rels

def agregar_atributos(escena, im):
    """Agrega `attributes` a cada objeto y `extra_relations` a la escena. Usa sólo la imagen y el SceneJSON."""
    W, H = escena["image"]["width"], escena["image"]["height"]
    hsv = np.asarray(im.convert("HSV"))
    objetos = escena["objects"]
    masks = [rle_decode(o["mask"]) for o in objetos]
    cobertura = np.zeros((H, W), np.uint16)                # cuántas máscaras cubren cada píxel
    for m in masks:
        cobertura += m
    b = PARAMS_ATRIBUTOS["borde_px"]
    for o, m in zip(objetos, masks):
        x1, y1 = int(o["bbox"][0]), int(o["bbox"][1])
        x2, y2 = max(int(np.ceil(o["bbox"][2])), x1 + 1), max(int(np.ceil(o["bbox"][3])), y1 + 1)
        mc = m[y1:y2, x1:x2]
        tapado = ((cobertura[y1:y2, x1:x2] - mc) > 0) & ~mc   # píxeles de la caja cubiertos por otro objeto
        color, ratio = color_dominante(hsv, m)
        o["attributes"] = dict(color=color, color_ratio=ratio, occlusion=round(float(tapado.mean()), 3),
                               touches_border=bool(o["bbox"][0] <= b or o["bbox"][1] <= b
                                                   or o["bbox"][2] >= W - b or o["bbox"][3] >= H - b))
    escena["extra_relations"] = relaciones_near(objetos, W, H)
    return escena["extra_relations"]

# --- Demostración sobre las detecciones de desarrollo de la Fase 3 ---
# Armamos una escena mínima por imagen con las detecciones finales y sus máscaras de SAM2.
t0 = time.time()
filas_attr, n_near = [], []
for img_id, d_img in dets_final.groupby("image_id"):
    r = img_meta[img_id]
    esc_tmp = dict(image=dict(id=r.fname, width=r.width, height=r.height),
                   objects=[dict(id=f"obj_{k}", category_id=int(d.category_id), confidence=float(d.score),
                                 bbox=[d.bbox[0], d.bbox[1], d.bbox[0] + d.bbox[2], d.bbox[1] + d.bbox[3]], mask=d.rle_sam)
                            for k, d in enumerate(d_img.sort_values("score", ascending=False).itertuples(), 1)])
    n_near.append(len(agregar_atributos(esc_tmp, Image.open(DEV / "images" / r.fname).convert("RGB"))))
    filas_attr += [dict(image_id=img_id, clase=id2name[o["category_id"]], **o["attributes"]) for o in esc_tmp["objects"]]
attr = pd.DataFrame(filas_attr)
print(f"Atributos de {len(attr)} objetos en {len(n_near)} imágenes ({time.time() - t0:.0f} s) | relaciones near por imagen: media {np.mean(n_near):.0f}, máx {max(n_near)}")
print("\nDistribución de colores:", attr.color.value_counts(normalize=True).round(2).to_dict())
print("Oclusión media: {:.2f} | objetos con oclusión > 0,3: {:.0%} | tocan el borde: {:.0%}".format(
    attr.occlusion.mean(), (attr.occlusion > 0.3).mean(), attr.touches_border.mean()))

# Chequeo de plausibilidad del color: clases con un color esperable (aproximación, no es ground truth)
ESPERADO = {"broccoli": {"green"}, "banana": {"yellow", "green"}, "zebra": {"black", "white", "gray"},
            "elephant": {"gray", "brown"}, "giraffe": {"brown", "orange", "yellow"}}
plaus = attr[attr.clase.isin(ESPERADO)].assign(plausible=lambda d: [c in ESPERADO[k] for k, c in zip(d.clase, d.color)])
print("\nPlausibilidad del color en clases con color esperable:")
print(plaus.groupby("clase").agg(objetos=("color", "size"), plausible=("plausible", "mean"),
                                  colores=("color", lambda s: s.value_counts().head(3).to_dict())).round(2).to_string())
