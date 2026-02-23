import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
} from "remotion";
import { BG, GREEN, BLUE, AMBER } from "../helpers/colors";
import { S6_DUR } from "../helpers/timing";
import { useEnvelope, useFadeIn, clamp } from "../helpers/animations";
import { FloatingParticles } from "../components/FloatingParticles";
import { Vignette } from "../components/Vignette";
import { StatCounter } from "../components/StatCounter";

export const Scene6Results: React.FC = () => {
  const f = useCurrentFrame();
  const env = useEnvelope(S6_DUR);
  const title = useFadeIn(5, 14, 12);

  const pulse = interpolate(Math.sin(f * 0.06), [-1, 1], [0.3, 0.8]);

  return (
    <AbsoluteFill style={{ background: BG, ...env }}>
      <FloatingParticles />

      <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ position: "absolute", width: 900, height: 500, borderRadius: "50%", background: `radial-gradient(circle, ${GREEN}12 0%, transparent 70%)`, opacity: pulse }} />
      </AbsoluteFill>

      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 50 }}>
        <div style={{ fontSize: 32, fontFamily: "monospace", color: GREEN, letterSpacing: 8, textTransform: "uppercase", ...title }}>
          The Numbers
        </div>

        <div style={{ display: "flex", gap: 50 }}>
          <StatCounter value="10x" label="Faster Quoting" color={GREEN} delay={40} />
          <StatCounter value="30%" label="More Jobs Won" color={BLUE} delay={130} />
          <StatCounter value="0" label="Wasted Site Visits" color={AMBER} delay={220} />
        </div>
      </AbsoluteFill>

      <Vignette />
    </AbsoluteFill>
  );
};
