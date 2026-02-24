import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  spring,
} from "remotion";
import { BG, GREEN, BLUE, WHITE, GRAY } from "../helpers/colors";
import { S3_DUR, FPS } from "../helpers/timing";
import { useEnvelope, useFadeIn, clamp } from "../helpers/animations";
import { FloatingParticles } from "../components/FloatingParticles";
import { Vignette } from "../components/Vignette";
import { PhoneFrame } from "../components/PhoneFrame";

const getScreen = (f: number): "link" | "map" | "photos" | "done" => {
  if (f < 70) return "link";
  if (f < 160) return "map";
  if (f < 250) return "photos";
  return "done";
};

const LinkScreen: React.FC<{ f: number }> = ({ f }) => {
  const prog = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: 10, durationInFrames: 16, config: { damping: 8 } });
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14 }}>
      <div style={{ fontSize: 36, opacity: prog, transform: `scale(${prog})` }}>🔗</div>
      <div style={{ fontSize: 14, color: GREEN, fontFamily: "monospace", fontWeight: 700, opacity: prog, textAlign: "center" }}>
        NO APP DOWNLOAD
      </div>
      <div style={{ fontSize: 11, color: "#aaa", fontFamily: "monospace", opacity: interpolate(f, [30, 45], [0, 1], clamp), textAlign: "center" }}>
        Customer opens your link
      </div>
      <div
        style={{
          background: `${GREEN}15`,
          border: `1px solid ${GREEN}35`,
          borderRadius: 8,
          padding: "6px 14px",
          fontSize: 10,
          color: GREEN,
          fontFamily: "monospace",
          opacity: interpolate(f, [40, 55], [0, 1], clamp),
        }}
      >
        primehaul.co.uk/quote/abc123
      </div>
    </div>
  );
};

const MapScreen: React.FC<{ f: number }> = ({ f }) => {
  const localF = f - 70;
  const pin1 = spring({ frame: Math.max(0, localF), fps: FPS, from: 0, to: 1, delay: 15, durationInFrames: 15, config: { damping: 6, stiffness: 200 } });
  const pin2 = spring({ frame: Math.max(0, localF), fps: FPS, from: 0, to: 1, delay: 40, durationInFrames: 15, config: { damping: 6, stiffness: 200 } });

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{ fontSize: 13, color: GREEN, fontFamily: "monospace", fontWeight: 700 }}>
        DROP COLLECTION & DELIVERY PINS
      </div>
      <div style={{ flex: 1, background: "#1a1a2e", borderRadius: 8, position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", inset: 0, backgroundImage: `linear-gradient(${GRAY}10 1px, transparent 1px), linear-gradient(90deg, ${GRAY}10 1px, transparent 1px)`, backgroundSize: "24px 24px" }} />
        <div style={{ position: "absolute", left: "25%", top: "30%", transform: `scale(${pin1}) translateY(${interpolate(pin1, [0, 1], [-20, 0])}px)`, fontSize: 28, filter: `drop-shadow(0 2px 4px ${GREEN}60)` }}>📍</div>
        <div style={{ position: "absolute", left: "65%", top: "60%", transform: `scale(${pin2}) translateY(${interpolate(pin2, [0, 1], [-20, 0])}px)`, fontSize: 28, filter: `drop-shadow(0 2px 4px ${BLUE}60)` }}>📍</div>
        <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
          <line x1="30%" y1="36%" x2="68%" y2="65%" stroke={GREEN} strokeWidth={2} strokeDasharray="6 4" opacity={interpolate(Math.max(0, localF), [45, 65], [0, 0.6], clamp)} />
        </svg>
      </div>
      <div style={{ display: "flex", gap: 4, fontSize: 9, fontFamily: "monospace" }}>
        <div style={{ flex: 1, background: `${GREEN}10`, border: `1px solid ${GREEN}30`, borderRadius: 5, padding: "4px 6px", color: "#aaa" }}>📦 12 Oak St, London</div>
        <div style={{ flex: 1, background: `${BLUE}10`, border: `1px solid ${BLUE}30`, borderRadius: 5, padding: "4px 6px", color: "#aaa" }}>🏠 45 Elm Rd, Manchester</div>
      </div>
    </div>
  );
};

