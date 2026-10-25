import gc

# --- Consultas de texto: la plantilla de la línea base y, para algunas clases, sinónimos (E7) ---
# Sólo sinónimos que no son el nombre de otra clase del vocabulario (por ejemplo, no "cap" ni "door handle").
SINONIMOS = {
    "person": ["man", "woman", "child"], "fireplug": ["fire hydrant"], "jean": ["jeans"], "trousers": ["pants"],
    "short pants": ["shorts"], "spectacles": ["eyeglasses"], "television set": ["television"],
    "wall socket": ["electrical outlet"], "flower arrangement": ["bouquet of flowers"], "streetlight": ["street lamp"],
    "trash can": ["garbage can"], "cell phone": ["mobile phone"], "computer monitor": ["computer screen"],
    "handbag": ["purse"], "necktie": ["tie"], "flowerpot": ["plant pot"], "taillight": ["tail light"],
    "license plate": ["number plate"], "teddy bear": ["stuffed animal"], "jersey": ["sports jersey"],
    "vent": ["air vent"], "frisbee": ["flying disc"],
}
assert set(SINONIMOS) <= set(VOCAB)
Q_TEXTOS, Q_CLASE, Q_BASE = [], [], []
for i, nombre in enumerate(VOCAB):
    for j, t in enumerate([nombre] + SINONIMOS.get(nombre, [])):
        Q_TEXTOS.append(f"a photo of a {t}"); Q_CLASE.append(i); Q_BASE.append(j == 0)
Q_CLASE_T, Q_BASE_T = torch.tensor(Q_CLASE, device=device), torch.tensor(Q_BASE, device=device)
VARIANTES_Q = {"sin_sinonimos": Q_BASE_T, "con_sinonimos": torch.ones_like(Q_BASE_T)}
print(f"Consultas de texto: {len(Q_TEXTOS)} ({sum(Q_BASE)} de la línea base + {len(Q_TEXTOS) - sum(Q_BASE)} sinónimos)")

MODELO_BASE, MODELO_LARGE = MODELO, "google/owlv2-large-patch14-ensemble"
OWL = {MODELO_BASE: (processor, model)}

def cargar_owl(nombre):
    if nombre not in OWL:
        OWL[nombre] = (Owlv2Processor.from_pretrained(nombre), Owlv2ForObjectDetection.from_pretrained(nombre).to(device).eval())
    return OWL[nombre]

@torch.no_grad()
def owl_pasada(im, nombre, umbral=0.05, k_max=3):
    """Una pasada de OWLv2 sobre una imagen PIL (completa o ventana). Recibe SÓLO la imagen y el vocabulario.
    Devuelve {variante de consultas: filas}, con cajas [x, y, w, h] en píxeles de `im`."""
    proc, mod = cargar_owl(nombre)
    W, H = im.size
    S = max(W, H)                                               # OWLv2 rellena la imagen hasta hacerla cuadrada
    out = mod(**proc(text=[Q_TEXTOS], images=im, return_tensors="pt").to(device))
    pq = out.logits[0].sigmoid()                                # (cajas, consultas)
    cajas = (out.pred_boxes[0] * S).cpu().numpy()               # (cx, cy, w, h) en píxeles
    res = {}
    for var, usar in VARIANTES_Q.items():
        idx = Q_CLASE_T[usar].expand(pq.shape[0], -1)
        p = torch.zeros(pq.shape[0], len(VOCAB), device=pq.device).scatter_reduce(1, idx, pq[:, usar], reduce="amax", include_self=False)
        top_p, top_c = (t.cpu().numpy() for t in p.topk(k_max, dim=1))   # puntaje de la clase = máximo entre sus consultas
        filas = []
        for i, rango in zip(*np.nonzero(top_p >= umbral)):
            cx, cy, w, h = cajas[i]
            x1, y1, x2, y2 = max(0.0, cx - w / 2), max(0.0, cy - h / 2), min(W, cx + w / 2), min(H, cy + h / 2)
            if x2 > x1 and y2 > y1:
                filas.append(dict(category_id=CAT_IDS[top_c[i, rango]], score=float(top_p[i, rango]),
                                  bbox=[float(x1), float(y1), float(x2 - x1), float(y2 - y1)], rango=int(rango)))
        res[var] = filas
    return res

FRAC_VENTANA, BORDE_VENTANA = 0.6, 3

def ventanas(W, H, frac=FRAC_VENTANA):
    """4 ventanas de frac × frac en las esquinas: se solapan en la franja central."""
    tw, th = int(round(W * frac)), int(round(H * frac))
    return [(x, y, x + tw, y + th) for y in (0, H - th) for x in (0, W - tw)]

