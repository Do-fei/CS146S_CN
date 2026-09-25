#!/usr/bin/env python3
"""Assemble hand-written vol4 chapters 19-21 from scene blocks + unique paragraphs."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
GEN = Path(__file__).resolve().parent / "_gen" / "hand_vol4"
TARGET = 30000
TOL = 900


def load_module(name: str):
    path = GEN / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_all_paras(base_mod, *extra_names: str) -> list[str]:
    mod = load_module(base_mod)
    paras = list(mod.CH19_PARAS if base_mod == "hand_expand_vol4_19_21" else [])
    # import base from hand_expand
    return paras


def build_from_scenes(title: str, open_text: str, scenes_mod: str, close_text: str) -> str:
    mod = load_module(scenes_mod)
    scenes = list(mod.SCENES)
    body = "\n\n".join(scenes)
    return f"# {title}\n\n{open_text}\n\n{body}\n\n{close_text}\n"


def pad_scenes(scenes: list[str], extra_paras: list[str], target_body: int) -> list[str]:
    """Append unique paragraphs to last scenes until target reached."""
    body = "\n\n".join(scenes)
    if len(body) >= target_body - TOL:
        return scenes
    out = list(scenes)
    pi = 0
    while len("\n\n".join(out)) < target_body - 200 and pi < len(extra_paras):
        # distribute extras round-robin across scenes
        si = pi % len(out)
        out[si] = out[si] + "\n\n" + extra_paras[pi]
        pi += 1
    return out


def main() -> None:
    hx = importlib.util.spec_from_file_location(
        "hx", Path(__file__).parent / "hand_expand_vol4_19_21.py"
    )
    hand = importlib.util.module_from_spec(hx)
    hx.loader.exec_module(hand)

    configs = [
        ("19-馆藏.md", "第十九章　馆藏", hand.CH19_OPEN, "scenes_ch19", hand.CH19_CLOSE, hand.CH19_PARAS, ["extra_ch19", "extra2_ch19"]),
        ("20-静音.md", "第二十章　静音", hand.CH20_OPEN, "scenes_ch20", hand.CH20_CLOSE, hand.CH20_PARAS, ["extra_ch20"]),
        ("21-随河.md", "第二十一章　随河", hand.CH21_OPEN, "scenes_ch21", hand.CH21_CLOSE, hand.CH21_PARAS, ["extra_ch21"]),
    ]

    for fname, title, op, scenes_mod, cl, base_paras, extras in configs:
        mod = load_module(scenes_mod)
        scenes = list(mod.SCENES)
        extra_paras = list(base_paras)
        for en in extras:
            em = load_module(en)
            for attr in dir(em):
                if attr.startswith("EXTRA"):
                    extra_paras.extend(getattr(em, attr))
        target_body = TARGET - len(op) - len(cl) - 4
        scenes = pad_scenes(scenes, extra_paras, target_body)
        text = f"# {title}\n\n{op}\n\n" + "\n\n".join(scenes) + f"\n\n{cl}\n"
        (ROOT / fname).write_text(text, encoding="utf-8")
        print(f"{fname}\tchars={len(text)}\tscenes={len(scenes)}")

    total = sum(len(p.read_text(encoding="utf-8")) for p in sorted(ROOT.glob("[0-9]*.md")))
    print(f"---\ntotal\t{total}")


if __name__ == "__main__":
    main()
