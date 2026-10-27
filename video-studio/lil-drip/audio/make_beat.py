# Synthesizes a 20-second beat for the Lil Drip video. Deterministic: seeded noise, no external files.
import math, random, struct, wave

SR = 44100
DUR = 20.0
N = int(SR * DUR)
BPM = 92
BEAT = 60.0 / BPM
rng = random.Random(7)
buf = [0.0] * N

def add(start, length, fn):
    i0 = int(start * SR)
    for i in range(int(length * SR)):
        j = i0 + i
        if 0 <= j < N:
            buf[j] += fn(i / SR)

def kick(t):
    # sine sweep 130 -> 45 Hz, exponential decay
    f = 45 + 85 * math.exp(-28 * t)
    return 0.9 * math.exp(-9 * t) * math.sin(2 * math.pi * (45 * t + (85 / 28) * (1 - math.exp(-28 * t))))

def hat(t):
    return 0.18 * math.exp(-60 * t) * (rng.random() * 2 - 1)

def pluck(freq):
    return lambda t: 0.25 * math.exp(-5 * t) * math.sin(2 * math.pi * freq * t)

def swoosh(t):
    # filtered-noise sweep for the paint wipe
    return 0.35 * math.sin(math.pi * min(t / 0.9, 1)) * (rng.random() * 2 - 1)

def boom(t):
    return 1.0 * math.exp(-4 * t) * math.sin(2 * math.pi * (40 * t)) + 0.4 * math.exp(-18 * t) * (rng.random() * 2 - 1)

# four-on-the-floor kick with off-beat hats, starting at 0
beats = int(DUR / BEAT)
for b in range(beats):
    t = b * BEAT
    if t > 8.0 and t < 9.4:   # hold the drums while the paint covers the frame
        continue
    add(t, 0.5, kick)
    add(t + BEAT / 2, 0.08, hat)

# chimes on the three text reveals
for t, f in [(0.3, 660), (4.3, 880), (6.1, 990), (10.0, 330)]:
    add(t, 1.2, pluck(f))
add(8.0, 1.0, swoosh)      # paint wipe
add(9.4, 1.2, boom)        # crash-out hit
add(16.8, 1.2, boom)       # final line

peak = max(abs(x) for x in buf) or 1
scale = 0.85 / peak
with wave.open("audio/beat.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, x * scale)) * 32767)) for x in buf))
print("wrote audio/beat.wav", round(DUR, 1), "s")
