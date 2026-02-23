import { useCurrentFrame, interpolate } from "remotion";
import React from "react";
import { TRANS } from "./timing";

export const clamp = {
  extrapolateLeft: "clamp" as const,
  extrapolateRight: "clamp" as const,
};

export const useFadeIn = (
  start: number,
  dur = 12,
  slideY = 20
): React.CSSProperties => {
  const f = useCurrentFrame();
  return {
    opacity: interpolate(f, [start, start + dur], [0, 1], clamp),
    transform: `translateY(${interpolate(f, [start, start + dur], [slideY, 0], clamp)}px)`,
  };
};

export const useFadeOut = (
  start: number,
  dur = 12
): React.CSSProperties => {
  const f = useCurrentFrame();
  return {
    opacity: interpolate(f, [start, start + dur], [1, 0], clamp),
  };
};

export const useEnvelope = (sceneDur: number): React.CSSProperties => {
  const f = useCurrentFrame();
  const fadeIn = interpolate(f, [0, TRANS], [0, 1], clamp);
  const fadeOut = interpolate(f, [sceneDur - TRANS, sceneDur], [1, 0], clamp);
  const scaleIn = interpolate(f, [0, TRANS], [1.06, 1], clamp);
  const scaleOut = interpolate(
    f,
    [sceneDur - TRANS, sceneDur],
    [1, 0.92],
    clamp
  );
  const scale = f < sceneDur - TRANS ? scaleIn : scaleOut;
  return { opacity: Math.min(fadeIn, fadeOut), transform: `scale(${scale})` };
};

export const useTypewriter = (
  text: string,
  start: number,
  charsPerFrame = 0.8
): string => {
  const f = useCurrentFrame();
  const elapsed = Math.max(0, f - start);
  const charCount = Math.min(text.length, Math.floor(elapsed * charsPerFrame));
  return text.slice(0, charCount);
};
