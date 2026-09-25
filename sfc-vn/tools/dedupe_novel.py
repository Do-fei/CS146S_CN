#!/usr/bin/env python3
"""Remove duplicate paragraph blocks without truncating at markers."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"


def dedupe_paragraphs(text: str) -> str:
    blocks = re.split(r"\n\n+", text.strip())
    seen = set()
    kept = []
    for block in blocks:
        key = re.sub(r"\s+", "", block)
        if len(key) < 20:
            kept.append(block)
            continue
        if key in seen:
            continue
        seen.add(key)
        kept.append(block)
    return "\n\n".join(kept) + "\n"


def main():
    for path in sorted(ROOT.glob("[0-9]*.md")):
        original = path.read_text(encoding="utf-8")
        cleaned = dedupe_paragraphs(original)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        if cleaned != original:
            path.write_text(cleaned, encoding="utf-8")
            print(f"deduped {path.name}: {len(original)} -> {len(cleaned)}")


if __name__ == "__main__":
    main()
