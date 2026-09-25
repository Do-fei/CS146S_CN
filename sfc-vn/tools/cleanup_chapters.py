#!/usr/bin/env python3
"""Remove duplicate paragraphs and numbered-loop padding."""

import re
from pathlib import Path

NOVEL = Path(__file__).resolve().parents[1] / "docs" / "novel"
FILES = [f"0{i}-" + n for i, n in [
    (0, "序.md"), (1, "发送失败.md"), (2, "空位.md"), (3, "赵宜家.md"),
    (4, "胡同.md"), (5, "第三夜.md"), (6, "胡同深.md"), (7, "便利店.md"),
]]


def cleanup(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"^---\s*$", "", text, flags=re.M)
    title = ""
    paras = []
    seen = set()
    loop_seen = 0
    for p in re.split(r"\n\s*\n", text):
        p = p.strip()
        if not p:
            continue
        if p.startswith("#"):
            title = p
            continue
        # Drop excessive numbered-loop padding (keep first 2)
        if re.match(r"第\d+次", p):
            loop_seen += 1
            if loop_seen > 2:
                continue
        key = re.sub(r"\s+", "", p)
        if key in seen:
            continue
        seen.add(key)
        paras.append(p)
    return (title + "\n\n" if title else "") + "\n\n".join(paras)


def main():
    for f in FILES:
        path = NOVEL / f
        body = cleanup(path.read_text(encoding="utf-8"))
        path.write_text(body.strip() + "\n", encoding="utf-8")
        print(f"{f}\t{len(body.strip())}")


if __name__ == "__main__":
    main()
