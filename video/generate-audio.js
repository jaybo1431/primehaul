const fs = require("fs");
const path = require("path");

const API_KEY = process.env.ELEVENLABS_API_KEY || "sk_37d6b8b433874b0dde1d2305ce31dcd961d6bf2cd8fad32b";
const VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"; // George — British male, turbo v2.5

const scenes = [
  {
    file: "s1.mp3",
    text: "PrimeHaul. Stop quoting blind. Start quoting smart.",
  },
  {
    file: "s2.mp3",
    text: "You're driving across town for site visits that go nowhere. By the time you send a quote, the customer's already booked someone else.",
  },
  {
    file: "s3.mp3",
    text: "With PrimeHaul, you send a link. Your customer drops a pin, snaps a few photos room by room, and that's it. Five minutes, done.",
  },
  {
    file: "s4.mp3",
    text: "Our AI scans every photo and identifies each item. Sofas, wardrobes, boxes. It calculates the exact volume and weight. No guesswork.",
  },
  {
    file: "s5.mp3",
    text: "The survey lands on your dashboard with the full inventory. Set your price, hit approve, and your customer gets the quote instantly. They pay a deposit through Stripe. Job locked in.",
  },
  {
    file: "s6.mp3",
    text: "Quote ten times faster. Win thirty percent more jobs. Zero wasted site visits.",
  },
  {
    file: "s7.mp3",
    text: "Try it free today. PrimeHaul dot co dot UK.",
  },
];

async function generate() {
  const outDir = path.join(__dirname, "public");
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

  for (const scene of scenes) {
    console.log(`Generating ${scene.file}...`);
    try {
      const response = await fetch(
        `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`,
        {
          method: "POST",
          headers: {
            "xi-api-key": API_KEY,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: scene.text,
            model_id: "eleven_turbo_v2_5",
            voice_settings: {
              stability: 0.25,
              similarity_boost: 0.7,
              style: 0.7,
              use_speaker_boost: true,
            },
          }),
        }
      );

      if (!response.ok) {
        const err = await response.text();
        throw new Error(`HTTP ${response.status}: ${err}`);
      }

      const buffer = Buffer.from(await response.arrayBuffer());
      fs.writeFileSync(path.join(outDir, scene.file), buffer);
      console.log(`  Done: ${scene.file} (${buffer.length} bytes)`);
    } catch (err) {
      console.error(`  FAILED: ${scene.file} - ${err.message}`);
    }
  }

  console.log("\nAll done!");
}

generate();
