#!/usr/bin/env python3
"""Remove expansion HTML comment markers from novel chapters."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"

def main():
    for path in sorted(ROOT.glob("[0-9]*.md")):
        text = path.read_text(encoding="utf-8")
        cleaned = re.sub(r"\n<!--EXPAND[^>]*-->\n", "\n", text)
        cleaned = re.sub(r"\n<!--FINAL-->\n", "\n", cleaned)
        cleaned = re.sub(r"\n<!--PASS2[^>]*-->[^\n]*\n?", "\n", cleaned)
        # collapse excessive blank lines
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        if cleaned != text:
            path.write_text(cleaned.rstrip() + "\n", encoding="utf-8")
            print(f"cleaned {path.name}")

if __name__ == "__main__":
    main()
