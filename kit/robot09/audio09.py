"""v08 soundtrack: CC0 Kenney SFX (footsteps, cloth, page flip, clicks, chime, leather) + sounds synthesised here
(beep, bell ring, servo, clunk, power-down, broom swish, whoosh, wood tock, room tone, birds, crickets, wind)
+ an original music bed composed in code (music box routine motif, pads, piano). Events are placed from the timeline."""
import json, subprocess, numpy as np, sys
from scipy.signal import butter, sosfilt, fftconvolve
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import edl09
SR = 48000; FPS = 24
NOUT = edl09.total(); DUR = NOUT / FPS + 1.0
L = np.zeros(int(DUR * SR)); R = np.zeros_like(L)          # SFX bus
ML = np.zeros_like(L); MR = np.zeros_like(L)              # music bus
AL = np.zeros_like(L); AR = np.zeros_like(L)              # ambience bus
rng = np.random.RandomState(8)
K1 = "/workspace/robot2d/audio/src/kenney_interface-sounds/Audio/"; K2 = "/workspace/robot2d/audio/src/kenney_rpg-audio/Audio/"
def load(p, rate=1.0):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(int(SR / rate)), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)
def put(sig, t, g=1.0, pan=0.0, bus="sfx"):
    i = int(t * SR); n = min(len(sig), len(L) - i)
    if n <= 0 or i < 0: return
    gl, gr = g * np.sqrt(0.5 * (1 - pan)), g * np.sqrt(0.5 * (1 + pan))
    a, b = {"sfx": (L, R), "mus": (ML, MR), "amb": (AL, AR)}[bus]
    a[i:i + n] += sig[:n] * gl; b[i:i + n] += sig[:n] * gr
def tt(n): return np.arange(int(n * SR)) / SR
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def adsr(n, a=0.005, r=0.05):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e
# ---------------- synthesized SFX
def beep():
    out = []
    for f, d in ((1568, 0.07), (2093, 0.09)):
        t = tt(d); s = np.sin(2 * np.pi * f * t) + 0.15 * np.sin(2 * np.pi * 3 * f * t); out.append(s * adsr(len(t), 0.003, 0.02)); out.append(np.zeros(int(0.012 * SR)))
    return np.concatenate(out) * 0.22
def bell_ring(d, f0=1150):
    t = tt(d); ir_t = tt(0.35)
    ir = sum(a * np.sin(2 * np.pi * f0 * m * ir_t) * np.exp(-ir_t / tau) for m, a, tau in ((1, 1, 0.25), (2.32, 0.5, 0.12), (4.25, 0.3, 0.07), (6.63, 0.15, 0.04)))
    imp = np.zeros(len(t)); step = int(SR / 18.0)
    for k in range(0, len(t), step): imp[k] = 1.0 if (k // step) % 2 == 0 else 0.8
    s = fftconvolve(imp, ir)[:len(t) + len(ir_t)]
    return s / np.max(np.abs(s)) * 0.30
def servo(d=0.13):
    t = tt(d); f = 520 + 260 * t / d; s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 90 * t)))
    return lp(s, 3000) * adsr(len(t), 0.01, 0.04) * 0.07
def clunk():
    t = tt(0.16); s = np.sin(2 * np.pi * (70 + 40 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.05)
    s[:200] += rng.randn(200) * 0.4 * np.linspace(1, 0, 200)
    return s * 0.5
def powerdown():
    t = tt(0.6); f = 700 * np.exp(-t * 3.0) + 110; s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    return s * 0.12
def swish(g=1.0):
    d = 0.22 + rng.rand() * 0.06; n = rng.randn(int(d * SR)); e = np.sin(np.linspace(0, np.pi, len(n))) ** 1.5
    c = 2800 + rng.rand() * 1600
    return bp(n, c * 0.5, min(c * 1.8, 20000)) * e * 0.14 * g
def whoosh():
    n = rng.randn(int(0.3 * SR)); e = np.sin(np.linspace(0, np.pi, len(n))) ** 2
    return bp(n, 500, 2400) * e * 0.10
def tock():
    t = tt(0.12); s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau) for f, a, tau in ((820, 1, 0.03), (1370, 0.6, 0.02), (2210, 0.3, 0.012)))
    s[:60] += rng.randn(60) * 0.3
    return s * 0.28
def glitch():
    n = rng.randn(int(0.18 * SR)); gate = (np.sin(2 * np.pi * 37 * tt(0.18)) > 0.3).astype(float)
    return bp(n * gate, 900, 6000) * 0.08
