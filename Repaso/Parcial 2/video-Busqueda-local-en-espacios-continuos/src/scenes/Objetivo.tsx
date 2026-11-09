import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";
import { RomaniaMap } from "../components/RomaniaMap";
import { Tex } from "../components/Tex";
import { Badge, Panel, Reveal } from "../components/ui";
import { assign, CITIES, fmt, objective, P, START } from "../lib/romania";
import { lerp, prog, useCue } from "../lib/timing";
import { C } from "../theme";

const FAR: P = { x: 335, y: 300 };

export const Objetivo: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = useCue();
  const ci = cue("ci");
  const formula = cue("formula");
  const local = cue("local");
  const cambia = cue("cambia");
  const global = cue("global");

  // En "cambia" el aeropuerto 1 se va lejos; algunas ciudades cambian de dueño.
  const move = prog(frame, cambia + 10, 75);
  const airports: P[] = START.map((a, i) => (i === 0 ? { x: lerp(a.x, FAR.x, move), y: lerp(a.y, FAR.y, move) } : a));

  const switched = useMemo(() => {
    const before = assign(START);
    const after = assign([FAR, START[1], START[2]]);
    return CITIES.map((_, k) => k).filter((k) => before[k] !== after[k]);
  }, []);
  const c1 = CITIES.filter((_, k) => assign(START)[k] === 0).map((c) => c.name);

  const flashP = ((frame - (cambia + 70)) % 30) / 30;
  const flashing = frame > cambia + 70 && frame < global;

  return (
    <>
      <div style={{ position: "absolute", left: 70, top: 215 }}>
        <RomaniaMap
          width={940}
          airports={airports}
          linksOpacity={1}
          colorCities={1}
          highlight={0}
          highlightP={prog(frame, ci) * (1 - prog(frame, cambia))}
          flashCities={flashing ? switched : []}
          flashP={flashP}
        />
      </div>

      <div style={{ position: "absolute", left: 1060, top: 200, width: 800, display: "flex", flexDirection: "column", gap: 20 }}>
        <Reveal p={prog(frame, ci)}>
          <Panel style={{ padding: "20px 30px" }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: 14 }}>
              <Tex tex={"C_i"} size={44} color={C.a[0]} />
              <span style={{ fontSize: 28 }}>= ciudades cuyo aeropuerto más cercano es el i</span>
            </div>
            <div style={{ fontSize: 24, color: C.muted, marginTop: 8 }}>
              Ejemplo: <span style={{ color: C.a[0], fontWeight: 700 }}>C1</span> = las {c1.length} ciudades rojas del mapa
            </div>
          </Panel>
        </Reveal>
        <Reveal p={prog(frame, formula)}>
          <Panel style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, padding: "20px 30px" }}>
            <Tex
              tex={"\\displaystyle f(\\mathbf{x}) = \\sum_{i=1}^{3} \\sum_{c \\in C_i} (x_i - x_c)^2 + (y_i - y_c)^2"}
              size={38}
            />
            <div style={{ display: "flex", justifyContent: "space-between", width: "100%", alignItems: "center" }}>
              <span style={{ fontSize: 24, color: C.muted }}>Ecuación (4.1)</span>
              <span style={{ fontSize: 32, fontVariantNumeric: "tabular-nums" }}>
                f(x) = <b style={{ color: C.good }}>{fmt(objective(airports))}</b>
              </span>
            </div>
          </Panel>
        </Reveal>
        <div style={{ display: "flex", gap: 16 }}>
          <Reveal p={prog(frame, local)}>
            <Badge color={C.good} style={{ fontSize: 28 }}>✓ Vale localmente</Badge>
          </Reveal>
          <Reveal p={prog(frame, global)}>
            <Badge color={C.bad} style={{ fontSize: 28 }}>✕ No vale globalmente</Badge>
          </Reveal>
        </div>
        <Reveal p={prog(frame, cambia + 70)}>
          <Panel style={{ borderColor: `${C.a[2]}88`, padding: "20px 30px" }}>
            <div style={{ fontSize: 30 }}>
              Si A1 se mueve mucho, algunas ciudades <b>cambian de aeropuerto</b>.
            </div>
            <div style={{ fontSize: 28, color: C.a[2], marginTop: 8 }}>
              Los <Tex tex={"C_i"} size={32} /> cambian → hay que recalcularlos
            </div>
          </Panel>
        </Reveal>
      </div>
    </>
  );
};
