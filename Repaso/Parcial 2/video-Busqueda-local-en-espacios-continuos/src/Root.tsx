import { Composition } from "remotion";
import { totalFrames } from "./lib/timing";
import { FPS, HEIGHT, WIDTH } from "./theme";
import { SCENE_ORDER, Video } from "./Video";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="BusquedaLocalContinua"
      component={Video}
      durationInFrames={totalFrames(SCENE_ORDER, FPS)}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};
