# 《Robot》

一部像素风动画短片：阁楼里的小机器人每天按清单打扫、按下按钮，某天停机后重新醒来，终于放下日常，坐在窗边看了一场日落。

## 成片
- `robot_story_full_14.mp4` —— 最终版（1920×1080，24 fps，yuv420p）：在 v13 基础上消除了镜头 1 像素跳动，每一帧都严格对齐 384×216 原生像素网格（×5）
- `robot_story_full_14_444.mp4` —— 同一版本的 yuv444p 高保真版
- `robot_2d_13_*.png` —— 关键静帧（画面内容与 v14 相同）

## 目录
- `kit/` —— 构建代码与素材：Aseprite Lua 绘制脚本（`kit/aseprite/`）、精灵与 `.aseprite` 源文件（`kit/sprites/`）、调色板、Tiled 地图、各版本 Python 生成脚本（`kit/v04`–`kit/v14`、`kit/robot06`–`kit/robot10`）
- `godot/` —— Godot 4 工程（合成、光照、着色器、Movie Maker 渲染）
- `audio/src/` —— Kenney CC0 音效素材（混音由 `kit/v13/audio13.py` 生成）
- `v11_notes.md`、`v12_notes.md`、`v14_notes.md`、`closeup_research.md` —— 制作笔记（v14 抖动扫描报告见 `kit/v14/jitter_report_v13.md`）

## 如何重新构建（v14）
脚本内使用绝对路径 `/workspace/robot2d/`，请把仓库克隆或软链接到该路径。
依赖：Python 3（numpy、Pillow）、ffmpeg、Godot 4.x、xvfb-run（无头渲染），重绘精灵时需要 Aseprite。

```bash
ln -s "$PWD" /workspace/robot2d        # 或直接克隆到该路径
cd /workspace/robot2d
python3 kit/v13/audio13.py             # 生成 audio/robot_story_13_mix.wav
python3 kit/v14/cam14.py               # 生成镜头轨迹 kit/robot09/frames/timeline14.json
for s in 0 300 600 900; do OUT=/tmp/w14 bash kit/robot10/render14.sh $s 300; done
OUT=/tmp/w14 bash kit/robot10/render14.sh 1200 326   # Godot 渲染宽镜头帧（输出到 /tmp/w14_*）
python3 kit/v14/assemble14.py robot_story_full_14.mp4            # 合成 yuv420p 成片
python3 kit/v14/assemble14.py robot_story_full_14_444.mp4 yuv444p
python3 kit/v14/scan_jitter.py robot_story_full_14_444.mp4 scan.json   # 可选：逐帧检查整体位移
python3 kit/v14/grid_check.py robot_story_full_14_444.mp4 grid.json    # 可选：检查原生像素网格对齐
```
详细流程和各版本修改见 `v11_notes.md`、`v12_notes.md`、`v14_notes.md`。

## 许可
素材与工具的来源和许可见 [`assets_licenses.md`](assets_licenses.md)。美术与音乐为本项目原创；音效采用 Kenney 的 CC0 素材（许可文件在 `audio/src/*/License.txt`）。
