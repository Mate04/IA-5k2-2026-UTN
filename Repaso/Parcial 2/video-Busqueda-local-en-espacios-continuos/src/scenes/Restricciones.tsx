import React from "react";
import { useCurrentFrame } from "remotion";
import { RomaniaMap } from "../components/RomaniaMap";
import { Tex } from "../components/Tex";
import { Badge, Check, Panel, Reveal } from "../components/ui";
import { P } from "../lib/romania";
import { lerp, prog, useCue } from "../lib/timing";
import { C } from "../theme";

// Programación lineal de ejemplo: max 3x1 + 2x2 con x1 + 2x2 <= 8, 3x1 + x2 <= 9, x2 <= 3.5, x >= 0.
const PW = 760;
const PH = 640;
const MAXV = 4.6;
const sx = (x: number) => 70 + (x / MAXV) * (PW - 110);
const sy = (y: number) => PH - 60 - (y / MAXV) * (PH - 110);
const POLY = [
  [0, 0],
  [3, 0],
  [2, 3],
  [1, 3.5],
  [0, 3.5],
];
const LINES = [
  { a: [0, 4], b: [4.6, 1.7] },
  { a: [1.53, 4.6], b: [3, 0] },
  { a: [0, 3.5], b: [4.6, 3.5] },
];

const LPPlot: React.FC<{ linesP: number[]; fillP: number; sweep: number; starP: number }> = ({ linesP, fillP, sweep, starP }) => {
  // Recta de nivel 3x1 + 2x2 = c, recortada al gráfico.
  const c = sweep * 12;
  const p1 = { x: 0, y: c / 2 };
  const p2 = { x: c / 3, y: 0 };
  return (
    <svg width={PW} height={PH}>
      <line x1={sx(0)} y1={sy(0)} x2={sx(MAXV)} y2={sy(0)} stroke={C.muted} strokeWidth={2} />
      <line x1={sx(0)} y1={sy(0)} x2={sx(0)} y2={sy(MAXV)} stroke={C.muted} strokeWidth={2} />
      <text x={sx(MAXV)} y={sy(0) + 40} textAnchor="end" fill={C.muted} fontSize={28}>
        x<tspan dy={8} fontSize={20}>1</tspan>
      </text>
      <text x={sx(0) - 20} y={sy(MAXV) + 10} textAnchor="end" fill={C.muted} fontSize={28}>
        x<tspan dy={8} fontSize={20}>2</tspan>
      </text>
      <polygon
        points={POLY.map(([x, y]) => `${sx(x)},${sy(y)}`).join(" ")}
        fill={C.good}
        fillOpacity={0.22 * fillP}
        stroke={C.good}
        strokeWidth={3}
        strokeOpacity={fillP}
      />
      {LINES.map((l, i) => (
        <g key={i} opacity={linesP[i]}>
          <line x1={sx(l.a[0])} y1={sy(l.a[1])} x2={sx(l.b[0])} y2={sy(l.b[1])} stroke={C.a[1]} strokeWidth={3} />
        </g>
      ))}
      {sweep > 0 && (
        <g>
          <clipPath id="plotClip">
            <rect x={sx(0)} y={sy(MAXV)} width={sx(MAXV) - sx(0)} height={sy(0) - sy(MAXV)} />
          </clipPath>
          <line
            x1={sx(p1.x - 2)}
            y1={sy(p1.y + 3)}
            x2={sx(p2.x + 2)}
            y2={sy(p2.y - 3)}
            stroke={C.a[2]}
            strokeWidth={4}
            strokeDasharray="12 8"
            clipPath="url(#plotClip)"
          />
        </g>
      )}
      {POLY.map(([x, y], i) => (
        <circle key={i} cx={sx(x)} cy={sy(y)} r={8} fill={C.good} opacity={fillP} />
      ))}
      <g opacity={starP}>
        <circle cx={sx(2)} cy={sy(3)} r={18 + 6 * starP} fill="none" stroke={C.a[2]} strokeWidth={4} />
        <circle cx={sx(2)} cy={sy(3)} r={10} fill={C.a[2]} />
        <text x={sx(2) + 30} y={sy(3) - 26} fill={C.a[2]} fontSize={30} fontWeight={800}>
          óptimo (vértice)
        </text>
      </g>
    </svg>
  );
};

