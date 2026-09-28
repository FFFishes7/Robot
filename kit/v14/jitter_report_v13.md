# v13 jitter scan (robot_story_full_13_444.mp4)

Method: `kit/v14/scan_jitter.py` phase-correlates every consecutive pair of 1080p frames (whole frame + 120 px tiles).
Shifts are in OUTPUT pixels at 1080p (1 native px = 5 output px); film shift = -(camera step).

## Unintended (fixed in v14)

| film frame | time | shift (dx,dy) out px | cause |
|---|---|---|---|
| 148 | 0:06.17 | (0,0) | same drift step, but inside the world-locked task close-up, so not visible |
| 204 | 0:08.50 | (-1,1) | camera drift (50,8)->(52,6) over f80-586, isolated 1/5-native step off the native grid |
| 246 | 0:10.25 | (-1,1) | camera drift (50,8)->(52,6) over f80-586, isolated 1/5-native step off the native grid — coincides with the wall device switching to the ✔ screen (alarm 'off' at f246); Alan's 0:09/0:10 screenshot pair shows the whole room moved (+1 down, -1 left) output px = this step, the device layer itself has the same canvas/anchor in every state |
| 282 | 0:11.75 | (-1,1) | camera drift (50,8)->(52,6) over f80-586, isolated 1/5-native step off the native grid |
| 317 | 0:13.21 | (-1,1) | camera drift (50,8)->(52,6) over f80-586, isolated 1/5-native step off the native grid |
| 350 | 0:14.58 | (-1,1) | camera drift (50,8)->(52,6) over f80-586, isolated 1/5-native step off the native grid |
| 385 | 0:16.04 | (-1,1) | camera drift (50,8)->(52,6) over f80-586, isolated 1/5-native step off the native grid |
| 518 | 0:21.58 | (-1,1) | camera drift (50,8)->(52,6) over f80-586, isolated 1/5-native step off the native grid |
| 593-647 | 0:24.7-0:27.0 | 1 out px every 1-3 frames | dusk push quantised to output px (off native grid) |
| 760-787 | 0:31.7-0:32.8 | 1-2 out px/frame | ring pull quantised to output px (off native grid) |
| 12-79 | 0:00.5-0:03.3 | 1-7 out px/frame | intro pan quantised to output px (off native grid) |
| 1085-1104 then 1105-1196 | 0:45.2-0:49.8 | x -1..-4 then +1..+9 | follow spring swung right then left (back-and-forth); tail crept single output px at 1163-1196 (isolated steps at 1177, 1180, 1185, 1188, 1196) |
| pano 1634-1650 | 1:08.1-1:08.8 | clouds 1 native px down every few frames under a static sky | night tilt: frame top clamped at row 0 at off~77 while layers kept following off up to 96 |

## Intended (kept)

- Hard cuts (close-ups / sunset / panorama / credits): film frames [92, 153, 393, 475, 649, 744, 940, 992, 1450, 1490].
- Night panorama tilt 1593-1633 (native-px steps per layer, monotonic).
- Cloud drift in the panorama (1 native px every 11/16/20 frames, one direction), birds, star twinkle, robot animation, dust motes, calendar page turn.
- Tile scan during camera holds: no prop/UI/sprite layer shifts found (all tile outliers are the robot walking or low-confidence during pans).

## v14 re-scan (robot_story_full_14_444.mp4)
- Whole-frame shifts outside the 10 hard cuts occur only in 5 motion runs: film 13-80 (intro pan), 589-610 (dusk push),
  761-782 (ring pull), 1087-1168 (pan to the window), 1593-1648 (night tilt). Every shift is a multiple of 5 output px
  (whole native pixels); each run is one-directional per axis; 0 isolated steps; the camera is exactly still in every hold.
- Native grid (`grid_check.py`): 1818/1826 frames have 0% (<2%) edge energy off the x5 grid, all with phase 0.
  The rest are 6 black fade frames and 2 fade frames (474, 1739, 1.4-4.5%, identical in v13) where x264 softens a few
  edges; their dominant phase is still on-grid. v13 had 508 off-grid frames.
- Tile outliers left are false matches on periodic textures (wall panels, rug dots) during pans, checked visually.
