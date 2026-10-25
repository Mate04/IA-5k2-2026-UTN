## 0. Identificación de la corrida (agregado en la v6)

Cada ejecución recibe un **`RUN_ID`** que aparece en todas las trazas y en cada SceneJSON del envío (campo `trace`). Acá también se fijan las semillas y se registran las versiones del entorno. Al final (Fase 9), `manifiesto_corrida.json` junta el `RUN_ID`, la configuración completa con su hash (`config_hash`), los tiempos de cada fase y la lista de artefactos generados con su tamaño y su SHA-256. Con eso se puede reconstruir qué corrida produjo cada archivo y con qué parámetros.
