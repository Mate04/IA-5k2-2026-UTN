import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont("normal", {
  weights: ["400", "500", "600", "700", "800"],
  subsets: ["latin", "latin-ext"],
});

export const FONT = fontFamily;

export const C = {
  bg: "#0c1120",
  bg2: "#141b30",
  panel: "rgba(255,255,255,0.045)",
  panelBorder: "rgba(255,255,255,0.10)",
  text: "#eef2ff",
  muted: "#98a2c0",
  faint: "#4a5578",
  good: "#2ee6a6",
  bad: "#ff5c7a",
  accent: "#8b7bff",
  // Un color por aeropuerto.
  a: ["#ff6b6b", "#4cc9f0", "#ffd166"],
};

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
