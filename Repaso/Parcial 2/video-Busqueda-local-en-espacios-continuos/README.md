# 4.2 · Búsqueda local en espacios continuos (video explicativo)

Video de ~8,5 minutos que explica la sección 4.2 de *Inteligencia Artificial: un enfoque moderno*
(Russell & Norvig), hecho con Remotion y narrado con ElevenLabs (voz "Matilda").

## Ver el video

```console
npm run dev
```

Abre Remotion Studio en http://localhost:3000. La composición se llama `BusquedaLocalContinua`.

## Exportar a MP4

```console
npx remotion render BusquedaLocalContinua out/busqueda-local-continua.mp4
```

## Cómo está armado

- `scripts/narration.mjs`: el guion, una entrada por escena. Las marcas `{{nombre}}` indican cuándo arranca cada animación.
- `scripts/generate-voiceover.mjs`: pide toda la narración a ElevenLabs en un solo pedido, la guarda en
  `public/voiceover/full.mp3` y la corta por escena. También escribe `src/voiceover/data.json` con los tiempos
  de cada marca y de cada palabra (para los subtítulos).
  Si el guion no cambió, reutiliza el audio guardado y no gasta créditos.
  ```console
  node --env-file=.env.local scripts/generate-voiceover.mjs
  ```
- `src/scenes/`: una escena por archivo (intro, discreto vs. continuo, aeropuertos, función objetivo,
  discretizar, gradiente, tamaño de paso, demo, Newton-Raphson, Newton en los aeropuertos, problemas,
  restricciones, resumen).
- `src/lib/romania.ts`: el mapa de Rumania y las cuentas reales del problema de los aeropuertos
  (ecuaciones 4.1 y 4.2, descenso por gradiente y pasos de Newton).
- `scripts/stills.mjs`: renderiza fotogramas sueltos para revisar sin exportar todo.

La key de ElevenLabs está en `.env.local` (excluido de git).
