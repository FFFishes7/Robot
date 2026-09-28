# Assets and licences (robot2d, v02–v04)

## Tools (not shipped with the output)
| Tool | Version | Licence / how obtained |
|---|---|---|
| Godot Engine | 4.7.2 stable | MIT. Used for compositing, lighting, particles and Movie Maker rendering |
| Aseprite | 1.3.18.6 | Compiled from source under the Aseprite EULA (personal use; source build allowed). Used for all sprite and prop drawing via Lua scripts |
| Tiled | 1.11 (apt) | GPL-2.0 for the tool; the maps it produces (attic.tmx, attic04.tmx) are ours |
| Skia m124 | — | BSD-3; Aseprite build dependency |

## Palettes
- The house palette (kit/palette/attic_palette.*) was built by hand for this project.
- Lospec **Resurrect 64** by Kerrie Lake was used for a few accent colours; it is published on Lospec for free use. **Apollo** was downloaded but only used for reference.

## Sprites and art
- **All sprites, tiles and props in the rendered images are custom-drawn** by the scripts in kit/aseprite/ (robot_parts.lua, robot_anim.lua, room.lua, room04.lua).
- itch.io packs we looked at but **did not use**: Sleepless Poetry "Cozy Interior", Ktarsis "Cozy Home 32x32" and moku.px furniture. All are top-down 16/32 px packs, free for commercial use but not redistributable. No pixels from them are in the output.

## Reference images (study only, not shipped, not redistributed)
- refs_games/stardew_*.png: Stardew Valley interior maps from the Stardew Valley Wiki. © ConcernedApe.
- refs_games/tothemoon_*.jpg: To the Moon © Freebird Games.
  - Steam store screenshots (house_blue_night, house_warm_rooms, study_lamp_night, origami_room, lighthouse exterior).
  - Let's Play Archive captures (lighthouse_interior_lamp_room, lighthouse_interior_stairs, house_bedroom_rabbits_piano). Source URLs are in tothemoon_urls.txt.
- The original 5 pixel-short reference screenshots came from a Bilibili repost; the original author is unknown.
- compare_0*.png include cropped reference images for internal side-by-side review only.