# ---------------- ambience
def brown(d):
    w = np.cumsum(rng.randn(int(d * SR))); w -= lp(w, 1.0, 1); return lp(w, 400) / 400.0
def birds_phrase():
    out = []
    for k in range(rng.randint(3, 7)):
        d = 0.05 + rng.rand() * 0.07; t = tt(d); f0 = 3000 + rng.rand() * 1500; f = f0 + (rng.rand() - 0.3) * 1800 * t / d + 150 * np.sin(2 * np.pi * 38 * t)
        out.append(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.linspace(0, np.pi, len(t))) ** 2); out.append(np.zeros(int((0.03 + rng.rand() * 0.08) * SR)))
    return np.concatenate(out) * 0.035
def crickets(d):
    t = tt(d); car = np.sin(2 * np.pi * 4600 * t); pulse = (np.sin(2 * np.pi * 30 * t) > 0).astype(float)
    group = ((t % 0.7) < 0.1).astype(float)
    return lp(car * pulse * group, 8000) * 0.015
def wind(d):
    n = rng.randn(int(d * SR)); s = lp(n, 420, 2); lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * tt(d) + 1.0)
    return s * lfo * 0.10
# ---------------- music (original, composed here)
def midi(m): return 440.0 * 2 ** ((m - 69) / 12)
def musicbox(m, d=1.2):
    t = tt(d); f = midi(m)
    s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t / (0.55 / k ** 0.6)) for k, a in ((1, 1), (2, 0.28), (3, 0.08), (5.4, 0.05)))
    return s * adsr(len(t), 0.002, 0.05) * 0.10
def piano(m, d=2.2, v=1.0):
    t = tt(d); f = midi(m)
    s = sum((1 / k ** 1.3) * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * np.exp(-t / (1.3 / k ** 0.5)) for k in range(1, 7))
    return lp(s, 3500) * adsr(len(t), 0.004, 0.25) * 0.09 * v
def pad(ms, d, v=1.0):
    t = tt(d); s = np.zeros(len(t))
    for m in ms:
        for det in (-0.12, 0.0, 0.11):
            f = midi(m + det)
            s += sum((1 / k) * np.sin(2 * np.pi * f * k * t + rng.rand() * 6) for k in range(1, 7))
    s = lp(s, 1400, 2) / (len(ms) * 3)
    a = int(min(1.6, d / 3) * SR); e = np.ones(len(t)); e[:a] = np.linspace(0, 1, a) ** 1.5; e[-a:] *= np.linspace(1, 0, a) ** 1.5
    return s * e * 0.10 * v
def sec(f): return f / FPS
mk = edl09.M["marks"]; ow = edl09.out_of_wide; cs = edl09.clip_start
T_task, T_cal, T_face, T_press = sec(cs("task")), sec(cs("cal")), sec(cs("face")), sec(cs("press"))
T_night = sec(ow(mk["cal_cut"] - 70)); T_day2 = sec(ow(mk["day2"])); T_dusk = sec(ow(mk["dusk"])); T_ring = sec(ow(mk["ring"]))
T_click = T_press + 23 / FPS; T_end = NOUT / FPS
# routine motif (C major, 96 bpm) on music box + a soft pluck bass
BEAT = 0.625
MOTIF = [(76, 0), (79, 1), (84, 2), (79, 3), (81, 4), (79, 5), (76, 6), (74, 7), (76, 8), (79, 9), (84, 10), (86, 11), (84, 12), (79, 14)]
BASS = [(48, 0), (55, 2), (53, 4), (55, 6), (48, 8), (55, 10), (53, 12), (55, 14)]
def routine(t0, t1, v=1.0):
    bar = 16 * BEAT; t = t0
    while t < t1:
        for m, b in MOTIF:
            if t + b * BEAT < t1 - 0.2: put(musicbox(m), t + b * BEAT, v, 0.15, "mus")
        for m, b in BASS:
            if t + b * BEAT < t1 - 0.2: put(piano(m - 12, 1.2, 0.6), t + b * BEAT, v * 0.8, -0.1, "mus")
        t += bar
