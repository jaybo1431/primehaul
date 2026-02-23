import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { GREEN, BLUE, AMBER } from "../helpers/colors";

const PARTICLES = Array.from({ length: 30 }, (_, i) => ({
  x: (i * 137.5) % 100,
  y: (i * 61.8) % 100,
  size: 1 + (i % 3),
  speed: 0.3 + (i % 5) * 0.12,
  opacity: 0.07 + (i % 4) * 0.05,
  color: [GREEN, BLUE, AMBER][i % 3],
}));

export const FloatingParticles: React.FC = () => {
  const f = useCurrentFrame();

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {PARTICLES.map((p, i) => {
        const pulse = interpolate(
          Math.sin(f * 0.04 + i * 0.9),
          [-1, 1],
          [0.4, 1]
        );
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${p.x + Math.sin(f * 0.015 + i) * 4}%`,
              top: `${((p.y + f * p.speed * 0.08) % 115) - 8}%`,
              width: p.size,
              height: p.size,
              borderRadius: "50%",
              background: p.color,
              opacity: p.opacity * pulse,
              boxShadow: `0 0 ${p.size * 4}px ${p.color}40`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