## v06 additions
All v06 art (attic ceiling, string lights, side-wing and front-strip props, rocking horse, boxes, the part-based robot sprite
generator and every robot drawing, walk cycle, lighting shaders) is original, drawn procedurally in this repo
(kit/aseprite/room06.lua, kit/robot06/*.py, godot/shaders/*). No third-party art, fonts in-frame, or audio were used.
Reference screenshots in refs_games/ remain reference-only and are not included in any output.

## v07
All new v07 art is original and was made procedurally in this project:
- robot redraw (`robot07.py` / `drawings07.py`)
- room additions (calendar with page overlays, reminder task/pressed-button states, redrawn rocking horse)
- both close-up inserts (`kit/closeups07/`)

No third-party art. The reference video is a Bilibili repost (original author unknown) and was used only as a mood and story reference.

## v08
Art: all new v08 art is original and was made procedurally in this project:
- robot drawings (`kit/robot08/`)
- night and dawn window skies (`kit/v08/prep8.py`)
- device, calendar and press close-ups (`kit/closeups08/`)

Audio (`kit/robot08/audio08.py` builds `audio/robot_story_08_mix.wav`):

Third-party samples, all **CC0 1.0** (public domain, no attribution required):
- **Kenney "RPG Audio"** by Kenney Vleugels (kenney.nl): `footstep00`–`footstep09` (pitched ×1.25, for his footsteps), `cloth1`–`cloth4` (body and cloth movement), `bookFlip2`/`bookFlip3` (calendar page), `metalClick`, `handleSmallLeather` (broom grab), `creak1` (window seat), `dropLeather` (landing). Licence file: `audio/src/kenney_rpg-audio/License.txt`.
- **Kenney "Interface Sounds"** by Kenney Vleugels: `click_001` (button press), `confirmation_001`/`confirmation_002` (check chime), `toggle_001`. Licence file: `audio/src/kenney_interface-sounds/License.txt`.
- Sources were downloaded from kenney.nl. The original zips are kept in `audio/src/`.

Synthesized in code for this project (original, no licence restrictions):
- SFX: device beeps, the bell ring (a modal bell struck at 18 Hz), servo whirr, the attention clunk, power-down, broom swish, whoosh, wood tock, boot glitch.
- Ambience: room tone (filtered brown noise), day and dawn birds, night crickets, dusk wind.

Music: composed in code for this project (original). It covers the music-box routine motif, the night pad, the dusk pads and piano arpeggios, the uneasy pad under the ring, and the F-major piano epilogue.

No third-party music was used. The reference is still a Bilibili repost (original author unknown) and was used only for mood.

## v09
- **Room art.** Original and procedural.
  - The window bench was redrawn: cushioned, with legs and a shadow gap underneath.
  - The telescope was moved against the wall between the window and the clock.
  - Both are in `kit/aseprite/room09.lua` → `kit/v09/albedo09.png`.
- **Robot drawings.** New climb in-betweens, a new broom lean and a sleep pose (`kit/robot09/`), all original.
- **Lighting.** The moonlit night grade uses the shader `godot/shaders/light09.gdshader`, which is original.
- **Audio.** No new third-party audio. It uses the same Kenney CC0 samples as v08. The ring was re-cut into three shorter synthesized bursts. Mix: `audio/robot_story_09_mix.wav`.

## v10
- **Close-up insets, sunset shot, panorama, credits art.** All original and generated in code (`kit/v10/`: `panels10.py`, `up3.py`, `detail.py`, `calfx.py`, `sunset10.py`, `panorama10.py`, `credits10.py`). The insets and the sunset shot are derived from the project's own room and robot art.
- **Font.** **Pixelify Sans** by Stefie Justprince, SIL Open Font License 1.1 (Google Fonts; copy with its license at `kit/fonts/`). Used unmodified, rendered without antialiasing. Credited in the end credits.
- **Style references (not copied, no assets used).** Stardew Valley (ConcernedApe) portraits, title-screen panoramas (day and night) and a fan-made night-beach image, all from images Alan supplied in `refs_games/stardew_closeups/`. The motion reference is still a Bilibili repost (original author unknown).
- **Lighting.** `godot/shaders/light10.gdshader` and `main10.gd` (warm banded screen-glow pool at night) are original.
- **Audio.** No new third-party audio. Same Kenney CC0 samples as before. Music is original: an ending music-box return, a final F-major pad and crickets. Mix: `audio/robot_story_10_mix.wav`.

## v11
- **Close-ups (option B, full-screen ×3 zoom cuts).** No new art. They are the film's own wide frames, enlarged with nearest neighbour (`kit/v11/closeup11.py`).
- **Room layout fixes.** The small framed picture was moved to the wall right of the right window. The side table is now drawn behind the armchair. Both were edited in the project's own layers (`kit/v09/layer_frames.png`, `prep9.py`; backups in `kit/v09/bak_v10/`).
- **Ending panorama.** Redrawn procedurally in code, all original: `kit/v11/panorama11.py`, `clouds11.py`, `hills11b.py`, `colour11.py`.
- **Style references (not copied, no assets used).** Alan's Stardew title-sky, moon-night and beach Milky Way images (`refs_games/stardew_closeups/`). The motion reference is still a Bilibili repost (original author unknown).
- **Close-up research sources.** Cited in `closeup_research.md`; used for technique only.
- **Audio.** Unchanged v10 mix (`audio/robot_story_10_mix.wav`); timing is unchanged.

## v12
- **Code and art.** All changes are original, in code or edits of the project's own layers:
  - `godot/main12.gd` (native-grid world-space dust motes; screen glow off when powered down)
  - robot emissive layers (sleep eyes off, sit antenna off)
  - coat-rack umbrella removed
  - `kit/v12/panorama12.py`, `clouds12.py`
- **References.** No new third-party assets. Style references are still Alan's Stardew, moon-night and beach images; the motion reference is still a Bilibili repost (original author unknown).
