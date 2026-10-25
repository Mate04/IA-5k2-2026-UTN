# --- 8.1 ¿En qué etapa se pierde cada objeto real? (desarrollo, 120 imágenes) ---
def iou_matriz(A, B):
    """IoU entre dos listas de cajas [x, y, w, h] (vectorizado)."""
    A, B = np.asarray(A, float).reshape(-1, 4), np.asarray(B, float).reshape(-1, 4)
    iw = np.clip(np.minimum((A[:, 0] + A[:, 2])[:, None], (B[:, 0] + B[:, 2])[None]) - np.maximum(A[:, 0][:, None], B[:, 0][None]), 0, None)
    ih = np.clip(np.minimum((A[:, 1] + A[:, 3])[:, None], (B[:, 1] + B[:, 3])[None]) - np.maximum(A[:, 1][:, None], B[:, 1][None]), 0, None)
    inter = iw * ih
    return inter / (A[:, 2:].prod(1)[:, None] + B[:, 2:].prod(1)[None] - inter + 1e-9)

ETAPAS = ["OK", "máscara mala (SAM2)", "caja usada por otro objeto", "eliminado por NMS", "debajo del umbral",
          "localizado con otra clase", "no localizado"]
crudas_k = dets_multi[dets_multi.rango < K_MAX]
crudas_por_img = {i: d for i, d in crudas_k.groupby("image_id")}
final_por_img = {i: d for i, d in dets_final.groupby("image_id")}
vacio = dets_final.iloc[:0]

t0, filas_prop = time.time(), []
for img_id, r in img_meta.items():
    anns = anns_por_img[img_id]
    fin, cru = final_por_img.get(img_id, vacio), crudas_por_img.get(img_id, crudas_k.iloc[:0])
    # Emparejamiento uno a uno por clase, igual que evaluar_cajas (mayor confianza primero)
    asignada = {}
    for c in {a["category_id"] for a in anns}:
        gts = [a for a in anns if a["category_id"] == c]
        usado = [False] * len(gts)
        for idx, b in fin[fin.category_id == c].sort_values("score", ascending=False).bbox.items():
            ious = [-1 if usado[j] else iou_xywh(b, g["bbox"]) for j, g in enumerate(gts)]
            j = int(np.argmax(ious))
            if ious[j] >= 0.5:
                usado[j] = True
                asignada[gts[j]["id"]] = idx
    for a in anns:
        c, fila = a["category_id"], dict(image_id=img_id, ann_id=a["id"], clase=id2name[a["category_id"]], area=a["area"])
        if a["id"] in asignada:
            d = dets_final.loc[asignada[a["id"]]]
            gt_m = mask_utils.merge(mask_utils.frPyObjects(a["segmentation"], r.height, r.width))
            iou_m = float(mask_utils.iou([a_rle_coco(d.rle_sam)], [gt_m], [0])[0][0])
            filas_prop.append(dict(fila, etapa="OK" if iou_m >= 0.5 else "máscara mala (SAM2)", iou_mascara=round(iou_m, 3),
                                   score=round(float(d.score), 4), fuente=d.get("fuente", "imagen")))
            continue
        cubre = cru[iou_matriz([a["bbox"]], np.stack(cru.bbox.values))[0] >= 0.5] if len(cru) else cru
        de_su_clase = cubre[cubre.category_id == c]
        fin_c = fin[fin.category_id == c]
        sobrevive = len(fin_c) and (iou_matriz([a["bbox"]], np.stack(fin_c.bbox.values))[0] >= 0.5).any()
        if not len(cubre):
            etapa = "no localizado"
        elif not len(de_su_clase):
            etapa = "localizado con otra clase"
        elif de_su_clase.score.max() < UMBRAL:
            etapa = "debajo del umbral"
        elif not sobrevive:
            etapa = "eliminado por NMS"
        else:
            etapa = "caja usada por otro objeto"
        filas_prop.append(dict(fila, etapa=etapa, iou_mascara=np.nan,
                               score=round(float(de_su_clase.score.max()), 4) if len(de_su_clase) else np.nan, fuente=None))
prop = pd.DataFrame(filas_prop)
prop["tamaño"] = pd.cut(prop.area, [0, 32**2, 96**2, np.inf], labels=["chico (<32²)", "mediano", "grande (≥96²)"])
prop.to_csv(RESULTADOS / "propagacion_objetos.csv", index=False)
print(f"{len(prop)} objetos reales clasificados en {time.time() - t0:.0f} s")

tabla_prop = pd.crosstab(prop.etapa, prop["tamaño"], margins=True, margins_name="total").reindex(ETAPAS + ["total"])
tabla_prop["%"] = (100 * tabla_prop["total"] / len(prop)).round(1)
tabla_prop.to_csv(RESULTADOS / "propagacion_resumen.csv")
print(tabla_prop.to_string())
cajas_ok = prop.etapa.isin(["OK", "máscara mala (SAM2)"]).sum()
print(f"\nControl: objetos con caja correcta = {cajas_ok} (TP de cajas de 2.9 con la misma configuración: {int(tabla_det.loc[tabla_det.F1.idxmax(), 'TP'])})")
bajo = prop[prop.etapa == "debajo del umbral"].score
print(f"'Debajo del umbral': confianza máxima de su clase, mediana {bajo.median():.3f} (cuartiles {bajo.quantile(0.25):.3f} - {bajo.quantile(0.75):.3f})")
print(f"IoU de máscara de los objetos con caja correcta: media {prop.iou_mascara.mean():.3f} (oráculo con cajas reales, 3.3b: {oraculo.iou.mean():.3f})")
print("\nClases que más objetos pierden, por etapa:")
print(prop[prop.etapa != "OK"].groupby(["clase", "etapa"]).size().sort_values(ascending=False).head(10).to_string())
recall_clase = prop.etapa.isin(["OK", "máscara mala (SAM2)"]).groupby(prop.clase).mean()
print("Recall de cajas de las clases señaladas en 2.6 (en la línea base, person tenía 0,03 y book 26 de 43 sin caja):",
      {c: round(float(recall_clase[c]), 2) for c in ("person", "book", "shoe") if c in recall_clase})

pct = pd.crosstab(prop["tamaño"], prop.etapa, normalize="index").reindex(columns=ETAPAS) * 100
colores_etapa = [AZUL, "#7fa7c9", "#c9c9c9", "#a0a0a0", "#c98a2b", "#d9b26f", "#b03a2e"]
ax = pct.plot.barh(stacked=True, color=colores_etapa, figsize=(9, 3.2))
ax.set(title="¿En qué etapa se pierde cada objeto real? (por tamaño)", xlabel="% de los objetos reales", ylabel="")
ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8); plt.show()
