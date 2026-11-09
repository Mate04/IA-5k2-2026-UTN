import React from "react";
import { useCurrentFrame } from "remotion";
import { Tex } from "../components/Tex";
import { Reveal } from "../components/ui";
import { prog, useCue } from "../lib/timing";
import { C } from "../theme";

const CARDS = [
  { cue: "r1", title: "Infinitos sucesores", body: "factor de ramificación infinito", tex: "", color: C.a[1] },
  { cue: "r2", title: "Discretizar", body: "grilla de paso δ + gradiente empírico", tex: "", color: C.accent },
  { cue: "r3", title: "Gradiente", body: "cuidar el tamaño de paso α", tex: "\\mathbf{x} \\leftarrow \\mathbf{x} + \\alpha \\nabla f(\\mathbf{x})", color: "#ff4d8d" },
  { cue: "r4", title: "Newton-Raphson", body: "salta al óptimo de una aproximación cuadrática", tex: "\\mathbf{x} \\leftarrow \\mathbf{x} - \\mathbf{H}_f^{-1} \\nabla f(\\mathbf{x})", color: "#ffd166" },
  { cue: "r5", title: "Siguen los óptimos locales", body: "máximos locales, crestas y mesetas", tex: "", color: C.a[0] },
  { cue: "r6", title: "Restricciones", body: "programación lineal ⊂ optimización convexa", tex: "", color: C.good },
];

export const Resumen: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCue();
  return (
    <div
      style={{
        position: "absolute",
        left: 96,
        right: 96,
        top: 210,
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: 28,
      }}
    >
      {CARDS.map((card, i) => (
        <Reveal key={card.cue} p={prog(frame, cue(card.cue) - 4)}>
          <div
            style={{
              height: 320,
              borderRadius: 24,
              padding: "28px 30px",
              background: C.panel,
              border: `2px solid ${card.color}66`,
              display: "flex",
              flexDirection: "column",
              gap: 14,
            }}
          >
            <div
              style={{
                width: 54,
                height: 54,
                borderRadius: 54,
                background: card.color,
                color: C.bg,
                fontSize: 30,
                fontWeight: 800,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {i + 1}
            </div>
            <div style={{ fontSize: 40, fontWeight: 800 }}>{card.title}</div>
            {card.tex ? <Tex tex={card.tex} size={36} /> : null}
            <div style={{ fontSize: 30, color: C.muted, lineHeight: 1.35 }}>{card.body}</div>
          </div>
        </Reveal>
      ))}
    </div>
  );
};
