#!/usr/bin/env python3
"""Strip numbered suffix tails from all chapters (688万 quality pass)."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"

TAIL = re.compile(
    r"(?:"
    r"\s+[\u4e00-\u9fff]{1,8}·\d+。?"
    r"|"
    r"（[\u4e00-\u9fff]{1,8}·\d+）"
    r"|"
    r"（扩488·[\d·]+）"
    r"|"
    r"（(?:六月|七月|八月|九月|十月|十一月|十二月|一月|二月|三月|四月|五月)·\d+）"
    r"|"
    r"（\d+-\d+）"
    r"|"
    r"（\d+）"
    r")+\s*$"
)

INLINE_SUFFIX = re.compile(
    r"（(?:扩488·[\d·]+|[\u4e00-\u9fff]{1,8}·\d+)）"
)


def md5(s: str) -> str:
    import re as _re
    return hashlib.md5(_re.sub(r"\s+", "", s).encode()).hexdigest()


def clean_block(block: str) -> str:
    block = block.replace("她她", "她")
    block = INLINE_SUFFIX.sub("", block)
    prev = None
    while prev != block:
        prev = block
        block = TAIL.sub("", block).strip()
    if block and block[-1] not in "。！？…":
        block += "。"
    return block


def main() -> None:
    for path in sorted(ROOT.glob("[0-9]*.md")):
        raw = path.read_text(encoding="utf-8")
        parts: list[str] = []
        seen: set[str] = set()
        for block in re.split(r"\n\n+", raw.strip()):
            block = block.strip()
            if not block:
                continue
            if block.startswith("#"):
                parts.append(block)
                continue
            block = clean_block(block)
            key = md5(block)
            if key in seen:
                continue
            seen.add(key)
            parts.append(block)
        text = "\n\n".join(parts) + "\n"
        path.write_text(text, encoding="utf-8")
        print(f"{path.name}\t{len(raw)} -> {len(text)}")


if __name__ == "__main__":
    main()
