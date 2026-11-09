import "katex/dist/katex.min.css";
import katex from "katex";
import React, { useEffect, useMemo, useState } from "react";
import { continueRender, delayRender } from "remotion";

const KATEX_FONTS = [
  "20px KaTeX_Main",
  "bold 20px KaTeX_Main",
  "italic 20px KaTeX_Main",
  "italic 20px KaTeX_Math",
  "bold italic 20px KaTeX_Math",
  "20px KaTeX_Size1",
  "20px KaTeX_Size2",
  "20px KaTeX_Size3",
  "20px KaTeX_Size4",
  "20px KaTeX_AMS",
];

// Espera a que las fuentes de KaTeX estén cargadas antes de capturar frames.
export const useKatexFonts = () => {
  const [handle] = useState(() => delayRender("Cargando fuentes de KaTeX"));
  useEffect(() => {
    Promise.all(KATEX_FONTS.map((f) => document.fonts.load(f)))
      .catch(() => undefined)
      .then(() => continueRender(handle));
  }, [handle]);
};

export const Tex: React.FC<{
  tex: string;
  size?: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({ tex, size = 44, color, style }) => {
  const html = useMemo(
    () => katex.renderToString(tex, { throwOnError: false, output: "html", displayMode: false }),
    [tex],
  );
  return (
    <span
      style={{ fontSize: size, color, lineHeight: 1.2, whiteSpace: "nowrap", ...style }}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
};
