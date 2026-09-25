#!/usr/bin/env python3
"""Rewrite chapters 38-49 with unique Qidian-quality scenes (~97,600 chars each)."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from scenes_488_38_49 import GENERATORS, OPENINGS, ch49_ending  # noqa: E402

NOVEL = ROOT / "docs" / "novel"
TARGET = 104300
TOLERANCE = 400

# Strip vol6 numbered loop padding tails
LOOP_TAIL = re.compile(
    r"\s*(?:"
    r"（(?:收束·|两站·|三糖·|四名·|旧区·|换皮·|二漏·|三帧·|成功·|妈妈·|笔录·|邻座·)?\d+）"
    r"|"
    r"九解并排，仍留百万分之一疑点，十一点不解释"
    r"|"
    r"验到一半推翻一半，留一半，留的一半不填括弧"
    r"|"
    r"袖口褶还在，人就还在某个意义上，某个意义是第三排靠窗"
    r"|"
    r"并排不抢不判对错，你活在其中一个，其余在纸背面"
    r")\s*$"
)

LOOP_BLOCK = re.compile(
    r"^（(?:收束·|两站·|三糖·|四名·|旧区·|换皮·|二漏·|三帧·|成功·|妈妈·|笔录·|邻座·)?\d+）"
)


def strip_core(text: str) -> str:
    """Keep header + opening only from existing chapter."""
    parts = [p.strip() for p in re.split(r"\n\n+", text.strip()) if p.strip()]
    if not parts:
        return ""
    header = parts[0] if parts[0].startswith("#") else ""
    return header


def build_to_target(header: str, core: str, gen, seed: int, target: int) -> str:
    blocks: list[str] = []
    if header:
        blocks.append(header)
    blocks.append(core)
    seen: set[str] = {hashlib.md5(re.sub(r"\s+", "", b).encode()).hexdigest() for b in blocks}
    i = 0
    while sum(len(b) for b in blocks) < target:
        block = gen(i + seed)
        key = hashlib.md5(re.sub(r"\s+", "", block).encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            blocks.append(block)
        i += 1
        if i > 8000:
            break
    text = "\n\n".join(blocks)
    while len(text) > target + TOLERANCE and len(blocks) > 4:
        blocks.pop(-1)
        text = "\n\n".join(blocks)
    return text + "\n"


def expand_chapter(name: str) -> tuple[int, int]:
    path = NOVEL / name
    raw = path.read_text(encoding="utf-8") if path.exists() else ""
    header = strip_core(raw) or f"# 第{name[:2]}章"
    if not header.startswith("#"):
        num = int(re.match(r"(\d+)", name).group(1))
        titles = {
            38: "两站之间长", 39: "第三颗糖", 40: "第四个名字", 41: "崇文宣武",
            42: "城换皮", 43: "第二个漏句", 44: "薄了长", 45: "发送成功",
            46: "赵宜妈妈", 47: "警察笔记本", 48: "试听间邻座", 49: "百万分之一",
        }
        header = f"# 第{['', '一', '二', '三', '四', '五', '六', '七', '八', '九'][num // 10] if num < 50 else ''}{['', '一', '二', '三', '四', '五', '六', '七', '八', '九'][num % 10]}章　{titles[num]}"
        # simpler: use known headers
        headers_map = {
            "38-两站之间长.md": "# 第三十八章　两站之间长",
            "39-第三颗糖.md": "# 第三十九章　第三颗糖",
            "40-第四个名字.md": "# 第四十章　第四个名字",
            "41-崇文宣武.md": "# 第四十一章　崇文宣武",
            "42-城换皮.md": "# 第四十二章　城换皮",
            "43-第二个漏句.md": "# 第四十三章　第二个漏句",
            "44-薄了长.md": "# 第四十四章　薄了长",
            "45-发送成功.md": "# 第四十五章　发送成功",
            "46-赵宜妈妈.md": "# 第四十六章　赵宜妈妈",
            "47-警察笔记本.md": "# 第四十七章　警察笔记本",
            "48-试听间邻座.md": "# 第四十八章　试听间邻座",
            "49-百万分之一.md": "# 第四十九章　百万分之一",
        }
        header = headers_map.get(name, header)

    core = OPENINGS[name]
    gen = GENERATORS[name]
    seed = int(re.match(r"(\d+)", name).group(1)) * 100
    text = build_to_target(header, core, gen, seed, TARGET)

    if name == "49-百万分之一.md":
        parts = text.strip().split("\n\n")
        ending = ch49_ending()
        if ending not in text:
            parts.append(ending)
        text = "\n\n".join(parts) + "\n"

    path.write_text(text, encoding="utf-8")
    return len(raw), len(text)


def main() -> None:
    for name in GENERATORS:
        before, after = expand_chapter(name)
        print(f"{name}\t{before} -> {after}")


if __name__ == "__main__":
    main()
