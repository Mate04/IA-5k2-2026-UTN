# --- 7.2 E9: ¿conviene un umbral distinto para las cajas de las ventanas? ---
d_k = nms_por_k[K_MAX]
U_FUENTE = [0.15, 0.18, 0.20, 0.22, 0.25, 0.28, 0.30, 0.35]

def f1_por_fuente(u_img, u_vent, imagenes=None):
    """F1 de cajas con un umbral para las cajas de la imagen completa y otro para las de las ventanas (después del NMS)."""
    sel = d_k[np.where(d_k.fuente == "ventana", d_k.score >= u_vent, d_k.score >= u_img)]
    return evaluar_cajas(sel, imagenes=imagenes)["F1"]

print("Detecciones finales por fuente (k y umbral finales):", d_k[d_k.score >= UMBRAL].fuente.value_counts().to_dict())
if d_k.fuente.nunique() > 1:
    t0, filas_e9 = time.time(), []
    for i, prueba in enumerate(PARTICIONES, 1):
        entren = set(ids_cv) - prueba
        grilla = {(a, b): f1_por_fuente(a, b, entren) for a in U_FUENTE for b in U_FUENTE}
        a, b = max(grilla, key=grilla.get)                                     # dos umbrales
        u1 = max((u for u in U_FUENTE), key=lambda u: grilla[(u, u)])          # un umbral, elegido igual
        filas_e9.append(dict(particion=i, umbral_imagen=a, umbral_ventanas=b, F1_prueba_dos_umbrales=f1_por_fuente(a, b, prueba),
                             umbral_unico=u1, F1_prueba_umbral_unico=f1_por_fuente(u1, u1, prueba)))
    e9 = pd.DataFrame(filas_e9)
    e9.to_csv(RESULTADOS / "det_umbral_por_fuente.csv", index=False)
    print(f"E9 en {time.time() - t0:.0f} s\n")
    print(e9.round(4).to_string(index=False))
    dif = e9.F1_prueba_dos_umbrales - e9.F1_prueba_umbral_unico
    print(f"\nDos umbrales: {e9.F1_prueba_dos_umbrales.mean():.4f} ± {e9.F1_prueba_dos_umbrales.std():.4f} | "
          f"umbral único: {e9.F1_prueba_umbral_unico.mean():.4f} ± {e9.F1_prueba_umbral_unico.std():.4f} | "
          f"diferencia media {dif.mean():+.4f} (mejora en {int((dif > 0).sum())} de 5 particiones, empeora en {int((dif < 0).sum())})")
else:
    print("La configuración final no usa ventanas: E9 no aplica.")
marcar_fase("7 validación cruzada")
