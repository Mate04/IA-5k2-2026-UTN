import React, { useMemo } from "react";
import { Img, useCurrentFrame } from "remotion";
import { RomaniaMap } from "../components/RomaniaMap";
import { Tex } from "../components/Tex";
import { Arrow, Badge, Panel, Reveal } from "../components/ui";
import { CITIES, mean, P, START } from "../lib/romania";
import { lerp, prog, useCue, useWord } from "../lib/timing";
import { C } from "../theme";

// Paisaje de ejemplo: dos colinas. u, v en [0, 1].
const h = (u: number, v: number) =>
  Math.exp(-((u - 0.68) ** 2 + (v - 0.4) ** 2) / (2 * 0.16 ** 2)) +
  0.55 * Math.exp(-((u - 0.22) ** 2 + (v - 0.68) ** 2) / (2 * 0.12 ** 2)) +
  0.08 * u;
const grad = (u: number, v: number) => {
  const e = 1e-4;
  return { gu: (h(u + e, v) - h(u - e, v)) / (2 * e), gv: (h(u, v + e) - h(u, v - e)) / (2 * e) };
};

const W = 1040;
const H = 600;
const STOPS: [number, number[]][] = [
  [0, [16, 24, 58]],
  [0.3, [29, 78, 137]],
  [0.55, [42, 157, 143]],
  [0.8, [233, 196, 106]],
  [1, [244, 162, 97]],
];
const colormap = (t: number) => {
  for (let i = 1; i < STOPS.length; i++) {
    if (t <= STOPS[i][0]) {
      const [t0, c0] = STOPS[i - 1];
      const [t1, c1] = STOPS[i];
      const f = (t - t0) / (t1 - t0);
      return c0.map((c, k) => c + (c1[k] - c) * f);
    }
  }
  return STOPS[STOPS.length - 1][1];
};

const useHeatmap = () =>
  useMemo(() => {
    const w = W / 2;
    const hh = H / 2;
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = hh;
    const ctx = canvas.getContext("2d")!;
    const img = ctx.createImageData(w, hh);
    for (let y = 0; y < hh; y++) {
      for (let x = 0; x < w; x++) {
        const val = h(x / w, y / hh);
        const [r, g, b] = colormap(Math.min(1, val / 1.08));
        const contour = (val * 12) % 1 < 0.07 ? 1.35 : 1;
        const i = (y * w + x) * 4;
        img.data[i] = Math.min(255, r * contour);
        img.data[i + 1] = Math.min(255, g * contour);
        img.data[i + 2] = Math.min(255, b * contour);
        img.data[i + 3] = 255;
      }
    }
    ctx.putImageData(img, 0, 0);
    return canvas.toDataURL();
  }, []);

// Camino de ascenso por gradiente desde un punto de partida.
const PATH = (() => {
  const pts = [{ u: 0.36, v: 0.86 }];
  for (let i = 0; i < 400; i++) {
    const p = pts[pts.length - 1];
    const g = grad(p.u, p.v);
    const n = Math.hypot(g.gu, g.gv);
    if (n < 0.05) break;
    pts.push({ u: p.u + (g.gu / n) * 0.004, v: p.v + (g.gv / n) * 0.004 });
  }
  return pts;
})();

