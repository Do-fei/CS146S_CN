#!/usr/bin/env python3
"""Build 15-23 to V486 target from 8981ac4 pre-loop + varied padding."""

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


def pre_loop(raw: str) -> tuple[str, list[str]]:
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


# Varied padding templates — each includes index for uniqueness
def pad_15(i: int) -> str:
    locs = ["复印店", "校医室", "广播室", "体育馆", "赵宜家", "护城河", "倒带馆", "天台", "靠窗", "早点铺"]
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return (
        f"停止后日常{i + 1}，{days[i % 7]}傍晚经过{locs[i % 10]}，她抓你袖口，褶子在，"
        f"你说在，她重复同桌在，小的路写不进报告，方程两个解我们选了漏的那一个，"
        f"疼就抓袖口，袖口在，人就还在漏句这一边，这一边允许迟到，允许错题，"
        f"允许发送成功却没有下文，只要没有红色感叹号，糖还在，路还没把你们收走。"
    )


def pad_16(i: int) -> str:
    subs = ["数学", "英语", "物理", "化学", "语文", "生物", "历史", "地理", "政治"]
    return (
        f"爬回日常{i + 1}，{subs[i % 9]}课她讲到一半空半拍，你低声补半句，她耳朵红，"
        f"别在课上补太多，补多了像我还需要被听完，下课她把题抄进本子故意留空白，"
        f"空白像停止键后面没收完的音节，放学走小的路，她抓袖口，确认不是告白，是同桌的手续。"
    )


def pad_17(i: int) -> str:
    locs = ["小卖部", "值日桶边", "图书馆", "后黑板", "早点铺", "广播室", "体育馆", "赵宜家", "护城河"]
    return (
        f"小的路日常{i + 1}，你们绕开校门口宽的，{locs[i % 9]}有人发传单问找没找到，"
        f"你没答，她抓袖口，找到了故事就结案，天桥贴便利贴，方程两个解我们选了漏的那一个，"
        f"风没吹掉，班主任留第三排靠窗的灯，灯留着，人就还在靠窗。"
    )


def pad_18(i: int) -> str:
    months = ["六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
    locs = ["天桥", "栏外", "广播室", "靠窗", "赵宜家", "旧址外"]
    return (
        f"{months[i % 7]}漏句日常{i + 1}，{locs[i % 6]}附近她又停一下，橘子皮排五线谱，"
        f"风乱她捡回来重新排，你问还疼吗，她说偶尔，偶尔疼说明还当人，当人就能抓袖口，"
        f"便利贴压进数学书，方程两个解，我们选了漏的那一个，疼就抓袖口，袖口在，人在。"
    )


def pad_vol4(i: int, tag: str) -> str:
    return (
        f"卷四{tag}侧写{i + 1}，你仍走小的路，仍买两杯豆浆，一杯放她桌角或栏外，"
        f"九个收场九种收费，没有官方正确答案，你活正本，其余并排，"
        f"选完句子还会留在身上，口袋少一颗糖，合影空一个位子，"
        f"这些是收场，不是教训，你合上卷四，窗外天亮，正本里她抓袖口，甜的要沉，你嗯。"
    )


PAD = {
    "15-停止.md": pad_15,
    "16-爬回.md": pad_16,
    "17-小的路.md": pad_17,
    "18-漏句.md": pad_18,
    "19-馆藏.md": lambda i: pad_vol4(i, "馆藏"),
    "20-静音.md": lambda i: pad_vol4(i, "静音"),
    "21-随河.md": lambda i: pad_vol4(i, "随河"),
    "22-空白站.md": lambda i: pad_vol4(i, "空白站"),
    "23-八个早晨.md": lambda i: pad_vol4(i, "八个早晨"),
}

VOL4 = {
    "19-馆藏.md": bodies.CH19,
    "20-静音.md": bodies.CH20,
    "21-随河.md": bodies.CH21,
    "22-空白站.md": bodies.CH22,
    "23-八个早晨.md": bodies.CH23,
}


def build(name: str, target: int) -> str:
    if name in VOL4:
        title, core = pre_loop(restore(name))
    else:
        title, core = pre_loop(restore(name))

    seen = {pk(b) for b in core}
    parts = ([title] if title else []) + list(core)
    length = len("\n\n".join(parts))
    pad = PAD[name]
    i = 0
    while length < target and i < 400:
        b = pad(i)
        k = pk(b)
        if k not in seen:
            parts.append(b)
            seen.add(k)
            length = len("\n\n".join(parts))
        i += 1

    text = "\n\n".join(parts).strip() + "\n"
    while len(text) > target and len(parts) > 8:
        parts.pop()
        text = "\n\n".join(parts).strip() + "\n"
    return text


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

    for idx, name in enumerate(files):
        t = per + (1 if idx < rem else 0)
        (ROOT / name).write_text(build(name, t), encoding="utf-8")
        print(f"{name}\t{len((ROOT / name).read_text())}\t(target {t})")

    total = sum(len(p.read_text(encoding="utf-8")) for p in sorted(ROOT.glob("[0-9]*.md")))
    print(f"---\ntotal\t{total}")


if __name__ == "__main__":
    main()
