import React from "react";
import { useCurrentFrame } from "remotion";
import { GREEN } from "../helpers/colors";

export const PhoneFrame: React.FC<{
  children: React.ReactNode;
  color?: string;
  width?: number;
  height?: number;
}> = ({ children, color = GREEN, width = 220, height = 440 }) => {
  const f = useCurrentFrame();
  const angle = f * 2;

  return (
    <div
      style={{
        position: "relative",
        width,
        height,
        borderRadius: 28,
        padding: 3,
        background: `conic-gradient(from ${angle}deg, ${color}aa, transparent 30%, ${color}50, transparent 60%, ${color}aa)`,
        boxShadow: `0 0 50px ${color}15, 0 20px 60px rgba(0,0,0,0.8)`,
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          borderRadius: 25,
          background: "#111114",
          overflow: "hidden",
          position: "relative",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Notch */}
        <div
          style={{
            width: 50,
            height: 14,
            background: "#0b0b0c",
            borderRadius: "0 0 10px 10px",
            alignSelf: "center",
            flexShrink: 0,
          }}
        />
        {/* Content */}
        <div
          style={{
            flex: 1,
            padding: 8,
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
          }}
        >
          {children}
        </div>
        {/* Home indicator */}
        <div
          style={{
            width: 44,
            height: 3,
            background: "#444",
            borderRadius: 2,
            alignSelf: "center",
            marginBottom: 4,
            flexShrink: 0,
          }}
        />
      </div>
    </div>
  );
};
