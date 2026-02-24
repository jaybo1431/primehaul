export const FPS = 30;
export const TRANS = 18;

// Scene durations (frames) — matched to ElevenLabs audio + 1s buffer
export const S1_DUR = 140;  // Intro (4.7s)    — audio: 3.7s
export const S2_DUR = 250;  // The Problem (8.3s) — audio: 7.3s
export const S3_DUR = 294;  // Customer Flow (9.8s) — audio: 8.8s
export const S4_DUR = 352;  // AI Magic (11.7s) — audio: 10.7s
export const S5_DUR = 380;  // Boss Dashboard (12.7s) — audio: 11.7s
export const S6_DUR = 208;  // Results (6.9s) — audio: 5.9s
export const S7_DUR = 136;  // CTA (4.5s)      — audio: 3.5s

// Scene start frames
export const S1_START = 0;
export const S2_START = S1_DUR;
export const S3_START = S2_START + S2_DUR;
export const S4_START = S3_START + S3_DUR;
export const S5_START = S4_START + S4_DUR;
export const S6_START = S5_START + S5_DUR;
export const S7_START = S6_START + S6_DUR;

export const TOTAL_FRAMES = S7_START + S7_DUR; // 1760 frames ≈ 58.7s
