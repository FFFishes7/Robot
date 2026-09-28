#!/bin/sh
# rebuild the v06 room: Aseprite script -> .aseprite -> per-layer PNGs -> composites -> Tiled map
set -e
cd /workspace/robot2d/kit/v06
aseprite -b --script ../aseprite/room06.lua
aseprite -b room06.aseprite --split-layers --save-as 'layer_{layer}.png'
python3 prep6.py
cd ../tiled && python3 make_tmx06.py
