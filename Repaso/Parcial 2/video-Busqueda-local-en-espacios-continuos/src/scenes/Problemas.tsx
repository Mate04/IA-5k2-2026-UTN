import React from "react";
import { useCurrentFrame } from "remotion";
import { Badge, Reveal } from "../components/ui";
import { prog, useCue } from "../lib/timing";
import { C } from "../theme";

const sig = (z: number) => 1 / (1 + Math.exp(-z));
const y = (x: number) =>
  0.08 +
  0.55 * Math.exp(-(((x - 0.18) / 0.08) ** 2)) +
  1.0 * Math.exp(-(((x - 0.78) / 0.09) ** 2)) +
  0.3 * (sig((x - 0.36) / 0.012) - sig((x - 0.56) / 0.012));
const dy = (x: number) => (y(x + 1e-4) - y(x - 1e-4)) / 2e-4;

const W = 1560;
const H = 470;
const X = (x: number) => 40 + x * (W - 80);
const Y = (v: number) => 30 + ((1.15 - v) / 1.15) * (H - 60);
const CURVE = Array.from({ length: 301 }, (_, i) => `${i ? "L" : "M"} ${X(i / 300)} ${Y(y(i / 300))}`).join(" ");

// Reinicios aleatorios: cada bolita hace ascenso de colina desde un punto al azar.
const STARTS = [0.05, 0.3, 0.46, 0.64, 0.95];
const CLIMBS = STARTS.map((x0) => {
  const xs = [x0];
  for (let i = 0; i < 120; i++) {
    const x = xs[xs.length - 1];
    xs.push(Math.max(0, Math.min(1, x + 0.0009 * dy(x))));
  }
  return xs;
});

const Stars: React.FC<{ p: number }> = ({ p }) => (
  <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: p }}>
    {Array.from({ length: 260 }).map((_, i) => {
      const r = Math.sin(i * 12.9898) * 43758.5453;
      const r2 = Math.sin(i * 78.233) * 12543.123;
      const fx = r - Math.floor(r);
      const fy = r2 - Math.floor(r2);
      return <circle key={i} cx={fx * 1920} cy={fy * 1080} r={1 + (i % 3)} fill={C.muted} opacity={0.3 + (i % 5) * 0.12} />;
    })}
  </svg>
);

export const Problemas: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCue();
  const problemas = cue("problemas");
  const soluciones = cue("soluciones");
  const perderse = cue("perderse");

  const climbT = Math.max(0, Math.min(1, (frame - soluciones - 15) / 90));
  const lost = prog(frame, perderse, 30);

  const labels = [
    { x: 0.78, text: "máximo global", color: C.good, dyPx: -30 },
    { x: 0.18, text: "máximo local", color: C.a[2], dyPx: -30 },
    { x: 0.46, text: "meseta", color: C.a[1], dyPx: -26 },
  ];

  return (
    <>
      <div style={{ position: "absolute", left: 180, top: 215, opacity: 1 - 0.85 * lost, scale: 1 - 0.25 * lost }}>
        <svg width={W} height={H}>
          <path d={CURVE} fill="none" stroke={C.muted} strokeWidth={5} />
          {labels.map((l, i) => (
            <g key={l.text} opacity={prog(frame, problemas + i * 20)}>
              <circle cx={X(l.x)} cy={Y(y(l.x))} r={10} fill={l.color} />
              <text x={X(l.x)} y={Y(y(l.x)) + l.dyPx} textAnchor="middle" fill={l.color} fontSize={32} fontWeight={700}>
                {l.text}
              </text>
            </g>
          ))}
          {CLIMBS.map((xs, i) => {
            const x = xs[Math.floor(climbT * (xs.length - 1))];
            const o = prog(frame, soluciones + i * 4, 10);
            return (
              <g key={i} opacity={o}>
                <circle cx={X(xs[0])} cy={Y(y(xs[0]))} r={6} fill={C.text} opacity={0.5} />
                <circle cx={X(x)} cy={Y(y(x)) - 16} r={14} fill="#ff4d8d" stroke={C.bg} strokeWidth={3} />
              </g>
            );
          })}
        </svg>
      </div>

      <div style={{ position: "absolute", left: 0, right: 0, top: 730, display: "flex", justifyContent: "center", gap: 24, opacity: 1 - lost }}>
        <Reveal p={prog(frame, problemas)}>
          <Badge color={C.a[2]}>Máximos locales</Badge>
        </Reveal>
        <Reveal p={prog(frame, problemas + 20)}>
          <Badge color={C.a[2]}>Crestas</Badge>
        </Reveal>
        <Reveal p={prog(frame, problemas + 40)}>
          <Badge color={C.a[2]}>Mesetas</Badge>
        </Reveal>
        <Reveal p={prog(frame, soluciones)}>
          <Badge color={C.good}>Reinicios aleatorios</Badge>
        </Reveal>
        <Reveal p={prog(frame, soluciones + 30)}>
          <Badge color={C.good}>Recocido simulado</Badge>
        </Reveal>
      </div>

      <Stars p={lost} />
      <Reveal
        p={prog(frame, perderse + 20)}
        style={{ position: "absolute", left: 0, right: 0, top: 420, textAlign: "center" }}
      >
        <div style={{ fontSize: 64, fontWeight: 800 }}>Muchas dimensiones = un espacio enorme</div>
        <div style={{ fontSize: 40, color: C.muted, marginTop: 12 }}>es muy fácil perderse</div>
      </Reveal>
    </>
  );
};
