# 《Robot》

一部像素风动画短片：阁楼里的小机器人每天按清单打扫、按下按钮，某天停机后重新醒来，终于放下日常，坐在窗边看了一场日落。

## 成片
- `robot_story_full_15.mp4` —— 最终版（1920×1080，24 fps，yuv420p）：在 v13 基础上去掉了镜头的慢速漂移和孤立的 1 像素跳动，摇镜保持 v13 的平滑（v14 的整原生像素步进会让摇镜发顿）。视频文件较大，不进 git，按下面的步骤构建
- `robot_2d_13_*.png` —— 关键静帧

## 目录
- `kit/` —— 构建代码与素材：Aseprite Lua 绘制脚本（`kit/aseprite/`）、精灵与 `.aseprite` 源文件（`kit/sprites/`）、调色板、Tiled 地图、各版本 Python 生成脚本（`kit/v04`–`kit/v15`、`kit/robot06`–`kit/robot10`）、片尾字体（`kit/fonts/`）
- `godot/` —— Godot 4 工程（合成、光照、着色器、Movie Maker 渲染）
- `audio/src/` —— Kenney CC0 音效素材（混音由 `kit/v13/audio13.py` 生成）
- `v11_notes.md`、`v12_notes.md`、`v14_notes.md`、`v15_notes.md`、`closeup_research.md` —— 制作笔记（v14 抖动扫描报告见 `kit/v14/jitter_report_v13.md`）

## 如何重新构建（v15）
构建用到的文件都在仓库内：路径由 `kit/paths.py` 按仓库位置推出，渲染帧和中间产物写到 `build/`，成片写到仓库根目录（这些都不进 git）。Windows 和 Linux 使用同一组命令。
依赖：Python 3（numpy、scipy、Pillow）、ffmpeg、Godot 4.7.2；Linux 无显示环境时还需要 xvfb-run；重绘精灵时需要 Aseprite。
Godot 放在 `tools/godot/`（官方发行包解压即可），或用环境变量 `GODOT` 指定可执行文件。Windows 上渲染时 Godot 窗口不能最小化，否则会录出重复帧（`render15.py` 会检查并报错）。

```bash
python kit/v13/audio13.py       # 生成 audio/robot_story_13_mix.wav
python kit/v15/cam15.py         # 生成镜头轨迹 kit/robot09/frames/timeline15.json
python kit/v15/render15.py      # Godot 渲染宽镜头帧到 build/w15_*（可只渲某几段：render15.py 0 300）
python kit/v15/assemble15.py    # 生成翻页补丁并合成 robot_story_full_15.mp4（yuv420p）
python kit/v15/assemble15.py robot_story_full_15_444.mp4 yuv444p   # 可选：yuv444p 高保真版
python kit/v14/scan_jitter.py robot_story_full_15.mp4 build/scan.json   # 可选：逐帧检查整体位移
```
v14 及更早版本的入口脚本（如 `assemble14.py`、`render14.sh`）没有迁移，仍引用 `/workspace/robot2d/` 与 `/tmp/`，不能直接用来构建。
详细流程和各版本修改见 `v11_notes.md`、`v12_notes.md`、`v14_notes.md`、`v15_notes.md`。

## 许可
素材与工具的来源和许可见 [`assets_licenses.md`](assets_licenses.md)。美术与音乐为本项目原创；音效采用 Kenney 的 CC0 素材（许可文件在 `audio/src/*/License.txt`）。
