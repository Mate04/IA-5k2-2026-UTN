import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { AirportMarker, RomaniaMap } from "../components/RomaniaMap";
import { Tex } from "../components/Tex";
import { Arrow, Badge, Panel, Reveal } from "../components/ui";
import { fmt, objective, P, START } from "../lib/romania";
import { lerp, prog, useCue } from "../lib/timing";
import { C } from "../theme";

const DELTA = 30;
const snap = (v: number) => Math.round(v / DELTA) * DELTA;
const SNAPPED: P[] = START.map((a) => ({ x: snap(a.x), y: snap(a.y) }));
const MOVES = [
  { dx: 1, dy: 0 },
  { dx: -1, dy: 0 },
  { dx: 0, dy: 1 },
  { dx: 0, dy: -1 },
];
// Direcciones "al azar" (fijas para que el video sea reproducible).
const ANGLES = [0.6, 2.4, 4.1, 5.5, 1.2];

export const Discretizar: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCue();
  const grilla = cue("grilla");
  const doce = cue("doce");
  const azar = cue("azar");
  const empirico = cue("empirico");
  const achicar = cue("achicar");

  const snapP = prog(frame, grilla + 25, 25);
  const airports = START.map((a, i) => ({ x: lerp(a.x, SNAPPED[i].x, snapP), y: lerp(a.y, SNAPPED[i].y, snapP) }));

  // El espaciado de la grilla se achica: delta -> delta/2 -> delta/4.
  const shrink = interpolate(frame, [achicar + 10, achicar + 40, achicar + 80, achicar + 110], [1, 0.5, 0.5, 0.25], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const delta = DELTA * shrink;
  const deltaLabel = shrink > 0.75 ? "δ" : shrink > 0.375 ? "δ/2" : "δ/4";

  const succP = prog(frame, doce, 12) * (1 - prog(frame, azar - 10, 12));
  const randomP = prog(frame, azar, 12) * (1 - prog(frame, achicar, 12));

  // Muestreo al azar alrededor de A1.
  const k = Math.min(ANGLES.length - 1, Math.max(0, Math.floor((frame - azar) / (0.9 * fps))));
  const ang = ANGLES[k];
  const sampleP = ((frame - azar) % (0.9 * fps)) / (0.9 * fps);
  const a1 = SNAPPED[0];
  const sampled: P = { x: a1.x + Math.cos(ang) * DELTA, y: a1.y + Math.sin(ang) * DELTA };
  const fNow = objective(SNAPPED);
  const fNext = objective([sampled, SNAPPED[1], SNAPPED[2]]);

  return (
    <>
      <div style={{ position: "absolute", left: 70, top: 205 }}>
        <RomaniaMap
          width={1000}
          airports={airports}
          linksOpacity={0.35}
          colorCities={1}
          namesOpacity={0.6}
          roadsOpacity={0.15}
          underlay={(proj) => {
            const lines = [];
            const o = prog(frame, grilla, 20);
            for (let x = 30; x <= 630; x += delta) {
              const a = proj.pt({ x, y: 240 });
              const b = proj.pt({ x, y: 615 });
              lines.push(<line key={`x${x}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={C.accent} strokeWidth={1} opacity={0.35 * o} />);
            }
            for (let y = 240; y <= 615; y += delta) {
              const a = proj.pt({ x: 45, y });
              const b = proj.pt({ x: 610, y });
              lines.push(<line key={`y${y}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={C.accent} strokeWidth={1} opacity={0.35 * o} />);
            }
            return <g>{lines}</g>;
          }}
          overlay={(proj) => (
            <g>
              {succP > 0 &&
                SNAPPED.flatMap((a, i) =>
                  MOVES.map((m, j) => {
                    const q = Math.max(0, Math.min(1, succP * 3 - (i * 4 + j) * 0.12));
                    const from = proj.pt(a);
                    const to = proj.pt({ x: a.x + m.dx * DELTA, y: a.y + m.dy * DELTA });
                    return (
                      <g key={`${i}-${j}`} opacity={q}>
                        <Arrow x1={from.x} y1={from.y} x2={to.x} y2={to.y} color={C.a[i]} width={3} head={12} p={q} />
                        <circle cx={to.x} cy={to.y} r={9} fill="none" stroke={C.a[i]} strokeWidth={3} />
                      </g>
                    );
                  }),
                )}
              {randomP > 0 && (
                <g opacity={randomP}>
                  <circle
                    cx={proj.pt(a1).x}
                    cy={proj.pt(a1).y}
                    r={DELTA * proj.s}
                    fill="none"
                    stroke={C.text}
                    strokeWidth={2}
                    strokeDasharray="6 6"
                  />
                  <Arrow
                    x1={proj.pt(a1).x}
                    y1={proj.pt(a1).y}
                    x2={proj.pt(sampled).x}
                    y2={proj.pt(sampled).y}
                    color={C.text}
                    width={4}
                    p={Math.min(1, sampleP * 3)}
                  />
                  <AirportMarker x={proj.pt(sampled).x} y={proj.pt(sampled).y} i={0} ghost opacity={Math.min(1, sampleP * 3)} />
                </g>
              )}
            </g>
          )}
        />
      </div>

      <div style={{ position: "absolute", left: 1130, top: 200, width: 720, display: "flex", flexDirection: "column", gap: 16 }}>
        <Reveal p={prog(frame, grilla)}>
          <Panel style={{ padding: "18px 28px" }}>
            <div style={{ fontSize: 34, fontWeight: 700 }}>Cuadrícula con espaciado δ</div>
            <div style={{ fontSize: 28, color: C.muted, marginTop: 6 }}>
              solo se permiten los cruces · espaciado = <b style={{ color: C.text }}>{deltaLabel}</b>
            </div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, doce)}>
          <Panel style={{ padding: "18px 28px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <Tex tex={"6 \\text{ variables} \\times 2\\ (\\pm\\delta) = 12"} size={38} />
              <span style={{ fontSize: 28, color: C.muted }}>sucesores</span>
            </div>
            <div style={{ fontSize: 26, color: C.muted, marginTop: 6 }}>→ sirve cualquier búsqueda local</div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, azar)}>
          <Panel style={{ padding: "18px 28px" }}>
            <div style={{ fontSize: 30 }}>
              <b>O muestrear al azar:</b> <span style={{ color: C.muted }}>mover δ en una dirección aleatoria</span>
            </div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, empirico)}>
          <Panel style={{ borderColor: `${C.good}88`, padding: "18px 28px" }}>
            <div style={{ fontSize: 30 }}>
              <b>Gradiente empírico:</b> <span style={{ color: C.muted }}>comparar f en dos puntos cercanos</span>
            </div>
            <div style={{ fontSize: 30, marginTop: 8, fontVariantNumeric: "tabular-nums" }}>
              f(x) = {fmt(fNow)} → f(x′) = {fmt(fNext)}{" "}
              <b style={{ color: fNext < fNow ? C.good : C.bad }}>{fNext < fNow ? "mejora" : "empeora"}</b>
            </div>
            <div style={{ fontSize: 26, color: C.muted, marginTop: 6 }}>= ascenso de colina más empinada, discretizado</div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, achicar + 40)}>
          <Badge color={C.a[2]} style={{ fontSize: 27 }}>
            δ más chico → más precisión, pero sin garantía de óptimo global
          </Badge>
        </Reveal>
      </div>
    </>
  );
};
