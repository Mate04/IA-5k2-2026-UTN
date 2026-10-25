for e in escenas:
    e["questions_llm"] = preguntas_llm.get(e["image"]["id"], [])

problemas = {e["image"]["id"]: problemas_de_fila(e) for e in escenas}
malas = {k: v for k, v in problemas.items() if v}
print("Filas con problemas:", len(malas), "de", len(escenas))
assert not malas, list(malas.items())[:3]
con_llm = sum(len(e["questions_llm"]) > 0 for e in escenas)
print("Filas con questions_llm:", con_llm, "| respuestas:", sum(len(e["questions_llm"]) for e in escenas))
assert con_llm == qs.image_key.nunique()

envio = pd.DataFrame(dict(image_id=[e["image"]["id"] for e in escenas],
                          SceneJSON=[json.dumps(e, separators=(",", ":"), ensure_ascii=False) for e in escenas]))
assert list(envio.image_id) == list(sub.image_id), "filas u orden distintos al sample"
envio.to_csv(SALIDA / "submission.csv", index=False)
envio.to_csv(SALIDA / "solution.csv", index=False)

ev_llm.to_csv(RESULTADOS / "qa_llm_respuestas.csv", index=False)
ev_desc.to_csv(RESULTADOS / "qa_llm_descripciones.csv", index=False)
ev_extra_llm.to_csv(RESULTADOS / "qa_llm_extra.csv", index=False)
pd.DataFrame(traza_llm).to_csv(SALIDA / "traza_llm.csv", index=False)

# Resumen de la versión: todos los números salen de las variables de esta corrida
seg_elegido = tabla_seg.loc[tabla_seg.segmentador == SAM_ID].iloc[0]
resumen_corrida = pd.DataFrame([
    dict(etapa="detección", metrica="F1 de cajas (dev, IoU 0,5, LVIS)", valor=round(float(g.F1), 4), linea_base=0.660),
    dict(etapa="segmentación", metrica="F1 de máscaras (dev)", valor=round(float(seg_elegido.F1), 4), linea_base=0.620),
    dict(etapa="QA determinista", metrica="exactitud en cerradas", valor=round(float(ev_det.correcta.mean()), 4), linea_base=0.75),
    dict(etapa="QA LLM", metrica="exactitud en cerradas", valor=round(float(cerr.correcta_llm.astype(bool).mean()), 4), linea_base=None),
    dict(etapa="QA LLM", metrica="interpretación correcta al primer intento", valor=round(float(ev_llm.interpretacion_ok_1.mean()), 4), linea_base=None),
    dict(etapa="QA LLM", metrica="interpretación correcta", valor=round(float(ev_llm.interpretacion_ok.mean()), 4), linea_base=None),
    dict(etapa="QA LLM", metrica="descripciones redactadas por el LLM", valor=round(float((ev_desc.redaccion == "llm").mean()), 4), linea_base=None),
])
resumen_corrida.to_csv(RESULTADOS / "resumen_corrida.csv", index=False)
print("\nConfiguración:", json.dumps(dict(detector=DET_CONFIG, segmentador=SAM_ID, caja_desde_mascara=bool(CAJA_DESDE_MASCARA),
                                           llm=LLM_CONFIG), ensure_ascii=False))
print(resumen_corrida.to_string(index=False))
print(f"\nsubmission.csv: {(SALIDA / 'submission.csv').stat().st_size / 1e6:.1f} MB | resultados en {RESULTADOS}")
marcar_fase("6 modo LLM")
