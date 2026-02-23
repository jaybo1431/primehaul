import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  spring,
} from "remotion";
import { BG, GREEN, WHITE, GRAY } from "../helpers/colors";
import { S7_DUR, FPS } from "../helpers/timing";
import { useEnvelope, useTypewriter, clamp } from "../helpers/animations";
import { FloatingParticles } from "../components/FloatingParticles";
import { Vignette } from "../components/Vignette";

export const Scene7CTA: React.FC = () => {
  const f = useCurrentFrame();
  const env = useEnvelope(S7_DUR);

  const btnProg = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: 15, durationInFrames: 20, config: { damping: 8, stiffness: 120 } });
  const btnBreathe = interpolate(Math.sin(f * 0.12), [-1, 1], [0.97, 1.05]);
  const url = useTypewriter("primehaul.co.uk", 55, 0.7);
  const noCCOpacity = interpolate(f, [85, 105], [0, 1], clamp);
  const djamOpacity = interpolate(f, [130, 160], [0, 1], clamp);
  const logoProg = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: 5, durationInFrames: 18, config: { damping: 9 } });
  const ringAngle = f * 3;
  const glowSize = interpolate(Math.sin(f * 0.08), [-1, 1], [60, 120]);

  return (
    <AbsoluteFill style={{ background: BG, ...env }}>
      <FloatingParticles />

      <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ position: "absolute", width: 600, height: 600, borderRadius: "50%", background: `conic-gradient(from ${ringAngle}deg, ${GREEN}25, transparent 25%, ${GREEN}15, transparent 50%, ${GREEN}25, transparent 75%, ${GREEN}25)`, opacity: 0.4, filter: "blur(10px)" }} />
      </AbsoluteFill>

      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 30 }}>
        <div style={{ fontSize: 80, fontWeight: 900, fontFamily: "sans-serif", color: WHITE, letterSpacing: -3, opacity: logoProg, transform: `scale(${logoProg})` }}>
          Prime<span style={{ color: GREEN }}>Haul</span>
        </div>

        <div style={{ position: "relative", opacity: btnProg }}>
          <div style={{ position: "absolute", inset: -24, borderRadius: 22, background: GREEN, filter: `blur(${glowSize}px)`, opacity: 0.15 }} />
          <div style={{ position: "relative", background: GREEN, color: "#000", fontWeight: 800, fontSize: 34, fontFamily: "sans-serif", padding: "20px 60px", borderRadius: 16, transform: `scale(${btnBreathe})`, boxShadow: `0 0 30px ${GREEN}40, 0 8px 30px rgba(0,0,0,0.5)`, letterSpacing: 1 }}>
            Start Free Trial
          </div>
        </div>

        <div style={{ fontSize: 38, fontFamily: "monospace", color: WHITE, letterSpacing: 3 }}>
          {url}
          {url.length < 15 && <span style={{ opacity: Math.sin(f * 0.3) > 0 ? 1 : 0, color: GREEN }}>|</span>}
        </div>

        <div style={{ fontSize: 22, fontFamily: "sans-serif", color: GRAY, opacity: noCCOpacity }}>
          No credit card needed
        </div>

        <div style={{ fontSize: 18, fontFamily: "monospace", color: `${GRAY}88`, opacity: djamOpacity, marginTop: 16 }}>
          Built by djam.ai
        </div>
      </AbsoluteFill>

      <Vignette />
    </AbsoluteFill>
  );
};
