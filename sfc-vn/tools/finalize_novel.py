#!/usr/bin/env python3
"""Remove expansion markers and duplicate appended blocks from novel chapters."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"


def truncate_at_markers(text: str) -> str:
    for marker in ("<!--EXPAND", "<!--FINAL"):
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    return text


def dedupe_paragraphs(text: str) -> str:
    """Keep first occurrence of each paragraph block."""
    blocks = re.split(r"\n\n+", text.strip())
    seen = set()
    kept = []
    for block in blocks:
        key = re.sub(r"\s+", "", block)
        if len(key) < 12:
            kept.append(block)
            continue
        if key in seen:
            continue
        seen.add(key)
        kept.append(block)
    return "\n\n".join(kept)


def main():
    for path in sorted(ROOT.glob("[0-9]*.md")):
        original = path.read_text(encoding="utf-8")
        text = truncate_at_markers(original)
        text = re.sub(r"\n<!--[^>]+-->\n", "\n", text)
        text = dedupe_paragraphs(text)
        text = re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"finalized {path.name}: {len(original)} -> {len(text)}")


if __name__ == "__main__":
    main()
