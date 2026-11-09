import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { RomaniaMap } from "../components/RomaniaMap";
import { Tex } from "../components/Tex";
import { Panel, Reveal } from "../components/ui";
import { fmt, gradient, gradientDescent, objective, START, stateAt } from "../lib/romania";
import { prog, useCue } from "../lib/timing";
import { C } from "../theme";

const ALPHA = 0.02;
const STEPS = 20;
const STATES = gradientDescent(START, ALPHA, STEPS);
const VALUES = STATES.map(objective);

export const Demo: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCue();
  const pasos = cue("pasos");
  const baja = cue("baja");

  // Un paso cada ~0.45 s a partir de "pasos".
  const t = interpolate(frame, [pasos + 20, pasos + 20 + STEPS * 13], [0, STEPS], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const airports = stateAt(STATES, t);
  const k = Math.floor(t);
  const g = gradient(airports);
  const arrowsP = prog(frame, pasos, 15);

  const CW = 640;
  const CH = 260;
  const vmax = VALUES[0];
  const vmin = VALUES[VALUES.length - 1] * 0.9;
  const cx = (i: number) => 20 + (i / STEPS) * (CW - 40);
  const cy = (v: number) => 20 + ((vmax - v) / (vmax - vmin)) * (CH - 40);

  return (
    <>
      <div style={{ position: "absolute", left: 70, top: 200 }}>
        <RomaniaMap
          width={1040}
          airports={airports}
          linksOpacity={0.8}
          colorCities={1}
          namesOpacity={0.55}
          overlay={(proj) => (
            <g>
              {STATES[0].map((_, i) => (
                <polyline
                  key={i}
                  points={STATES.slice(0, k + 1)
                    .map((s) => proj.pt(s[i]))
                    .concat([proj.pt(airports[i])])
                    .map((p) => `${p.x},${p.y}`)
                    .join(" ")}
                  fill="none"
                  stroke={C.a[i]}
                  strokeWidth={3}
                  strokeDasharray="3 7"
                  strokeLinecap="round"
                />
              ))}
              {airports.map((a, i) => {
                const p = proj.pt(a);
                // Flecha de -gradiente (hacia donde baja f), escalada para que se vea.
                const s = ALPHA * proj.s * 2.2;
                return (
                  <line
                    key={`g${i}`}
                    x1={p.x}
                    y1={p.y}
                    x2={p.x - g[i].x * s}
                    y2={p.y + g[i].y * s}
                    stroke="#ffffff"
                    strokeWidth={4}
                    strokeLinecap="round"
                    opacity={arrowsP * 0.9}
                  />
                );
              })}
            </g>
          )}
        />
      </div>

      <div style={{ position: "absolute", left: 1170, top: 205, width: 690, display: "flex", flexDirection: "column", gap: 22 }}>
        <Reveal p={prog(frame, 10)}>
          <Panel style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
            <Tex tex={"\\mathbf{x} \\leftarrow \\mathbf{x} - \\alpha \\, \\nabla f(\\mathbf{x})"} size={46} />
            <span style={{ fontSize: 24, color: C.muted }}>α = {ALPHA} · las líneas blancas apuntan cuesta abajo</span>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, pasos)}>
          <Panel>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 32, fontVariantNumeric: "tabular-nums" }}>
              <span>
                Paso <b>{k}</b>
              </span>
              <span>
                f = <b style={{ color: C.good }}>{fmt(objective(airports))}</b>
              </span>
            </div>
            <svg width={CW} height={CH} style={{ marginTop: 12 }}>
              <line x1={20} y1={CH - 20} x2={CW - 20} y2={CH - 20} stroke={C.faint} strokeWidth={2} />
              <polyline
                points={VALUES.slice(0, k + 1)
                  .map((v, i) => `${cx(i)},${cy(v)}`)
                  .concat([`${cx(t)},${cy(objective(airports))}`])
                  .join(" ")}
                fill="none"
                stroke={C.good}
                strokeWidth={4}
              />
              <circle cx={cx(t)} cy={cy(objective(airports))} r={8} fill={C.good} />
            </svg>
            <div style={{ fontSize: 24, color: C.muted }}>valor de f en cada paso</div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, baja)}>
          <div style={{ fontSize: 30, color: C.muted }}>
            f baja hasta que los aeropuertos <b style={{ color: C.text }}>se acomodan</b>
          </div>
        </Reveal>
      </div>
    </>
  );
};
