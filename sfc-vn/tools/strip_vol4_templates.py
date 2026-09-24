#!/usr/bin/env python3
"""Remove location-time template padding from vol4 chapters."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
CHS = ["19-馆藏.md", "20-静音.md", "21-随河.md", "22-空白站.md", "23-八个早晨.md"]

TIME_LOC = re.compile(
    r"^(早读前|第一节课后|午休|下午第四节|放学路上|晚饭前|"
    r"晚自习后|入夜前|周末午后|雨天傍晚|天快亮|数学课后)，"
)
TEMPLATE_MARKERS = (
    "压进数学书，书合拢",
    "你把某句咽回去，咽回去不等于没听见",
    "你把呼吸数到四停，四是呼吸断掉",
    "你把手机扣在桌上，扣像按停止，停止不是结束是留缝",
    "你把两颗糖一颗放扬声器墙下",
)


def is_template(block: str) -> bool:
    if TIME_LOC.match(block.strip()):
        return True
    hits = sum(1 for m in TEMPLATE_MARKERS if m in block)
    if hits >= 2:
        return True
    if hits >= 1 and len(block) < 200:
        return True
    return False


def strip(text: str) -> str:
    parts: list[str] = []
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if not block:
            continue
        if block.startswith("#"):
            parts.append(block)
            continue
        if is_template(block):
            continue
        parts.append(block)
    out = "\n\n".join(parts)
    if not out.endswith("\n"):
        out += "\n"
    return out


def main() -> None:
    for name in CHS:
        path = ROOT / name
        raw = path.read_text(encoding="utf-8")
        cleaned = strip(raw)
        path.write_text(cleaned, encoding="utf-8")
        print(f"{name}\t{len(raw)} -> {len(cleaned)}")


if __name__ == "__main__":
    main()
