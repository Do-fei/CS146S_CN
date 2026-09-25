#!/usr/bin/env python3
"""Remove 488万 expansion numbered loop paragraphs."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"

NUM_SUFFIX = re.compile(
    r"（(?:收束·|两站·|三糖·|四名·|旧区·|换皮·|二漏·|三帧·|成功·|妈妈·|笔录·|邻座·|"
    r"扩488·|票根·|末班·|日志·|海洋·|泵房·|玻璃后·|编目·|薄了·|B面·|好友·|卡片·|汤·|留灯·)?\d+）\s*$"
)
NUM_ONLY_SUFFIX = re.compile(r"（\d+）\s*$")

LOOP_PHRASES = (
    "九解并排，仍留百万分之一疑点，十一点不解释",
    "验到一半推翻一半，留一半，留的一半不填括弧",
    "袖口褶还在，人就还在某个意义上，某个意义是第三排靠窗",
    "并排不抢不判对错，你活在其中一个，其余在纸背面",
    "你摸袖口，褶还在，两站之间不属于任何人，所以可以留缝，缝窄，窄够了",
    "疼才能把故事按在两站之间，你读完了，疼在纸背面",
)


def is_loop_block(block: str) -> bool:
    if NUM_SUFFIX.search(block) or NUM_ONLY_SUFFIX.search(block):
        # short blocks ending with numbered suffix are loop padding
        if len(block) < 500:
            hits = sum(1 for p in LOOP_PHRASES if p in block)
            if hits >= 1:
                return True
            # vol6 template: location + month + repeating twist
            if block.count("你摸袖口") >= 1 and block.count("窄够了") >= 1:
                return True
            if re.match(r"^[\u4e00-\u9fff]{2,10}，", block) and len(block) < 350:
                return True
    # standalone numbered suffix lines
    if re.match(r"^（(?:收束·)?\d+）\s*$", block):
        return True
    return False


def clean(text: str) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if not block:
            continue
        block = SHOU_SUFFIX.sub("。", block)
        if block.startswith("#"):
            parts.append(block)
            continue
        if is_loop_block(block):
            continue
        if SHOU_SUFFIX.search(block) or re.search(r"收束·\d+", block):
            if len(block) < 350 and block.count("收束·") >= 1:
                continue
        key = hashlib.md5(re.sub(r"\s+", "", block).encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        parts.append(block)
    return "\n\n".join(parts) + "\n"


def main() -> None:
    for path in sorted(ROOT.glob("[0-9]*.md")):
        raw = path.read_text(encoding="utf-8")
        cleaned = clean(raw)
        if len(cleaned) < len(raw):
            path.write_text(cleaned, encoding="utf-8")
            print(f"{path.name}\t{len(raw)} -> {len(cleaned)}")


if __name__ == "__main__":
    main()
