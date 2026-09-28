#!/bin/bash
# still9.sh F out.png  -> renders wide frame F of timeline09 with main09
F=$1; OUT=$2; D=/tmp/st9_$F; rm -rf $D; mkdir -p $D
cd /workspace/robot2d/godot && timeout 300 xvfb-run -a -s "-screen 0 1920x1080x24" godot --path . --rendering-driver opengl3 --write-movie $D/f.png --fixed-fps 24 --quit-after 9 res://main09.tscn -- --mode=anim --tl=timeline09.json --start=$((F-3)) > $D.log 2>&1
cp $D/f00000006.png $OUT
