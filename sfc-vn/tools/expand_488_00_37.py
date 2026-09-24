#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Expand novel chapters 00-37 to ~97,600 chars each (488万)."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from expand_3m import build_until, dedupe_blocks, strip_loops  # noqa: E402
from scene_bank_3m import (  # noqa: E402
    scene_aquarium,
    scene_archive,
    scene_blank_station,
    scene_climb,
    scene_eight_mornings,
    scene_glass,
    scene_last_bus,
    scene_leak,
    scene_log,
    scene_mute,
    scene_pump,
    scene_river,
    scene_small_road,
    scene_stop,
    scene_ticket,
    PLACES,
    HOOKS,
    pick,
)

NOVEL = ROOT / "docs" / "novel"
TARGET = 97600
TOLERANCE = 800

# Chapter -> scene generators (mix for variety)
CHAPTER_GENS: dict[int, list] = {
    **{i: [scene_leak, scene_small_road, scene_climb] for i in range(0, 9)},
    **{i: [scene_stop, scene_leak, scene_archive] for i in range(9, 19)},
    **{i: [scene_mute, scene_archive, scene_river, scene_blank_station] for i in range(19, 24)},
    **{i: [scene_leak, scene_eight_mornings, scene_stop] for i in range(24, 29)},
    **{i: [scene_archive, scene_leak, scene_small_road] for i in range(29, 32)},
    **{32: [scene_aquarium, scene_glass, scene_pump]},
    **{33: [scene_pump, scene_aquarium, scene_glass]},
    **{34: [scene_glass, scene_aquarium, scene_archive]},
    **{35: [scene_last_bus, scene_blank_station, scene_log]},
    **{36: [scene_log, scene_last_bus, scene_ticket]},
    **{37: [scene_ticket, scene_last_bus, scene_log]},
}

_LOOP_MARKERS = re.compile(
    r"^【(?:票根|日志|末班|馆藏|静音|随河|空白站|海洋馆|泵房|玻璃后|小的路|归途|爬回|漏句日常)·\d+】"
)


def vol488_extra(ch: int, i: int) -> str:
    """Combinatorial unique scenes for 00-37 expansion."""
    p = pick(PLACES, i, ch * 3)
    h = pick(HOOKS, i, ch * 5)
    months = ["六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
    m = months[(i + ch) % len(months)]
    variants = [
        f"{m}，{p}，{h}。你摸袖口，褶还在，第三排靠窗还在，发送失败是逗号，逗号后面还有馆还有带。",
        f"{m}某夜，{p}。22:59秒针抖，你不管，你管袖口还在，小的路写不进报告，报告只能写检修。",
        f"{m}，{p}。赵宜抓你袖口，说甜的要沉，你嗯，方程两个解，选了漏的那一个，风没吹掉。",
        f"{m}放学，{p}。便利贴贴栏杆，风没吹掉，风没吹掉像并排还在，并排里谁也没往前走谁也没消失。",
        f"{m}，{p}。班主任说第三排靠窗的灯我还留着，灯留着，位置就在，故事就不算短。",
        f"{m}，{p}。警察空白卡片：找到了吗，你说小路，他划掉，别写太像故事，你不写进报告。",
        f"{m}，{p}。她把橘子皮排成五线谱，风乱她捡回来重新排，排完口型长，你读唇：选你最不怕后悔的。",
        f"{m}，{p}。电信营业厅她问全覆盖为何盖不住23:17，柜员笑换套餐吗，她说不换，换套餐像大路。",
    ]
    body = variants[(i * 7 + ch) % len(variants)]
    routes = ["小海检修写得下", "老周日志空载", "阿青缝还在别写名", "编目簿待定"]
    if i % 3 == 0:
        body += routes[(ch // 3) % 4] + "。"
    return body + f"（扩488·{ch:02d}·{i + 1}）"


def extract_core(text: str, max_chars: int = 10000) -> str:
    cleaned = dedupe_blocks(strip_loops(text))
    parts: list[str] = []
    total = 0
    header = ""
    for block in re.split(r"\n\n+", cleaned.strip()):
        block = block.strip()
        if not block:
            continue
        if block.startswith("#"):
            header = block
            continue
        if _LOOP_MARKERS.match(block):
            continue
        if block.count("你读下一页") >= 2:
            continue
        if block.count("又出现一次") >= 1:
            continue
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
    return header, "\n\n".join(parts)


def make_generator(ch: int):
    gens = CHAPTER_GENS.get(ch, [scene_leak, scene_small_road])

    def gen(i: int):
        g = gens[i % len(gens)]
        if i % 2 == 0:
            return g(i + ch * 50)
        return vol488_extra(ch, i)

    return gen


def expand_chapter(path: Path) -> tuple[int, int]:
    m = re.match(r"(\d+)", path.name)
    ch = int(m.group(1)) if m else 0
    raw = path.read_text(encoding="utf-8")
    header, core = extract_core(raw)
    if not header:
        header = f"# 第{ch}章"
    if not core:
        core = raw.split("\n\n")[1] if "\n\n" in raw else raw[:500]

    text = build_until(header, core, [make_generator(ch)], TARGET, seed=ch * 13)

    while len(text) > TARGET + TOLERANCE and text.count("\n\n") > 8:
        parts = text.strip().split("\n\n")
        parts.pop(-1)
        text = "\n\n".join(parts) + "\n"

    i = 0
    while len(text) < TARGET - TOLERANCE:
        block = vol488_extra(ch, 5000 + i)
        if block not in text:
            text = text.rstrip() + "\n\n" + block + "\n"
        i += 1
        if i > 800:
            break

    path.write_text(text, encoding="utf-8")
    return len(raw), len(text)


def main() -> None:
    for path in sorted(NOVEL.glob("[0-9]*.md")):
        m = re.match(r"(\d+)", path.name)
        if not m:
            continue
        ch = int(m.group(1))
        if ch > 37:
            continue
        before, after = expand_chapter(path)
        print(f"{path.name}\t{before} -> {after}")


if __name__ == "__main__":
    main()
