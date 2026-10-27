#!/usr/bin/env bash
# Re-check the video toolchain end to end. Run from /home/user/video-studio.
set -euo pipefail
cd "$(dirname "$0")"
echo "== versions"
node -v; ffmpeg -version | head -1; npx --no-install hyperframes --version
npx --no-install remotion versions 2>/dev/null | head -3 || true
echo "== hyperframes render"
(cd hf-test && npx --yes hyperframes@0.8.209 render --output renders/verify.mp4 >/dev/null 2>&1)
ffprobe -v error -show_entries format=duration -of csv=p=0 hf-test/renders/verify.mp4
echo "== remotion render"
(cd remotion-test && npx remotion render HelloWorld out/verify.mp4 >/dev/null 2>&1)
ffprobe -v error -show_entries format=duration -of csv=p=0 remotion-test/out/verify.mp4
echo "ALL OK"
