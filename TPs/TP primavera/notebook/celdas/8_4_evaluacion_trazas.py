# --- 8.4 Evaluación de las etapas a partir de las trazas ---
# Percepción (traza_envio.csv): costo y fallas de cada módulo en las 80 imágenes del envío
modulos = traza.groupby("modulo", sort=False).agg(ejecuciones=("ok", "size"), fallas=("ok", lambda s: int((~s).sum())),
                                                  ms_medio=("duracion_ms", "mean"), ms_p95=("duracion_ms", lambda s: s.quantile(0.95)),
                                                  salidas_medias=("n_salidas", "mean"))
modulos["% del tiempo"] = 100 * traza.groupby("modulo", sort=False).duracion_ms.sum() / traza.duracion_ms.sum()
modulos.to_csv(RESULTADOS / "traza_modulos.csv")
print("Percepción por módulo (80 imágenes):")
print(modulos.round(1).to_string())
n_crudas = int(traza[traza.modulo == "detector"].n_salidas.sum())
n_finales = int(traza[traza.modulo == "nms_umbral"].n_salidas.sum())
print(f"\nEmbudo del detector: {n_crudas} detecciones crudas (≥ 0,05) → {n_finales} tras NMS y umbral ({n_finales / n_crudas:.1%})"
      f" → {len(linaje)} objetos en los SceneJSON | escenas vacías por falla: {sum(len(e['objects']) == 0 for e in escenas)}")

# Linaje (traza_objetos.csv): de dónde salen los objetos que llegan al SceneJSON
print("Objetos por fuente:", linaje.fuente.value_counts(normalize=True).round(3).to_dict(),
      "| por rango de la clase en su caja:", linaje.rango_clase.value_counts().sort_index().to_dict(),
      "| máscaras de respaldo (caja):", int(linaje.mascara_respaldo.sum()))
print("Fracción de la caja cubierta por la máscara: mediana", round(float(linaje.relleno_caja.median()), 3),
      "| objetos con máscara < 20 % de su caja:", int((linaje.relleno_caja < 0.2).sum()))

# Modo LLM (traza_llm.csv): reintentos, normalización de clases y redacción
norm = Counter(n["como"] for x in traza_llm_df.normalizacion for n in json.loads(x))
print("\nIntérprete LLM | reintentos:", traza_llm_df.motivo_reintento.replace("", "ninguno").value_counts().to_dict(),
      "| normalización de clases:", dict(norm), f"| {traza_llm_df.ms_interprete.mean():.0f} ms por pregunta")
print("Redacción usada:", traza_llm_df.redaccion.value_counts().to_dict())
marcar_fase("8 trazas y propagación")