const Landscape: React.FC<{ arrowsP: number; walkP: number; heroP: number }> = ({ arrowsP, walkP, heroP }) => {
  const src = useHeatmap();
  const idx = Math.floor(walkP * (PATH.length - 1));
  const hiker = PATH[idx];
  const g = grad(hiker.u, hiker.v);
  const n = Math.hypot(g.gu, g.gv);
  const len = Math.min(170, 30 + n * 55);
  const hx = hiker.u * W;
  const hy = hiker.v * H;
  return (
    <div style={{ position: "relative", width: W, height: H, borderRadius: 24, overflow: "hidden", border: `1px solid ${C.panelBorder}` }}>
      <Img src={src} style={{ width: W, height: H }} />
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        {Array.from({ length: 13 * 8 }).map((_, k) => {
          const i = k % 13;
          const j = Math.floor(k / 13);
          const u = (i + 0.5) / 13;
          const v = (j + 0.5) / 8;
          const gg = grad(u, v);
          const nn = Math.hypot(gg.gu, gg.gv);
          if (nn < 0.05) return null;
          const l = Math.min(48, 10 + nn * 14);
          const x = u * W;
          const y = v * H;
          return (
            <Arrow
              key={k}
              x1={x}
              y1={y}
              x2={x + (gg.gu / nn) * l}
              y2={y + (gg.gv / nn) * l}
              color="rgba(255,255,255,0.85)"
              width={2.5}
              head={10}
              opacity={arrowsP}
            />
          );
        })}
        <polyline
          points={PATH.slice(0, idx + 1).map((p) => `${p.u * W},${p.v * H}`).join(" ")}
          fill="none"
          stroke="#ffffff"
          strokeWidth={4}
          strokeDasharray="2 10"
          strokeLinecap="round"
          opacity={walkP > 0 ? 0.9 : 0}
        />
        <g opacity={heroP}>
          <Arrow x1={hx} y1={hy} x2={hx + (g.gu / n) * len} y2={hy + (g.gv / n) * len} color="#ff4d8d" width={7} head={24} />
          <circle cx={hx} cy={hy} r={14} fill="#ffffff" stroke="#0c1120" strokeWidth={4} />
          <text x={hx + (g.gu / n) * len + 12} y={hy + (g.gv / n) * len - 12} fill="#ffffff" fontSize={36} fontWeight={800}>
            ∇f
          </text>
        </g>
      </svg>
      <div style={{ position: "absolute", right: 16, bottom: 12, fontSize: 22, color: "rgba(255,255,255,0.8)" }}>
        más claro = f más alta
      </div>
    </div>
  );
};

