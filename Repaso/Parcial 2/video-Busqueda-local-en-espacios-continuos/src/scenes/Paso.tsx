import React from "react";
import { useCurrentFrame } from "remotion";
import { Tex } from "../components/Tex";
import { Arrow, Badge, Panel, Reveal } from "../components/ui";
import { prog, useCue } from "../lib/timing";
import { C } from "../theme";

// Colina 1D para comparar tamaños de paso: f(x) = 1 - 2.2 (x - 0.55)^2.
const f = (x: number) => 1 - 2.2 * (x - 0.55) ** 2;
const PW = 780;
const PH = 360;
const px = (x: number) => 30 + x * (PW - 60);
const py = (y: number) => 20 + (1.05 - y) / 0.8 * (PH - 40);
const curve = Array.from({ length: 101 }, (_, i) => `${i ? "L" : "M"} ${px(i / 100)} ${py(f(i / 100))}`).join(" ");

// Error respecto del máximo multiplicado por `factor` en cada paso.
const steps = (factor: number, n: number) => {
  const xs = [0.1];
  for (let i = 0; i < n; i++) xs.push(0.55 + (xs[xs.length - 1] - 0.55) * factor);
  return xs;
};
const SMALL = steps(0.93, 40);
const BIG = steps(-0.9, 40);

const StepPlot: React.FC<{ xs: number[]; shown: number; color: string }> = ({ xs, shown, color }) => {
  const n = Math.max(0, Math.min(xs.length - 1, Math.floor(shown)));
  const pts = xs.slice(0, n + 1);
  return (
    <svg width={PW} height={PH}>
      <line x1={px(0.55)} y1={py(1)} x2={px(0.55)} y2={PH} stroke={C.good} strokeDasharray="6 6" strokeWidth={2} />
      <text x={px(0.55) + 10} y={py(1) - 2} fill={C.good} fontSize={24} fontWeight={700}>
        máximo
      </text>
      <path d={curve} fill="none" stroke={C.muted} strokeWidth={4} />
      {pts.slice(1).map((x, i) => (
        <line key={i} x1={px(pts[i])} y1={py(f(pts[i]))} x2={px(x)} y2={py(f(x))} stroke={color} strokeWidth={3} opacity={0.8} />
      ))}
      {pts.map((x, i) => (
        <circle key={i} cx={px(x)} cy={py(f(x))} r={i === n ? 14 : 5} fill={i === n ? color : C.text} opacity={i === n ? 1 : 0.6} />
      ))}
    </svg>
  );
};

// Búsqueda lineal: f a lo largo de la dirección del gradiente.
const phi = (t: number) => 1 - 3 * (t - 0.33) ** 2;
const LW = 1200;
const LH = 380;
const lx = (t: number) => 60 + (t / 0.6) * (LW - 120);
const ly = (y: number) => 30 + (1.03 - y) / 0.45 * (LH - 80);
const lcurve = Array.from({ length: 121 }, (_, i) => `${i ? "L" : "M"} ${lx((i / 120) * 0.6)} ${ly(phi((i / 120) * 0.6))}`).join(" ");
const TRIES = [
  { t: 0.06, label: "α" },
  { t: 0.12, label: "2α" },
  { t: 0.24, label: "4α" },
  { t: 0.48, label: "8α" },
];


