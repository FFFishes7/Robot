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

## Check
`python3 kit/v15/cam15.py` prints `bad: []` (no step in a hold, no reversal, no gap > 2 frames inside a move, every
frame on whole output px). After rendering, `kit/v14/scan_jitter.py` on the v15 film should show whole-frame shifts
only inside f12-80, 588-666, 760-788, 1087-1161 and the night tilt.
