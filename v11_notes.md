# Robot v11 notes (2026-09-28)

## Films
- `robot_story_full_11.mp4` (yuv420p) and `robot_story_full_11_444.mp4` (yuv444p). 1920×1080 at 24 fps, 1766 frames (73.6 s).
- Timing is the same as v10, so the v10 soundtrack is reused.

## Close-ups: option B (research in `closeup_research.md`)
- **Framed insets removed.** Each close-up is now a hard zoom cut to the full screen:
  - A 128×72 window of the **final wide frame's own native pixels**, including the page-turn patch.
  - Pixels are read at 5×5 block centres, with the grid aligned via the camera offset.
  - Enlarged **×3 by pure nearest neighbour**. Every frame has one pixel grain, and nothing is redrawn or smoothed.
- **Grid check.** Within-block std of the sampled source blocks is 0.14–0.42 in every shot (≈0 means aligned). A 2-px misalignment gives 12–23.
- **Framing.** Each shot's framing is locked in world coordinates on the union of the subject's boxes over the whole shot, so nothing is cut off and nothing jitters:
  - task [92,153): robot + device, origin (220,54)
  - cal [393,475): calendar + robot, origin (213,56)
  - face [649,744): robot, head-weighted, origin (233,49)
  - press [940,992): robot + device, origin (217,53)
- **Sunset window shot [1316,1390).** Uses the same ×3 zoom of the wide (window area, origin (100,40)). It replaces v10's redrawn glass and up3 polish, and opens with an 8-frame dissolve from the wide.
- Code: `kit/v11/closeup11.py`, `kit/v11/assemble11.py`.

## Room layout fixes (base layers, so the wide and the close-ups both update)
- **Small red/blue framed picture.** It overlapped the right window's left curtain (and was drawn on top of it). Moved to the free wall right of that window (x 349–366, y 58–80). The wall between the clock and the curtain now holds only the landscape frame.
- **Side table.** Now drawn before the armchair (painter's order by base line), so the chair arm sits in front instead of the table clipping over it.
- **Full overlap scan (layer-alpha intersections).** The remaining overlaps are intended depth overlaps:
  - window/curtain/bench
  - armchair in front of the curtain hem
  - basket beside and behind the armchair (base y125 vs 126)
  - chair tucked under the desk
  - crate on the trunk
  - sleeves behind the cabinet
  - telescope tip 2 px in front of the left curtain edge (it stands in front of the wall)
- **Wide re-render.** All five chunks were re-rendered in Godot.
- **Where the edits are.** `kit/v09/layer_frames.png` and `prep9.py`, which regenerate `albedo09.png`. Backups are in `kit/v09/bak_v10/`.

## Ending panorama (`kit/v11/panorama11.py`)
- **Sky.** 44 clean vertical bands, narrower toward the horizon, with no checker rows. The sun and moon glows are clean rings, and the Milky Way has no checker.
- **Clouds (`clouds11.py`).** Cumulus banks built from a smooth union of sphere lobes (big body lobes plus 3 generations of buds with irregular radii). They are shaded from normals, posterised to 5 tones and majority-cleaned. They have lit silhouette rims, cool undersides and crevice shadows, and darken to moonlit blue at night.
- **Hills (`hills11b.py` + `colour11.py`).**
  - 6 ridge rows, each a heightfield of rounded peaks with short slope-weighted spurs, shaded against the low sun and raymarched with a y-buffer.
  - Atmospheric perspective: far rows are lighter and hazier, near rows deep plum.
  - Lit faces are warmer (I/H band colours).
  - The warm crest rim shows only while the sun is up; the dusk-line bug is fixed.
  - Row masks now extend down, so per-row parallax no longer opens sky-coloured gaps.
- **Foliage.** Shaded leaf-lobe clusters with serrated leaf-stamp edges. The brown twig is gone and nothing floats.
- **Comparison and iterations.** Side-by-side vs Alan's references: `robot_2d_11_panorama_vs_ref.png`. There were 5 comparison iterations: proportions (smaller clouds, lower hills), hill scale, rim fix, parallax gap fix.

## Stills
- `robot_2d_11_closeup_{task,cal,face,press}.png`
- `robot_2d_11_sunset_window.png`
- `robot_2d_11_wide_layout.png`
- `robot_2d_11_panorama_{sunset,dusk,night}.png`
- `robot_2d_11_panorama_vs_ref.png`

## Known weak spots
- Hills read more as layered dunes than the Stardew reference's sharp small peaks.
- The corner foliage reads a bit like dark rock, not leafy trees.
- The close-ups are 3× chunkier than the wide by design (option B). The zoom cuts are hard cuts.
- In the face close-up the moved picture sits cut at the right edge of the frame.
