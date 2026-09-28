#!/bin/bash
# render12.sh S L -> /tmp/w10_S (wide frame F = f{6+F-S})
S=$1; L=$2; D=${OUT:-/tmp/w10}_$S; rm -rf $D; mkdir -p $D
cd /workspace/robot2d/godot && xvfb-run -a -s "-screen 0 1920x1080x24" godot --path . --rendering-driver opengl3 --write-movie $D/f.png --fixed-fps 24 --quit-after $((L+7)) res://main12.tscn -- --mode=anim --tl=timeline10.json --start=$((S-3)) > $D.log 2>&1
echo done $S
