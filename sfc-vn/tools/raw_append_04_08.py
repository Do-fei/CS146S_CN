#!/usr/bin/env python3
"""Rebuild 04-08 by concatenating all expansion sources without aggressive dedupe."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOVEL = ROOT / "docs" / "novel"
sys.path.insert(0, str(ROOT / "tools"))

TARGETS = {
    "04-胡同.md": 12000,
    "05-第三夜.md": 14000,
    "06-胡同深.md": 14000,
    "07-便利店.md": 14000,
    "08-天桥.md": 15000,
}


def light_clean(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    lines = text.split("\n")
    title = lines[0] if lines and lines[0].startswith("#") else ""
    body = text[len(title):].lstrip("\n") if title else text
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip() and not p.strip().startswith("---")]
    skip = [
        r"第[五六七八]章写完", r"下一章", r"后面一章", r"后面章", r"正本从发送失败",
        r"第四章止于", r"第五章写完", r"第六章走到", r"第七章写完", r"第八章写完",
        r"你已在路上。正本", r"后面倒带馆", r"第三夜会写", r"胡同深会写", r"便利店会写", r"天桥会写",
    ]
    seen = set()
    out = []
    for p in paras:
        if any(re.search(s, p) for s in skip):
            continue
        # exact dedupe only
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return title + "\n\n" + "\n\n".join(out) + "\n"


def append_blocks(path: Path, blocks: list[str]):
    t = path.read_text(encoding="utf-8")
    for b in blocks:
        b = b.strip()
        if b and b not in t:
            t = t.rstrip() + "\n\n" + b + "\n"
    path.write_text(t, encoding="utf-8")


def main():
    import clean_ch04
    import final_rewrite_04_08 as fr
    from expand_ch04_only import PARAS as CH04_PARAS
    from big_expand_04_08 import A, B, C, D
    from big_expand4 import BLOCKS as BIG4
    from expand_massive15 import BLOCKS as M15
    from append_batch2 import APPEND as B2
    from append_batch3 import APPEND as B3
    from append_batch4 import APPEND as B4
    from append_batch5 import APPEND as B5
    from mega_expand_00_08 import EXP
    from more_unique_04_08 import MORE

    # 04 base
    clean_ch04.main()
    bases = {
        "05-第三夜.md": fr.CH05,
        "06-胡同深.md": fr.CH06,
        "07-便利店.md": fr.CH07,
        "08-天桥.md": fr.CH08,
    }
    for fn, body in bases.items():
        (NOVEL / fn).write_text(body.strip() + "\n", encoding="utf-8")

    for fn in TARGETS:
        p = NOVEL / fn
        blocks = []
        for src in [B2, B3, B4, B5, M15, EXP, MORE]:
            if fn in src:
                blocks.append(src[fn])
        if fn == "04-胡同.md":
            blocks.extend(CH04_PARAS)
            blocks.extend([A, B, C, D, BIG4["04-胡同.md"]])
        else:
            blocks.extend([A, B, C, D, BIG4.get(fn, "")])
        append_blocks(p, blocks)
        t = light_clean(p.read_text(encoding="utf-8"))
        p.write_text(t, encoding="utf-8")
        n = len(t)
        print(f"{fn}\t{n}\t(target {TARGETS[fn]})")


if __name__ == "__main__":
    main()