// Ilustración chica: un paso sobre una colina (maximizar) o un valle (minimizar).
const MiniStep: React.FC<{ valley?: boolean; p: number }> = ({ valley = false, p }) => {
  const w = 520;
  const hh = 230;
  const fy = (x: number) => (valley ? 2.2 * (x - 0.55) ** 2 : 1 - 2.2 * (x - 0.55) ** 2);
  const X = (x: number) => 30 + x * (w - 60);
  const Y = (v: number) => (valley ? 30 + (1 - (v + 0.05) / 0.75) * (hh - 60) : 20 + (1.05 - v) / 0.75 * (hh - 50));
  const d = Array.from({ length: 61 }, (_, i) => `${i ? "L" : "M"} ${X(i / 60)} ${Y(fy(i / 60))}`).join(" ");
  const x0 = 0.18;
  const x1 = 0.34;
  const col = valley ? C.good : "#ff4d8d";
  return (
    <svg width={w} height={hh}>
      <path d={d} fill="none" stroke={C.muted} strokeWidth={4} />
      <Arrow x1={X(x0)} y1={Y(fy(x0))} x2={X(x1)} y2={Y(fy(x1))} color={col} width={5} head={18} p={p} />
      <circle cx={X(x0)} cy={Y(fy(x0))} r={12} fill={C.text} />
      <text x={X(x1) + 18} y={Y(fy(x1)) + (valley ? 30 : -6)} fill={col} fontSize={28} fontWeight={700}>
        {valley ? "baja" : "sube"}
      </text>
    </svg>
  );
};