def owl_ventanas(im, nombre, umbral=0.05, k_max=3):
    """E4: OWLv2 sobre cada ventana. Descarta las cajas que tocan un borde INTERNO de la ventana (objeto cortado)
    y devuelve el resto en coordenadas de la imagen completa."""
    W, H = im.size
    res = defaultdict(list)
    for x1, y1, x2, y2 in ventanas(W, H):
        for var, filas in owl_pasada(im.crop((x1, y1, x2, y2)), nombre, umbral, k_max).items():
            for f in filas:
                bx, by, bw, bh = f["bbox"]
                cortada = ((x1 > 0 and bx <= BORDE_VENTANA) or (y1 > 0 and by <= BORDE_VENTANA) or
                           (x2 < W and bx + bw >= (x2 - x1) - BORDE_VENTANA) or (y2 < H and by + bh >= (y2 - y1) - BORDE_VENTANA))
                if not cortada:
                    res[var].append(dict(f, bbox=[bx + x1, by + y1, bw, bh]))
    return res

def pasada_dev(nombre, con_ventanas=False):
    """Corre una variante del detector sobre las 120 imágenes de desarrollo (umbral 0,05, k ≤ 3) y guarda las crudas."""
    filas, t0 = [], time.time()
    for img_id, fname in imgs[["id", "fname"]].itertuples(index=False):
        im = Image.open(DEV / "images" / fname).convert("RGB")
        for var, lista in (owl_ventanas if con_ventanas else owl_pasada)(im, nombre).items():
            filas += [dict(f, image_id=img_id, variante=var, fuente="ventana" if con_ventanas else "imagen") for f in lista]
    df = pd.DataFrame(filas)
    df.to_pickle(SALIDA / f"dets_{nombre.split('/')[-1]}_{'ventanas' if con_ventanas else 'completa'}_dev.pkl")
    print(f"{nombre.split('/')[-1]} {'(4 ventanas)' if con_ventanas else '(imagen completa)'}: "
          f"{len(df)} detecciones crudas en {(time.time() - t0) / 60:.1f} min")
    return df

UMBRALES_GRUESOS = [0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.3, 0.35, 0.4]

def mejor_config(crudas, ks=(1, 2, 3)):
    """Mejor (k, umbral) por F1 de cajas: barrido grueso y después fino (paso 0,01) alrededor del óptimo."""
    mejores = []
    for k in ks:
        dk = aplicar_nms(crudas[crudas.rango < k])
        curva = {u: evaluar_cajas(dk[dk.score >= u]) for u in UMBRALES_GRUESOS}
        u0 = max(curva, key=lambda u: curva[u]["F1"])
        for u in np.round(np.arange(max(0.03, u0 - 0.03), u0 + 0.031, 0.01), 3):
            if float(u) not in curva:
                curva[float(u)] = evaluar_cajas(dk[dk.score >= u])
        u = max(curva, key=lambda u: curva[u]["F1"])
        mejores.append(dict(k=k, umbral=float(u), **curva[u]))
    return max(mejores, key=lambda r: r["F1"])

resultados_det, candidatos = [], {}

def registrar(nombre, crudas, modelo, sinonimos, con_ventanas, ensamble=False):
    m = mejor_config(crudas)
    candidatos[nombre] = crudas
    resultados_det.append(dict(variante=nombre, modelo=modelo, sinonimos=sinonimos, ventanas=con_ventanas, ensamble_large=ensamble,
                               **{c: m[c] for c in ["k", "umbral", "P", "R", "F1", "TP", "FP", "FN", "cobertura"]}))
    print(f"  {nombre:42s} F1 {m['F1']:.4f}  (P {m['P']:.3f}, R {m['R']:.3f}, k = {m['k']}, umbral {m['umbral']:.2f})")

# Línea base: las mismas detecciones crudas de 2.7, con el barrido fino de umbral
print("Línea base y E3 (modelo):")
registrar("base", dets_multi.assign(variante="sin_sinonimos", fuente="imagen"), MODELO_BASE, False, False)
base_q = pasada_dev(MODELO_BASE)
ctrl = aplicar_nms(base_q[(base_q.variante == "sin_sinonimos") & (base_q.rango < 2)])
print("  Control: sin sinónimos, k = 2 y umbral 0,20 reproduce la Fase 2 (F1 0,660):", round(evaluar_cajas(ctrl[ctrl.score >= 0.2])["F1"], 3))
large_q = pasada_dev(MODELO_LARGE)
registrar("large", large_q[large_q.variante == "sin_sinonimos"], MODELO_LARGE, False, False)
F1_E3 = {r["modelo"]: r["F1"] for r in resultados_det}
M = max(F1_E3, key=F1_E3.get)
crudas_M = large_q if M == MODELO_LARGE else base_q
corto = "large" if M == MODELO_LARGE else "base"

print(f"E7 (sinónimos), sobre el mejor modelo de E3 ({corto}):")
registrar(f"{corto} + sinónimos", crudas_M[crudas_M.variante == "con_sinonimos"], M, True, False)

