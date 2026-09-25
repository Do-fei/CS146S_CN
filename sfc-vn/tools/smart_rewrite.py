#!/usr/bin/env python3
"""Dedupe, de-AI expand, and write chapters 01-07."""

import re
from pathlib import Path

NOVEL = Path(__file__).resolve().parents[1] / "docs" / "novel"
TARGET = {f"{i:02d}": 20800 for i in range(1, 8)}
TARGET["00"] = 7000


def dedupe_paragraphs(text: str) -> str:
    """Remove duplicate paragraphs and HTML comment blocks."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"^---\s*$", "", text, flags=re.M)
    paras = []
    seen = set()
    for p in re.split(r"\n\s*\n", text):
        p = p.strip()
        if not p or p.startswith("#"):
            if p.startswith("#"):
                paras.append(p)
            continue
        key = re.sub(r"\s+", "", p)[:120]
        if key in seen:
            continue
        seen.add(key)
        paras.append(p)
    title = paras[0] if paras and paras[0].startswith("#") else ""
    body = [title] if title else []
    body.extend(x for x in paras if not x.startswith("#"))
    return "\n\n".join(body)


def merge_short_sentences(para: str) -> str:
    """Merge telegraphic chains into comma sentences where obvious."""
    if "。" not in para or len(para) > 80:
        return para
    parts = [x.strip() for x in para.split("。") if x.strip()]
    if len(parts) < 4:
        return para
    if all(len(p) <= 8 for p in parts[:6]):
        merged = "，".join(parts[:4]) + "。"
        if len(parts) > 4:
            merged += "，".join(parts[4:]) + "。"
        return merged
    return para


def expand_ch01() -> str:
    from gen_ch01 import SCENES  # noqa
    exec(Path(__file__).parent.joinpath("gen_ch01.py").read_text().split("body = ")[0])
    base = "\n\n".join(SCENES)
    extras = Path(__file__).parent.joinpath("extras_ch01.txt")
    if extras.exists():
        base += "\n\n" + extras.read_text(encoding="utf-8").strip()
    return base


def main():
    for i in range(1, 8):
        name = f"{i:02d}-" + {
            1: "发送失败",
            2: "空位",
            3: "赵宜家",
            4: "胡同",
            5: "第三夜",
            6: "胡同深",
            7: "便利店",
        }[i] + ".md"
        path = NOVEL / name
        if i == 1 and Path(__file__).parent.joinpath("extras_ch01.txt").exists():
            body = expand_ch01()
        else:
            raw = path.read_text(encoding="utf-8")
            body = dedupe_paragraphs(raw)
            body = "\n\n".join(merge_short_sentences(p) for p in body.split("\n\n"))
        path.write_text(body.strip() + "\n", encoding="utf-8")
        print(name, len(body.strip()))


if __name__ == "__main__":
    main()
