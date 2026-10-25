# --- 7.1 Validación cruzada (5 particiones por imagen) de k y del umbral ---
ids_cv = np.array(sorted(img_meta))
np.random.default_rng(SEMILLA).shuffle(ids_cv)
PARTICIONES = [set(p) for p in np.array_split(ids_cv, 5)]
UMBRALES_CV = np.round(np.arange(0.10, 0.401, 0.01), 2)
nms_por_k = {k: aplicar_nms(dets_multi[dets_multi.rango < k]) for k in (1, 2, 3)}
F1_DEV_FINAL = float(tabla_det.F1.max())     # F1 de la configuración final, medido dentro de la muestra (2.9)

def elegir_config(imagenes):
    """(k, umbral, F1) de mayor F1 de cajas en esas imágenes: el criterio de 2.9 con paso 0,01."""
    return max(((k, float(u), evaluar_cajas(d[d.score >= u], imagenes=imagenes)["F1"])
                for k, d in nms_por_k.items() for u in UMBRALES_CV), key=lambda x: x[2])

t0 = time.time()
filas_cv = []
for i, prueba in enumerate(PARTICIONES, 1):
    entren = set(ids_cv) - prueba
    k, u, f1_entren = elegir_config(entren)
    m = evaluar_cajas(nms_por_k[k][nms_por_k[k].score >= u], imagenes=prueba)
    d_fin = nms_por_k[K_MAX]
    filas_cv.append(dict(particion=i, imagenes_prueba=len(prueba), k=k, umbral=u, F1_entrenamiento=f1_entren,
                         F1_prueba=m["F1"], P_prueba=m["P"], R_prueba=m["R"],
                         F1_prueba_config_final=evaluar_cajas(d_fin[d_fin.score >= UMBRAL], imagenes=prueba)["F1"]))
cv = pd.DataFrame(filas_cv)
cv.to_csv(RESULTADOS / "det_validacion_cruzada.csv", index=False)
print(f"Validación cruzada en {time.time() - t0:.0f} s\n")
print(cv.round(4).to_string(index=False))
print(f"\nF1 en las particiones de prueba: {cv.F1_prueba.mean():.4f} ± {cv.F1_prueba.std():.4f} (media ± desvío)")
print(f"F1 de la configuración final dentro de la muestra (2.9): {F1_DEV_FINAL:.4f} -> optimismo estimado {F1_DEV_FINAL - cv.F1_prueba.mean():+.4f}")
print("Umbrales elegidos:", sorted(cv.umbral.tolist()), "| k elegidos:", cv.k.value_counts().to_dict())

# Sensibilidad: F1 sobre las 120 imágenes según el umbral, con el k final
curva_u = pd.DataFrame([dict(umbral=float(u), **evaluar_cajas(nms_por_k[K_MAX][nms_por_k[K_MAX].score >= u])) for u in UMBRALES_CV])
curva_u.to_csv(RESULTADOS / "det_curva_umbral.csv", index=False)
cerca = curva_u[(curva_u.umbral >= UMBRAL - 0.03) & (curva_u.umbral <= UMBRAL + 0.03)]
print(f"F1 con umbrales a ±0,03 del final: entre {cerca.F1.min():.4f} y {cerca.F1.max():.4f}")
ax = curva_u.plot(x="umbral", y=["P", "R", "F1"], marker=".", color=[GRIS, "#c98a2b", AZUL])
ax.axvspan(cv.umbral.min() - 0.005, cv.umbral.max() + 0.005, color=AZUL, alpha=0.12, label="umbrales elegidos en la validación cruzada")
ax.axvline(UMBRAL, color=GRIS, ls="--", label=f"umbral final ({UMBRAL:.2f})")
ax.set(title=f"Sensibilidad del F1 de cajas al umbral (k = {K_MAX}, 120 imágenes)", xlabel="Umbral de confianza", ylabel="Valor")
ax.legend(); plt.show()
