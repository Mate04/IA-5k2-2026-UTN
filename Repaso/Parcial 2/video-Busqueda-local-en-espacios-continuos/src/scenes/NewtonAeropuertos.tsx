import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { AirportMarker, RomaniaMap } from "../components/RomaniaMap";
import { Tex } from "../components/Tex";
import { Arrow, Badge, Panel, Reveal } from "../components/ui";
import { centroids, countPerAirport, fmt, newtonSteps, objective, START, stateAt } from "../lib/romania";
import { prog, useCue } from "../lib/timing";
import { C } from "../theme";

const STATES = newtonSteps(START, 4);

const Hessian: React.FC<{ counts: number[]; diagP: number }> = ({ counts, diagP }) => {
  const cell = 74;
  return (
    <div style={{ display: "grid", gridTemplateColumns: `repeat(6, ${cell}px)`, gap: 6 }}>
      {Array.from({ length: 36 }).map((_, k) => {
        const r = Math.floor(k / 6);
        const c = k % 6;
        const diag = r === c;
        const airport = Math.floor(r / 2);
        return (
          <div
            key={k}
            style={{
              height: cell,
              borderRadius: 12,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: diag ? 30 : 26,
              fontWeight: diag ? 800 : 500,
              fontVariantNumeric: "tabular-nums",
              background: diag ? `${C.a[airport]}${diagP > 0.5 ? "33" : "14"}` : "rgba(255,255,255,0.04)",
              border: `2px solid ${diag ? C.a[airport] : "transparent"}`,
              color: diag ? C.text : C.faint,
              opacity: diag ? 1 : 1 - 0.45 * diagP,
            }}
          >
            {diag ? (diagP > 0.5 ? 2 * counts[airport] : "?") : "0"}
          </div>
        );
      })}
    </div>
  );
};

export const NewtonAeropuertos: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCue();
  const diagonal = cue("diagonal");
  const centroide = cue("centroide");
  const repetir = cue("repetir");
  const costo = cue("costo");

  // Paso 1 en "centroide"; pasos 2..4 en "repetir".
  const t = interpolate(frame, [centroide + 30, centroide + 70, repetir + 10, repetir + 100], [0, 1, 1, 4], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const airports = stateAt(STATES, t);
  const k = Math.min(STATES.length - 1, Math.floor(t + 0.001));
  const counts = countPerAirport(STATES[Math.min(k, STATES.length - 1)]);
  const targets = centroids(STATES[Math.min(k, STATES.length - 1)]);
  const showTargets = prog(frame, centroide) * (1 - prog(frame, costo));

  const matrixP = 1 - prog(frame, costo - 10, 15);
  const costP = prog(frame, costo, 15);

  return (
    <>
      <div style={{ position: "absolute", left: 90, top: 205, width: 700 }}>
        {matrixP > 0 && (
          <div style={{ opacity: matrixP }}>
            <Panel style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
              <div style={{ fontSize: 32, fontWeight: 700, alignSelf: "flex-start" }}>
                Hessiana <Tex tex={"\\mathbf{H}_f"} size={34} /> (6 × 6)
              </div>
              <Hessian counts={counts} diagP={prog(frame, diagonal, 20)} />
              <Reveal p={prog(frame, diagonal + 30)}>
                <div style={{ fontSize: 26, color: C.muted, textAlign: "center" }}>
                  fuera de la diagonal: 0 · en la diagonal: <Tex tex={"2\\,|C_i|"} size={30} color={C.text} />
                </div>
              </Reveal>
            </Panel>
          </div>
        )}
        {costP > 0 && (
          <div style={{ opacity: costP, position: "absolute", top: 0, left: 0, width: 700, display: "flex", flexDirection: "column", gap: 20 }}>
            <Panel>
              <div style={{ fontSize: 34, fontWeight: 700 }}>El costo</div>
              <div style={{ fontSize: 28, color: C.muted, marginTop: 6 }}>
                con <i>n</i> variables, la Hessiana tiene <Tex tex={"n^2"} size={32} color={C.text} /> entradas
              </div>
              <div style={{ marginTop: 18, display: "flex", flexDirection: "column", gap: 12, fontSize: 32, fontVariantNumeric: "tabular-nums" }}>
                {[
                  ["n = 6", "36"],
                  ["n = 1.000", "1.000.000"],
                  ["n = 1.000.000", "10¹²"],
                ].map(([n, v], i) => (
                  <Reveal key={n} p={prog(frame, costo + 40 + i * 30)}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span>{n}</span>
                      <b style={{ color: i === 2 ? C.bad : C.text }}>{v} entradas</b>
                    </div>
                  </Reveal>
                ))}
              </div>
              <Reveal p={prog(frame, costo + 150)}>
                <div style={{ fontSize: 28, color: C.muted, marginTop: 16 }}>… y además hay que invertirla</div>
              </Reveal>
            </Panel>
            <Reveal p={prog(frame, costo + 240)}>
              <Badge color={C.good} style={{ fontSize: 28 }}>
                → versiones aproximadas de Newton-Raphson
              </Badge>
            </Reveal>
          </div>
        )}
      </div>

      <div style={{ position: "absolute", left: 870, top: 210 }}>
        <RomaniaMap
          width={980}
          airports={airports}
          linksOpacity={0.8}
          colorCities={1}
          namesOpacity={0.5}
          overlay={(proj) => (
            <g opacity={showTargets}>
              {targets.map((c, i) => {
                const p = proj.pt(c);
                const a = proj.pt(airports[i]);
                return (
                  <g key={i}>
                    <Arrow x1={a.x} y1={a.y} x2={p.x} y2={p.y} color={C.a[i]} width={3} head={14} dash="6 6" opacity={0.9} />
                    <AirportMarker x={p.x} y={p.y} i={i} ghost />
                  </g>
                );
              })}
            </g>
          )}
        />
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8, fontSize: 28, fontVariantNumeric: "tabular-nums" }}>
          <Reveal p={prog(frame, centroide)}>
            <span style={{ color: C.muted }}>
              <span style={{ color: C.text, fontWeight: 700 }}>Punteado</span> = centroide de <Tex tex={"C_i"} size={30} /> · paso {k}
            </span>
          </Reveal>
          <Reveal p={prog(frame, centroide)}>
            <span>
              f = <b style={{ color: C.good }}>{fmt(objective(airports))}</b>
            </span>
          </Reveal>
        </div>
      </div>
    </>
  );
};
