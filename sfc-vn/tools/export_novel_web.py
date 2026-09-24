#!/usr/bin/env python3
"""复制小说章节到 player/novel，供 GitHub Pages 在线阅读。"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOVEL_SRC = ROOT / "docs" / "novel"


def _title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def export_novel(out: Path) -> None:
    chapters_dir = out / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    for old in chapters_dir.glob("*.md"):
        old.unlink()

    manifest: list[dict[str, str]] = []
    for src in sorted(NOVEL_SRC.glob("[0-9]*.md")):
        text = src.read_text(encoding="utf-8")
        dest = chapters_dir / src.name
        dest.write_text(text, encoding="utf-8")
        manifest.append({"file": src.name, "title": _title(text, src.stem)})

    (out / "chapters.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"novel: {len(manifest)} chapters -> {out}")
