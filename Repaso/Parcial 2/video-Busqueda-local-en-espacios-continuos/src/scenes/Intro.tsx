import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Panel, Reveal } from "../components/ui";
import { lerp, prog, useCue } from "../lib/timing";
import { C } from "../theme";

const Board: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cell = 46;
  // La reina salta de casilla en casilla: estados discretos.
  const path = [5, 2, 6, 1, 4];
  const k = Math.max(0, Math.floor((frame - start - 0.6 * fps) / (1.1 * fps)));
  const idx = Math.min(path.length - 1, Math.max(0, k));
  const hop = (frame - start - 0.6 * fps) / (1.1 * fps) - k;
  const lift = k > 0 && k < path.length && hop < 0.25 ? Math.sin((hop / 0.25) * Math.PI) * 14 : 0;
  return (
    <svg width={cell * 8} height={cell * 8}>
      {Array.from({ length: 64 }).map((_, i) => {
        const r = Math.floor(i / 8);
        const c = i % 8;
        return (
          <rect key={i} x={c * cell} y={r * cell} width={cell} height={cell} fill={(r + c) % 2 ? "#2a3352" : "#3b4670"} />
        );
      })}
      {path.slice(0, idx + 1).map((row, i) =>
        i < idx ? (
          <circle key={i} cx={3 * cell + cell / 2} cy={row * cell + cell / 2} r={6} fill={C.accent} opacity={0.5} />
        ) : null,
      )}
      <text
        x={3 * cell + cell / 2}
        y={path[idx] * cell + cell / 2 - lift}
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={40}
        fill="#ffd166"
        style={{ fontFamily: "Segoe UI Symbol, DejaVu Sans, serif" }}
      >
        ♛
      </text>
    </svg>
  );
};

const Continuous: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const w = 460;
  const h = 300;
  const f = (x: number) => 150 - 70 * Math.sin(x * 0.018) - 40 * Math.sin(x * 0.041 + 1);
  const d = Array.from({ length: 93 }, (_, i) => `${i ? "L" : "M"} ${i * 5} ${f(i * 5)}`).join(" ");
  const t = (frame - start) / fps;
  const x = 230 + 180 * Math.sin(t * 0.9);
  return (
    <div style={{ position: "relative" }}>
      <svg width={w} height={h}>
        <path d={d} fill="none" stroke={C.a[1]} strokeWidth={5} />
        <line x1={x} y1={f(x)} x2={x} y2={h} stroke={C.muted} strokeDasharray="6 6" strokeWidth={2} />
        <circle cx={x} cy={f(x)} r={13} fill="#ffd166" stroke={C.bg} strokeWidth={3} />
      </svg>
      <div style={{ fontSize: 30, color: C.muted, textAlign: "center", fontVariantNumeric: "tabular-nums" }}>
        x = {(x / 100).toFixed(5)}…
      </div>
    </div>
  );
};

export const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCue();
  const reina = cue("reina");
  const continuo = cue("continuo");
  const up = prog(frame, reina - 10, 24);

  return (
    <>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: lerp(330, 110, up),
          textAlign: "center",
          opacity: interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        <div style={{ fontSize: 30, fontWeight: 600, color: C.accent, letterSpacing: 4, textTransform: "uppercase" }}>
          Sección 4.2
        </div>
        <div style={{ fontSize: lerp(104, 68, up), fontWeight: 800, marginTop: 10, lineHeight: 1.05 }}>
          Búsqueda local en espacios continuos
        </div>
        <div style={{ fontSize: lerp(36, 28, up), color: C.muted, marginTop: 18 }}>
          Inteligencia Artificial: un enfoque moderno · Russell &amp; Norvig
        </div>
      </div>

      <div style={{ position: "absolute", top: 390, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 70 }}>
        <Reveal p={prog(frame, reina)}>
          <Panel style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18, width: 560 }}>
            <div style={{ fontSize: 38, fontWeight: 700 }}>Hasta ahora: discreto</div>
            <Board start={reina} />
            <div style={{ fontSize: 28, color: C.muted }}>Saltos entre casillas</div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, continuo)}>
          <Panel style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 18, width: 560 }}>
            <div style={{ fontSize: 38, fontWeight: 700 }}>Mundo real: continuo</div>
            <Continuous start={continuo} />
            <div style={{ fontSize: 28, color: C.muted }}>Cualquier valor real</div>
          </Panel>
        </Reveal>
      </div>
    </>
  );
};
