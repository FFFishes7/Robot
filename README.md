# 《Robot》

一部像素风动画短片：阁楼里的小机器人每天按清单打扫、按下按钮，某天停机后重新醒来，终于放下日常，坐在窗边看了一场日落。

## 成片
- `robot_story_full_13.mp4` —— 最终版（1920×1080，24 fps，yuv420p）
- `robot_story_full_13_444.mp4` —— 同一版本的 yuv444p 高保真版
- `robot_2d_13_*.png` —— 关键静帧

## 目录
- `kit/` —— 构建代码与素材：Aseprite Lua 绘制脚本（`kit/aseprite/`）、精灵与 `.aseprite` 源文件（`kit/sprites/`）、调色板、Tiled 地图、各版本 Python 生成脚本（`kit/v04`–`kit/v13`、`kit/robot06`–`kit/robot10`）
- `godot/` —— Godot 4 工程（合成、光照、着色器、Movie Maker 渲染）
- `audio/src/` —— Kenney CC0 音效素材（混音由 `kit/v13/audio13.py` 生成）
- `v11_notes.md`、`v12_notes.md`、`closeup_research.md` —— 制作笔记

## 如何重新构建（v13）
脚本内使用绝对路径 `/workspace/robot2d/`，请把仓库克隆或软链接到该路径。
依赖：Python 3（numpy、Pillow）、ffmpeg、Godot 4.x、xvfb-run（无头渲染），重绘精灵时需要 Aseprite。

```bash
ln -s "$PWD" /workspace/robot2d        # 或直接克隆到该路径
cd /workspace/robot2d
python3 kit/v13/audio13.py             # 生成 audio/robot_story_13_mix.wav
bash kit/robot10/render13.sh <起始帧> <帧数>   # Godot 渲染宽镜头帧（输出到 /tmp/w10_*）
python3 kit/v13/assemble13.py robot_story_full_13.mp4            # 合成 yuv420p 成片
python3 kit/v13/assemble13.py robot_story_full_13_444.mp4 yuv444p
```
详细流程和各版本修改见 `v11_notes.md`、`v12_notes.md`。

## 许可
素材与工具的来源和许可见 [`assets_licenses.md`](assets_licenses.md)。美术与音乐为本项目原创；音效采用 Kenney 的 CC0 素材（许可文件在 `audio/src/*/License.txt`）。
