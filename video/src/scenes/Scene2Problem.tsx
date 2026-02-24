import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  spring,
} from "remotion";
import { BG, RED, AMBER, WHITE } from "../helpers/colors";
import { S2_DUR, FPS } from "../helpers/timing";
import { useEnvelope, clamp } from "../helpers/animations";
import { FloatingParticles } from "../components/FloatingParticles";
import { Vignette } from "../components/Vignette";

const PAIN_POINTS = [
  {
    icon: "\u26FD",
    text: "Driving across town for site visits that lead nowhere",
    color: RED,
    delay: 20,
  },
  {
    icon: "\u231B",
    text: "Customers waiting days while competitors swoop in",
    color: AMBER,
    delay: 100,
  },
  {
    icon: "\uD83D\uDCB8",
    text: "Losing jobs and burning fuel every single week",
    color: RED,
    delay: 175,
  },
];

export const Scene2Problem: React.FC = () => {
  const f = useCurrentFrame();
  const env = useEnvelope(S2_DUR);

  return (
    <AbsoluteFill style={{ background: BG, ...env }}>
      <FloatingParticles />

      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 50,
        }}
      >
        <div
          style={{
            fontSize: 32,
            fontFamily: "monospace",
            color: RED,
            letterSpacing: 8,
            textTransform: "uppercase",
            opacity: interpolate(f, [10, 25], [0, 1], clamp),
          }}
        >
          Sound Familiar?
        </div>

        <div style={{ display: "flex", gap: 56, alignItems: "flex-start" }}>
          {PAIN_POINTS.map((point, i) => {
            const prog = spring({
              frame: f,
              fps: FPS,
              from: 0,
              to: 1,
              delay: point.delay,
              durationInFrames: 20,
              config: { damping: 9 },
            });

            const pulse = interpolate(Math.sin(f * 0.06 + i * 2), [-1, 1], [0.7, 1]);

            return (
              <div
                key={i}
                style={{
                  opacity: prog,
                  transform: `scale(${interpolate(prog, [0, 1], [0.4, 1])}) translateY(${interpolate(prog, [0, 1], [30, 0])}px)`,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: 20,
                  width: 320,
                }}
              >
                <div
                  style={{
                    width: 110,
                    height: 110,
                    borderRadius: "50%",
                    background: `${point.color}12`,
                    border: `2px solid ${point.color}40`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 48,
                    boxShadow: `0 0 ${30 * pulse}px ${point.color}25`,
                  }}
                >
                  {point.icon}
                </div>

                <div
                  style={{
                    fontSize: 28,
                    fontFamily: "sans-serif",
                    color: WHITE,
                    textAlign: "center",
                    lineHeight: 1.35,
                  }}
                >
                  {point.text}
                </div>

                <div
                  style={{
                    width: interpolate(f, [point.delay + 10, point.delay + 30], [0, 80], clamp),
                    height: 3,
                    background: point.color,
                    borderRadius: 2,
                    opacity: 0.6,
                  }}
                />
              </div>
            );
          })}
        </div>
      </AbsoluteFill>

      <Vignette />
    </AbsoluteFill>
  );
};
