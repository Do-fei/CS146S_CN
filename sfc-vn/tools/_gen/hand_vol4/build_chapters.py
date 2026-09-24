#!/usr/bin/env python3
"""Build hand-written vol4 chapters 19-21 to ~30k chars each."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "docs" / "novel"
HERE = Path(__file__).resolve().parent


def read_scenes(name: str) -> list[str]:
    path = HERE / f"{name}_full.txt"
    text = path.read_text(encoding="utf-8")
    scenes = []
    buf = []
    for line in text.splitlines():
        if line.strip() == "---":
            if buf:
                scenes.append("\n".join(buf).strip())
                buf = []
        else:
            buf.append(line)
    if buf:
        scenes.append("\n".join(buf).strip())
    return scenes


def build(title: str, scenes: list[str], close: str) -> str:
    return f"# {title}\n\n" + "\n\n".join(scenes) + f"\n\n{close}\n"


def main():
    for num, cn_title, mod, close_file in [
        ("19-馆藏.md", "第十九章　馆藏", "ch19", "ch19_close.txt"),
        ("20-静音.md", "第二十章　静音", "ch20", "ch20_close.txt"),
        ("21-随河.md", "第二十一章　随河", "ch21", "ch21_close.txt"),
    ]:
        scenes = read_scenes(mod)
        close = (HERE / close_file).read_text(encoding="utf-8").strip()
        text = build(cn_title, scenes, close)
        out = ROOT / num
        out.write_text(text, encoding="utf-8")
        lens = [len(s) for s in scenes]
        print(f"{num}\tscenes={len(scenes)}\tmin={min(lens)}\tmax={max(lens)}\ttotal={len(text)}")


if __name__ == "__main__":
    main()