const PhotoScreen: React.FC<{ f: number }> = ({ f }) => {
  const localF = f - 160;
  const rooms = [
    { label: "Living Room", icon: "🛋️", delay: 8 },
    { label: "Bedroom", icon: "🛏️", delay: 24 },
    { label: "Kitchen", icon: "🍳", delay: 40 },
    { label: "Garage", icon: "🔧", delay: 56 },
  ];

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{ fontSize: 13, color: GREEN, fontFamily: "monospace", fontWeight: 700 }}>
        ROOM-BY-ROOM PHOTOS
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, flex: 1 }}>
        {rooms.map((room, i) => {
          const prog = spring({ frame: Math.max(0, localF), fps: FPS, from: 0, to: 1, delay: room.delay, durationInFrames: 14, config: { damping: 8 } });
          return (
            <div key={i} style={{ background: `${GREEN}08`, border: `1px solid ${GREEN}20`, borderRadius: 8, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 5, opacity: prog, transform: `scale(${interpolate(prog, [0, 1], [0.6, 1])})` }}>
              <div style={{ fontSize: 24 }}>{room.icon}</div>
              <div style={{ fontSize: 9, color: "#aaa", fontFamily: "monospace" }}>{room.label}</div>
              <div style={{ fontSize: 7, color: GREEN, fontFamily: "monospace" }}>4 photos</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const DoneScreen: React.FC<{ f: number }> = ({ f }) => {
  const localF = f - 250;
  const progress = interpolate(localF, [5, 45], [0, 100], clamp);
  const checkScale = spring({ frame: Math.max(0, localF), fps: FPS, from: 0, to: 1, delay: 50, durationInFrames: 16, config: { damping: 6, stiffness: 200 } });

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 12 }}>
      <div style={{ width: "80%", height: 8, background: "#222", borderRadius: 4, overflow: "hidden" }}>
        <div style={{ width: `${progress}%`, height: "100%", background: `linear-gradient(90deg, ${GREEN}, ${BLUE})`, borderRadius: 4, boxShadow: `0 0 10px ${GREEN}50` }} />
      </div>
      <div style={{ fontSize: 11, color: GRAY, fontFamily: "monospace" }}>{Math.floor(progress)}% complete</div>
      {localF > 48 && (
        <div style={{ fontSize: 48, transform: `scale(${checkScale})`, filter: `drop-shadow(0 0 10px ${GREEN}80)` }}>✅</div>
      )}
      {localF > 60 && (
        <div style={{ fontSize: 14, color: GREEN, fontFamily: "monospace", fontWeight: 700, textAlign: "center", opacity: interpolate(localF, [60, 75], [0, 1], clamp) }}>
          SURVEY COMPLETE
        </div>
      )}
      {localF > 70 && (
        <div style={{ fontSize: 10, color: "#aaa", fontFamily: "monospace", textAlign: "center", opacity: interpolate(localF, [70, 85], [0, 1], clamp) }}>
          Took 4 mins 32 secs
        </div>
      )}
    </div>
  );
};

export const Scene3CustomerFlow: React.FC = () => {
  const f = useCurrentFrame();
  const env = useEnvelope(S3_DUR);
  const screen = getScreen(f);
  const title = useFadeIn(5, 14, 12);

  return (
    <AbsoluteFill style={{ background: BG, ...env }}>
      <FloatingParticles />

      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 28 }}>
        <div style={{ fontSize: 32, fontFamily: "monospace", color: GREEN, letterSpacing: 8, textTransform: "uppercase", ...title }}>
          How It Works
        </div>

        <PhoneFrame color={GREEN} width={300} height={580}>
          {screen === "link" && <LinkScreen f={f} />}
          {screen === "map" && <MapScreen f={f} />}
          {screen === "photos" && <PhotoScreen f={f} />}
          {screen === "done" && <DoneScreen f={f} />}
        </PhoneFrame>

        <div style={{ display: "flex", gap: 14 }}>
          {["Open Link", "Pin Locations", "Snap Photos", "Done"].map((step, i) => {
            const active =
              (i === 0 && screen === "link") ||
              (i === 1 && screen === "map") ||
              (i === 2 && screen === "photos") ||
              (i === 3 && screen === "done");
            return (
              <div key={i} style={{ fontSize: 16, fontFamily: "monospace", color: active ? GREEN : GRAY, padding: "6px 16px", background: active ? `${GREEN}15` : "transparent", border: `1px solid ${active ? GREEN : GRAY}30`, borderRadius: 14 }}>
                {step}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>

      <Vignette />
    </AbsoluteFill>
  );
};
