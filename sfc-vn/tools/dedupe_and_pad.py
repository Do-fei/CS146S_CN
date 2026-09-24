#!/usr/bin/env python3
"""Dedupe paragraphs and report lengths."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
FILES = [f"{i:02d}-" + n for i, n in [
    (0, "序.md"), (1, "发送失败.md"), (2, "空位.md"), (3, "赵宜家.md"),
    (4, "胡同.md"), (5, "第三夜.md"), (6, "胡同深.md"), (7, "便利店.md"), (8, "天桥.md"),
]]


def dedupe(text: str) -> str:
    lines = text.split("\n")
    title = lines[0] if lines and lines[0].startswith("#") else ""
    body = text[len(title):].lstrip("\n") if title else text
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    seen = set()
    out = []
    for p in paras:
        if p.startswith("---"):
            continue
        key = re.sub(r"\s+", "", p)
        if len(key) < 20:
            out.append(p)
            continue
        sig = key[:100]
        if sig in seen:
            continue
        seen.add(sig)
        out.append(p)
    if title:
        return title + "\n\n" + "\n\n".join(out) + "\n"
    return "\n\n".join(out) + "\n"


def main():
    for fn in FILES:
        p = ROOT / fn
        if not p.exists():
            print(f"missing {fn}")
            continue
        t = dedupe(p.read_text(encoding="utf-8"))
        p.write_text(t, encoding="utf-8")
        print(f"{fn}\t{len(t)}")


if __name__ == "__main__":
    main()