export const Gradiente: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCue();
  const gradiente = cue("gradiente");
  const flechas = cue("flechas");
  const componentes = cue("componentes");
  const cero = cue("cero");
  const tres = cue("tres");
  const word = useWord();
  const eq42 = word("localmente");

  const phaseA = 1 - prog(frame, componentes - 12, 15);
  const phaseB = prog(frame, componentes, 15);

  // Con un solo aeropuerto: el óptimo es el promedio de todas las ciudades.
  const avg = mean(CITIES);
  const oneStart: P = { x: 520, y: 560 };
  const oneP = prog(frame, cero + 50, 50);
  const one: P = { x: lerp(oneStart.x, avg.x, oneP), y: lerp(oneStart.y, avg.y, oneP) };
  const threeP = prog(frame, tres, 18);

  return (
    <>
      {phaseA > 0 && (
        <div style={{ opacity: phaseA }}>
          <div style={{ position: "absolute", left: 80, top: 205 }}>
            <Reveal p={prog(frame, 0, 20)}>
              <Landscape arrowsP={prog(frame, flechas, 20)} walkP={prog(frame, flechas + 20, 200, (t) => t)} heroP={prog(frame, gradiente)} />
            </Reveal>
          </div>
          <div style={{ position: "absolute", left: 1170, top: 205, width: 680, display: "flex", flexDirection: "column", gap: 22 }}>
            <Reveal p={prog(frame, 15)}>
              <Panel>
                <div style={{ fontSize: 30, color: C.muted }}>Si tenemos la fórmula de f:</div>
                <div style={{ fontSize: 36, fontWeight: 700, marginTop: 6 }}>usamos cálculo, no prueba y error</div>
              </Panel>
            </Reveal>
            <Reveal p={prog(frame, gradiente)}>
              <Panel style={{ borderColor: "#ff4d8d88" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                  <Tex tex={"\\nabla f"} size={54} color="#ff4d8d" />
                  <span style={{ fontSize: 36, fontWeight: 700 }}>= gradiente (un vector)</span>
                </div>
                <div style={{ fontSize: 30, marginTop: 16, lineHeight: 1.5 }}>
                  <b>Dirección:</b> <span style={{ color: C.muted }}>hacia donde f sube más rápido</span>
                  <br />
                  <b>Largo:</b> <span style={{ color: C.muted }}>qué tan empinada es la subida</span>
                </div>
              </Panel>
            </Reveal>
            <Reveal p={prog(frame, flechas)}>
              <Panel>
                <div style={{ fontSize: 30, lineHeight: 1.45 }}>
                  Montaña con niebla: el gradiente es la flecha que apunta a la <b>subida más fuerte</b> desde donde estás parado.
                </div>
              </Panel>
            </Reveal>
          </div>
        </div>
      )}

      {phaseB > 0 && (
        <div style={{ opacity: phaseB }}>
          <div style={{ position: "absolute", left: 96, right: 96, top: 205, display: "flex", justifyContent: "center" }}>
            <Panel style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
              <Tex
                tex={
                  "\\nabla f = \\left( \\color{#ff6b6b}{\\frac{\\partial f}{\\partial x_1}}, \\color{#ff6b6b}{\\frac{\\partial f}{\\partial y_1}}, \\color{#4cc9f0}{\\frac{\\partial f}{\\partial x_2}}, \\color{#4cc9f0}{\\frac{\\partial f}{\\partial y_2}}, \\color{#ffd166}{\\frac{\\partial f}{\\partial x_3}}, \\color{#ffd166}{\\frac{\\partial f}{\\partial y_3}} \\right)"
                }
                size={48}
              />
              <div style={{ fontSize: 26, color: C.muted }}>6 componentes: una derivada parcial por coordenada</div>
            </Panel>
          </div>

          <div style={{ position: "absolute", left: 90, top: 440 }}>
            <Reveal p={prog(frame, cero)}>
              <RomaniaMap
                width={760}
                airports={threeP > 0.5 ? START : [one]}
                linksOpacity={1}
                colorCities={1}
                namesOpacity={0}
                highlight={0}
                highlightP={prog(frame, eq42)}
                overlay={(proj) =>
                  threeP < 0.5 && oneP > 0 ? (
                    <g opacity={1 - threeP * 2}>
                      <circle cx={proj.pt(avg).x} cy={proj.pt(avg).y} r={34} fill="none" stroke={C.good} strokeWidth={3} strokeDasharray="6 6" />
                      <text x={proj.pt(avg).x + 44} y={proj.pt(avg).y + 50} fill={C.good} fontSize={28} fontWeight={700}>
                        promedio
                      </text>
                    </g>
                  ) : null
                }
              />
            </Reveal>
          </div>

          <div style={{ position: "absolute", left: 930, top: 450, width: 920, display: "flex", flexDirection: "column", gap: 20 }}>
            {frame < tres && (
            <Reveal p={prog(frame, cero) * (1 - prog(frame, tres - 12, 12))}>
              <Panel>
                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  <Tex tex={"\\nabla f = \\mathbf{0}"} size={44} />
                  <span style={{ fontSize: 30 }}>a veces se puede resolver directo</span>
                </div>
                <div style={{ fontSize: 28, color: C.muted, marginTop: 8 }}>
                  1 aeropuerto → <b style={{ color: C.good }}>promedio de todas las ciudades</b>
                </div>
              </Panel>
            </Reveal>
            )}
            {frame >= tres && (
            <Reveal p={prog(frame, tres)}>
              <Panel style={{ borderColor: `${C.bad}88` }}>
                <div style={{ fontSize: 30 }}>
                  3 aeropuertos → <b style={{ color: C.bad }}>sin fórmula cerrada</b>
                </div>
                <div style={{ fontSize: 28, color: C.muted, marginTop: 8 }}>
                  los <Tex tex={"C_i"} size={30} /> dependen del estado → gradiente <b style={{ color: C.text }}>local</b>
                </div>
              </Panel>
            </Reveal>
            )}
            <Reveal p={prog(frame, eq42 - 10)}>
              <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
                <Badge color={C.a[0]} style={{ padding: "16px 30px" }}>
                  <Tex tex={"\\displaystyle \\frac{\\partial f}{\\partial x_1} = 2 \\sum_{c \\in C_1} (x_1 - x_c)"} size={40} />
                </Badge>
                <span style={{ fontSize: 26, color: C.muted }}>Ecuación (4.2)</span>
              </div>
            </Reveal>
          </div>
        </div>
      )}
    </>
  );
};
