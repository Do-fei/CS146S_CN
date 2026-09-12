# 十一点的城市

彩色都市灵异文字冒险。故事发生在北京。赵宜失踪第三天，短信把你约到南城天桥。三条路：西单倒带馆、北京海洋馆、无名地铁。每条线有关键抉择和独立结局。

从零写的原创作品，不是任何商业游戏的汉化。

<p align="center">
  <img src="docs/web_title.png" alt="标题" width="320">
  <img src="docs/web_dialogue.png" alt="对白与立绘" width="320">
  <img src="docs/web_menu.png" alt="存读档菜单" width="320">
</p>

## 怎么玩（推荐网页）

用浏览器打开 `player/index.html`（需本地服务器，见下）。彩色立绘、随时存读三格档。

```bash
cd sfc-vn
python3 tools/export_web.py
python3 -m http.server -d player 8765
```

然后访问 `http://127.0.0.1:8765`。

- **Z / 空格 / 点击**：继续、确认
- **↑↓**：移动选项
- **Esc**：菜单，随时保存或读取（三格）

单条线大约四五十分钟阅读，加上看画面和存档，一轮接近一小时。三条线可重玩。

## 超任卡带

`dist/city11.sfc` 可用 Snes9x / bsnes / RetroArch 打开。

- **Start**：进游戏；游戏中 **Start 存档**（SRAM 槽）
- **Select**：读档
- **A**：继续 / 确认
- **上下**：选项

## 从源码重建

```bash
python3 -m pip install pillow pytest
make test
make web
make rom
```

## 目录

- `game/route_*.py` — 开场与三条分支剧本
- `player/` — 彩色网页运行时
- `tools/art.py` — 场景与立绘
- `tools/build_rom.py` — 65816 引擎与 `.sfc`
