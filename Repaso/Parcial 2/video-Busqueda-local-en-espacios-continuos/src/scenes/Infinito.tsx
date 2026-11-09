import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { Badge, Check, Panel, Reveal } from "../components/ui";
import { prog, useCue } from "../lib/timing";
import { C } from "../theme";

const DiscreteNeighbors: React.FC<{ p: number }> = ({ p }) => {
  const size = 380;
  const c = size / 2;
  const gap = 120;
  const n = [-1, 0, 1].flatMap((dx) => [-1, 0, 1].map((dy) => ({ dx, dy }))).filter((v) => v.dx || v.dy);
  return (
    <svg width={size} height={size}>
      {n.map((v, i) => {
        const q = Math.max(0, Math.min(1, p * 2 - i * 0.12));
        const x = c + v.dx * gap;
        const y = c + v.dy * gap;
        return (
          <g key={i} opacity={q}>
            <line x1={c} y1={c} x2={c + v.dx * gap * q} y2={c + v.dy * gap * q} stroke={C.muted} strokeWidth={3} />
            <circle cx={x} cy={y} r={22} fill={C.bg2} stroke={C.a[1]} strokeWidth={4} />
            <text x={x} y={y} textAnchor="middle" dominantBaseline="central" fill={C.text} fontSize={22} fontWeight={700}>
              {i + 1}
            </text>
          </g>
        );
      })}
      <circle cx={c} cy={c} r={28} fill="#ffd166" />
    </svg>
  );
};

const ContinuousRays: React.FC<{ rays: number; fill: number }> = ({ rays, fill }) => {
  const size = 380;
  const c = size / 2;
  const R = 160;
  const n = Math.round(rays);
  return (
    <svg width={size} height={size}>
      <circle cx={c} cy={c} r={R} fill={C.a[1]} opacity={0.18 * fill} />
      {Array.from({ length: n }).map((_, i) => {
        const a = (i / n) * Math.PI * 2;
        return (
          <line
            key={i}
            x1={c}
            y1={c}
            x2={c + Math.cos(a) * R}
            y2={c + Math.sin(a) * R}
            stroke={C.a[1]}
            strokeWidth={n > 60 ? 1.5 : 3}
            opacity={0.85}
          />
        );
      })}
      <circle cx={c} cy={c} r={28} fill="#ffd166" />
    </svg>
  );
};

export const Infinito: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCue();
  const discreto = cue("discreto");
  const continuo = cue("continuo");
  const infinito = cue("infinito");
  const rompe = cue("rompe");
  const excepcion = cue("excepcion");

  const rays = interpolate(frame, [continuo + 10, infinito], [8, 240], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => t * t,
  });
  const shown = rays < 200 ? Math.round(rays).toString() : "∞";

  return (
    <>
      <div style={{ position: "absolute", top: 210, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 60 }}>
        <Reveal p={prog(frame, discreto - 8)}>
          <Panel style={{ width: 720, height: 520, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ fontSize: 40, fontWeight: 700 }}>Espacio discreto</div>
            <DiscreteNeighbors p={prog(frame, discreto, 40)} />
            <div style={{ fontSize: 32, color: C.muted }}>
              <b style={{ color: C.text }}>8 vecinos</b>: se pueden revisar todos
            </div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, continuo - 8)}>
          <Panel style={{ width: 720, height: 520, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ fontSize: 40, fontWeight: 700 }}>Espacio continuo</div>
            <ContinuousRays rays={rays} fill={prog(frame, infinito - 20, 30)} />
            <div style={{ fontSize: 32, color: C.muted, fontVariantNumeric: "tabular-nums" }}>
              Sucesores: <b style={{ color: C.text, fontSize: 40 }}>{shown}</b>
            </div>
          </Panel>
        </Reveal>
      </div>

      <Reveal p={prog(frame, infinito)} style={{ position: "absolute", top: 140, right: 96 }}>
        <Badge color={C.a[1]}>Factor de ramificación = ∞</Badge>
      </Reveal>

      {/* Qué algoritmos sirven y cuáles no */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "rgba(8,11,22,0.86)",
          opacity: prog(frame, rompe - 6, 14),
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 34 }}>
        <Reveal p={prog(frame, rompe)}>
          <div style={{ display: "flex", alignItems: "center", gap: 22, fontSize: 44 }}>
            <Check ok={false} size={54} />
            <span>
              La mayoría de los algoritmos: <span style={{ color: C.muted }}>necesitan revisar todos los sucesores</span>
            </span>
          </div>
        </Reveal>
        <Reveal p={prog(frame, excepcion)}>
          <div style={{ display: "flex", alignItems: "center", gap: 22, fontSize: 44 }}>
            <Check ok size={54} />
            <span>Ascenso de colina de primera opción</span>
          </div>
        </Reveal>
        <Reveal p={prog(frame, excepcion + 30)}>
          <div style={{ display: "flex", alignItems: "center", gap: 22, fontSize: 44 }}>
            <Check ok size={54} />
            <span>Recocido simulado</span>
          </div>
        </Reveal>
        <Reveal p={prog(frame, excepcion + 110)}>
          <Badge color={C.good} style={{ marginTop: 20 }}>
            Les alcanza con elegir un sucesor al azar
          </Badge>
        </Reveal>
        </div>
      </div>
    </>
  );
};
