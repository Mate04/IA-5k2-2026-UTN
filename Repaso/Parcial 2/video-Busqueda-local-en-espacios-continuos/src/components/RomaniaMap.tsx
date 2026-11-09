import React from "react";
import { assign, BORDER, CITIES, LAKE, P, ROADS } from "../lib/romania";
import { C, FONT } from "../theme";
import { mix } from "./ui";

const X0 = 45;
const X1 = 610;
const Y0 = 238;
const Y1 = 615;

export type Proj = {
  s: number;
  pt: (p: P) => { x: number; y: number };
};

export const makeProj = (width: number): Proj => {
  const s = width / (X1 - X0);
  return { s, pt: (p) => ({ x: (p.x - X0) * s, y: (Y1 - p.y) * s }) };
};

export const mapHeight = (width: number) => (width / (X1 - X0)) * (Y1 - Y0);

// Curva suave que pasa por los puntos (para el contorno y el lago).
const smoothPath = (pts: { x: number; y: number }[]) => {
  const n = pts.length;
  let d = `M ${pts[0].x} ${pts[0].y}`;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n];
    const p1 = pts[i];
    const p2 = pts[(i + 1) % n];
    const p3 = pts[(i + 2) % n];
    const c1 = { x: p1.x + (p2.x - p0.x) / 6, y: p1.y + (p2.y - p0.y) / 6 };
    const c2 = { x: p2.x - (p3.x - p1.x) / 6, y: p2.y - (p3.y - p1.y) / 6 };
    d += ` C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${p2.x} ${p2.y}`;
  }
  return d + " Z";
};

export const AirportMarker: React.FC<{
  x: number;
  y: number;
  i: number;
  scale?: number;
  opacity?: number;
  ghost?: boolean;
}> = ({ x, y, i, scale = 1, opacity = 1, ghost = false }) => {
  const s = 22 * scale;
  return (
    <g opacity={opacity} transform={`translate(${x} ${y})`}>
      {!ghost && <circle r={s * 1.6} fill={C.a[i]} opacity={0.18} />}
      <rect
        x={-s}
        y={-s}
        width={s * 2}
        height={s * 2}
        rx={s * 0.45}
        fill={ghost ? "none" : C.a[i]}
        stroke={ghost ? C.a[i] : C.bg}
        strokeWidth={ghost ? 3 : 3}
        strokeDasharray={ghost ? "6 5" : undefined}
      />
      {!ghost && (
        <text
          textAnchor="middle"
          dominantBaseline="central"
          fontFamily={FONT}
          fontWeight={800}
          fontSize={s * 0.95}
          fill={C.bg}
        >
          A{i + 1}
        </text>
      )}
    </g>
  );
};

export const RomaniaMap: React.FC<{
  width: number;
  airports?: P[];
  airportsP?: number; // aparición de los aeropuertos (0..1)
  cityP?: number; // aparición de las ciudades (0..1)
  namesOpacity?: number;
  roadsOpacity?: number;
  borderOpacity?: number;
  linksOpacity?: number; // líneas ciudad -> aeropuerto
  colorCities?: number; // 0 = gris, 1 = color de su aeropuerto
  highlight?: number | null; // aeropuerto resaltado (los demás se atenúan)
  highlightP?: number;
  lakeOpacity?: number;
  flashCities?: number[]; // índices de ciudades a marcar con un anillo
  flashP?: number;
  overlay?: (proj: Proj) => React.ReactNode;
  underlay?: (proj: Proj) => React.ReactNode;
  style?: React.CSSProperties;
}> = ({
  width,
  airports,
  airportsP = 1,
  cityP = 1,
  namesOpacity = 1,
  roadsOpacity = 0.35,
  borderOpacity = 1,
  linksOpacity = 0,
  colorCities = 0,
  highlight = null,
  highlightP = 0,
  lakeOpacity = 0,
  flashCities = [],
  flashP = 0,
  overlay,
  underlay,
  style,
}) => {
  const proj = makeProj(width);
  const h = mapHeight(width);
  const owner = airports ? assign(airports) : CITIES.map(() => -1);
  const dim = (i: number) => (highlight === null || i === highlight ? 1 : 1 - 0.75 * highlightP);
  const fontSize = Math.max(17, 12 * proj.s);

  return (
    <svg width={width} height={h} style={{ overflow: "visible", ...style }}>
      <path
        d={smoothPath(BORDER.map(proj.pt))}
        fill="rgba(139,123,255,0.06)"
        stroke="rgba(139,123,255,0.35)"
        strokeWidth={2}
        opacity={borderOpacity}
      />
      {lakeOpacity > 0 && (
        <path d={smoothPath(LAKE.map(proj.pt))} fill="#1f6feb55" stroke="#4c9bff" strokeWidth={2} opacity={lakeOpacity} />
      )}
      {underlay?.(proj)}
      {ROADS.map(([a, b], k) => {
        const pa = proj.pt(a);
        const pb = proj.pt(b);
        return (
          <line key={k} x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y} stroke={C.muted} strokeWidth={2} opacity={roadsOpacity * cityP} />
        );
      })}
      {airports &&
        linksOpacity > 0 &&
        CITIES.map((c, k) => {
          const pc = proj.pt(c);
          const pa = proj.pt(airports[owner[k]]);
          return (
            <line
              key={k}
              x1={pc.x}
              y1={pc.y}
              x2={pa.x}
              y2={pa.y}
              stroke={C.a[owner[k]]}
              strokeWidth={2.5}
              opacity={linksOpacity * 0.7 * dim(owner[k])}
            />
          );
        })}
      {CITIES.map((c, k) => {
        const appear = Math.max(0, Math.min(1, cityP * 1.6 - (k / CITIES.length) * 0.6));
        const pc = proj.pt(c);
        const col = owner[k] >= 0 ? mix("#c9d1ea", C.a[owner[k]], colorCities) : "#c9d1ea";
        const o = appear * (owner[k] >= 0 ? dim(owner[k]) : 1);
        const flash = flashCities.includes(k) ? flashP : 0;
        return (
          <g key={c.name} opacity={o}>
            {flash > 0 && <circle cx={pc.x} cy={pc.y} r={10 + 26 * flash} fill="none" stroke={C.text} strokeWidth={3} opacity={1 - flash} />}
            <circle cx={pc.x} cy={pc.y} r={8} fill={col} stroke={C.bg} strokeWidth={2} />
            <text
              x={pc.x + 12}
              y={pc.y - 10}
              fontFamily={FONT}
              fontSize={fontSize}
              fontWeight={500}
              fill={C.muted}
              opacity={namesOpacity}
            >
              {c.name}
            </text>
          </g>
        );
      })}
      {airports?.map((a, i) => {
        const pa = proj.pt(a);
        const appear = Math.max(0, Math.min(1, airportsP * 1.5 - i * 0.25));
        return (
          <AirportMarker
            key={i}
            x={pa.x}
            y={pa.y - (1 - appear) * 60}
            i={i}
            opacity={appear * (highlight === null || i === highlight ? 1 : 1 - 0.6 * highlightP)}
          />
        );
      })}
      {overlay?.(proj)}
    </svg>
  );
};
