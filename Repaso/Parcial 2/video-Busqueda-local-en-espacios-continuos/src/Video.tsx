import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import React from "react";
import { useVideoConfig } from "remotion";
import { Scene } from "./components/Scene";
import { useKatexFonts } from "./components/Tex";
import { sceneFrames, SceneId, TRANSITION_FRAMES } from "./lib/timing";
import { Aeropuertos } from "./scenes/Aeropuertos";
import { Demo } from "./scenes/Demo";
import { Discretizar } from "./scenes/Discretizar";
import { Gradiente } from "./scenes/Gradiente";
import { Infinito } from "./scenes/Infinito";
import { Intro } from "./scenes/Intro";
import { Newton } from "./scenes/Newton";
import { NewtonAeropuertos } from "./scenes/NewtonAeropuertos";
import { Objetivo } from "./scenes/Objetivo";
import { Paso } from "./scenes/Paso";
import { Problemas } from "./scenes/Problemas";
import { Restricciones } from "./scenes/Restricciones";
import { Resumen } from "./scenes/Resumen";

export const SCENE_ORDER: SceneId[] = [
  "intro",
  "infinito",
  "aeropuertos",
  "objetivo",
  "discretizar",
  "gradiente",
  "paso",
  "demo",
  "newton",
  "newtonAeropuertos",
  "problemas",
  "restricciones",
  "resumen",
];

export const Video: React.FC = () => {
  const { fps } = useVideoConfig();
  useKatexFonts();
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence name="1 · Intro" durationInFrames={sceneFrames("intro", fps)}>
        <Scene id="intro">
          <Intro />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="2 · Discreto vs continuo" durationInFrames={sceneFrames("infinito", fps)}>
        <Scene id="infinito" title="Discreto vs. continuo">
          <Infinito />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="3 · Aeropuertos" durationInFrames={sceneFrames("aeropuertos", fps)}>
        <Scene id="aeropuertos" title="Ejemplo: 3 aeropuertos en Rumania">
          <Aeropuertos />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="4 · Función objetivo" durationInFrames={sceneFrames("objetivo", fps)}>
        <Scene id="objetivo" title="La función objetivo">
          <Objetivo />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="5 · Discretizar" durationInFrames={sceneFrames("discretizar", fps)}>
        <Scene id="discretizar" title="Idea 1: discretizar">
          <Discretizar />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="6 · Gradiente" durationInFrames={sceneFrames("gradiente", fps)}>
        <Scene id="gradiente" title="Idea 2: el gradiente">
          <Gradiente />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="7 · Tamaño de paso" durationInFrames={sceneFrames("paso", fps)}>
        <Scene id="paso" title="Moverse con el gradiente">
          <Paso />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="8 · Demo en el mapa" durationInFrames={sceneFrames("demo", fps)}>
        <Scene id="demo" title="Descenso por gradiente en el mapa">
          <Demo />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="9 · Newton-Raphson" durationInFrames={sceneFrames("newton", fps)}>
        <Scene id="newton" title="Newton-Raphson">
          <Newton />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="10 · Newton en los aeropuertos" durationInFrames={sceneFrames("newtonAeropuertos", fps)}>
        <Scene id="newtonAeropuertos" title="Newton en los aeropuertos">
          <NewtonAeropuertos />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="11 · Problemas" durationInFrames={sceneFrames("problemas", fps)}>
        <Scene id="problemas" title="Los problemas de siempre">
          <Problemas />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="12 · Restricciones" durationInFrames={sceneFrames("restricciones", fps)}>
        <Scene id="restricciones" title="Optimización con restricciones">
          <Restricciones />
        </Scene>
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })} />
      <TransitionSeries.Sequence name="13 · Resumen" durationInFrames={sceneFrames("resumen", fps)}>
        <Scene id="resumen" title="Resumen">
          <Resumen />
        </Scene>
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
