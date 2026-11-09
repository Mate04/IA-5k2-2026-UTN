import { Audio } from "@remotion/media";
import React from "react";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { LEAD_IN, SceneContext, SceneId, VOICEOVER } from "../lib/timing";
import { C, FONT } from "../theme";
import { Subtitles } from "./Subtitles";

const Header: React.FC<{ title?: string }> = ({ title }) => {
  const frame = useCurrentFrame();
  if (!title) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 96,
        top: 64,
        opacity: interpolate(frame, [6, 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        translate: `${interpolate(frame, [6, 24], [-24, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px 0px`,
      }}
    >
      <div style={{ fontSize: 24, fontWeight: 600, color: C.accent, letterSpacing: 2, textTransform: "uppercase" }}>
        4.2 · Búsqueda local en espacios continuos
      </div>
      <div style={{ fontSize: 60, fontWeight: 800, color: C.text, marginTop: 6 }}>{title}</div>
    </div>
  );
};

// Envuelve una escena: fondo, título, narración y subtítulos.
export const Scene: React.FC<{
  id: SceneId;
  title?: string;
  subtitles?: boolean;
  children: React.ReactNode;
}> = ({ id, title, subtitles = true, children }) => {
  const { fps } = useVideoConfig();
  const audio = VOICEOVER[id];
  return (
    <SceneContext.Provider value={{ id, fps }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(1200px 800px at 75% 20%, ${C.bg2} 0%, ${C.bg} 70%)`,
          fontFamily: FONT,
          color: C.text,
        }}
      >
        <Header title={title} />
        {children}
        {subtitles ? <Subtitles words={audio.words} /> : null}
        <Audio name={`Voz: ${id}`} src={staticFile(audio.file)} from={Math.round(LEAD_IN * fps)} />
      </AbsoluteFill>
    </SceneContext.Provider>
  );
};
