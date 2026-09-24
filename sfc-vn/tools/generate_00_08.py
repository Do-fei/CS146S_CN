#!/usr/bin/env python3
"""Generate chapters 00-08 to target char counts with deduped base + unique scenes."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
TARGETS = {
    "00-序.md": 15000,
    "01-发送失败.md": 15000,
    "02-空位.md": 15000,
    "03-赵宜家.md": 15000,
    "04-胡同.md": 12000,
    "05-第三夜.md": 14000,
    "06-胡同深.md": 14000,
    "07-便利店.md": 14000,
    "08-天桥.md": 15000,
}


def dedupe(text: str) -> str:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip() and not p.strip().startswith("#")]
    seen = set()
    out = []
    for p in paras:
        key = re.sub(r"\s+", "", p)[:80]
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    title = text.split("\n")[0] if text.startswith("#") else ""
    if title.startswith("#"):
        return title + "\n\n" + "\n\n".join(out)
    return "\n\n".join(out)


def pad(name: str, scenes: list[str], target: int, base: str | None = None):
    if base is None:
        base = ROOT.joinpath(name).read_text(encoding="utf-8") if ROOT.joinpath(name).exists() else ""
    text = dedupe(base)
    used = set(re.sub(r"\s+", "", p)[:80] for p in re.split(r"\n\s*\n", text) if p.strip())
    for s in scenes:
        if len(text) >= target:
            break
        key = re.sub(r"\s+", "", s)[:80]
        if key in used:
            continue
        used.add(key)
        text = text.rstrip() + "\n\n" + s.strip()
    ROOT.joinpath(name).write_text(text.strip() + "\n", encoding="utf-8")
    n = len(text)
    print(f"{name}\t{n}\t{'OK' if n >= target - 500 else 'LOW'}")


# Import scene banks
from generate_00_08_scenes import SCENES

def main():
    for name, target in TARGETS.items():
        scenes = SCENES.get(name, [])
        # Special full rewrites
        if name in SCENES and SCENES[name] and SCENES[name][0].startswith("#"):
            ROOT.joinpath(name).write_text(SCENES[name][0].strip() + "\n", encoding="utf-8")
            n = len(SCENES[name][0])
            print(f"{name}\t{n}\t{'OK' if n >= target - 500 else 'LOW'} (full)")
            continue
        pad(name, scenes, target)


if __name__ == "__main__":
    main()
