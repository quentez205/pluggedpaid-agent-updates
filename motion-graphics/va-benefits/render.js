// Renders index.html to an MP4 by pausing every CSS animation and stepping
// it to an exact timestamp for each frame, so the output is deterministic.
//
// Usage: node render.js [outputMp4] [framesDir]
// Requires: playwright (Chromium) and ffmpeg on PATH.

const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');

const FPS = 30;
const DURATION = 45; // seconds
const WIDTH = 1920;
const HEIGHT = 1080;

const here = __dirname;
const outFile = path.resolve(process.argv[2] || path.join(here, 'ai-avatars-45s.mp4'));
const framesDir = path.resolve(process.argv[3] || path.join(here, '.frames'));

(async () => {
  fs.rmSync(framesDir, { recursive: true, force: true });
  fs.mkdirSync(framesDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT } });
  await page.goto('file://' + path.join(here, 'index.html'));
  await page.evaluate(() => document.fonts.ready);

  // Pause everything so only our explicit timestamps drive the picture.
  await page.evaluate(() => {
    document.getAnimations().forEach((a) => a.pause());
  });

  const total = DURATION * FPS;
  for (let i = 0; i < total; i++) {
    const t = i / FPS;
    await page.evaluate((ms) => {
      document.getAnimations().forEach((a) => { a.currentTime = ms; });
    }, t * 1000);
    const file = path.join(framesDir, `frame_${String(i).padStart(5, '0')}.jpg`);
    await page.screenshot({ path: file, type: 'jpeg', quality: 95 });
    if (i % 150 === 0) console.log(`frame ${i}/${total} (t=${t.toFixed(2)}s)`);
  }

  await browser.close();

  execFileSync('ffmpeg', [
    '-y',
    '-framerate', String(FPS),
    '-i', path.join(framesDir, 'frame_%05d.jpg'),
    '-c:v', 'libx264',
    '-preset', 'slow',
    '-crf', '17',
    '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart',
    outFile,
  ], { stdio: 'inherit' });

  fs.rmSync(framesDir, { recursive: true, force: true });
  console.log('wrote', outFile);
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
