import json
T = []
def add(n, k): T.extend([n] * k)
for _ in range(3):
    for i in range(1, 9): add(f"sweep{i}", 2)
for n, k in [("stop", 4), ("notice", 6), ("antic", 4), ("look1", 2), ("look2", 2), ("look3", 6), ("look4", 8), ("look4_blink", 3), ("look4", 9)]: add(n, k)
for _ in range(3): add("startle1", 2); add("startle2", 2)
for n, k in [("turn", 8), ("reach_antic", 5), ("reach", 5), ("press", 6), ("release", 4), ("lookback", 4), ("lookback2", 3), ("lookback", 5)]: add(n, k)
assert len(T) == 144, len(T)
alarm = []
for f in range(144):
    if f < 92: alarm.append("idle")
    elif f < 122: alarm.append("ring" if (f - 92) % 5 < 3 else "ring_off")
    else: alarm.append("off")
json.dump({"fps": 24, "robot": T, "alarm": alarm}, open("frames/timeline.json", "w"))
print(len(T))