export const Paso: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCue();
  const regla = cue("regla");
  const signo = cue("signo");
  const alfa = cue("alfa");
  const chico = cue("chico");
  const grande = cue("grande");
  const lineal = cue("lineal");
  const empeora = cue("empeora");

  const plotsP = prog(frame, chico - 8) * (1 - prog(frame, lineal - 12, 12));
  const lineP = prog(frame, lineal, 15);
  const tryAt = [lineal + 75, lineal + 140, lineal + 205, empeora];
  const alphaGlow = prog(frame, alfa) * (1 - prog(frame, chico + 30));

  return (
    <>
      <div style={{ position: "absolute", left: 0, right: 0, top: 190, display: "flex", justifyContent: "center" }}>
        <Reveal p={prog(frame, regla - 6)}>
          <Panel style={{ display: "flex", gap: 60, alignItems: "center", padding: "24px 44px" }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
              <Tex tex={"\\mathbf{x} \\leftarrow \\mathbf{x} + \\boxed{\\alpha} \\, \\nabla f(\\mathbf{x})"} size={52} />
              <span style={{ fontSize: 26, color: C.muted }}>maximizar: un paso hacia arriba</span>
            </div>
            <div style={{ opacity: prog(frame, signo), display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
              <Tex tex={"\\mathbf{x} \\leftarrow \\mathbf{x} \\,\\color{#2ee6a6}{-}\\, \\alpha \\, \\nabla f(\\mathbf{x})"} size={52} />
              <span style={{ fontSize: 26, color: C.good }}>minimizar (aeropuertos): descenso por gradiente</span>
            </div>
          </Panel>
        </Reveal>
      </div>
      <Reveal p={alphaGlow} style={{ position: "absolute", top: 395, left: 0, right: 0, display: "flex", justifyContent: "center", zIndex: 2 }}>
        <Badge color={C.a[2]}>α = tamaño de paso</Badge>
      </Reveal>

      {frame < chico && (
        <div
          style={{
            position: "absolute",
            top: 480,
            left: 0,
            right: 0,
            display: "flex",
            justifyContent: "center",
            gap: 80,
            opacity: 1 - prog(frame, chico - 15, 12),
          }}
        >
          <Reveal p={prog(frame, regla + 20)}>
            <MiniStep p={prog(frame, regla + 40, 25)} />
          </Reveal>
          <Reveal p={prog(frame, signo + 20)}>
            <MiniStep valley p={prog(frame, signo + 40, 25)} />
          </Reveal>
        </div>
      )}

      {plotsP > 0 && (
        <div style={{ position: "absolute", top: 440, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 50, opacity: plotsP }}>
          <Panel style={{ padding: "18px 20px" }}>
            <div style={{ fontSize: 32, fontWeight: 700, marginLeft: 12 }}>
              α muy chico <span style={{ color: C.muted, fontWeight: 500 }}>· pasos: {Math.max(0, Math.min(40, Math.floor((frame - chico) / 5)))}</span>
            </div>
            <StepPlot xs={SMALL} shown={(frame - chico) / 5} color={C.a[1]} />
            <div style={{ fontSize: 26, color: C.muted, marginLeft: 12 }}>avanza de a poquito: muchísimos pasos</div>
          </Panel>
          <Panel style={{ padding: "18px 20px", opacity: prog(frame, grande - 6) }}>
            <div style={{ fontSize: 32, fontWeight: 700, marginLeft: 12 }}>α muy grande</div>
            <StepPlot xs={BIG} shown={(frame - grande) / 9} color={C.a[0]} />
            <div style={{ fontSize: 26, color: C.muted, marginLeft: 12 }}>se pasa del máximo y rebota</div>
          </Panel>
        </div>
      )}

      {lineP > 0 && (
        <div style={{ position: "absolute", top: 440, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: lineP }}>
          <Panel style={{ padding: "18px 26px", display: "flex", gap: 20 }}>
            <div>
              <div style={{ fontSize: 32, fontWeight: 700 }}>
                Búsqueda lineal <span style={{ color: C.muted, fontWeight: 500 }}>(el libro: “búsqueda online”)</span>
              </div>
              <svg width={LW} height={LH}>
                <line x1={lx(0)} y1={LH - 40} x2={lx(0.6)} y2={LH - 40} stroke={C.faint} strokeWidth={2} />
                <text x={lx(0.6)} y={LH - 8} textAnchor="end" fill={C.muted} fontSize={22}>
                  distancia en la dirección del gradiente →
                </text>
                <path d={lcurve} fill="none" stroke={C.muted} strokeWidth={4} />
                <circle cx={lx(0)} cy={ly(phi(0))} r={13} fill={C.text} />
                <text x={lx(0) - 10} y={ly(phi(0)) - 26} fill={C.text} fontSize={24}>
                  x actual
                </text>
                {TRIES.map((tr, i) => {
                  const p = prog(frame, tryAt[i], 12);
                  const bad = i === 3 && frame >= empeora + 8;
                  const best = i === 2 && frame >= empeora + 40;
                  const col = bad ? C.bad : best ? C.good : C.a[2];
                  return (
                    <g key={tr.label} opacity={p}>
                      <line x1={lx(tr.t)} y1={ly(phi(tr.t))} x2={lx(tr.t)} y2={LH - 40} stroke={col} strokeDasharray="5 6" strokeWidth={2} />
                      <circle cx={lx(tr.t)} cy={ly(phi(tr.t))} r={best ? 16 : 12} fill={col} />
                      <text x={lx(tr.t)} y={LH - 48} textAnchor="middle" fill={C.text} fontSize={26} fontWeight={700}>
                        {tr.label}
                      </text>
                    </g>
                  );
                })}
                <g opacity={prog(frame, empeora + 8)}>
                  <text x={lx(0.48)} y={ly(phi(0.48)) - 28} textAnchor="middle" fill={C.bad} fontSize={26} fontWeight={700}>
                    f empeoró: frenar
                  </text>
                </g>
                <g opacity={prog(frame, empeora + 40)}>
                  <text x={lx(0.24) - 24} y={ly(phi(0.24)) - 24} textAnchor="end" fill={C.good} fontSize={26} fontWeight={700}>
                    nuevo estado actual
                  </text>
                </g>
                <g opacity={prog(frame, empeora + 100)}>
                  <Arrow
                    x1={lx(0.24)}
                    y1={ly(phi(0.24))}
                    x2={lx(0.24) + 130}
                    y2={ly(phi(0.24)) + 95}
                    color={C.accent}
                    width={5}
                    p={prog(frame, empeora + 100, 20)}
                  />
                  <text x={lx(0.24) + 145} y={ly(phi(0.24)) + 112} fill={C.accent} fontSize={26} fontWeight={700}>
                    nueva dirección
                  </text>
                </g>
              </svg>
            </div>
          </Panel>
        </div>
      )}
    </>
  );
};
