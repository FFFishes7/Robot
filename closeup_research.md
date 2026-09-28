# How pixel-art games handle close-ups (research for Robot v11)

Researched 2026-09-28 (web). Question: is a pixel-art close-up (a) an integer camera zoom with chunkier pixels,
(b) a separate drawing at the same pixel size as the world, or (c) an inset/portrait frame? And how do games keep it
consistent with the wide shot?

## Findings

**Stardew Valley (events):**
- Events keep the world at the player's normal zoom and move the camera with `viewport x y` (pan/centre); there is no cutscene zoom command. https://stardewmodding.wiki.gg/wiki/Tutorial:_Anatomy_of_an_Event
- Player zoom (75–200%) scales every world pixel uniformly. https://stardewvalleywiki.com/Modding:Modder_Guide/Game_Fundamentals
- Close-ups are separate **64×64 hand-drawn portraits** (option b), shown in a framed box beside the dialogue (option c). https://www.reddit.com/r/StardewValley/comments/94mm3o/ , https://www.nexusmods.com/stardewvalley/articles/1459
- Consistency comes from hand-drawing the same design. The portrait is a UI element, not a crop of the world.

**Celeste (Pedro Medeiros / saint11):**
- The game canvas is 320×180, scaled by an integer with nearest neighbour.
- "Never use any smoothing algorithms for scaling pixel art". If sprites must be scaled, "scale all sprites by the same integer number".
- Dialogue portraits and UI are a separate high-resolution "world". The rule is quarantine: each world stays internally consistent, and styles never leak between worlds.
- Source: https://saint11.art/blog/consistency/ . Portraits are 160×160 files: https://saplonily.top/celeste_wiki/mappings/xml/portraits_xml/

**To the Moon / RPG Maker:**
- Cutscene close-ups use a screen zoom (`$gameScreen.startZoom(x, y, scale, duration)`) of the same art, so pixels get chunkier.
- Non-integer or filtered zoom goes blurry; the recommended fix is integer scale or a lower base resolution.
- Sources: https://forums.rpgmakerweb.com/threads/global-zoom-in.134920/ , https://forums.rpgmakerweb.com/threads/zooming-camera-view-on-maps.60625/ , https://www.reddit.com/r/RPGMaker/comments/i2e28s/

**Eastward:**
- 480×270 pixel art in a 3D-lit engine. Community reports say the camera zooms between levels, with assets scaled by whole numbers (nearest neighbour), so zoomed pixels are chunkier.
- Sources: https://www.reddit.com/r/eastward/comments/si03ra/zoom/ , https://www.redbull.com/us-en/eastward-interview , https://pixpilgames.tumblr.com/post/154715527832/

**Owlboy:**
- A fixed 640×360 canvas with no dynamic camera zoom; drama comes from staging and room layout.
- https://forums.tigsource.com/index.php?topic=17398.200 , https://steamcommunity.com/app/115800/discussions/0/154644928859299729/

**Sea of Stars:**
- The big close-ups are separate hand-animated 2D cinematics (DuCoup Animation), not zooms of the pixel world.
- https://techmash.co.uk/2023/09/26/sea-of-stars-in-game-cinematics-du-coup-animation/ , https://nintendoeverything.com/sea-of-stars-reaches-kickstarter-target-and-first-stretch-goal-now-looking-to-fund-animated-2d-cutscenes/

**General pixel-art rules:**
- **Integer nearest scaling only.** Fractional scaling duplicates or drops pixels. https://gamedev.stackexchange.com/questions/131445/ , https://nikles.it/2017/gamemaker-tutorial/scale-2d-pixel-art-games-using-surfaces-to-avoid-pixel-decimation-in-gamemaker-studio-2/ , https://www.moddb.com/games/space-station-continuum/tutorials/pixel-art-screen-resolution-and-zooming
- **Mixed pixel sizes ("mixels") look amateur** unless the ratio is a clean integer and the intent is clear. https://www.reddit.com/r/PixelArt/comments/1sep8tf/ , https://www.slynyrd.com/blog/2018/5/16/pixelblog-5-back-to-basics

## Answer
Professionals use all three approaches, each with a strict rule:
- **(a) Integer camera zoom** of the same pixels (To the Moon, Eastward): chunkier pixels, but a single grain on screen.
- **(b) A separate drawing at a pixel size of its own** (Stardew portraits, Sea of Stars cinematics, Celeste HD portraits): hand-drawn, never generated from the world by smoothing.
- **(c) Insets:** portraits in a UI frame, treated as a separate "world" that is internally consistent.

Nobody resamples the world with smoothing or edge-redrawing upscalers. That is exactly what broke our v10 insets: Scale3x plus skeleton outlines plus re-detailing.

## Decision: option B, approved 2026-09-28 and implemented in v11 (kit/v11/closeup11.py)

Original recommendation:
- **Recommended: B. A full-screen integer ×3 camera zoom cut, To the Moon / RPG Maker style but integer only.**
  - Cut from the wide to a 128×72 window of the wide's own native pixels at that frame, aligned to the grid and enlarged ×3 by nearest neighbour, then cut back.
  - Every frame on screen has exactly one pixel grain, and nothing is redrawn or smoothed.
  - Mock: robot_2d_11_closeup_mockB_fullzoom.png (frame 700).
- **Alternative: A. A framed inset showing the same native pixels ×3 nearest over the live wide** (saint11's "quarantined world" idea).
  - It is crisp and exact, but two grains share the screen (15-px blocks inside the inset, 5-px outside).
  - Mock: robot_2d_11_closeup_mockA_inset.png (the crop box is the old v10 face region; at frame 700 the robot has moved, so the framing would need to follow the robot).
- **High-effort option: C. Stardew-style hand-drawn portraits** at the film's 1× grain. This needs genuinely hand-authored art per pose; the v10 generated redraws failed.
- For consistency with the wide, A and B are sampled directly from the final wide frame (verified: within-block std 0.2–0.8 on the grid), so props, lighting and timing match by construction.
