#!/usr/bin/env python3
"""Assemble hand-written vol4 chapters 19-21 from scene modules. No template loops."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
GEN = Path(__file__).resolve().parent / "_gen" / "hand_vol4"


def load_scenes(mod_name: str) -> list[str]:
    path = GEN / f"{mod_name}.py"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    scenes = []
    i = 1
    while hasattr(mod, f"S{i:02d}"):
        scenes.append(getattr(mod, f"S{i:02d}"))
        i += 1
    return scenes


def assemble(title: str, scenes: list[str], close: str) -> str:
    body = "\n\n".join(scenes)
    return f"# {title}\n\n{body}\n\n{close}\n"


def main() -> None:
    chapters = [
        ("19-馆藏.md", "ch19", "第十九章　馆藏", "ch19_close"),
        ("20-静音.md", "ch20", "第二十章　静音", "ch20_close"),
        ("21-随河.md", "ch21", "第二十一章　随河", "ch21_close"),
    ]
    for fname, mod, title, close_mod in chapters:
        scenes = load_scenes(mod)
        close_path = GEN / f"{close_mod}.py"
        spec = importlib.util.spec_from_file_location(close_mod, close_path)
        cm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cm)
        text = assemble(title, scenes, cm.CLOSE)
        out = ROOT / fname
        out.write_text(text, encoding="utf-8")
        print(f"{fname}\tscenes={len(scenes)}\tchars={len(text)}")


if __name__ == "__main__":
    main()
