# v14 notes — camera / jitter fix

Goal: no shake or shift that is not a deliberate effect, and every frame on the exact integer native grid (384x216 x5).

## What was wrong in v13 (full scan: `kit/v14/jitter_report_v13.md`)
- **Ultra-slow camera drift** toward the upper right (key (50,8) -> (52,6) eased over f80-586, 2 native px in 21 s).
  The render rounds the camera to OUTPUT pixels, so this came out as isolated 1-output-px whole-frame jumps at
  film f204 (0:08.5), f246 (0:10.25, exactly when the wall device switches to the ✔ screen), 282, 317, 350, 385, 518,
  each leaving the frame 1/5 native px off the grid. Alan's 0:09/0:10 pair: the whole room moved 1 output px down-left;
  the device layer itself has the same canvas and anchor in every state.
- **All camera moves were quantised to output pixels** (1/5 native): 508 of 1826 frames were off the native grid.
- **Robot-follow spring** at f1085-1196 swung right 10 native px, then panned left (back and forth), and its tail
  crept in isolated output-pixel steps until f1196.
- **Night panorama tilt**: the frame top clamped at row 0 (pano f143) while the parallax layers kept following the
  tilt value, so clouds slid 1 native px at a time under a static sky for 17 frames.

## Fix (build code)
- `kit/v14/cam14.py` -> `timeline14.json`: camera is only HOLD or MOVE, always integer native px (render offset = multiple
  of 5 output px). Drift removed (hold (50,8) from f80). Each move steps along its line with a trapezoid speed profile
  whose slowest cadence is 1 native px per 3 frames: monotonic, no isolated steps. Framings unchanged: intro pan
  (0,72)->(50,8) f10-80, dusk push ->(58,4) f586-610 (steady 1 px / 3 frames), ring pull ->(50,6) f758-782, final pan
  ->(0,0) f1084-1168 as the robot walks to the window (robot keeps >= 61 native px margin).
- `kit/v14/panorama14.py`: tilt value ends exactly where the frame top reaches row 0 (76.8 instead of 96), so every
  layer stops together; nothing else changed.
- `kit/v14/assemble14.py`: close-up sampler reads timeline14 and the v14 wide renders (`kit/robot10/render14.sh`, /tmp/w14_*).
- Audio, cut and timing identical to v13 (`audio/robot_story_13_mix.wav`, 1826 frames, 76.08 s).

## Kept on purpose
Hard cuts, the night tilt, cloud drift (1 native px every 11/16/20 frames, one direction), birds, stars, robot
animation, dust motes, page turn.

## Tools
- `kit/v14/scan_jitter.py film out.json` — phase correlation of consecutive frames (whole frame + tiles).
- `kit/v14/grid_check.py film out.json` — share of edges off the x5 native grid per frame.