const Shape: React.FC<{ convex: boolean }> = ({ convex }) => {
  const pts = convex ? "30,140 60,40 160,25 210,110 140,175" : "30,40 210,40 210,90 90,90 90,175 30,175";
  const seg = convex ? [60, 130, 170, 60] : [60, 160, 190, 62];
  return (
    <svg width={240} height={200}>
      <polygon points={pts} fill={convex ? `${C.good}33` : `${C.bad}26`} stroke={convex ? C.good : C.bad} strokeWidth={3} />
      <line x1={seg[0]} y1={seg[1]} x2={seg[2]} y2={seg[3]} stroke={C.text} strokeWidth={4} />
      <circle cx={seg[0]} cy={seg[1]} r={8} fill={C.text} />
      <circle cx={seg[2]} cy={seg[3]} r={8} fill={C.text} />
    </svg>
  );
};

export const Restricciones: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCue();
  const restr = cue("restr");
  const lp = cue("lp");
  const vertice = cue("vertice");
  const convexo = cue("convexo");
  const poli = cue("poli");
  const convexa = cue("convexa");

  const partA = 1 - prog(frame, lp - 10, 15);
  const partB = prog(frame, lp, 15);

  // Un aeropuerto intenta ir al lago y otro salir del país.
  const tryP = prog(frame, restr + 150, 45);
  const airports: P[] = [
    { x: 230, y: 362 },
    { x: lerp(235, 302, tryP), y: lerp(462, 505, tryP) },
    { x: lerp(470, 655, tryP), y: lerp(400, 420, tryP) },
  ];
  const badP = prog(frame, restr + 195, 12);

  return (
    <>
      {partA > 0 && (
        <div style={{ opacity: partA }}>
          <div style={{ position: "absolute", left: 70, top: 205 }}>
            <RomaniaMap
              width={1020}
              airports={airports}
              linksOpacity={0.6}
              colorCities={1}
              namesOpacity={0.45}
              lakeOpacity={prog(frame, restr)}
              overlay={(proj) => (
                <g opacity={badP}>
                  {[airports[1], airports[2]].map((a, i) => {
                    const p = proj.pt(a);
                    return (
                      <g key={i}>
                        <circle cx={p.x} cy={p.y} r={40} fill="none" stroke={C.bad} strokeWidth={5} />
                        <line x1={p.x - 26} y1={p.y - 26} x2={p.x + 26} y2={p.y + 26} stroke={C.bad} strokeWidth={6} />
                      </g>
                    );
                  })}
                  <text x={proj.pt(airports[1]).x} y={proj.pt(airports[1]).y - 54} textAnchor="middle" fill={C.bad} fontSize={28} fontWeight={800}>
                    en un lago
                  </text>
                  <text x={proj.pt(airports[2]).x - 20} y={proj.pt(airports[2]).y - 54} textAnchor="middle" fill={C.bad} fontSize={28} fontWeight={800}>
                    fuera del país
                  </text>
                </g>
              )}
            />
          </div>
          <div style={{ position: "absolute", left: 1160, top: 215, width: 690, display: "flex", flexDirection: "column", gap: 22 }}>
            <Reveal p={prog(frame, restr)}>
              <Panel>
                <div style={{ fontSize: 34, fontWeight: 700 }}>Restricciones</div>
                <div style={{ fontSize: 28, color: C.muted, marginTop: 8 }}>condiciones estrictas sobre las variables</div>
              </Panel>
            </Reveal>
            <Reveal p={prog(frame, restr + 70)}>
              <div style={{ display: "flex", gap: 16, alignItems: "center", fontSize: 32 }}>
                <Check ok /> dentro de Rumania
              </div>
            </Reveal>
            <Reveal p={prog(frame, restr + 110)}>
              <div style={{ display: "flex", gap: 16, alignItems: "center", fontSize: 32 }}>
                <Check ok /> en tierra firme (no en un lago)
              </div>
            </Reveal>
          </div>
        </div>
      )}

      {partB > 0 && (
        <div style={{ opacity: partB }}>
          <div style={{ position: "absolute", left: 80, top: 200 }}>
            <Panel style={{ padding: 0 }}>
              <LPPlot
                linesP={[0, 1, 2].map((i) => prog(frame, lp + 40 + i * 25))}
                fillP={prog(frame, lp + 120)}
                sweep={prog(frame, vertice, 120, (t) => t)}
                starP={prog(frame, vertice + 120)}
              />
            </Panel>
          </div>
          <div style={{ position: "absolute", left: 920, top: 200, width: 930, display: "flex", flexDirection: "column", gap: 22 }}>
            <Reveal p={prog(frame, lp)}>
              <Panel style={{ display: "flex", gap: 30, alignItems: "center" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 34, fontWeight: 700 }}>Programación lineal</div>
                  <div style={{ fontSize: 26, color: C.muted, marginTop: 8, lineHeight: 1.4 }}>
                    restricciones = desigualdades lineales
                    <br />
                    objetivo = función lineal
                  </div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <Tex tex={"\\max\\ \\color{#ffd166}{3x_1 + 2x_2}"} size={32} />
                  <Tex tex={"x_1 + 2x_2 \\le 8"} size={28} color={C.a[1]} />
                  <Tex tex={"3x_1 + x_2 \\le 9"} size={28} color={C.a[1]} />
                  <Tex tex={"x_2 \\le 3.5, \\;\\; x_1, x_2 \\ge 0"} size={28} color={C.a[1]} />
                </div>
              </Panel>
            </Reveal>

            {frame < convexa && (
              <Reveal p={prog(frame, convexo) * (1 - prog(frame, convexa - 12, 12))}>
                <Panel>
                  <div style={{ fontSize: 30 }}>
                    <b>Conjunto convexo:</b>{" "}
                    <span style={{ color: C.muted }}>el segmento entre dos puntos cualesquiera queda adentro</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-around", marginTop: 10 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                      <Shape convex />
                      <Check ok />
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 12, opacity: prog(frame, convexo + 45) }}>
                      <Shape convex={false} />
                      <Check ok={false} />
                    </div>
                  </div>
                </Panel>
              </Reveal>
            )}
            {frame >= convexa - 12 && (
              <Reveal p={prog(frame, convexa)}>
                <Panel style={{ display: "flex", gap: 28, alignItems: "center" }}>
                  <svg width={260} height={200}>
                    <ellipse cx={130} cy={100} rx={125} ry={95} fill={`${C.accent}26`} stroke={C.accent} strokeWidth={3} />
                    <ellipse cx={130} cy={128} rx={70} ry={50} fill={`${C.good}33`} stroke={C.good} strokeWidth={3} />
                    <text x={130} y={52} textAnchor="middle" fill={C.text} fontSize={22} fontWeight={700}>
                      convexa
                    </text>
                    <text x={130} y={134} textAnchor="middle" fill={C.text} fontSize={20} fontWeight={700}>
                      lineal
                    </text>
                  </svg>
                  <div style={{ fontSize: 28, lineHeight: 1.45 }}>
                    <b>Optimización convexa</b>
                    <br />
                    <span style={{ color: C.muted }}>región convexa + objetivo convexo</span>
                    <br />
                    <span style={{ color: C.muted }}>polinomial (bajo ciertas condiciones), miles de variables</span>
                    <br />
                    <span style={{ color: C.muted }}>aprendizaje automático y control</span>
                  </div>
                </Panel>
              </Reveal>
            )}
            <Reveal p={prog(frame, poli)}>
              <Badge color={C.good} style={{ fontSize: 30 }}>
                Programación lineal: tiempo polinomial en el nº de variables
              </Badge>
            </Reveal>
          </div>
        </div>
      )}
    </>
  );
};
