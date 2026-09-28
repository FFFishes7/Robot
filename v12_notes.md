# Robot v12 notes (2026-09-28)

## Films
- `robot_story_full_12.mp4` and `robot_story_full_12_444.mp4`. 1920×1080 at 24 fps, 1766 frames (73.6 s).
- Cut and timing are the same as v11. The v10 soundtrack is reused.

## Fixes
1. **Eyes stay off after shutdown.**
   - Powerdown at wide frame 307 (pd1), then standby → sleep → standby until the reboot at 503.
   - The sleep drawing used to add two glowing eye pixels (`sleep_e.png`); it is now empty.
   - `main12.gd` turns off the screen-glow light and the room/robot glow pools whenever the drawing is standby or sleep.
   - From the sit at 1280 on (sunset watch), the antenna-tip emission is also removed from the sit drawings. He faces away, so no eyes show there.
   - Audit: `timeline10.json`, every drawing from 307 on. Wide frames, the cal zoom cut (393–474) and the sunset window zoom all come from the same renders.
   - Backups: `kit/robot09/frames/bak_v11/`.
2. **Dust motes are in room space.**
   - The CPUParticles2D was a child of the moving world node with global coordinates, so emitted motes stayed put on screen while the room panned.
   - They now live in the native 448×288 lit-world viewport (`litvp`): 1-px specks on the native grid, emitted inside the two shaft polygons in room coordinates.
   - They pan with the room and keep the uniform pixel grain (`godot/main12.gd`).
3. **Blue blob by the coat rack removed.** It was a badly shaped leaning umbrella, plus its gold tip pixels at the rack foot. Removed from `kit/v09/layer_coatrack.png` and `albedo09.png` regenerated (backup in `kit/v09/bak_v11/`). The rack now reads as a hat, scarf and towel on a stand.
4. **Panorama redone (`kit/v12/panorama12.py`, `clouds12.py`).**
   - **Framing:** framed higher, horizon at y≈154 of 216, so sky is about 70% and the hills are a low band.
   - **Sky:** bands built from the room's dusk LUT with saturation lifted and a gold horizon; 52 clean bands, no dither rows.
   - **Sun:** right of centre (x=250), with posterised ray wedges and banded glow that fade as it sets.
   - **Clouds:** lit by the low sun, with gold flanks and undersides, rose bodies, violet tops and glow rims. Three small mid-sky cloudlets were added.
   - **Hills:** 7 green ridge rows. Yellow-green lit faces, orange crest rims, teal/violet shade, far rows hazed toward the horizon glow.
   - **Trees:** leafy corner trees made of about 260 individually shaded leaf clumps, with serrated crown edges and branches that start inside the canopy.
   - **Timing:** night arrives earlier (muted teal hills, village lights, Milky Way) and holds before the tilt up to the moon and credits.

## Stills
- `robot_2d_12_panorama_{sunset,dusk,night,night_sky}.png`
- `robot_2d_12_panorama_vs_ref.png`
- `robot_2d_12_wide_night_eyes_off.png`, `robot_2d_12_closeup_cal_eyes_off.png`
- `robot_2d_12_wide_sit.png`, `robot_2d_12_sunset_window.png`
- `robot_2d_12_wide_coatrack.png`
- `robot_2d_12_closeup_{task,face,press}.png`

## Weak spots
- The clouds' inner edges are a little straight and blobby next to Stardew's hand-painted cumulus.
- The corner trees are leafy but a bit uniform, like broccoli.
- The ray wedges end in visible distance steps. This is deliberate posterisation, but it reads graphic.
