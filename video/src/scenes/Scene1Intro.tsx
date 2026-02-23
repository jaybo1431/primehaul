import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  spring,
} from "remotion";
import { BG, GREEN, WHITE } from "../helpers/colors";
import { S1_DUR, FPS } from "../helpers/timing";
import { useEnvelope, useFadeIn, clamp } from "../helpers/animations";
import { FloatingParticles } from "../components/FloatingParticles";
import { Vignette } from "../components/Vignette";

export const Scene1Intro: React.FC = () => {
  const f = useCurrentFrame();
  const env = useEnvelope(S1_DUR);

  const logoScale = spring({
    frame: f,
    fps: FPS,
    from: 0,
    to: 1,
    delay: 8,
    durationInFrames: 24,
    config: { damping: 8, stiffness: 120 },
  });

  const glowSize = interpolate(Math.sin(f * 0.1), [-1, 1], [50, 100]);
  const tagline = useFadeIn(45, 16, 15);
  const subtag = useFadeIn(70, 16, 12);

  const burstScale = interpolate(f, [8, 40], [0, 1.8], clamp);
  const burstOpacity = interpolate(f, [8, 24, 40], [0, 0.4, 0], clamp);

  return (
    <AbsoluteFill style={{ background: BG, ...env }}>
      <FloatingParticles />

      <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            position: "absolute",
            width: 700,
            height: 700,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${GREEN}35 0%, ${GREEN}18 35%, transparent 70%)`,
            transform: `scale(${burstScale})`,
            opacity: burstOpacity,
          }}
        />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 24,
        }}
      >
        <div
          style={{
            fontSize: 140,
            fontWeight: 900,
            fontFamily: "sans-serif",
            color: WHITE,
            letterSpacing: -4,
            transform: `scale(${logoScale})`,
            textShadow: `0 0 ${glowSize}px ${GREEN}50`,
          }}
        >
          Prime<span style={{ color: GREEN }}>Haul</span>
        </div>

        <div
          style={{
            fontSize: 40,
            fontFamily: "sans-serif",
            color: WHITE,
            fontWeight: 700,
            letterSpacing: 2,
            ...tagline,
          }}
        >
          Stop Quoting Blind.
        </div>

        <div
          style={{
            fontSize: 36,
            fontFamily: "sans-serif",
            color: GREEN,
            fontWeight: 600,
            letterSpacing: 2,
            ...subtag,
          }}
        >
          Start Quoting Smart.
        </div>

        <div
          style={{
            width: interpolate(f, [80, 110], [0, 180], clamp),
            height: 4,
            background: `linear-gradient(90deg, transparent, ${GREEN}, transparent)`,
            borderRadius: 2,
          }}
        />
      </AbsoluteFill>

      <Vignette />
    </AbsoluteFill>
  );
};
