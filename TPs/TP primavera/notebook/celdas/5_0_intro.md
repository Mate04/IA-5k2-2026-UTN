## 5. Preguntas en modo determinista

Objetivo de la fase: responder las consignas del benchmark **leyendo sólo el SceneJSON predicho**. No se usa LLM, y el código decide cada conteo, filtro y relación.

```
pregunta + campos estructurados ─► consulta intermedia (JSON validado) ─► motor determinista ─► respuesta normalizada + evidencia
```

La consulta intermedia es el contrato entre "entender la pregunta" y "responderla". En esta fase la arma un parser con reglas. En la Fase 6 la va a armar un LLM, y la va a ejecutar **el mismo motor**.

Operaciones soportadas:

| Intención | Salida normalizada | Cómo se resuelve |
|---|---|---|
| `count` | entero | cantidad de objetos de la clase |
| `existence` | `yes` / `no` | hay al menos un objeto de la clase |
| `position` | una de las 9 zonas | `position` de la instancia elegida |
| `size` | `small` / `medium` / `large` | `size` de la instancia elegida |
| `relation` | `yes` / `no` | la tripleta está en `relations` (o en `extra_relations` si es `near`) |
| `attribute` | nombre de color | `attributes.color` de la instancia elegida |
| `compare` | `yes` / `no` | compara las cantidades de dos clases |
| `description` | texto | plantilla con conteos, zonas y el objeto más grande |

Casos especiales, siempre explícitos:
- **Ambigua:** hay varias instancias de la clase. Se responde por la de mayor confianza, `status = "ambiguous"`, las demás van en `alternatives` y la confianza se reparte entre ellas.
- **Información insuficiente:** la clase no se detectó. En posición, tamaño, atributo y relación se responde `unknown` en lugar de inventar.
- **No soportada:** clase fuera del vocabulario, operación inexistente o atributo no calculado. Se responde `unsupported`.

Regla anti-fuga: `ejecutar()` recibe la consulta y el SceneJSON predicho. Las anotaciones aparecen recién en 5.5, sólo para medir.
