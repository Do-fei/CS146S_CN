#!/usr/bin/env python3
"""Remove vol4 numbered loop padding from ch19-23."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
CHS = ["19-馆藏.md", "20-静音.md", "21-随河.md", "22-空白站.md", "23-八个早晨.md"]

LOOP_TAIL = re.compile(r"大韦，第\d+次守[^。\n]*。（\d+）")
LOOP_LINE = re.compile(r"^\s*大韦，第\d+次守.*$", re.M)
BROKEN = re.compile(r"（补\{i\}）|（补i）")


def clean(text: str) -> str:
    text = BROKEN.sub("", text)
    text = LOOP_TAIL.sub("", text)
    text = LOOP_LINE.sub("", text)
    # truncate at first loop block start (paragraph repeating 交带那夜 after 够了)
    marker = "大韦，第1次守"
    if marker in text:
        pos = text.index(marker)
        head = text[:pos]
        end = head.rfind("够了。")
        if end > len(head) * 0.25:
            text = head[: end + 3] + "\n"
        else:
            text = head
    text = text.replace("mourning", "留空")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main() -> None:
    for name in CHS:
        path = ROOT / name
        raw = path.read_text(encoding="utf-8")
        cleaned = clean(raw)
        path.write_text(cleaned, encoding="utf-8")
        print(f"{name}\t{len(raw)} -> {len(cleaned)}")


if __name__ == "__main__":
    main()
