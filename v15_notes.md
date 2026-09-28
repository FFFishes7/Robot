# v15 notes — slow camera steps fixed on the v13 base

Goal: v13's smooth camera, minus every slow stray step; no side effects (v14 made the pans stepped).

## What was wrong
Godot renders `world.position = -(cam*5).round()`, so the camera lands on OUTPUT pixels (1/5 native).
- **v13**: whenever the camera moved slower than ~1 output px per 2 frames, the film showed isolated 1-px whole-frame
  jumps (scan of `robot_story_full_13.mp4` with `kit/v14/scan_jitter.py`):
  - drift (50,8) -> (52,6) over f80-586: jumps at f205, 247, 283, 318, 351, 386, 519 in a still shot;
  - smoothstep ease tails of the dusk push (f594, 598, 646, 648) and the ring pull;
  - epilogue follow spring: its target came from the standing robot (cx 236), so the camera swung right to x 60 before
    panning left, y went 6 -> 0.5 -> 2 -> 0, and the asymptotic tail crept single pixels until f1197.
- **v14** (`kit/v14/cam14.py`) moved every step by whole native px (5 output px). Scan of `robot_story_full_14.mp4`:
  dusk push / ring pull = one 5-px jump every 3 frames; the final pan = 5-px jumps at irregular 1-2 frame gaps next to
  the walking robot; the intro pan alternates 0/5/10-px x steps. That is the v14 stutter.

## Fix (build code)
- `kit/v15/cam15.py` -> `timeline15.json` (timeline13 with only `cam` replaced): the camera is HOLD (exactly still) or
  MOVE, always whole output px.
  - drift removed: hold (50,8) from f80 to the dusk push;
  - each move keeps the v13 smoothstep speed shape with a floor of 0.5 output px/frame on its dominant axis, so it
    steps at least every 2 frames from start to end (no isolated tail steps), one direction per axis;
  - epilogue: one move (50,6) -> (0,0) from f1085 (where the v13 spring started) to f1161 (robot reaches the window
    corner, first `corner_bl`); robot centre stays at 559-940 output px on screen (v13: 551-929).
  - framings unchanged: intro (0,72) -> (50,8) f10-80, dusk push -> (58,4) f586-666, ring pull -> (50,6) f758-788.
- As in v13, frames inside a move sit on output px, so they are off the x5 native grid by 1-4 px as a whole
  (`kit/v14/grid_check.py` will flag them); holds are on the grid. This is what keeps the pans smooth.
- Night panorama tilt: v14's `panorama14` (layers stop together at the top) is kept; it was already on the native
  grid in v13 and v14 and is not a source of the v14 stutter.
- `kit/v15/render15.py` (Godot wide renders from timeline15 to build/w15_*, Windows or Linux; checks every chunk for
  frames that repeat although the timeline changed), `kit/v15/assemble15.py` (makes the page-turn patches, then the
  close-up sampler reads timeline15 and the w15 renders). Close-up crops are identical to v13.
- Everything the v15 build reads or writes is inside the repository (`kit/paths.py`; renders in `build/`, Pixelify Sans
  in `kit/fonts/`); `godot/main12.gd` finds `kit/` from the project location.
- Audio, cut and timing identical to v13 (`audio/robot_story_13_mix.wav`, 1826 frames).

## Room: armchair group no longer interpenetrates
Props whose floor base lines were within 1-2 px of each other overlapped (the v11 fix only drew the side table behind
the armchair): armchair x side table (111 px), basket x armchair (66 px), the basket's yarn strand x armchair (26 px).
From the robot's walk/sweep area (world x <= 299-313) to the wardrobe (x 405) there is no room for all four side by
side, so (world px, edited in `kit/v09/layer_*.png`, `albedo09.png` rebuilt with `prep9.py`):
- side table (+ lamp, teacup, the lamp-shade glow in `kit/v07/layer_emit.png` / `emit_lamps07.png`) and plant: +4 x;
- armchair: -4 x; basket + yarn: -3 x, +9 y, now standing in front of the armchair (base y133 vs y125) and drawn after
  it (`prep9.py` order); its top stays below the robot's standing zone (y <= 109) and the dust specks (y <= 113);
- shadows and contact shadows moved with their props (pixels assigned to each prop's ellipse / rect, shapes unchanged);
- table-lamp lights `lamp` / `lamp_core` +4 x in `kit/tiled/make_tmx07.py` (attic07.tmx/.json regenerated, Tiled 1.12.2);
- slippers redrawn so they read as slippers: a pair side by side, cream opening behind a blue felt toe (was two 8x4
  red blobs next to the red armchair).
- record sleeves: -3 x, so they stand against the cabinet's left side (touching, no longer inside it); shadow moved.
- resting broom (`kit/robot09/drawings09.py`: `Tw, Cw` (250,61),(241,75) -> (255,61),(251,75), ~16 deg lean, plus the
  lean / grab in-between poses and hand positions): the bristles lay under his feet (x 289-301 vs feet 286-291 at the same
  depth), so he seemed to stand on the broom. Now bristles x 301-312 vs feet <= 298 (world), and the broom never
  overlaps the armchair or the basket (the robot layer draws over the room). 256 frames regenerated (`_a`, `_s`); the 8
  hand-edited `sit*_e` / `sleep_e` frames are unchanged. Close-up crops move 2-3 px (task, cal) to keep the broom in frame.
- broom / robot / dustpan depth: a broom held in front of him was drawn over his legs while its bristle base (y 79) sat
  behind his feet (y 81), so it read as lying on his feet; `drawings09.py` now moves a front-held broom down 3 px (bristle
  base below the feet; hands on the handle and dust puffs follow; a broom behind him is unchanged). The dustpan is part
  of the room and the robot layer draws over it, so the first sweep strokes lay on top of it: the dustpan (+ shadow)
  moves -14 x (Lua 197-212) so the bristles stop at its lip, and the dust stages gather at x 212 instead of 226
  (`kit/v07/prep7.py`, dust1-7 regenerated; its other outputs are unchanged).
- Check over all 195 drawings used in the film x the 46 room props: the robot or broom never draws over a prop whose base
  line is in front of his feet (the only hits are the window seat while he stands / sits on it).
The remaining same-depth overlaps are intended contact (desk/chair, curtains, lamp cord).
`kit/aseprite/room09.lua` still has the old positions (as after the v11/v12 layer edits, the layer PNGs are the source).

## Check
`python3 kit/v15/cam15.py` prints `bad: []` (no step in a hold, no reversal, no gap > 2 frames inside a move, every
frame on whole output px). After rendering, `kit/v14/scan_jitter.py` on the v15 film should show whole-frame shifts
only inside f12-80, 588-666, 760-788, 1087-1161 and the night tilt.
