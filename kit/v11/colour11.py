"""Palette application for the v11 panorama index maps (hills). Sunset / dusk / night via a palette dict P
(band colours A F G H I D of the room's dusk window) and a night factor nt."""
import numpy as np
def mix(a, b, t): return np.array(a, float) * (1 - t) + np.array(b, float) * t
def hill_colours(P, nt, nrows):
    """per row: 5 tones (deep shadow .. highlight) with atmospheric perspective (far rows lighter/hazier)"""
    out = []
    for k in range(nrows):
        d = k / max(1, nrows - 1)                                   # 0 far .. 1 near
        # sunset: far = hazy rose-violet close to the horizon glow; near = deep plum. night: muted teal ramp
        body_s = mix(mix(P["G"], P["D"], 0.38), (36, 24, 52), d ** 0.7)
        body_n = mix((62, 84, 118), (14, 26, 40), d ** 0.7)
        body = mix(body_s, body_n, nt)
        sh = mix(body, mix((30, 20, 52), (10, 22, 36), nt), 0.45 + 0.1 * d)
        deep = mix(body, mix((22, 14, 40), (6, 14, 26), nt), 0.62 + 0.1 * d)
        lit = mix(body, mix(mix(P["I"], P["H"], 0.3), (100, 150, 150), nt), 0.62 - 0.14 * d)
        hi = mix(body, mix(mix(P["D"], P["I"], 0.4), (150, 190, 184), nt), 0.80 - 0.22 * d)
        rim = mix(mix(hi, lit, min(1.0, nt / 0.3)), (255, 226, 186), 0.5 * max(0.0, 1 - nt / 0.3))
        out.append([deep, sh, body, lit, hi, rim])
    return out
def colour_hills(img, r, P, nt):
    cols = hill_colours(P, nt, r["n"])
    tone = r["tone"].copy()
    # crest-lit, base-dark: tones step down toward each row's valley (clean posterised bands)
    drop = np.floor(r["vf"] * 2.4).astype(int)
    tone = np.clip(tone - drop, 0, 4)
    for k in range(r["n"]):
        m = r["row"] == k
        for t in range(5):
            mm = m & (tone == t)
            img[mm] = cols[k][t]
        img[m & r["rim"]] = cols[k][5]
    return img
