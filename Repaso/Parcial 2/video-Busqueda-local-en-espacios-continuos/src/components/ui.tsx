import React from "react";
import { C } from "../theme";

export const mix = (a: string, b: string, t: number) => {
  const pa = parseInt(a.slice(1), 16);
  const pb = parseInt(b.slice(1), 16);
  const ch = (p: number, s: number) => (p >> s) & 255;
  const m = (s: number) => Math.round(ch(pa, s) + (ch(pb, s) - ch(pa, s)) * t);
  return `rgb(${m(16)},${m(8)},${m(0)})`;
};

// Contenedor que aparece con fundido y un leve desplazamiento hacia arriba.
export const Reveal: React.FC<{
  p: number;
  style?: React.CSSProperties;
  dy?: number;
  children: React.ReactNode;
}> = ({ p, style, dy = 24, children }) => (
  <div style={{ opacity: p, translate: `0px ${(1 - p) * dy}px`, ...style }}>{children}</div>
);

export const Panel: React.FC<{ style?: React.CSSProperties; children: React.ReactNode }> = ({ style, children }) => (
  <div
    style={{
      background: C.panel,
      border: `1px solid ${C.panelBorder}`,
      borderRadius: 24,
      padding: "28px 34px",
      ...style,
    }}
  >
    {children}
  </div>
);

export const Badge: React.FC<{
  color?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ color = C.accent, children, style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 12,
      padding: "10px 22px",
      borderRadius: 999,
      background: `${color}22`,
      border: `2px solid ${color}`,
      color: C.text,
      fontSize: 32,
      fontWeight: 600,
      ...style,
    }}
  >
    {children}
  </div>
);

// Flecha SVG de (x1,y1) a (x2,y2). `p` recorta el largo para animarla.
export const Arrow: React.FC<{
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  color?: string;
  width?: number;
  head?: number;
  p?: number;
  opacity?: number;
  dash?: string;
}> = ({ x1, y1, x2, y2, color = C.text, width = 4, head = 16, p = 1, opacity = 1, dash }) => {
  const ex = x1 + (x2 - x1) * p;
  const ey = y1 + (y2 - y1) * p;
  const ang = Math.atan2(ey - y1, ex - x1);
  const len = Math.hypot(ex - x1, ey - y1);
  if (len < 1) return null;
  const h = Math.min(head, len * 0.6);
  const bx = ex - Math.cos(ang) * h * 0.8;
  const by = ey - Math.sin(ang) * h * 0.8;
  const l = { x: ex - Math.cos(ang - 0.45) * h, y: ey - Math.sin(ang - 0.45) * h };
  const r = { x: ex - Math.cos(ang + 0.45) * h, y: ey - Math.sin(ang + 0.45) * h };
  return (
    <g opacity={opacity}>
      <line x1={x1} y1={y1} x2={bx} y2={by} stroke={color} strokeWidth={width} strokeLinecap="round" strokeDasharray={dash} />
      <polygon points={`${ex},${ey} ${l.x},${l.y} ${r.x},${r.y}`} fill={color} />
    </g>
  );
};

export const Check: React.FC<{ ok: boolean; size?: number }> = ({ ok, size = 40 }) => (
  <span
    style={{
      display: "inline-flex",
      width: size,
      height: size,
      borderRadius: size,
      alignItems: "center",
      justifyContent: "center",
      background: ok ? C.good : C.bad,
      color: C.bg,
      fontWeight: 800,
      fontSize: size * 0.62,
      flexShrink: 0,
    }}
  >
    {ok ? "✓" : "✕"}
  </span>
);
