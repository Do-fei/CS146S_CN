#!/usr/bin/env python3
"""V486 finalize: distribute unique pre-loop + vol4 cores."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
COMMIT = "8981ac4"
TARGET = 486000
LOOP = "回来的第"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clean_novel_ai import clean_text
import rewrite_15_23_bodies as bodies


def pk(p: str) -> str:
    return hashlib.md5(re.sub(r"\s+", "", p).encode()).hexdigest()


def restore(name: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{COMMIT}:sfc-vn/docs/novel/{name}"], text=True
    )


def pre_loop_blocks(raw: str) -> tuple[str, list[str]]:
    text = clean_text(raw)
    blocks = text.split("\n\n")
    title = blocks[0] if blocks[0].startswith("#") else ""
    body = blocks[1:] if title else blocks
    kept, seen = [], set()
    for b in body:
        b = b.strip()
        if not b or LOOP in b or "不写进报告" in b:
            if LOOP in b:
                break
            continue
        k = pk(b)
        if k in seen:
            continue
        seen.add(k)
        kept.append(b)
    return title, kept


def master_pool() -> list[str]:
    pool, seen = [], set()
    for n in ["15-停止.md", "16-爬回.md", "17-小的路.md", "18-漏句.md"]:
        _, blocks = pre_loop_blocks(restore(n))
        for b in blocks:
            if len(b) < 25:
                continue
            k = pk(b)
            if k not in seen:
                seen.add(k)
                pool.append(b)
    return pool


POOL = master_pool()


def assemble_chapter(title: str, core: list[str], target: int, used: set[str]) -> str:
    parts = ([title] if title else []) + list(core)
    seen = {pk(b) for b in parts}
    length = len("\n\n".join(parts))

    for b in POOL:
        if length >= target:
            break
        k = pk(b)
        if k in seen or k in used:
            continue
        parts.append(b)
        seen.add(k)
        used.add(k)
        length = len("\n\n".join(parts))

    text = "\n\n".join(parts).strip() + "\n"
    while len(text) > target and len(parts) > 10:
        dropped = parts.pop()
        if pk(dropped) in used and dropped not in core:
            used.discard(pk(dropped))
        text = "\n\n".join(parts).strip() + "\n"
    return text


def vol4_chapter(core_text: str, target: int, used: set[str]) -> str:
    blocks = [b.strip() for b in core_text.strip().split("\n\n") if b.strip()]
    title = blocks[0] if blocks[0].startswith("#") else ""
    body = blocks[1:] if title else blocks
    return assemble_chapter(title, body, target, used)


def main() -> None:
    files = sorted(
        [p.name for p in ROOT.glob("[0-9]*.md") if 15 <= int(p.name[:2]) <= 23]
    )
    base = sum(
        len(p.read_text(encoding="utf-8"))
        for p in sorted(ROOT.glob("[0-9]*.md"))
        if int(p.name[:2]) <= 14
    )
    need = TARGET - base
    per = need // len(files)
    rem = need % len(files)
    used: set[str] = set()

    vol4 = {
        "19-馆藏.md": bodies.CH19,
        "20-静音.md": bodies.CH20,
        "21-随河.md": bodies.CH21,
        "22-空白站.md": bodies.CH22,
        "23-八个早晨.md": bodies.CH23,
    }

    for idx, name in enumerate(files):
        t = per + (1 if idx < rem else 0)
        if name in vol4:
            text = vol4_chapter(vol4[name], t, used)
        else:
            title, core = pre_loop_blocks(restore(name))
            text = assemble_chapter(title, core, t, used)
        (ROOT / name).write_text(text, encoding="utf-8")

    for name in files:
        print(f"{name}\t{len((ROOT / name).read_text(encoding='utf-8'))}")
    total = sum(len(p.read_text(encoding="utf-8")) for p in sorted(ROOT.glob("[0-9]*.md")))
    print(f"---\npool\t{sum(len(p) for p in POOL)}\ntotal\t{total}")


if __name__ == "__main__":
    main()
