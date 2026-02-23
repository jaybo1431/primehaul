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
    text: "Right now, you're driving across town for site visits that lead nowhere. Customers are waiting days for a quote, and by the time you get back to them, they've already booked someone else. You're losing jobs and burning fuel.",
  },
  {
    file: "s3.mp3",
    text: "With PrimeHaul, you send your customer a simple link. No app to download. No signup. They drop a pin for collection, drop a pin for delivery, then walk room by room snapping photos of everything that needs moving. The whole thing takes five minutes.",
  },
  {
    file: "s4.mp3",
    text: "Here's where it gets clever. Our AI scans every single photo and identifies each item automatically. Sofa, wardrobe, dining table, boxes. It calculates the exact cubic metres and weight for every piece. This isn't guesswork. It's trained on thousands of household items, so your inventory is accurate down to the last box.",
  },
  {
    file: "s5.mp3",
    text: "The completed survey lands straight on your dashboard. You see the full inventory, the measured volume, the total weight. You set your own price. Your rates, your margins, your rules. Hit approve, and your customer gets the quote instantly. They pay a deposit right there through Stripe. Job locked in. No chasing. No back and forth.",
  },
  {
    file: "s6.mp3",
    text: "Removal companies on PrimeHaul quote ten times faster, win thirty percent more jobs, and spend zero hours on wasted site visits. That's more revenue with less driving.",
  },
  {
    file: "s7.mp3",
    text: "Start your free trial today. No credit card needed. PrimeHaul dot co dot UK.",
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
