#!/usr/bin/env python3
"""导出网页玩家所需的剧本和彩色立绘/场景。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.story import story_to_plain
from tools.art import all_portrait_names, all_scene_names, paint_portrait, paint_scene


def export(out: Path) -> None:
    assets = out / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    data = story_to_plain()
    (out / "story.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    for name in all_scene_names():
        paint_scene(name).save(assets / f"scene_{name}.png")
    for name in all_portrait_names():
        paint_portrait(name).save(assets / f"portrait_{name}.png")
    print(f"exported {len(data['nodes'])} nodes, ~{data['minutes']} min")


if __name__ == "__main__":
    export(ROOT / "player")
