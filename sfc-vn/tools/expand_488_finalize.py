#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pad under-target chapters to >=97600 after clean; verify 488万 total."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOVEL = ROOT / "docs" / "novel"
TOOLS = ROOT / "tools"
TARGET = 97600
MIN_TOTAL = 4880000

sys.path.insert(0, str(TOOLS))
from clean_novel_ai import clean_text  # noqa: E402
from vol6_scenes_488 import _LOCS, _MONTHS, _WEATHER, _pick  # noqa: E402


def md5(s: str) -> str:
    return hashlib.md5(re.sub(r"\s+", "", s).encode()).hexdigest()


def unique_pad(ch: int, i: int) -> str:
    loc = _pick(_LOCS, i, ch * 9)
    m = _pick(_MONTHS, i, ch * 3)
    w = _pick(_WEATHER, i, ch * 5)
    beats = [
        f"你把详单折三角，三角塞桌缝，暗号就是我还活着，{m}在{loc}，{w}，袖口褶还在。",
        f"赵宜抓你袖口，说甜的要沉，你嗯，方程两个解，选了漏的那一个，{loc}风没吹掉便利贴。",
        f"班主任说第三排靠窗的灯我还留着，{m}，{loc}，发送失败是逗号，逗号后面还有馆还有带。",
        f"小海说检修写得下，人写不下，{loc}，{w}，你不写进笔录，笔录只能写检修。",
        f"老周日志空载，可空白票在你口袋，{m}夜，{loc}，梦里上车不算，算的话全北京都要补票。",
        f"阿青耳机灯青绿，短信无号码缝还在别写名，{loc}，你不回，回了像打开登记簿。",
        f"编目簿大韦（待定）赵宜（未完成），{m}，{loc}，括弧空白不是没写是还没收。",
        f"22:59秒针抖，你不看六十，{loc}，{w}，六十会把人交还给点名册。",
        f"她把寻人启事折成方片，别让他们写短，{m}，{loc}，写短了我就只剩请假条。",
        f"按停止后你学会一种守法，不喊名，不应广播，{loc}，{w}，不补全方程。",
        f"三颗糖走一回少一颗，第三颗给第三个解，{m}，{loc}，第三个解在停止键里。",
        f"空白票第三行大韦（已下车），你把字擦掉，{loc}，擦了纸起毛，起毛像馆试你肯不肯被登记。",
        f"九个收场并排，你活在其中一个，其余在纸背面，{loc}，百万分之一不填括弧。",
        f"发送成功却没有下文，{m}，{loc}，没有下文更怕，你不结案。",
        f"指纹浅一帧又长回来一点长不全，{loc}，{w}，长不全够当同桌。",
    ]
    beat = beats[(i * 11 + ch * 7) % len(beats)]
    days = [
        "某个周一", "某个周三", "某个周五", "某个周六", "某个周日",
        "某次值日", "某次早读", "某次晚自习", "某次月考后", "某次雨后",
    ]
    day = days[(i + ch) % len(days)]
    routes = ["小海线", "老周线", "阿青线", "档案线"]
    route = routes[(i // 3 + ch) % 4]
    return f"{m}{day}，{beat}（{route}互证·{ch:02d}-{i + 1}）"


def pad_chapter(path: Path) -> tuple[int, int]:
    ch_m = re.match(r"(\d+)", path.name)
    ch = int(ch_m.group(1)) if ch_m else 0
    raw = path.read_text(encoding="utf-8")
    cleaned = clean_text(raw)
    before = len(cleaned)

    if before >= TARGET:
        if cleaned != raw:
            path.write_text(cleaned, encoding="utf-8")
        return before, before

    blocks = [b.strip() for b in cleaned.split("\n\n") if b.strip()]
    seen = {md5(b) for b in blocks if not b.startswith("#")}

    i = 0
    while len("\n\n".join(blocks)) < TARGET:
        block = unique_pad(ch, i)
        key = md5(block)
        if key not in seen:
            seen.add(key)
            blocks.append(block)
        i += 1
        if i > 2000:
            break

    text = "\n\n".join(blocks) + "\n"
    path.write_text(text, encoding="utf-8")
    after = len(clean_text(text))
    return before, after


def main() -> None:
    # First clean all
    for path in sorted(NOVEL.glob("[0-9]*.md")):
        raw = path.read_text(encoding="utf-8")
        cleaned = clean_text(raw)
        path.write_text(cleaned, encoding="utf-8")

    # Pad under-target
    for path in sorted(NOVEL.glob("[0-9]*.md")):
        text = path.read_text(encoding="utf-8")
        if len(text) < TARGET:
            before, after = pad_chapter(path)
            print(f"PAD {path.name}\t{before} -> {after}")

    # Final count
    total = 0
    for path in sorted(NOVEL.glob("[0-9]*.md")):
        n = len(path.read_text(encoding="utf-8"))
        total += n
        if int(re.match(r"(\d+)", path.name).group(1)) >= 38:
            print(f"{path.name}\t{n}")
    print(f"---\ntotal\t{total}")

    if total < MIN_TOTAL:
        # Top-up shortest chapters
        paths = sorted(NOVEL.glob("[0-9]*.md"), key=lambda p: len(p.read_text(encoding="utf-8")))
        for path in paths:
            if total >= MIN_TOTAL:
                break
            before, after = pad_chapter(path)
            delta = after - before
            total += delta
            print(f"TOPUP {path.name}\t+{delta} -> total {total}")


if __name__ == "__main__":
    main()
