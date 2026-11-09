import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { LEAD_IN, Word } from "../lib/timing";
import { C, FONT } from "../theme";

// Agrupa las palabras en frases cortas para mostrarlas de a una.
const chunk = (words: Word[]) => {
  const out: Word[][] = [];
  let cur: Word[] = [];
  let len = 0;
  for (const w of words) {
    cur.push(w);
    len += w.text.length + 1;
    const strong = /[.?!:;]$/.test(w.text);
    const soft = /,$/.test(w.text);
    if (strong || (soft && len > 38) || len > 66) {
      out.push(cur);
      cur = [];
      len = 0;
    }
  }
  if (cur.length) out.push(cur);
  return out;
};

export const Subtitles: React.FC<{ words: Word[] }> = ({ words }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const chunks = useMemo(() => chunk(words), [words]);
  const t = frame / fps - LEAD_IN;

  // La frase activa es la última que ya empezó; se oculta si hubo un silencio largo.
  let active = -1;
  chunks.forEach((c, i) => {
    if (c[0].start <= t + 0.05) active = i;
  });
  if (active < 0) return null;
  const current = chunks[active];
  if (t > current[current.length - 1].end + 1.2) return null;

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 44,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          maxWidth: 1500,
          padding: "12px 28px",
          borderRadius: 16,
          background: "rgba(5,8,18,0.72)",
          border: `1px solid ${C.panelBorder}`,
          fontFamily: FONT,
          fontSize: 38,
          fontWeight: 500,
          lineHeight: 1.3,
          textAlign: "center",
        }}
      >
        {current.map((w, i) => (
          <span key={i} style={{ color: w.start <= t + 0.03 ? C.text : "rgba(238,242,255,0.45)" }}>
            {w.text}
            {i < current.length - 1 ? " " : ""}
          </span>
        ))}
      </div>
    </div>
  );
};