routine(0.8, T_night + 1.0, 0.9)
put(pad([45, 52, 60], T_day2 - T_night + 1.5, 0.8), T_night, 1.0, 0, "mus")                 # night: soft A minor
put(pad([48, 55, 64], 4.0, 0.7), T_cal + 1.2, 1.0, 0, "mus")                               # dawn resolves to C
routine(T_day2, T_dusk + 1.2, 0.85)
# dusk: warm pads swell, slow piano arpeggios (F  Em7  Dm7  Gsus  F)
chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [55, 60, 62, 67], [53, 57, 60, 65]]
cd = (T_ring - T_dusk) / len(chords)
for k, ch in enumerate(chords):
    t0 = T_dusk + k * cd
    put(pad(ch, cd + 1.2, 0.7 + 0.25 * k / len(chords)), t0, 1.0, 0, "mus")
    for j, m in enumerate(ch + [ch[1] + 12]):
        put(piano(m + 12, 2.4, 0.7), t0 + j * cd / 5, 1.0, (j - 2) * 0.2, "mus")
# alarm: a held, uneasy pad under the ring
put(pad([50, 57, 62, 64], T_click - T_ring + 1.5, 0.5), T_ring, 1.0, 0, "mus")
# epilogue theme (F major, 72 bpm): piano melody over pads; the routine motif returns slowly on the music box at the end
B2 = 0.833; T_epi = T_click + 1.6
prog = [[53, 57, 60], [52, 55, 60], [50, 53, 57, 60], [46, 50, 53, 57], [48, 53, 57], [48, 52, 55], [53, 57, 60, 65]]
mel = [(69, 0), (72, 1), (77, 2), (76, 3.5), (74, 4), (72, 5), (69, 6), (67, 7.5), (65, 8), (69, 9), (72, 10), (74, 11), (72, 12), (70, 13), (69, 14), (67, 15),
       (69, 16), (72, 17), (77, 18), (79, 19.5), (77, 20), (76, 21), (74, 22), (72, 23.5), (72, 24), (69, 25), (67, 26), (65, 28)]
for k, ch in enumerate(prog):
    t0 = T_epi + k * 4 * B2
    if t0 > T_end: break
    put(pad(ch, 4 * B2 + 1.5, 0.9 if k < 6 else 1.1), t0, 1.0, 0, "mus")
    put(piano(ch[0] - 12, 3.0, 0.8), t0, 1.0, -0.2, "mus")
for m, b in mel:
    t0 = T_epi + b * B2
    if t0 < T_end - 1.0: put(piano(m, 2.6, 0.95), t0, 1.0, 0.1, "mus")
tail = T_epi + 26 * B2
for m, b in [(77, 0), (81, 1), (84, 2), (81, 3), (82, 4), (81, 5), (77, 6)]:
    if tail + b * B2 * 0.9 < T_end - 0.6: put(musicbox(m + 0, 1.6), tail + b * B2 * 0.9, 0.8, 0.2, "mus")
# ---------------- ambience
put(brown(DUR), 0, 0.5, 0, "amb")
for t0 in np.arange(0.5, T_night, 2.2): put(birds_phrase(), t0 + rng.rand() * 1.2, 0.8, rng.rand() * 1.4 - 0.7, "amb")
for t0 in np.arange(T_cal + 1.8, T_dusk, 2.0): put(birds_phrase(), t0 + rng.rand(), 0.8, rng.rand() * 1.4 - 0.7, "amb")
cr = crickets(T_day2 - T_night); cr *= np.minimum(1, np.minimum(np.arange(len(cr)) / (1.5 * SR), (len(cr) - np.arange(len(cr))) / (1.0 * SR)))
put(cr, T_night + 0.5, 1.0, 0.3, "amb")
wd = wind(T_end - T_dusk + 1); wd *= np.minimum(1, np.arange(len(wd)) / (3 * SR)); put(wd, T_dusk, 1.0, 0.4, "amb")
# ---------------- SFX events from the timeline (wide-frame -> output time)
def mixs(a, b):
    n = max(len(a), len(b)); return np.pad(a, (0, n - len(a))) + np.pad(b, (0, n - len(b)))
foot = [load(K2 + f"footstep0{k}.ogg", 1.25) for k in range(10)]
cloth = [load(K2 + f"cloth{k}.ogg") for k in range(1, 5)]
S = {"beep": lambda g: beep(), "servo": lambda g: servo(), "clunk": lambda g: mixs(clunk(), load(K1 + "toggle_001.ogg") * 0.4),
     "chime": lambda g: load(K1 + "confirmation_002.ogg") * 0.5, "swish": lambda g: swish(), "tock": lambda g: tock(), "powerdown": lambda g: powerdown(),
     "glitch": lambda g: glitch(), "whoosh": lambda g: whoosh(), "cloth": lambda g: cloth[rng.randint(4)] * 0.35,
     "step": lambda g: foot[rng.randint(10)] * 0.35, "climb": lambda g: mixs(load(K2 + "handleSmallLeather.ogg") * 0.4, load(K2 + "creak1.ogg") * 0.3),
     "thump": lambda g: lp(load(K2 + "dropLeather.ogg"), 1800) * 0.5}
