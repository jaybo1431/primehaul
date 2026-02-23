import React from "react";
import { useCurrentFrame, interpolate, spring } from "remotion";
import { FPS } from "../helpers/timing";
import { clamp } from "../helpers/animations";

export const StatCounter: React.FC<{
  value: string;
  label: string;
  color: string;
  delay?: number;
}> = ({ value, label, color, delay = 0 }) => {
  const f = useCurrentFrame();

  const prog = spring({
    frame: f,
    fps: FPS,
    from: 0,
    to: 1,
    delay,
    durationInFrames: 22,
    config: { damping: 8, stiffness: 160 },
  });

  const countUp = interpolate(f, [delay, delay + 30], [0, 1], clamp);
  const shake =
    f > delay && f < delay + 8 ? Math.sin(f * 45) * 3 : 0;
  const glow = interpolate(Math.sin(f * 0.08), [-1, 1], [0.6, 1]);

  return (
    <div
      style={{
        opacity: prog,
        transform: `scale(${interpolate(prog, [0, 1], [0.3, 1])}) translateX(${shake}px)`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
        padding: "32px 48px",
        background: `${color}08`,
        border: `1px solid ${color}25`,
        borderRadius: 20,
        minWidth: 280,
      }}
    >
      <div
        style={{
          fontSize: 96,
          fontWeight: 900,
          fontFamily: "monospace",
          color,
          opacity: countUp,
          textShadow: `0 0 ${30 * glow}px ${color}60`,
          letterSpacing: -3,
        }}
      >
        {value}
      </div>
      <div
        style={{
          fontSize: 24,
          color: "#ccc",
          fontFamily: "sans-serif",
          textAlign: "center",
          maxWidth: 240,
          lineHeight: 1.3,
        }}
      >
        {label}
      </div>
    </div>
  );
};
