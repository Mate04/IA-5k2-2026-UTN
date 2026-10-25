@torch.no_grad()
def segmentar_con(proc, mod, im, cajas_xywh, lote=64):
    """Igual que segmentar(), pero con el segmentador que se le pasa (para comparar modelos)."""
    mascaras = []
    for i in range(0, len(cajas_xywh), lote):
        xyxy = [[x, y, x + w, y + h] for x, y, w, h in cajas_xywh[i:i + lote]]
        inp = proc(images=im, input_boxes=[xyxy], return_tensors="pt").to(device)
        out = mod(**inp, multimask_output=False)
        m = proc.post_process_masks(out.pred_masks.cpu(), inp["original_sizes"].cpu())[0]
        mascaras += [mm[0].numpy().astype(bool) for mm in m]
    return mascaras

def caja_de_mascara(m):
    """Caja [x, y, w, h] que encierra los píxeles de la máscara."""
    ys, xs = np.nonzero(m)
    return [float(xs.min()), float(ys.min()), float(xs.max() - xs.min() + 1), float(ys.max() - ys.min() + 1)]

res_seg = [dict(segmentador=SAM_ID, **evaluar_mascaras(dets_final, "rle_sam"))]
SAM_LARGE = "facebook/sam2.1-hiera-large"
if ES_SAM2:
    sam_proc_L = Sam2Processor.from_pretrained(SAM_LARGE)
    sam_L = Sam2Model.from_pretrained(SAM_LARGE).to(device).eval()
    rle_L, t0 = {}, time.time()
    for img_id, d_img in dets_final.groupby("image_id", sort=False):
        r = img_meta[img_id]
        im = Image.open(DEV / "images" / r.fname).convert("RGB")
        for idx, b, m in zip(d_img.index, d_img.bbox, segmentar_con(sam_proc_L, sam_L, im, d_img.bbox.tolist())):
            rle_L[idx] = rle_encode(m if m.sum() else caja_a_mascara(b, r.height, r.width))
    dets_final["rle_sam_large"] = pd.Series(rle_L)
    res_seg.append(dict(segmentador=SAM_LARGE, **evaluar_mascaras(dets_final, "rle_sam_large")))
    print(f"SAM2 large: {len(rle_L)} máscaras en {(time.time() - t0) / 60:.1f} min")
tabla_seg = pd.DataFrame(res_seg)
print("\nE6 · F1 de máscaras con las mismas cajas:")
print(tabla_seg.round(4).to_string(index=False))

# El mejor segmentador pasa a la pipeline (Fase 4 usa sam_proc, sam y SAM_ID)
if len(res_seg) > 1 and res_seg[1]["F1"] > res_seg[0]["F1"]:
    sam_proc, sam, SAM_ID = sam_proc_L, sam_L, SAM_LARGE
    dets_final["rle_sam"] = dets_final["rle_sam_large"]
elif ES_SAM2:
    del sam_proc_L, sam_L
gc.collect(); torch.cuda.empty_cache() if device == "cuda" else None
print("Segmentador elegido:", SAM_ID)
dets_final.to_pickle(SALIDA / "dets_final_dev_con_mascaras.pkl")

# Caja del detector vs. caja que encierra la máscara
cajas_m = dets_final.rle_sam.map(lambda r: caja_de_mascara(rle_decode(r)))
F1_CAJA_DET = evaluar_cajas(dets_final)["F1"]
F1_CAJA_MASC = evaluar_cajas(dets_final.assign(bbox=cajas_m))["F1"]
CAJA_DESDE_MASCARA = F1_CAJA_MASC > F1_CAJA_DET
print(f"\nF1 de cajas | caja del detector: {F1_CAJA_DET:.4f} | caja de la máscara: {F1_CAJA_MASC:.4f}"
      f" -> se usa la {'de la máscara' if CAJA_DESDE_MASCARA else 'del detector'}")

# E5 · Oráculo: SAM2 (el elegido) con las cajas reales
seg_por_ann = {a["id"]: a["segmentation"] for a in ann["annotations"]}
filas_or, t0 = [], time.time()
for img_id, g_img in objs.groupby("image_id"):
    r = img_meta[img_id]
    im = Image.open(DEV / "images" / r.fname).convert("RGB")
    for a, m in zip(g_img.itertuples(), segmentar(im, g_img.bbox.tolist())):
        gt = mask_utils.decode(mask_utils.merge(mask_utils.frPyObjects(seg_por_ann[a.id], r.height, r.width))).astype(bool)
        union = (m | gt).sum()
        filas_or.append(dict(area=a.area, iou=float((m & gt).sum() / union) if union else 0.0))
oraculo = pd.DataFrame(filas_or)
oraculo["tamaño"] = pd.cut(oraculo.area, [0, 32**2, 96**2, np.inf], labels=["chico (<32²)", "mediano", "grande (≥96²)"])
print(f"\nE5 · Oráculo ({len(oraculo)} objetos reales, {(time.time() - t0) / 60:.1f} min): IoU medio {oraculo.iou.mean():.3f} | "
      f"máscaras con IoU ≥ 0,5: {(oraculo.iou >= 0.5).mean():.1%}")
print(oraculo.groupby("tamaño", observed=True).iou.agg(objetos="size", iou_medio="mean",
                                                        iou_ge_05=lambda s: (s >= 0.5).mean()).round(3).to_string())
tabla_seg.to_csv(RESULTADOS / "seg_experimentos.csv", index=False)
oraculo.to_csv(RESULTADOS / "seg_oraculo.csv", index=False)
marcar_fase("3 segmentación")
