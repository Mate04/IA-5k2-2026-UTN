// Renderiza fotogramas sueltos para revisar el video sin exportarlo entero.
// Uso: node scripts/stills.mjs <carpeta-salida> <frame> [frame...]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";

const [outDir, ...frames] = process.argv.slice(2);
const root = path.resolve(import.meta.dirname, "..");
const serveUrl = await bundle({ entryPoint: path.join(root, "src", "index.ts"), publicDir: path.join(root, "public") });
const composition = await selectComposition({ serveUrl, id: "BusquedaLocalContinua" });
console.log("Duración total:", composition.durationInFrames, "frames =", (composition.durationInFrames / composition.fps).toFixed(1), "s");
for (const f of frames) {
  const output = path.join(outDir, `f${String(f).padStart(5, "0")}.png`);
  await renderStill({ serveUrl, composition, frame: Number(f), output, scale: 0.5 });
  console.log("ok", output);
}