PAN = lambda f: 0.0
for (F, s, g) in edl09.M["events"]:
    if s == "ring_start": continue
    t0 = sec(ow(F)); sig = S[s](g)
    put(sig, t0, g, 0.25 if s in ("beep", "chime", "tock") else 0.0)
# v09 ring: three short bursts (startle ~1.4 s, a nag while he sighs ~0.7 s, then from his decision to the click), < 6 s total
RSEG = []
for s_, e_ in edl09.M["ring"]:
    t0 = sec(ow(s_)); t1 = T_click if e_ is None else sec(ow(e_)); RSEG.append((t0, t1))
    dur = t1 - t0; rg = bell_ring(dur + 0.45); env = np.ones(len(rg)); ns = int(dur * SR)
    env[ns:] = np.exp(-np.arange(len(rg) - ns) / (0.09 * SR))
    atk = int(0.02 * SR); env[:atk] *= np.linspace(0, 1, atk)
    gain = 1.0 if e_ is None or s_ == edl09.M["ring"][0][0] else 0.7
    put(rg * env, t0, gain, 0.3)
RING_TOTAL = sum(b - a_ for a_, b in RSEG); print("ring total s", round(RING_TOTAL, 2), RSEG)
# close-up clip sounds (clip-local frames)
for f in range(0, 56, 8): put(beep(), T_task + f / FPS, 1.1, 0.2)
put(glitch(), T_task + 44 / FPS, 0.8); put(servo(), T_task + 48 / FPS, 0.6); put(mixs(clunk(), load(K1 + "toggle_001.ogg") * 0.4), T_task + 56 / FPS, 1.0)
put(load(K2 + "bookFlip2.ogg") * 0.6, T_cal + 22 / FPS, 1.0, 0.1); put(load(K2 + "bookFlip3.ogg") * 0.4, T_cal + 30 / FPS, 1.0, 0.3)
put(servo(0.1), T_face + 10 / FPS, 0.4)
put(whoosh(), T_press + 14 / FPS, 0.5); put(load(K2 + "metalClick.ogg") * 0.6, T_click, 1.0, 0.2); put(load(K1 + "click_001.ogg") * 0.6, T_click, 1.0, 0.2)
put(load(K1 + "confirmation_001.ogg") * 0.35, T_press + 30 / FPS, 1.0, 0.2)
# ---------------- mix: small-room reverb on music + sfx, duck music under the ring, master limit
ir_t = tt(1.6); ir = rng.randn(len(ir_t)) * np.exp(-ir_t / 0.45); ir = lp(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2))
def verb(x, wet): return x + wet * fftconvolve(x, ir)[:len(x)]
duck = np.ones(len(L)); a, b = int(T_ring * SR), int(T_click * SR); duck[a:b] = 0.8
for t0, t1 in RSEG: duck[int(t0 * SR):int((t1 + 0.3) * SR)] = 0.55
duck = np.convolve(duck, np.ones(2400) / 2400, mode="same")
ML2, MR2 = verb(ML, 0.35) * duck, verb(MR, 0.35) * duck
L2, R2 = verb(L, 0.12), verb(R, 0.12)
mixL = 0.85 * ML2 + L2 + 0.8 * AL; mixR = 0.85 * MR2 + R2 + 0.8 * AR
fade = np.ones(len(mixL)); fe = int(T_end * SR); fs = int((T_end - 2.0) * SR); fade[fs:fe] = np.linspace(1, 0, fe - fs); fade[fe:] = 0
fi = int(0.8 * SR); fade[:fi] *= np.linspace(0, 1, fi)
mixL *= fade; mixR *= fade
pk = max(np.max(np.abs(mixL)), np.max(np.abs(mixR))); g = 0.89 / pk
mixL *= g; mixR *= g
st = np.stack([mixL, mixR], 1)[: int(T_end * SR)].astype(np.float32)
import wave
with wave.open("/workspace/robot2d/audio/robot_story_09_mix.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
rms = np.sqrt(np.mean(st ** 2)); print("mix", round(T_end, 2), "s peak gain", round(g, 3), "rms dBFS", round(20 * np.log10(rms), 1),
      {k: round(v, 2) for k, v in dict(task=T_task, night=T_night, cal=T_cal, day2=T_day2, dusk=T_dusk, face=T_face, ring=T_ring, click=T_click, epi=T_epi).items()})
