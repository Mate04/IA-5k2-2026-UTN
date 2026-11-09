import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { Tex } from "../components/Tex";
import { Badge, Panel, Reveal } from "../components/ui";
import { prog, useCue } from "../lib/timing";
import { C } from "../theme";

const PW = 900;
const PH = 600;

// Parte 1: encontrar la raíz de g(x) = x^3 - 2x - 5 (el ejemplo clásico de Newton).
const g = (x: number) => x ** 3 - 2 * x - 5;
const dg = (x: number) => 3 * x ** 2 - 2;
const gx = (x: number) => 60 + ((x - 0.8) / 2.6) * (PW - 120);
const gy = (y: number) => 40 + ((22 - y) / 30) * (PH - 80);
const gCurve = Array.from({ length: 121 }, (_, i) => {
  const x = 0.8 + (i / 120) * 2.6;
  return `${i ? "L" : "M"} ${gx(x)} ${gy(g(x))}`;
}).join(" ");
const ITERS = (() => {
  const xs = [3.2];
  for (let i = 0; i < 4; i++) xs.push(xs[i] - g(xs[i]) / dg(xs[i]));
  return xs;
})();

// Parte 2: minimizar f(x) = d^2 + 0.3 d^4 con d = x - 1, ajustando una parábola.
const fq = (x: number) => (x - 1) ** 2 + 0.3 * (x - 1) ** 4;
const df = (x: number) => 2 * (x - 1) + 1.2 * (x - 1) ** 3;
const ddf = (x: number) => 2 + 3.6 * (x - 1) ** 2;
const fx = (x: number) => 60 + ((x + 1) / 3.4) * (PW - 120);
const fy = (y: number) => 40 + ((9 - y) / 9.6) * (PH - 80);
const fCurve = Array.from({ length: 121 }, (_, i) => {
  const x = -1 + (i / 120) * 3.4;
  return `${i ? "L" : "M"} ${fx(x)} ${fy(fq(x))}`;
}).join(" ");
const X0 = -0.6;
const X1 = X0 - df(X0) / ddf(X0);
const quad = (x: number) => fq(X0) + df(X0) * (x - X0) + 0.5 * ddf(X0) * (x - X0) ** 2;
const qCurve = Array.from({ length: 81 }, (_, i) => {
  const x = -1 + (i / 80) * 2.4;
  return `${i ? "L" : "M"} ${fx(x)} ${fy(quad(x))}`;
}).join(" ");

const Axis: React.FC<{ y: number }> = ({ y }) => (
  <line x1={30} y1={y} x2={PW - 20} y2={y} stroke={C.faint} strokeWidth={2} />
);

const RootPlot: React.FC<{ done: number }> = ({ done }) => {
  return (
    <svg width={PW} height={PH}>
      <Axis y={gy(0)} />
      <text x={PW - 30} y={gy(0) - 12} textAnchor="end" fill={C.muted} fontSize={24}>
        x
      </text>
      <path d={gCurve} fill="none" stroke={C.a[1]} strokeWidth={5} />
      <text x={gx(2.75) - 16} y={gy(g(2.75))} fill={C.a[1]} fontSize={30} fontWeight={700} textAnchor="end">
        g(x)
      </text>
      <circle cx={gx(2.0946)} cy={gy(0)} r={12} fill="none" stroke={C.good} strokeWidth={4} />
      <text x={gx(2.0946) - 14} y={gy(0) + 44} fill={C.good} fontSize={26} fontWeight={700} textAnchor="end">
        raíz: g(x) = 0
      </text>
      {ITERS.slice(0, 4).map((x, i) => {
        const p = Math.max(0, Math.min(1, done - i));
        if (p <= 0) return null;
        const next = ITERS[i + 1];
        const tangent = Math.min(1, p * 1.6);
        const drop = Math.max(0, (p - 0.65) / 0.35);
        const tx = x + (next - x) * tangent;
        const ty = g(x) + dg(x) * (tx - x);
        return (
          <g key={i} opacity={i < Math.floor(done) - 1 ? 0.35 : 1}>
            <line x1={gx(x)} y1={gy(0)} x2={gx(x)} y2={gy(g(x))} stroke={C.muted} strokeDasharray="5 6" strokeWidth={2} />
            <circle cx={gx(x)} cy={gy(g(x))} r={10} fill="#ffd166" />
            <line x1={gx(x)} y1={gy(g(x))} x2={gx(tx)} y2={gy(ty)} stroke="#ffd166" strokeWidth={3} />
            {drop > 0 && <circle cx={gx(next)} cy={gy(0)} r={9} fill="#ff4d8d" opacity={drop} />}
            <text x={gx(x)} y={gy(0) + 34} fill={C.text} fontSize={24} textAnchor="middle" opacity={i < 2 ? 1 : 0}>
              x<tspan dy={8} fontSize={18}>{i}</tspan>
            </text>
          </g>
        );
      })}
    </svg>
  );
};

