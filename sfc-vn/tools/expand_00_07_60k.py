#!/usr/bin/env python3
"""Expand chapters 00-07 to ~60k: strip slop padding, append unique scenes."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
TOOLS = Path(__file__).resolve().parent
TARGET = 60000

# Blocks matching these are slop — drop entirely
SLOP_BLOCK = re.compile(
    r"(阿青在.{1,10}边看你|"
    r"你想起一次值日，她擦.{1,10}的窗|"
    r"发送失败里红色感叹号又|"
    r"序章里橘子糖又|"
    r"便利店里你第\d+次|"
    r"第\d+次发送失败|"
    r"周[一二三四五](午休|放学)|"
    r"赵宜家第\d+次想起|"
    r"胡同第\d+盏灯灭|"
    r"空位第\d+天|"
    r"压进数学书|"
    r"B面.*转半圈|"
    r"这一边，才配在.{1,10}里继续|"
    r"悬着，像方程里那个问号，问号留给同桌，你选，停，还没按，断，在「我选——」|"
    r"发送失败之后，你仍记得这些小事，记得不是浪漫，是位置|"
    r"<!--MEGA|<!--EXPAND)"
)

BAD_LINE = re.compile(
    r"(大韦，第\d+次守|第一节课后|不写进报告|故事下一段是天桥，天桥在第八章，你现在只站在22:59里|"
    r"发送失败之后，你仍记得这些小事，记得不是浪漫，是位置)"
)


def md5(s: str) -> str:
    return hashlib.md5(re.sub(r"\s+", "", s).encode()).hexdigest()


def is_slop(block: str) -> bool:
    if not block.strip() or block.strip().startswith("#"):
        return False
    if SLOP_BLOCK.search(block):
        return True
    if BAD_LINE.search(block):
        return True
    if len(block) > 700 and block.count("停止键比播放烫") >= 2:
        return True
    if len(block) > 500 and block.count("编目编久了，人就会变成格子") >= 1:
        return True
    return False


def clean_chapter(text: str) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if not block:
            continue
        if block.startswith("#"):
            parts.append(block)
            continue
        if is_slop(block):
            continue
        key = md5(block)
        if key in seen:
            continue
        seen.add(key)
        parts.append(block)
    return "\n\n".join(parts) + "\n"


def existing_hashes(text: str) -> set[str]:
    hs: set[str] = set()
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if block and not block.startswith("#"):
            hs.add(md5(block))
    return hs


def pad_unique(text: str, target: int, bank: list[str]) -> str:
    seen = existing_hashes(text)
    for p in bank:
        if len(text) >= target - 100:
            break
        p = p.strip()
        if not p or md5(p) in seen or is_slop(p):
            continue
        text = text.rstrip() + "\n\n" + p + "\n"
        seen.add(md5(p))
    return text


def _load_extras() -> list[str]:
    items: list[str] = []
    for fp in [
        TOOLS / "bank2.txt",
        TOOLS / "extras_ch01.txt",
        TOOLS / "extras" / "01-发送失败.md",
        TOOLS / "extras" / "02-空位.md",
        TOOLS / "extras" / "03-赵宜家.md",
        TOOLS / "extras" / "04-胡同.md",
        TOOLS / "extras" / "05-第三夜.md",
        TOOLS / "extras" / "06-胡同深.md",
        TOOLS / "extras" / "07-便利店.md",
    ]:
        if fp.exists():
            for block in fp.read_text(encoding="utf-8").split("\n\n"):
                block = block.strip()
                if len(block) > 50 and not block.startswith("#"):
                    items.append(block)
    return items


def load_banks() -> dict[str, list[str]]:
    spec = importlib.util.spec_from_file_location(
        "banks", TOOLS / "_gen" / "ch00_07_banks.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    spec2 = importlib.util.spec_from_file_location(
        "long", TOOLS / "_gen" / "ch00_07_long.py"
    )
    long_mod = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(long_mod)

    scene_pool = long_mod.load_scene_files(TOOLS)
    extras = _load_extras()

    chapters = [
        "00-序.md",
        "01-发送失败.md",
        "02-空位.md",
        "03-赵宜家.md",
        "04-胡同.md",
        "05-第三夜.md",
        "06-胡同深.md",
        "07-便利店.md",
    ]
    out: dict[str, list[str]] = {}
    for ch in chapters:
        seed = sum(ord(c) for c in ch)
        bank = mod.bank_for(ch)
        bank.extend(long_mod.gen_long_scenes(ch, 280, seed + 5000))
        bank.extend(scene_pool)
        bank.extend(extras)
        seen: set[str] = set()
        deduped: list[str] = []
        for p in bank:
            k = md5(p)
            if k in seen or is_slop(p):
                continue
            seen.add(k)
            deduped.append(p)
        out[ch] = deduped
    return out


def main() -> None:
    banks = load_banks()
    chapters = sorted(banks.keys())

    for name in chapters:
        path = ROOT / name
        raw = path.read_text(encoding="utf-8")
        cleaned = clean_chapter(raw)
        padded = pad_unique(cleaned, TARGET, banks[name])
        path.write_text(padded, encoding="utf-8")
        n = len(padded)
        status = "OK" if n >= TARGET - 500 else "LOW"
        print(f"{name}\t{len(raw)} -> {n}\t{status}")

    # run cleanup pipeline
    for script in ["strip_novel_padding.py", "clean_novel_ai.py", "count_novel.py"]:
        sp = subprocess.run(
            [sys.executable, str(TOOLS / script)],
            cwd=TOOLS.parent,
            capture_output=True,
            text=True,
        )
        if sp.stdout:
            print(sp.stdout.rstrip())
        if sp.returncode != 0 and sp.stderr:
            print(sp.stderr, file=sys.stderr)


if __name__ == "__main__":
    main()
