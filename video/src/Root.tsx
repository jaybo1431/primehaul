import React from "react";
import { Composition } from "remotion";
import { PrimeHaulDemo } from "./PrimeHaulDemo";
import { TOTAL_FRAMES, FPS } from "./helpers/timing";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="PrimeHaulDemo"
        component={PrimeHaulDemo}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1920}
        height={1080}
      />
      <Composition
        id="PrimeHaulTikTok"
        component={PrimeHaulDemo}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
      />
      <Composition
        id="PrimeHaulSquare"
        component={PrimeHaulDemo}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1080}
      />
    </>
  );
};
