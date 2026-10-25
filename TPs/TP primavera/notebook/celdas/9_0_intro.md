## 9. Manifiesto de la corrida y resumen de resultados (agregado en la v6)

Cierre de la traza. `manifiesto_corrida.json` registra:
- `run_id` y `config_hash`: el hash de **toda** la configuración (percepción, LLM, prompts y semilla). El SceneJSON de cada fila trae el `run_id` y el hash de la parte de percepción, así que cada fila del envío se puede atar a esta corrida;
- las versiones del entorno y el tiempo de cada fase;
- la lista de **artefactos** generados (`submission.csv`, trazas, `results/*.csv`, detecciones crudas) con su tamaño y su SHA-256.

`results/resumen_final.csv` junta en una tabla las métricas principales de cada etapa, con el archivo de donde sale cada número. Es la tabla que cita el reporte (`REPORTE.md`).
