#!/usr/bin/env python3
"""Strip known padding patterns from novel chapters."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"


def strip_ch26(text: str) -> str:
    """Keep only content before B-side loop blocks."""
    marker = "B面里，第三口气又转半圈"
    if marker in text:
        text = text[: text.index(marker)].rstrip()
    if not text.endswith("\n"):
        text += "\n"
    return text


def strip_ch23(text: str) -> str:
    parts: list[str] = []
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if not block:
            continue
        if block.startswith("#") or block.startswith("**"):
            parts.append(block)
            continue
        if "playback" in block.lower():
            continue
        if block.count("你读下一页") >= 2:
            continue
        if len(block) > 900 and block.count("这一页") >= 4:
            continue
        if block.count("别倒带，倒带再薄一毫米") >= 1 and len(block) > 400:
            continue
        parts.append(block)
    return "\n\n".join(parts) + "\n"


def fix_typos(text: str) -> str:
    return text.replace("Tonight", "今晚").replace("youTonight", "今晚")


def main() -> None:
    jobs = [
        ("19-馆藏.md", lambda t: fix_typos(t)),
        ("23-八个早晨.md", strip_ch23),
        ("26-磁带背面.md", strip_ch26),
    ]
    for name, fn in jobs:
        path = ROOT / name
        raw = path.read_text(encoding="utf-8")
        cleaned = fn(raw)
        path.write_text(cleaned, encoding="utf-8")
        print(f"{name}\t{len(raw)} -> {len(cleaned)}")


if __name__ == "__main__":
    main()