print(f"E4 (ventanas), sobre {corto}:")
vent = pasada_dev(M, con_ventanas=True)
for var, con_sin in (("sin_sinonimos", False), ("con_sinonimos", True)):
    combinadas = pd.concat([crudas_M[crudas_M.variante == var], vent[vent.variante == var]], ignore_index=True)
    registrar(f"{corto} + ventanas" + (" + sinónimos" if con_sin else ""), combinadas, M, con_sin, True)

# E8 (v5): ensamble con large. Large solo rinde menos, pero puede encontrar objetos que base no ve; el NMS une los duplicados
if M == MODELO_BASE:
    print("E8 (ensamble base + large):")
    ens = pd.concat([crudas_M[crudas_M.variante == "con_sinonimos"], vent[vent.variante == "con_sinonimos"],
                     large_q[large_q.variante == "con_sinonimos"]], ignore_index=True)
    registrar("base + ventanas + sinónimos + large", ens, M, True, True, ensamble=True)

tabla_det = pd.DataFrame(resultados_det)
RESULTADOS = SALIDA / "results"
RESULTADOS.mkdir(exist_ok=True)
tabla_det.to_csv(RESULTADOS / "det_experimentos.csv", index=False)
print("\n" + tabla_det.drop(columns=["modelo"]).round(4).to_string(index=False))

# --- Configuración ganadora: reemplaza a la de la Fase 2 ---
g = tabla_det.loc[tabla_det.F1.idxmax()]
MODELO, K_MAX, UMBRAL = g.modelo, int(g.k), float(g.umbral)
VAR_ELEGIDA = "con_sinonimos" if g.sinonimos else "sin_sinonimos"
DET_CONFIG = dict(modelo=MODELO, prompt="a photo of a {clase}", sinonimos=bool(g.sinonimos), ventanas=bool(g.ventanas),
                  frac_ventana=FRAC_VENTANA if g.ventanas else None, ensamble_large=bool(g.ensamble_large),
                  k_max=K_MAX, nms_iou=0.5, umbral=UMBRAL)
dets_multi = candidatos[g.variante]
processor, model = cargar_owl(MODELO)
for nombre in [n for n in OWL if n != MODELO and not (DET_CONFIG["ensamble_large"] and n == MODELO_LARGE)]:   # liberar la GPU
    del OWL[nombre]
gc.collect(); torch.cuda.empty_cache() if device == "cuda" else None

def detectar_multi(img_path, umbral=0.05, k_max=None):
    """Detector final (configuración elegida en 2.9). Recibe SÓLO la imagen y el vocabulario."""
    im = Image.open(img_path).convert("RGB")
    k_max = k_max or K_MAX
    filas = [dict(f, fuente="imagen") for f in owl_pasada(im, MODELO, umbral, k_max)[VAR_ELEGIDA]]   # fuente: linaje (v6)
    if DET_CONFIG["ventanas"]:
        filas += [dict(f, fuente="ventana") for f in owl_ventanas(im, MODELO, umbral, k_max)[VAR_ELEGIDA]]
    if DET_CONFIG["ensamble_large"]:
        filas += [dict(f, fuente="large") for f in owl_pasada(im, MODELO_LARGE, umbral, k_max)[VAR_ELEGIDA]]
    return filas

print(f"\nConfiguración elegida: {g.variante} -> F1 {g.F1:.4f} (línea base 0,660: {g.F1 - 0.660:+.3f})")
print(json.dumps(DET_CONFIG, ensure_ascii=False))

# ¿Mejoró donde decía la hipótesis? Recall por tamaño, línea base vs. elegida
def recall_por_tamano(crudas, k, u):
    dk = aplicar_nms(crudas[crudas.rango < k])
    gd = gt_detectados(dk[dk.score >= u])
    gd["tamaño"] = pd.cut(gd.area, [0, 32**2, 96**2, np.inf], labels=["chico (<32²)", "mediano", "grande (≥96²)"])
    return gd.groupby("tamaño", observed=True).detectado.mean()
rb = tabla_det.iloc[0]
comp_tam = pd.DataFrame({"línea base": recall_por_tamano(candidatos["base"], int(rb.k), float(rb.umbral)),
                         "elegida": recall_por_tamano(dets_multi, K_MAX, UMBRAL)})
print("\nRecall por tamaño del objeto:\n", comp_tam.round(3).to_string())

ax = tabla_det.set_index("variante").F1.plot.barh(color=[AZUL if v == g.variante else GRIS for v in tabla_det.variante])
ax.axvline(0.50, color="#b03a2e", ls=":", label="mínimo promoción (0,50)")
ax.set(title="F1 de cajas en desarrollo por variante del detector", xlabel="F1 (mejor k y umbral de cada una)", ylabel="")
ax.set_xlim(0.4, max(0.8, tabla_det.F1.max() + 0.02)); ax.legend(); plt.show()
marcar_fase("2 detección")
