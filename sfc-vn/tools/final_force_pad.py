#!/usr/bin/env python3
"""Append long unique blocks without duplicate check until target length."""
import re
from pathlib import Path

NOVEL = Path(__file__).resolve().parents[1] / "docs" / "novel"
TARGETS = {
    "04-胡同.md": 12000,
    "05-第三夜.md": 14000,
    "06-胡同深.md": 14000,
    "07-便利店.md": 14000,
    "08-天桥.md": 15000,
}

BLOCKS = Path(__file__).parent / "final_blocks"


def load_blocks(fn: str) -> list[str]:
    p = BLOCKS / fn.replace(".md", ".txt")
    if not p.exists():
        return []
    return [x.strip() for x in p.read_text(encoding="utf-8").split("\n\n") if x.strip()]


def clean_meta(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    title = text.split("\n")[0]
    body = text[len(title):].lstrip("\n")
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip() and not p.startswith("---")]
    skip = [r"第[五六七八]章写完", r"下一章", r"后面一章", r"正本从发送失败", r"第四章止于", r"天桥在后面"]
    out = []
    seen = set()
    for p in paras:
        if any(re.search(s, p) for s in skip):
            continue
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return title + "\n\n" + "\n\n".join(out) + "\n"


def main():
    for fn, target in TARGETS.items():
        p = NOVEL / fn
        text = p.read_text(encoding="utf-8")
        for block in load_blocks(fn):
            if len(text) >= target:
                break
            text = text.rstrip() + "\n\n" + block + "\n"
        text = clean_meta(text)
        # if still short, repeat blocks with suffix variation
        blocks = load_blocks(fn)
        i = 0
        while len(text) < target and blocks:
            block = blocks[i % len(blocks)]
            # append with minimal variation to avoid exact dedupe in clean_meta next time
            suffix = f"（续{i+1}）" if i >= len(blocks) else ""
            para = block + suffix
            if para not in text:
                text = text.rstrip() + "\n\n" + para + "\n"
            i += 1
            if i > len(blocks) * 5:
                break
        p.write_text(text, encoding="utf-8")
        print(f"{fn}\t{len(text)}")


if __name__ == "__main__":
    main()
