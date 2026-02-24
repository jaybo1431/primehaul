import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  spring,
} from "remotion";
import { BG, GREEN, BLUE, AMBER, WHITE } from "../helpers/colors";
import { S4_DUR, FPS } from "../helpers/timing";
import { useEnvelope, useFadeIn, clamp } from "../helpers/animations";
import { FloatingParticles } from "../components/FloatingParticles";
import { Vignette } from "../components/Vignette";

const DETECTED_ITEMS = [
  { name: "3-Seater Sofa", cbm: "1.80", weight: "45kg", delay: 80, x: 10, y: 10 },
  { name: "Double Wardrobe", cbm: "2.14", weight: "62kg", delay: 110, x: 52, y: 8 },
  { name: "Dining Table + 4 Chairs", cbm: "1.45", weight: "38kg", delay: 140, x: 6, y: 52 },
  { name: "Moving Boxes x12", cbm: "3.60", weight: "84kg", delay: 170, x: 52, y: 50 },
];

export const Scene4AImagic: React.FC = () => {
  const f = useCurrentFrame();
  const env = useEnvelope(S4_DUR);
  const title = useFadeIn(5, 14, 12);

  const scanProgress = interpolate(f, [30, 170], [0, 100], clamp);
  const scanOpacity = interpolate(f, [30, 50, 160, 180], [0, 0.8, 0.8, 0], clamp);

  // Accuracy badge
  const accuracyProg = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: 200, durationInFrames: 18, config: { damping: 8 } });

  // Totals
  const totalsProg = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: 250, durationInFrames: 18, config: { damping: 8 } });
  const totalCBM = interpolate(f, [250, 290], [0, 8.99], clamp);
  const totalWeight = interpolate(f, [250, 290], [0, 229], clamp);
  const totalItems = interpolate(f, [250, 290], [0, 24], clamp);

  // Quote
  const quoteAppear = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: 310, durationInFrames: 18, config: { damping: 7, stiffness: 140 } });
  const priceCount = interpolate(f, [310, 345], [0, 849], clamp);

  return (
    <AbsoluteFill style={{ background: BG, ...env }}>
      <FloatingParticles />

      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 22 }}>
        <div style={{ fontSize: 32, fontFamily: "monospace", color: BLUE, letterSpacing: 8, textTransform: "uppercase", ...title }}>
          AI-Powered Accuracy
        </div>

        {/* Photo analysis area */}
        <div style={{ width: 780, height: 360, background: "#111118", borderRadius: 18, border: `1px solid ${BLUE}25`, position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, backgroundImage: `linear-gradient(${BLUE}06 1px, transparent 1px), linear-gradient(90deg, ${BLUE}06 1px, transparent 1px)`, backgroundSize: "36px 36px" }} />

          {/* Furniture shapes */}
          <div style={{ position: "absolute", left: "10%", top: "12%", width: 130, height: 60, background: `${BLUE}08`, borderRadius: 6, border: `1px solid ${BLUE}15` }} />
          <div style={{ position: "absolute", left: "55%", top: "8%", width: 110, height: 80, background: `${BLUE}08`, borderRadius: 6, border: `1px solid ${BLUE}15` }} />
          <div style={{ position: "absolute", left: "6%", top: "54%", width: 140, height: 65, background: `${BLUE}08`, borderRadius: 6, border: `1px solid ${BLUE}15` }} />
          <div style={{ position: "absolute", left: "54%", top: "52%", width: 130, height: 60, background: `${BLUE}08`, borderRadius: 6, border: `1px solid ${BLUE}15` }} />

          {/* Scan line */}
          <div style={{ position: "absolute", left: `${scanProgress}%`, top: 0, width: 3, height: "100%", background: `linear-gradient(180deg, transparent 5%, ${GREEN} 30%, ${GREEN} 70%, transparent 95%)`, boxShadow: `0 0 24px ${GREEN}60, -30px 0 40px ${GREEN}15`, opacity: scanOpacity }} />

          {/* Detected items */}
          {DETECTED_ITEMS.map((item, i) => {
            const prog = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: item.delay, durationInFrames: 16, config: { damping: 8 } });
            return (
              <div key={i} style={{ position: "absolute", left: `${item.x}%`, top: `${item.y}%`, opacity: prog, transform: `scale(${interpolate(prog, [0, 1], [0.5, 1])})` }}>
                <div style={{ background: `${GREEN}dd`, color: "#000", padding: "4px 10px", borderRadius: 5, fontSize: 15, fontFamily: "monospace", fontWeight: 700, whiteSpace: "nowrap", marginBottom: 4 }}>
                  {item.name}
                </div>
                <div style={{ display: "flex", gap: 5 }}>
                  <div style={{ background: `${BLUE}cc`, color: "#fff", padding: "3px 7px", borderRadius: 4, fontSize: 12, fontFamily: "monospace" }}>
                    {item.cbm} m³
                  </div>
                  <div style={{ background: `${AMBER}cc`, color: "#000", padding: "3px 7px", borderRadius: 4, fontSize: 12, fontFamily: "monospace" }}>
                    {item.weight}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Accuracy badge overlay */}
          <div style={{
            position: "absolute",
            top: 12,
            right: 12,
            opacity: accuracyProg,
            transform: `scale(${interpolate(accuracyProg, [0, 1], [0.5, 1])})`,
            background: `${GREEN}18`,
            border: `1px solid ${GREEN}50`,
            borderRadius: 8,
            padding: "6px 14px",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}>
            <div style={{ fontSize: 14 }}>🎯</div>
            <div style={{ fontSize: 13, fontFamily: "monospace", color: GREEN, fontWeight: 700 }}>
              Trained on 10,000+ items
            </div>
          </div>
        </div>

        {/* Totals row */}
        <div style={{ display: "flex", gap: 24, opacity: totalsProg, transform: `translateY(${interpolate(totalsProg, [0, 1], [12, 0])}px)` }}>
          {[
            { label: "Total Volume", value: `${totalCBM.toFixed(2)} m³`, color: BLUE },
            { label: "Total Weight", value: `${Math.floor(totalWeight)} kg`, color: AMBER },
            { label: "Items Detected", value: `${Math.floor(totalItems)}`, color: GREEN },
          ].map((stat, i) => (
            <div key={i} style={{ background: `${stat.color}10`, border: `1px solid ${stat.color}30`, borderRadius: 10, padding: "10px 24px", display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
              <div style={{ fontSize: 13, fontFamily: "monospace", color: "#aaa", textTransform: "uppercase" }}>{stat.label}</div>
              <div style={{ fontSize: 28, fontWeight: 900, fontFamily: "monospace", color: stat.color }}>{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Quote price */}
        <div style={{ opacity: quoteAppear, transform: `scale(${interpolate(quoteAppear, [0, 1], [0.6, 1])})`, display: "flex", alignItems: "center", gap: 20, background: `${GREEN}10`, border: `2px solid ${GREEN}40`, borderRadius: 14, padding: "14px 36px" }}>
          <div style={{ fontSize: 20, color: "#aaa", fontFamily: "monospace", textTransform: "uppercase" }}>Suggested Quote</div>
          <div style={{ fontSize: 52, fontWeight: 900, fontFamily: "monospace", color: GREEN, textShadow: `0 0 24px ${GREEN}40` }}>
            £{Math.floor(priceCount)}
          </div>
        </div>
      </AbsoluteFill>

      <Vignette />
    </AbsoluteFill>
  );
};