const BowlPlot: React.FC<{ fitAt: number }> = ({ fitAt }) => {
  const frame = useCurrentFrame();
  const fitP = prog(frame, fitAt, 30);
  const jumpP = prog(frame, fitAt + 70, 30);
  return (
    <svg width={PW} height={PH}>
      <Axis y={fy(0)} />
      <path d={fCurve} fill="none" stroke={C.a[1]} strokeWidth={5} />
      <text x={fx(2.35)} y={fy(fq(2.35)) - 14} fill={C.a[1]} fontSize={30} fontWeight={700} textAnchor="end">
        f(x)
      </text>
      <line x1={fx(0.55)} y1={fy(0)} x2={fx(1.45)} y2={fy(0)} stroke={C.good} strokeWidth={5} />
      <circle cx={fx(1)} cy={fy(0)} r={10} fill={C.good} />
      <text x={fx(1)} y={fy(0) + 40} fill={C.good} fontSize={26} fontWeight={700} textAnchor="middle">
        mínimo: pendiente 0
      </text>
      <g opacity={fitP}>
        <path d={qCurve} fill="none" stroke="#ffd166" strokeWidth={4} strokeDasharray="10 8" />
        <circle cx={fx(X0)} cy={fy(fq(X0))} r={12} fill="#ffd166" />
        <text x={fx(X0) + 18} y={fy(fq(X0)) - 6} fill="#ffd166" fontSize={26} fontWeight={700}>
          tazón cuadrático
        </text>
      </g>
      <g opacity={jumpP}>
        <path
          d={`M ${fx(X0)} ${fy(fq(X0))} Q ${fx((X0 + X1) / 2)} ${fy(fq(X0)) - 60} ${fx(X1)} ${fy(quad(X1))}`}
          fill="none"
          stroke="#ff4d8d"
          strokeWidth={4}
          strokeDasharray="6 6"
        />
        <circle cx={fx(X1)} cy={fy(quad(X1))} r={12} fill="#ff4d8d" />
        <text x={fx(X1) + 18} y={fy(quad(X1)) + 36} fill="#ff4d8d" fontSize={26} fontWeight={700}>
          salta al fondo
        </text>
      </g>
    </svg>
  );
};

export const Newton: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCue();
  const raices = cue("raices");
  const tangente = cue("tangente");
  const formula = cue("formula");
  const converge = cue("converge");
  const conexion = cue("conexion");
  const hessiana = cue("hessiana");
  const tazon = cue("tazon");

  const partA = 1 - prog(frame, conexion + 40, 15);
  const partB = prog(frame, conexion + 50, 15);

  return (
    <>
      <div style={{ position: "absolute", left: 70, top: 200 }}>
        <Panel style={{ padding: 0, width: PW, height: PH, position: "relative", overflow: "hidden" }}>
          {partA > 0 && (
            <div style={{ position: "absolute", inset: 0, opacity: partA * prog(frame, raices) }}>
              <RootPlot
                done={interpolate(frame, [tangente, tangente + 180, converge, converge + 100], [0, 1, 1, 4], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                })}
              />
            </div>
          )}
          {partB > 0 && (
            <div style={{ position: "absolute", inset: 0, opacity: partB }}>
              <BowlPlot fitAt={tazon} />
            </div>
          )}
        </Panel>
      </div>

      {partA > 0 && (
      <div style={{ position: "absolute", left: 1020, top: 200, width: 840, display: "flex", flexDirection: "column", gap: 20, opacity: partA }}>
        <Reveal p={prog(frame, 10)}>
          <Panel>
            <div style={{ fontSize: 30, color: C.muted }}>Encontrar raíces: resolver</div>
            <Tex tex={"g(x) = 0"} size={48} />
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, formula)}>
          <Panel style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <Tex tex={"\\displaystyle x \\leftarrow x - \\frac{g(x)}{g'(x)}"} size={48} />
            <span style={{ fontSize: 26, color: C.muted, maxWidth: 300 }}>
              donde la tangente corta al eje
            </span>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, converge)}>
          <Badge color={C.good} style={{ fontSize: 28 }}>Repitiendo, converge muy rápido</Badge>
        </Reveal>
      </div>
      )}

      {partB > 0 && (
      <div style={{ position: "absolute", left: 1020, top: 200, width: 840, display: "flex", flexDirection: "column", gap: 20, opacity: partB }}>
        <Reveal p={prog(frame, conexion + 50)}>
          <Panel style={{ borderColor: `${C.good}88` }}>
            <div style={{ fontSize: 30 }}>
              En un máximo o mínimo: <Tex tex={"\\nabla f(\\mathbf{x}) = \\mathbf{0}"} size={38} />
            </div>
            <div style={{ fontSize: 28, color: C.muted, marginTop: 8 }}>
              → usamos Newton con <Tex tex={"g = \\nabla f"} size={34} color={C.text} />
            </div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, hessiana)}>
          <Panel style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <Tex tex={"\\mathbf{x} \\leftarrow \\mathbf{x} - \\mathbf{H}_f^{-1}(\\mathbf{x}) \\, \\nabla f(\\mathbf{x})"} size={46} />
            <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
              <span style={{ fontSize: 28, color: C.muted }}>Hessiana:</span>
              <Tex tex={"\\displaystyle H_{ij} = \\frac{\\partial^2 f}{\\partial x_i \\, \\partial x_j}"} size={38} />
              <span style={{ fontSize: 26, color: C.muted }}>(segundas derivadas)</span>
            </div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, tazon)}>
          <Badge color="#ffd166" style={{ fontSize: 28 }}>
            Ajusta un tazón cuadrático y salta a su fondo
          </Badge>
        </Reveal>
      </div>
      )}
    </>
  );
};
