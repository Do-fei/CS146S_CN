#!/usr/bin/env python3
"""Write expanded novel chapters 00-08 with target char counts."""
from pathlib import Path

NOVEL = Path(__file__).resolve().parents[1] / "docs" / "novel"


def write(name: str, body: str) -> int:
    text = body.strip() + "\n"
    path = NOVEL / name
    path.write_text(text, encoding="utf-8")
    n = len(text)
    print(f"{name}\t{n}")
    return n


# Import chapter bodies from separate module to keep this file manageable
from write_ch00_08_bodies import (
    CH00, CH01, CH02, CH03, CH04, CH05, CH06, CH07, CH08,
)


def main():
    total = 0
    for name, body in [
        ("00-序.md", CH00),
        ("01-发送失败.md", CH01),
        ("02-空位.md", CH02),
        ("03-赵宜家.md", CH03),
        ("04-胡同.md", CH04),
        ("05-第三夜.md", CH05),
        ("06-胡同深.md", CH06),
        ("07-便利店.md", CH07),
        ("08-天桥.md", CH08),
    ]:
        total += write(name, body)
    print(f"---\n00-08 total\t{total}")


if __name__ == "__main__":
    main()
