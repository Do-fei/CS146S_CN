#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Expand novel chapters 38-49 to ~97,600 chars each (488万 Vol6)."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from expand_3m import (  # noqa: E402
    ch38_scenes,
    ch39_scenes,
    ch40_scenes,
    ch41_scenes,
    ch42_scenes,
    ch43_scenes,
    ch44_scenes,
    ch45_scenes,
    ch46_scenes,
    ch47_scenes,
    ch48_scenes,
    ch49_scenes,
    ch49_ending,
    build_until,
    dedupe_blocks,
    strip_loops,
)
from vol6_scenes_488 import (  # noqa: E402
    VOL6_GENERATORS,
    VOL6_HEADERS,
    VOL6_OPENINGS,
    ch49_ending as ch49_end_vol6,
)

NOVEL = ROOT / "docs" / "novel"
TARGET = 97600
TOLERANCE = 800

CHAPTER_FILES = {
    38: "38-两站之间长.md",
    39: "39-第三颗糖.md",
    40: "40-第四个名字.md",
    41: "41-崇文宣武.md",
    42: "42-城换皮.md",
    43: "43-第二个漏句.md",
    44: "44-薄了长.md",
    45: "45-发送成功.md",
    46: "46-赵宜妈妈.md",
    47: "47-警察笔记本.md",
    48: "48-试听间邻座.md",
    49: "49-百万分之一.md",
}

LEGACY_GENS = {
    38: ch38_scenes,
    39: ch39_scenes,
    40: ch40_scenes,
    41: ch41_scenes,
    42: ch42_scenes,
    43: ch43_scenes,
    44: ch44_scenes,
    45: ch45_scenes,
    46: ch46_scenes,
    47: ch47_scenes,
    48: ch48_scenes,
    49: ch49_scenes,
}

# Strip numbered loop tails like （488） or （17）
_LOOP_TAIL = re.compile(r"（\d+）\s*$")
_TICKET_LOOP = re.compile(r"^【票根·\d+】")
_BRACKET_LOOP = re.compile(r"^【[^】]+·\d+】")


def extract_unique_core(text: str, max_chars: int = 8000) -> str:
    """Keep deduped non-loop paragraphs from existing chapter."""
    cleaned = dedupe_blocks(strip_loops(text))
    parts: list[str] = []
    total = 0
    for block in re.split(r"\n\n+", cleaned.strip()):
        block = block.strip()
        if not block or block.startswith("#"):
            continue
        if _TICKET_LOOP.match(block) or _BRACKET_LOOP.match(block):
            continue
        if block.count("你读完了，疼在纸背面") > 0:
            continue
        if block.count("九解并排，仍留百万分之一疑点") > 1 and len(block) < 300:
            continue
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
    return "\n\n".join(parts)


def combined_gen(ch: int, i: int) -> str:
    """Vol6 extended scenes only — legacy tails dedupe under clean_novel_ai."""
    ext = VOL6_GENERATORS[ch]
    if i % 4 == 0:
        return ext(i)
    if i % 4 == 1:
        return ext(i + ch * 131)
    if i % 4 == 2:
        return ext(i + ch * 271)
    return ext(i + ch * 419)


def expand_chapter(ch: int) -> tuple[int, int]:
    fname = CHAPTER_FILES[ch]
    fp = NOVEL / fname
    raw = fp.read_text(encoding="utf-8") if fp.exists() else ""
    header = VOL6_HEADERS[ch]
    opening = VOL6_OPENINGS[ch]
    core_extra = extract_unique_core(raw)
    core = opening
    if core_extra and core_extra not in core:
        core = f"{opening}\n\n{core_extra}"

    def gen(i: int) -> str:
        return combined_gen(ch, i)

    text = build_until(header, core, [gen], TARGET, seed=ch * 17)

    if ch == 49:
        parts = text.strip().split("\n\n")
        parts = [p for p in parts if "你把九解写在数学书空白页" not in p]
        ending = ch49_end_vol6()
        if ending not in "\n\n".join(parts):
            parts.append(ending)
        text = "\n\n".join(parts) + "\n"

    # Trim if over target + tolerance
    while len(text) > TARGET + TOLERANCE and text.count("\n\n") > 10:
        parts = text.strip().split("\n\n")
        parts.pop(-2 if ch == 49 else -1)
        text = "\n\n".join(parts) + "\n"

    # Pad slightly if under target
    i = 0
    while len(text) < TARGET - TOLERANCE:
        block = VOL6_GENERATORS[ch](10000 + i)
        if block not in text:
            text = text.rstrip() + "\n\n" + block + "\n"
        i += 1
        if i > 500:
            break

    fp.write_text(text, encoding="utf-8")
    return len(raw), len(text)


def main() -> None:
    for ch in range(38, 50):
        before, after = expand_chapter(ch)
        print(f"{CHAPTER_FILES[ch]}\t{before} -> {after}")


if __name__ == "__main__":
    main()
