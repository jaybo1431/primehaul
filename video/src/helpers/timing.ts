export const FPS = 30;
export const TRANS = 18;

// Scene durations (frames) — matched to ElevenLabs audio + 1s buffer
export const S1_DUR = 150;  // Intro (5s)    — audio: 3.9s
export const S2_DUR = 396;  // The Problem (13.2s) — audio: 12.1s
export const S3_DUR = 510;  // Customer Flow (17s) — audio: 16.0s
export const S4_DUR = 672;  // AI Magic (22.4s) — audio: 21.4s
export const S5_DUR = 684;  // Boss Dashboard (22.8s) — audio: 21.7s
export const S6_DUR = 378;  // Results (12.6s) — audio: 11.5s
export const S7_DUR = 210;  // CTA (7s)      — audio: 6.0s

// Scene start frames
export const S1_START = 0;
export const S2_START = S1_DUR;
export const S3_START = S2_START + S2_DUR;
export const S4_START = S3_START + S3_DUR;
export const S5_START = S4_START + S4_DUR;
export const S6_START = S5_START + S5_DUR;
export const S7_START = S6_START + S6_DUR;

export const TOTAL_FRAMES = S7_START + S7_DUR; // 3000 frames = 100s
