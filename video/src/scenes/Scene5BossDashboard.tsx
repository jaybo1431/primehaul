import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  spring,
} from "remotion";
import { BG, GREEN, BLUE, AMBER, WHITE, GRAY } from "../helpers/colors";
import { S5_DUR, FPS } from "../helpers/timing";
import { useEnvelope, useFadeIn, clamp } from "../helpers/animations";
import { FloatingParticles } from "../components/FloatingParticles";
import { Vignette } from "../components/Vignette";

export const Scene5BossDashboard: React.FC = () => {
  const f = useCurrentFrame();
  const env = useEnvelope(S5_DUR);
  const title = useFadeIn(5, 14, 12);

  // Notification
  const notifProg = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: 15, durationInFrames: 14, config: { damping: 6, stiffness: 200 } });
  const notifShake = f > 15 && f < 23 ? Math.sin(f * 50) * 4 : 0;

  // Job card
  const cardProg = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: 50, durationInFrames: 18, config: { damping: 9 } });

  // Price editing — "Set your price"
  const priceEditProg = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: 140, durationInFrames: 16, config: { damping: 8 } });
  const priceValue = interpolate(f, [155, 200], [849, 925], clamp);
  const priceGlow = f > 155 && f < 220 ? interpolate(Math.sin(f * 0.15), [-1, 1], [0.3, 1]) : 0;

  // Approve — "Hit approve"
  const approveDelay = 230;
  const btnProg = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: approveDelay, durationInFrames: 12, config: { damping: 6, stiffness: 200 } });
  const btnPressed = f > approveDelay + 25;
  const checkProg = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: approveDelay + 28, durationInFrames: 14, config: { damping: 6, stiffness: 180 } });

  // Deposit — "They pay a deposit through Stripe"
  const depositProg = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: 310, durationInFrames: 18, config: { damping: 8 } });
  const depositAmount = interpolate(f, [310, 350], [0, 185], clamp);

  // Revenue
  const revProg = spring({ frame: f, fps: FPS, from: 0, to: 1, delay: 360, durationInFrames: 16, config: { damping: 8 } });

  return (
    <AbsoluteFill style={{ background: BG, ...env }}>
      <FloatingParticles />

      <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 20 }}>
        <div style={{ fontSize: 32, fontFamily: "monospace", color: AMBER, letterSpacing: 8, textTransform: "uppercase", ...title }}>
          Your Dashboard
        </div>

        <div style={{ width: 820, background: "#111118", borderRadius: 18, border: `1px solid ${BLUE}20`, padding: 24, display: "flex", flexDirection: "column", gap: 14 }}>
          {/* Notification */}
          <div style={{ display: "flex", alignItems: "center", gap: 12, opacity: notifProg, transform: `translateX(${notifShake}px)` }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: GREEN, boxShadow: `0 0 12px ${GREEN}80` }} />
            <div style={{ fontSize: 17, fontFamily: "monospace", color: GREEN }}>
              New survey completed — Sarah M. — London → Manchester
            </div>
            <div style={{ fontSize: 14, fontFamily: "monospace", color: GRAY, marginLeft: "auto" }}>Just now</div>
          </div>

          {/* Job card */}
          <div style={{ opacity: cardProg, transform: `translateY(${interpolate(cardProg, [0, 1], [20, 0])}px)`, background: `${BLUE}08`, border: `1px solid ${BLUE}25`, borderRadius: 12, padding: 18, display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 22, fontWeight: 700, color: WHITE, fontFamily: "sans-serif" }}>Sarah M. — 2 Bed Flat</div>
                <div style={{ fontSize: 15, color: GRAY, fontFamily: "monospace", marginTop: 3 }}>24 items • 8.99 m³ • 229 kg</div>
              </div>
              <div style={{ fontSize: 15, fontFamily: "monospace", color: BLUE, background: `${BLUE}15`, padding: "5px 12px", borderRadius: 8 }}>
                Pending Review
              </div>
            </div>

            {/* Inventory tags */}
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" as const }}>
              {["Sofa", "Wardrobe", "Dining Set", "12 Boxes", "Fridge", "Washing Machine"].map((item, i) => (
                <div key={i} style={{ fontSize: 13, fontFamily: "monospace", color: "#aaa", background: `${WHITE}08`, padding: "4px 10px", borderRadius: 5 }}>
                  {item}
                </div>
              ))}
            </div>

            {/* Price setting row */}
            <div style={{ opacity: priceEditProg, transform: `translateY(${interpolate(priceEditProg, [0, 1], [10, 0])}px)`, display: "flex", alignItems: "center", gap: 16, background: `${AMBER}08`, border: `1px solid ${AMBER}30`, borderRadius: 10, padding: "10px 16px" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <div style={{ fontSize: 12, fontFamily: "monospace", color: AMBER, textTransform: "uppercase", letterSpacing: 2 }}>Set Your Price</div>
                <div style={{ fontSize: 11, fontFamily: "monospace", color: GRAY }}>Your rates. Your margins. Your rules.</div>
              </div>
              <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ fontSize: 13, color: GRAY, fontFamily: "monospace", textDecoration: "line-through" }}>£849</div>
                <div style={{ fontSize: 36, fontWeight: 900, fontFamily: "monospace", color: AMBER, textShadow: priceGlow > 0 ? `0 0 ${20 * priceGlow}px ${AMBER}60` : "none" }}>
                  £{Math.floor(priceValue)}
                </div>
              </div>
            </div>

            {/* Approve button */}
            <div style={{ opacity: btnProg, alignSelf: "flex-end" }}>
              {!btnPressed ? (
                <div style={{ background: GREEN, color: "#000", fontWeight: 700, fontSize: 17, fontFamily: "monospace", padding: "10px 28px", borderRadius: 10, boxShadow: `0 0 18px ${GREEN}40` }}>
                  Approve & Send Quote ✓
                </div>
              ) : (
                <div style={{ display: "flex", alignItems: "center", gap: 10, transform: `scale(${checkProg})` }}>
                  <div style={{ fontSize: 30, filter: `drop-shadow(0 0 8px ${GREEN}80)` }}>✅</div>
                  <div style={{ fontSize: 17, fontFamily: "monospace", color: GREEN, fontWeight: 700 }}>QUOTE SENT INSTANTLY</div>
                </div>
              )}
            </div>
          </div>

          {/* Deposit paid card */}
          <div style={{ opacity: depositProg, transform: `translateY(${interpolate(depositProg, [0, 1], [15, 0])}px)`, background: `${AMBER}10`, border: `1px solid ${AMBER}35`, borderRadius: 12, padding: 14, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ fontSize: 24 }}>💳</div>
              <div>
                <div style={{ fontSize: 17, fontWeight: 700, color: AMBER, fontFamily: "monospace" }}>Deposit Paid via Stripe</div>
                <div style={{ fontSize: 13, color: GRAY, fontFamily: "monospace" }}>Job locked in. No chasing required.</div>
              </div>
            </div>
            <div style={{ fontSize: 30, fontWeight: 900, fontFamily: "monospace", color: AMBER, textShadow: `0 0 14px ${AMBER}40` }}>
              £{Math.floor(depositAmount)}
            </div>
          </div>
        </div>
      </AbsoluteFill>

      <Vignette />
    </AbsoluteFill>
  );
};
