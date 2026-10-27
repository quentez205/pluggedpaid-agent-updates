# Video studio

Installed toolchain (versions verified by render, not just install):

| Tool | Version | Location |
|---|---|---|
| Node.js | 22.22.0 | system |
| FFmpeg / FFprobe | 6.1.1 (libx264, libx265, VP9, AV1, AAC, MP3; drawtext, subtitles, xfade, loudnorm, zoompan) | /usr/bin |
| HyperFrames CLI | 0.8.209 | `npx hyperframes` |
| HyperFrames Chrome | Chrome Headless Shell 152 | `~/.cache/hyperframes/chrome` |
| Remotion | 4.0.539 | `remotion-test/` |
| Remotion Chrome | Headless Shell (remotion browser ensure) | `remotion-test/node_modules/.remotion` |

## Projects
- `hf-test/`: HyperFrames composition (`index.html`, GSAP timeline). Render: `cd hf-test && npm run render`. Check: `npm run check`.
- `remotion-test/`: Remotion hello-world (React). Studio: `npm run dev`. Render: `npx remotion render HelloWorld out/x.mp4`. Lint: `npm run lint`.

## Verify
`./verify.sh` re-renders one video in each tool and prints durations.
