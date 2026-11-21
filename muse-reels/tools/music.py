"""Generate the upbeat background loop for the Muse reels.

120 bpm, C major, I-V-vi-IV. Ukulele-style plucks (Karplus-Strong), bass,
glockenspiel melody, soft kick, clap and shaker. Exactly 60 seconds, ending
on a ringing C chord. Mixed quietly so a voiceover sits on top.

Usage: python3 music.py out.wav
"""
import sys
import wave
import numpy as np

SR = 44100
DUR = 60.0
BEAT = 0.5          # 120 bpm
BAR = 4 * BEAT
N = int(SR * DUR)
rng = np.random.default_rng(7)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def pluck(f, dur, vel=1.0):
    n = int(dur * SR)
    P = max(2, int(SR / f))
    y = np.zeros(n + P + 1)
    noise = rng.uniform(-1, 1, P)
    noise = 0.5 * (noise + np.roll(noise, 1))  # soften the attack
    y[1:P + 1] = noise
    k = P + 1
    while k < n + P + 1:
        e = min(k + P, n + P + 1)
        y[k:e] = 0.4985 * (y[k - P:e - P] + y[k - P - 1:e - P - 1])
        k = e
    out = y[P + 1:P + 1 + n]
    t = np.arange(n) / SR
    out *= np.minimum(1, (dur - t) / 0.05)  # short release
    return out * vel


def bass(f, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.008) * (0.55 + 0.45 * np.exp(-t * 5)) * np.minimum(1, (dur - t) / 0.04)
    return vel * env * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t))


def glock(f, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.003) * np.exp(-t * 4.5)
    return vel * env * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 9)
                        + 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 14))


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 85 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 11)


def noise_hit(dur, decay, hp=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.uniform(-1, 1, n)
    if hp:
        x = np.diff(np.concatenate([[0], x]))
    return x * np.exp(-t * decay)


L = np.zeros(N)
R = np.zeros(N)


def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N:
        return
    sig = sig[:N - i]
    L[i:i + len(sig)] += sig * gain * (1 - pan) * 0.5 ** 0.5 * 1.2
    R[i:i + len(sig)] += sig * gain * (1 + pan) * 0.5 ** 0.5 * 1.2


CHORDS = [  # (bass root, ukulele voicing)
    (36, [60, 64, 67, 72]),  # C
    (43, [55, 59, 62, 67]),  # G
    (45, [57, 60, 64, 69]),  # Am
    (41, [53, 57, 60, 65]),  # F
]
MELODY = [  # per bar: (eighth, midi, length in eighths)
    [(0, 76, 2), (2, 79, 1), (3, 84, 2), (6, 79, 2)],
    [(0, 74, 2), (2, 79, 2), (4, 83, 3)],
    [(0, 84, 2), (2, 81, 1), (3, 76, 2), (6, 81, 2)],
    [(0, 77, 2), (2, 81, 2), (4, 84, 2), (6, 81, 1), (7, 79, 1)],
    [(0, 76, 1), (1, 79, 1), (2, 84, 2), (4, 86, 2), (6, 88, 2)],
    [(0, 86, 3), (3, 83, 1), (4, 79, 4)],
    [(0, 81, 2), (2, 84, 2), (4, 88, 2), (6, 86, 2)],
    [(0, 84, 4), (4, 81, 2), (6, 79, 2)],
]
STRUM = [(0, 1), (2, 1), (3, -1), (5, -1), (6, 1), (7, -1)]  # eighth, direction
E8 = BEAT / 2
BARS = int(DUR / BAR)

for b in range(BARS):
    t0 = b * BAR
    root, voicing = CHORDS[b % 4]
    last = b == BARS - 1
    full = 2 <= b < BARS - 1
    if last:
        for k, m in enumerate(voicing):
            add(pluck(midi(m), 1.9, 0.9), t0 + k * 0.025, 0.34, -0.25)
        add(bass(midi(root), 1.9), t0, 0.32)
        for k, m in enumerate([72, 76, 79, 84, 88]):
            add(glock(midi(m), 1.5), t0 + 0.12 + k * 0.12, 0.2, 0.3)
        add(kick(), t0, 0.45)
        continue
    for e, d in STRUM:
        notes = voicing if d > 0 else voicing[::-1][:3]
        vel = 0.95 if e in (0, 6) else 0.7
        for k, m in enumerate(notes):
            add(pluck(midi(m), E8 * 2.2, vel), t0 + e * E8 + k * 0.012, 0.3, -0.25)
    for s in range(16):
        add(noise_hit(0.06, 70), t0 + s * E8 / 2, 0.045 if s % 2 else 0.07, 0.4)
    if full:
        add(bass(midi(root), BEAT * 1.6), t0, 0.3)
        add(bass(midi(root), BEAT * 0.9), t0 + 2 * BEAT, 0.26)
        add(bass(midi(root + 7), BEAT * 0.9), t0 + 3 * BEAT, 0.22)
        for beat in (0, 2):
            add(kick(), t0 + beat * BEAT, 0.5)
        add(kick(), t0 + 2.5 * BEAT, 0.25)
        for beat in (1, 3):
            add(noise_hit(0.18, 22), t0 + beat * BEAT, 0.16, -0.1)
        for e, m, ln in MELODY[(b - 2) % 8]:
            add(glock(midi(m), ln * E8 + 0.6), t0 + e * E8, 0.2, 0.3)

# light room ambience: a few early reflections
for d, gn in ((0.083, 0.22), (0.171, 0.14), (0.293, 0.08)):
    i = int(d * SR)
    L[i:] += gn * R[:-i]
    R[i:] += gn * L[:-i]

fade = np.ones(N)
fl = int(0.6 * SR)
fade[-fl:] = np.linspace(1, 0, fl) ** 1.5
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * 0.36, R / peak * 0.36  # about -9 dBFS peak, room for the voice

pcm = (np.stack([L, R], 1) * 32767).astype("<i2")
with wave.open(sys.argv[1] if len(sys.argv) > 1 else "music.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
