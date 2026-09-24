#!/usr/bin/env python3
"""Remove meta forward-refs and exact duplicates from 04-08."""
import re
from pathlib import Path

NOVEL = Path(__file__).resolve().parents[1] / "docs" / "novel"
FILES = ["04-胡同.md", "05-第三夜.md", "06-胡同深.md", "07-便利店.md", "08-天桥.md"]

SKIP = [
    r"第[五六七八]章写完",
    r"下一章",
    r"后面一章",
    r"后面章",
    r"正本从发送失败",
    r"第四章止于",
    r"第五章写完",
    r"第六章走到",
    r"第七章写完",
    r"第八章写完",
    r"你已在路上。正本",
    r"后面倒带馆",
    r"第三夜会写",
    r"胡同深会写",
    r"便利店会写",
    r"天桥会写",
    r"天桥在第八章",
    r"天桥在后面的章",
    r"按停止键，是后面的章",
    r"再往前，是第三夜、胡同深、便利店、天桥",
    r"也在，就够你走到赵宜家，走到胡同，走到天桥",
    r"胡同深处便利店天桥我选后面",
    r"某个地方在胡同深处，在便利店，在天桥",
    r"走到赵宜家，走到胡同，走到天桥",
    r"也在，就够你等到十一点",
]


def clean(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    title = text.split("\n")[0]
    body = text[len(title):].lstrip("\n")
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip() and not p.startswith("---")]
    seen = set()
    out = []
    for p in paras:
        if any(re.search(s, p) for s in SKIP):
            continue
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return title + "\n\n" + "\n\n".join(out) + "\n"


def main():
    for fn in FILES:
        p = NOVEL / fn
        t = clean(p.read_text(encoding="utf-8"))
        p.write_text(t, encoding="utf-8")
        print(f"{fn}\t{len(t)}")


if __name__ == "__main__":
    main()
