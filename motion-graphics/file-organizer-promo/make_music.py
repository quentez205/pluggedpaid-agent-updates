"""Generate an original 45-second backing track (no samples, no licensed audio).

Writes music.wav next to this file. Chord pad, bass, kick and hi-hat on a
simple 96 BPM groove, with a fade in and a fade out. Mix it under a voiceover
later by lowering the gain in mux step (see README in the render notes).

Usage: python3 make_music.py [out.wav]
"""
import math
import os
import random
import struct
import sys
import wave

SR = 44100
DUR = 45.0
BPM = 96
BEAT = 60.0 / BPM
CHORD_LEN = 5.0  # two bars per chord, 9 chords = 45s

# Frequencies (Hz) for the chord voicings, root in the bass register.
CHORDS = {
    "Am7": (110.00, [220.00, 261.63, 329.63, 392.00]),
    "Fmaj7": (87.31, [174.61, 220.00, 261.63, 329.63]),
    "C": (130.81, [261.63, 329.63, 392.00]),
    "G": (98.00, [196.00, 246.94, 293.66]),
}
PROGRESSION = ["Am7", "Fmaj7", "C", "G"] * 3
PROGRESSION = PROGRESSION[:9]


def env_pad(t, start, length):
    x = t - start
    if x < 0 or x > length:
        return 0.0
    attack = min(1.0, x / 1.2)
    release = min(1.0, (length - x) / 1.2)
    return attack * release


def sample(i, rng):
    t = i / SR
    out = 0.0

    # Pad: each chord's tones, slightly detuned pairs for width.
    idx = min(int(t // CHORD_LEN), len(PROGRESSION) - 1)
    root, tones = CHORDS[PROGRESSION[idx]]
    start = idx * CHORD_LEN
    e = env_pad(t, start, CHORD_LEN)
    pad = 0.0
    for f in tones:
        pad += math.sin(2 * math.pi * f * t) + 0.5 * math.sin(2 * math.pi * f * 1.004 * t)
    out += 0.05 * e * pad / len(tones)

    # Bass: eighth-note pulses on the root, short decay per note.
    eighth = BEAT / 2
    k = int(t / eighth)
    tk = t - k * eighth
    bass_env = math.exp(-tk * 7.0)
    if k * eighth < DUR and k % 2 == 0:
        out += 0.22 * bass_env * math.sin(2 * math.pi * root * t)

    # Kick on each beat: pitch sweep 120 -> 45 Hz.
    beat_i = int(t / BEAT)
    tb = t - beat_i * BEAT
    if tb < 0.35 and beat_i * BEAT < DUR:
        f = 45 + 75 * math.exp(-tb * 25)
        out += 0.5 * math.exp(-tb * 9) * math.sin(2 * math.pi * f * tb)

    # Hi-hat on offbeat eighths: short noise burst.
    off = (k * eighth) + eighth / 2
    if k % 2 == 1 and abs(t - off) < 0.03:
        out += 0.06 * rng.uniform(-1, 1) * math.exp(-(t - off + 0.03) * 120)

    return out


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "music.wav")
    rng = random.Random(7)
    n = int(SR * DUR)
    samples = [sample(i, rng) for i in range(n)]

    # Fade in 1s, fade out 2.5s, then normalize peak to -3 dBFS.
    fin, fout = int(1.0 * SR), int(2.5 * SR)
    for i in range(n):
        g = 1.0
        if i < fin:
            g = i / fin
        if i > n - fout:
            g *= (n - i) / fout
        samples[i] *= g
    peak = max(abs(s) for s in samples) or 1.0
    target = 10 ** (-3 / 20)
    scale = target / peak

    with wave.open(out_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = b"".join(struct.pack("<h", int(max(-1, min(1, s * scale)) * 32767)) for s in samples)
        w.writeframes(frames)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
