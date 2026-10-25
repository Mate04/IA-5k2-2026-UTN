# --- 9.1 Resumen de resultados: cada número sale de una variable de esta corrida y queda atado a su archivo ---
fila_det = tabla_det.loc[tabla_det.F1.idxmax()]
seg_fin = tabla_seg.loc[tabla_seg.segmentador == SAM_ID].iloc[0]
cerradas_llm = ev_llm[ev_llm.type != "description"]
aceptadas = ev_desc[ev_desc.redaccion == "llm"]
R = lambda x: round(float(x), 4)
resumen_final = pd.DataFrame([
    ("detección", "F1 de cajas en desarrollo (configuración final)", R(fila_det.F1), "det_experimentos.csv"),
    ("detección", "precisión / recall", f"{R(fila_det.P)} / {R(fila_det.R)}", "det_experimentos.csv"),
    ("detección", "cobertura de evaluación (LVIS)", R(fila_det.cobertura), "det_experimentos.csv"),
    ("detección", "F1 de cajas en validación cruzada (media)", R(cv.F1_prueba.mean()), "det_validacion_cruzada.csv"),
    ("detección", "F1 de cajas en validación cruzada (desvío)", R(cv.F1_prueba.std()), "det_validacion_cruzada.csv"),
    ("segmentación", "F1 de máscaras en desarrollo", R(seg_fin.F1), "seg_experimentos.csv"),
    ("segmentación", "IoU medio de SAM2 con cajas reales (oráculo)", R(oraculo.iou.mean()), "seg_oraculo.csv"),
    ("propagación", "objetos reales con caja y máscara correctas", R((prop.etapa == "OK").mean()), "propagacion_objetos.csv"),
    ("propagación", "objetos reales perdidos por el umbral", R((prop.etapa == "debajo del umbral").mean()), "propagacion_objetos.csv"),
    ("propagación", "objetos reales no localizados", R((prop.etapa == "no localizado").mean()), "propagacion_objetos.csv"),
    ("QA determinista", "exactitud en preguntas cerradas", R(ev_det.correcta.mean()), "qa_det_exactitud.csv"),
    ("QA determinista", "fidelidad al SceneJSON", R(fid.fiel.mean()), "qa_det_fidelidad.csv"),
    ("QA determinista", "casos extra bien manejados", R(ev_extra.correcto.mean()), "qa_extra_manejo.csv"),
    ("QA LLM", "clases escritas exactamente como en el vocabulario (sin normalizar)", R(ev_llm.clases_exactas_1.mean()), "qa_llm_respuestas.csv"),
    ("QA LLM", "interpretación correcta al primer intento", R(ev_llm.interpretacion_ok_1.mean()), "qa_llm_respuestas.csv"),
    ("QA LLM", "interpretación correcta (final)", R(ev_llm.interpretacion_ok.mean()), "qa_llm_respuestas.csv"),
    ("QA LLM", "JSON válido (final)", R(ev_llm.json_valido_final.mean()), "qa_llm_respuestas.csv"),
    ("QA LLM", "exactitud en preguntas cerradas", R(cerradas_llm.correcta_llm.astype(bool).mean()), "qa_llm_respuestas.csv"),
    ("QA LLM", "misma respuesta que el modo determinista", R(cerradas_llm.igual_det.astype(bool).mean()), "qa_llm_respuestas.csv"),
    ("QA LLM", "redacciones aceptadas por el control (cerradas)", R((cerradas_llm.redaccion == "llm").mean()), "qa_llm_respuestas.csv"),
    ("QA LLM", "descripciones redactadas por el LLM", R((ev_desc.redaccion == "llm").mean()), "qa_llm_descripciones.csv"),
    ("QA LLM", "clases alucinadas en las descripciones aceptadas", int(aceptadas.alucinadas.sum()), "qa_llm_descripciones.csv"),
    ("QA LLM", "cobertura de las 3 clases principales en la descripción", R(ev_desc.cobertura_top3.mean()), "qa_llm_descripciones.csv"),
    ("QA LLM", "casos extra bien manejados", R(ev_extra_llm.correcto.mean()), "qa_llm_extra.csv"),
    ("envío", "filas válidas", f"{sum(not problemas_de_fila(e) for e in escenas)} de {len(escenas)}", "submission.csv"),
], columns=["etapa", "metrica", "valor", "archivo"])
resumen_final.to_csv(RESULTADOS / "resumen_final.csv", index=False)
print(resumen_final.to_string(index=False))

# --- 9.2 Manifiesto: configuración completa, versiones, tiempos y artefactos ---
marcar_fase("9 resumen")
assert all(e.get("trace", {}).get("run_id") == RUN_ID for e in escenas), "hay filas del envío sin el RUN_ID de esta corrida"
CONFIG_COMPLETA = dict(semilla=SEMILLA, percepcion=CONFIG_PERCEPCION, llm=LLM_CONFIG,
                       prompts={n: huella(v) for n, v in dict(interprete=MENSAJES_INTERPRETE, verbalizar=MENSAJES_VERBALIZAR,
                                                              describir=[PROMPT_DESCRIBIR, EJEMPLO_DESCRIBIR]).items()},
                       qa=dict(conf_ausencia=CONF_AUSENCIA, alias_en=len(ALIAS_EN), reintentos_max=1))

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()

artefactos = [dict(ruta=p.relative_to(SALIDA).as_posix(), bytes=p.stat().st_size, sha256=sha256(p))
              for p in sorted(SALIDA.rglob("*")) if p.is_file() and p.name != "manifiesto_corrida.json" and ".ipynb" not in p.name]
manifiesto = dict(run_id=RUN_ID, config_hash=huella(CONFIG_COMPLETA), config_percepcion_hash=TRAZA_ESCENA["config_percepcion"],
                  config=CONFIG_COMPLETA, versiones=VERSIONES, tiempos_fase_s=TIEMPOS_FASE,
                  duracion_total_min=round((time.time() - T_INICIO) / 60, 1),
                  datos=dict(competencia=ROOT.name, schema_sha256=sha256(ROOT / "scene_schema.json"),
                             imagenes_desarrollo=len(img_meta), filas_envio=len(escenas), consignas=len(qs)),
                  artefactos=artefactos)
(SALIDA / "manifiesto_corrida.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\nmanifiesto_corrida.json | run_id {RUN_ID} | config_hash {manifiesto['config_hash']} | {len(artefactos)} artefactos "
      f"| {manifiesto['duracion_total_min']} min en total")
print("Tiempos por fase (s desde el inicio):", TIEMPOS_FASE)
print(pd.DataFrame(artefactos).assign(MB=lambda d: (d.bytes / 1e6).round(2))[["ruta", "MB", "sha256"]]
      .assign(sha256=lambda d: d.sha256.str.slice(0, 12)).to_string(index=False))
