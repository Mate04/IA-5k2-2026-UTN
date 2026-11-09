// Genera toda la narración con ElevenLabs en UN solo pedido y después la corta por escena.
//
// Uso:
//   node --env-file=.env.local scripts/generate-voiceover.mjs            -> genera (si cambió el guion) y corta
//   node --env-file=.env.local scripts/generate-voiceover.mjs --dry-run  -> solo cuenta caracteres
//   node --env-file=.env.local scripts/generate-voiceover.mjs --force    -> regenera aunque el guion no cambió
//
// Salidas:
//   public/voiceover/full.mp3 + full.json  -> audio completo y timestamps crudos (caché: no se vuelve a pagar)
//   public/voiceover/<escena>.mp3          -> un recorte por escena
//   src/voiceover/data.json                -> duración, marcas {{cue}} y palabras de cada escena (tiempos relativos a la escena)

import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { MODEL_ID, VOICE_ID, scenes } from "./narration.mjs";

const ROOT = path.resolve(import.meta.dirname, "..");
const AUDIO_DIR = path.join(ROOT, "public", "voiceover");
const FULL_MP3 = path.join(AUDIO_DIR, "full.mp3");
const FULL_JSON = path.join(AUDIO_DIR, "full.json");
const DATA_FILE = path.join(ROOT, "src", "voiceover", "data.json");
const SCENE_SEPARATOR = "\n\n";

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const force = args.includes("--force");

// Arma el texto completo sin las marcas {{cue}} y recuerda en qué carácter cae
// cada marca y dónde empieza/termina cada escena.
const buildScript = () => {
  let full = "";
  const parts = scenes.map((scene, i) => {
    if (i > 0) full += SCENE_SEPARATOR;
    const start = full.length;
    const cues = {};
    const re = /\{\{(\w+)\}\}/g;
    let last = 0;
    let m;
    while ((m = re.exec(scene.text))) {
      full += scene.text.slice(last, m.index);
      cues[m[1]] = full.length;
      last = m.index + m[0].length;
    }
    full += scene.text.slice(last);
    return { id: scene.id, start, end: full.length, cues };
  });
  return { full, parts };
};

const { full, parts } = buildScript();
const hash = createHash("sha1").update(`${VOICE_ID}|${MODEL_ID}|${full}`).digest("hex").slice(0, 12);
console.log(`Guion completo: ${full.length} caracteres.`);
if (dryRun) process.exit(0);

mkdirSync(AUDIO_DIR, { recursive: true });
mkdirSync(path.dirname(DATA_FILE), { recursive: true });

// 1) Generar (o reutilizar la caché si el guion no cambió).
let cached = existsSync(FULL_JSON) ? JSON.parse(readFileSync(FULL_JSON, "utf8")) : null;
if (force || !cached || cached.hash !== hash || !existsSync(FULL_MP3)) {
  console.log("Pidiendo la narración completa a ElevenLabs...");
  const client = new ElevenLabsClient();
  const res = await client.textToSpeech.convertWithTimestamps(
    VOICE_ID,
    {
      text: full,
      modelId: MODEL_ID,
      languageCode: "es",
      outputFormat: "mp3_44100_128",
      voiceSettings: { stability: 0.5, similarityBoost: 0.8 },
    },
    { timeoutInSeconds: 600 },
  );
  writeFileSync(FULL_MP3, Buffer.from(res.audioBase64, "base64"));
  cached = { hash, alignment: res.alignment };
  writeFileSync(FULL_JSON, JSON.stringify(cached));
} else {
  console.log("El guion no cambió: uso el audio que ya estaba generado.");
}

const al = cached.alignment;
const starts = al.characterStartTimesSeconds;
const ends = al.characterEndTimesSeconds;
if (al.characters.length !== full.length) {
  console.warn(`Aviso: la alineación tiene ${al.characters.length} caracteres y el texto ${full.length}.`);
}

const probeDuration = (file) =>
  Number(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file]).toString().trim());
const totalDuration = probeDuration(FULL_MP3);

const isSpace = (i) => /\s/.test(al.characters[i] ?? " ");
const firstSpoken = (from, to) => {
  for (let i = from; i < to; i++) if (!isSpace(i)) return i;
  return from;
};
const lastSpoken = (from, to) => {
  for (let i = to - 1; i >= from; i--) if (!isSpace(i)) return i;
  return to - 1;
};

// 2) Puntos de corte: el medio del silencio entre una escena y la siguiente.
const cuts = parts.map((p, i) => {
  const speechStart = starts[firstSpoken(p.start, p.end)];
  const speechEnd = ends[lastSpoken(p.start, p.end)];
  return { speechStart, speechEnd };
});
const bounds = parts.map((p, i) => {
  const from = i === 0 ? 0 : (cuts[i - 1].speechEnd + cuts[i].speechStart) / 2;
  const to = i === parts.length - 1 ? totalDuration : (cuts[i].speechEnd + cuts[i + 1].speechStart) / 2;
  return { from, to };
});

// 3) Cortar cada escena y calcular sus tiempos relativos.
const toWords = (from, to, offset) => {
  const words = [];
  let current = null;
  for (let i = from; i < to; i++) {
    if (isSpace(i)) {
      if (current) words.push(current);
      current = null;
      continue;
    }
    if (!current) current = { text: al.characters[i], start: starts[i] - offset, end: ends[i] - offset };
    else {
      current.text += al.characters[i];
      current.end = ends[i] - offset;
    }
  }
  if (current) words.push(current);
  return words.map((w) => ({ text: w.text, start: +w.start.toFixed(3), end: +w.end.toFixed(3) }));
};

const data = {};
parts.forEach((p, i) => {
  const { from, to } = bounds[i];
  const out = path.join(AUDIO_DIR, `${p.id}.mp3`);
  execFileSync("ffmpeg", [
    "-y", "-loglevel", "error",
    "-i", FULL_MP3,
    "-ss", from.toFixed(3), "-to", to.toFixed(3),
    "-af", "afade=t=in:d=0.03,areverse,afade=t=in:d=0.05,areverse",
    "-c:a", "libmp3lame", "-q:a", "2",
    out,
  ]);
  const cues = {};
  for (const [name, idx] of Object.entries(p.cues)) {
    const t = idx < starts.length ? starts[firstSpoken(idx, p.end)] : ends.at(-1);
    cues[name] = +(t - from).toFixed(3);
  }
  data[p.id] = {
    file: `voiceover/${p.id}.mp3`,
    duration: +probeDuration(out).toFixed(3),
    cues,
    words: toWords(p.start, p.end, from),
  };
  console.log(`  ${p.id.padEnd(18)} ${from.toFixed(2).padStart(7)}s -> ${to.toFixed(2).padStart(7)}s  (${data[p.id].duration}s)`);
});

writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
console.log(`Listo: ${parts.length} escenas, ${totalDuration.toFixed(1)}s de narración.`);
