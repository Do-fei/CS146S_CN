#!/usr/bin/env python3
"""统计 docs/novel 字数。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"


def main() -> None:
    total = 0
    for path in sorted(ROOT.glob("[0-9]*.md")):
        n = len(path.read_text(encoding="utf-8"))
        total += n
        print(f"{path.name}\t{n}")
    print(f"---\ntotal\t{total}")


if __name__ == "__main__":
    main()
