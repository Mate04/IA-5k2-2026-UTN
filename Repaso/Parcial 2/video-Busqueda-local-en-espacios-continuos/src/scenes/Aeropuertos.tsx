import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { RomaniaMap } from "../components/RomaniaMap";
import { Tex } from "../components/Tex";
import { Badge, Panel, Reveal } from "../components/ui";
import { P, START } from "../lib/romania";
import { prog, useCue } from "../lib/timing";
import { C } from "../theme";

export const Aeropuertos: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cue = useCue();
  const mapa = cue("mapa");
  const asignacion = cue("asignacion");
  const estado = cue("estado");
  const seis = cue("seis");
  const mover = cue("mover");

  // En "mover", el aeropuerto 1 da una vuelta por el mapa.
  const t = Math.max(0, (frame - mover) / fps);
  const k = prog(frame, mover, 12);
  const airports: P[] = START.map((a, i) =>
    i === 0 ? { x: a.x + k * (110 * Math.sin(t * 1.3)), y: a.y + k * (90 * (1 - Math.cos(t * 1.3))) } : a,
  );

  const coords = airports.flatMap((a, i) => [
    { name: `x_${i + 1}`, v: a.x, c: C.a[i] },
    { name: `y_${i + 1}`, v: a.y, c: C.a[i] },
  ]);

  return (
    <>
      <div style={{ position: "absolute", left: 80, top: 200 }}>
        <RomaniaMap
          width={1060}
          cityP={prog(frame, 0, 50)}
          airports={airports}
          airportsP={prog(frame, mapa, 30)}
          linksOpacity={prog(frame, asignacion)}
          colorCities={prog(frame, asignacion)}
        />
      </div>

      <div style={{ position: "absolute", left: 1210, top: 200, width: 640, display: "flex", flexDirection: "column", gap: 26 }}>
        <Reveal p={prog(frame, mapa)}>
          <Panel>
            <div style={{ fontSize: 34, fontWeight: 700 }}>Ubicar 3 aeropuertos</div>
            <div style={{ fontSize: 28, color: C.muted, marginTop: 8 }}>en cualquier punto de Rumania</div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, asignacion)}>
          <Panel>
            <div style={{ fontSize: 28, color: C.muted }}>Cada ciudad usa su aeropuerto más cercano.</div>
            <div style={{ fontSize: 32, fontWeight: 700, marginTop: 10 }}>
              Minimizar <span style={{ color: C.good }}>Σ distancia²</span>
            </div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, estado)}>
          <Panel>
            <div style={{ fontSize: 28, color: C.muted, marginBottom: 14 }}>Estado = coordenadas de los aeropuertos</div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "nowrap" }}>
              <Tex tex={"\\mathbf{x} = ("} size={40} />
              {coords.map((c, i) => (
                <span key={c.name} style={{ display: "inline-flex", flexDirection: "column", alignItems: "center", opacity: prog(frame, estado + 20 + i * 12) }}>
                  <Tex tex={`${c.name}${i < 5 ? "," : ""}`} size={40} color={c.c} />
                  <span style={{ fontSize: 22, color: C.muted, fontVariantNumeric: "tabular-nums", width: 52, textAlign: "center" }}>
                    {Math.round(c.v)}
                  </span>
                </span>
              ))}
              <Tex tex={")"} size={40} />
            </div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, seis)}>
          <Badge color={C.accent}>
            6 variables → <Tex tex={"\\mathbf{x} \\in \\mathbb{R}^6"} size={34} />
          </Badge>
        </Reveal>
        <Reveal p={prog(frame, mover)}>
          <div style={{ fontSize: 30, color: C.muted }}>
            Moverse en el espacio = <b style={{ color: C.text }}>mover aeropuertos</b>
          </div>
        </Reveal>
      </div>
    </>
  );
};
