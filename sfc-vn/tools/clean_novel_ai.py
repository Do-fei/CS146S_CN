#!/usr/bin/env python3
"""Strip MEGA/EXPAND padding, 不写进报告 loops, duplicate paragraphs."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"


_PADDING = re.compile(
    r"(不写进报告|停止后日常|漏句日常|回来的第|"
    r"日常\d+，|第\d+周记|<!--MEGA|<!--EXPAND|<!--BIG|<!--PASS|"
    r"赵宜家第\d+次想起|第\d+次发送失败|第\d+段归途|第\d+遍翻簿|"
    r"阿青在.{1,8}边看你|B面里，.{1,12}又转半圈)"
)


_SCENE_TAG = re.compile(
    r" (?:两站|三糖|四名|旧区|换皮|二漏|三帧|成功|妈妈|笔录|邻座|收束|"
    r"好友|B面|编目|薄了|留灯|卡片|汤|海洋|泵房|玻璃|末班|日志|票根)·\d+。$"
)


def _is_padding(block: str) -> bool:
    # vol6 unique scene blocks (ch38-49 rewrite)
    if _SCENE_TAG.search(block):
        return False
    if _PADDING.search(block):
        return True
    # template loop: "附近她又停一下，橘子皮排五线谱"
    if block.count("橘子皮排五线谱") and block.count("偶尔疼说明还当人"):
        return True
    if block.count("她抓你袖口，褶子在，你说在，她重复同桌在") > 0 and len(block) < 400:
        if not _SCENE_TAG.search(block):
            return True
    return False


def clean_text(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("<!--"):
            continue
        lines.append(line)
    text = "\n".join(lines)

    parts: list[str] = []
    seen: set[str] = set()
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if not block:
            continue
        if _is_padding(block):
            continue
        if block.startswith("#"):
            parts.append(block)
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
        cleaned = clean_text(raw)
        path.write_text(cleaned, encoding="utf-8")
        print(f"{path.name}\t{len(raw)} -> {len(cleaned)}")


if __name__ == "__main__":
    main()
