#!/usr/bin/env python3
"""Final quality pass: rewrite chapters 38-49 to Qidian-style prose, no loop suffixes."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOVEL = ROOT / "docs" / "novel"
TOOLS = Path(__file__).resolve().parent
TARGET = 98300
TOLERANCE = 600

CHAPTERS = [
    "38-两站之间长.md",
    "39-第三颗糖.md",
    "40-第四个名字.md",
    "41-崇文宣武.md",
    "42-城换皮.md",
    "43-第二个漏句.md",
    "44-薄了长.md",
    "45-发送成功.md",
    "46-赵宜妈妈.md",
    "47-警察笔记本.md",
    "48-试听间邻座.md",
    "49-百万分之一.md",
]

LOOP_SUFFIX = re.compile(
    r"\s*(?:"
    r"（?(?:收束·|两站·|三糖·|四名·|旧区·|换皮·|二漏·|三帧·|成功·|妈妈·|笔录·|邻座·|"
    r"票根·|留灯·|海洋·|末班·|日志·|泵房·|玻璃·|卡片·|汤·|编目·|薄了·|B面·|好友·|扩488·)\d+）?"
    r"|"
    r" 妈妈·\d+"
    r"|"
    r" 两站·\d+"
    r"|"
    r" 收束·\d+"
    r"|"
    r"playback"
    r")\s*$",
    re.MULTILINE,
)

BANNED_INLINE = re.compile(
    r"第\d+次|第一节课后，|压进数学书|B面转半圈|阿青在.{1,8}边看你|"
    r"（\d+-\d+）|（\d+）\s*$|【.{1,12}·.{1,8}】"
)


def md5(s: str) -> str:
    return hashlib.md5(re.sub(r"\s+", "", s).encode()).hexdigest()


def load_bank():
    spec = importlib.util.spec_from_file_location(
        "bank38", TOOLS / "_gen" / "scene_bank_488_38_49.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sanitize(text: str) -> str:
    text = LOOP_SUFFIX.sub("", text)
    text = re.sub(r"playback", "回放", text)
    text = text.replace("写不进报告", "写不进本子")
    text = text.replace("不写进报告", "不交给大路")
    text = text.replace("写进报告", "记进本子")
    return text.strip()


def is_bad_block(block: str) -> bool:
    if not block or len(block) < 30:
        return True
    if BANNED_INLINE.search(block):
        return True
    if re.search(r"(?:收束·|两站·|三糖·|四名·|旧区·|换皮·|二漏·|三帧·|成功·|妈妈·|笔录·|邻座·)\d+", block):
        return True
    if block.count("编目簿两行括弧空白") >= 2:
        return True
    if block.count("豆浆两杯她吸管点杯壁三下") >= 2:
        return True
    if "小海工牌干着，老周日志写空载，阿青编目簿写待定" in block:
        return True
    if block.count("你把话单折成方片，方片像证据") >= 1 and block.count("三条线在这分钟交叉") >= 1:
        return True
    return False


def _prefix_key(block: str) -> str:
    s = re.sub(r"\s+", "", block)[:24]
    return s


def build_chapter(ch_num: str, filename: str, bank_mod) -> str:
    header = bank_mod.HEADERS[ch_num]
    opening = bank_mod.OPENINGS[ch_num]
    seed = sum(ord(c) for c in filename) + 48800
    scenes = bank_mod.bank_for(ch_num, seed)

    blocks: list[str] = [header, opening, "---"]
    seen: set[str] = {md5(b) for b in blocks}
    prefix_count: dict[str, int] = {}
    opening_key = _prefix_key(opening)

    for scene in scenes:
        scene = sanitize(scene)
        if is_bad_block(scene):
            continue
        if _prefix_key(scene) == opening_key:
            continue
        pk = _prefix_key(scene)
        if prefix_count.get(pk, 0) >= 2:
            continue
        key = md5(scene)
        if key in seen:
            continue
        seen.add(key)
        prefix_count[pk] = prefix_count.get(pk, 0) + 1
        blocks.append(scene)
        if sum(len(b) for b in blocks) >= TARGET + TOLERANCE:
            break

    text = "\n\n".join(blocks)

    if ch_num == "49":
        ending = bank_mod.CH49_ENDING
        if md5(ending) not in seen:
            blocks.append(ending)
            text = "\n\n".join(blocks)

    while len(text) > TARGET + TOLERANCE and len(blocks) > 12:
        if blocks[-1] == bank_mod.CH49_ENDING and ch_num == "49":
            blocks.pop(-2)
        else:
            blocks.pop(-1)
        text = "\n\n".join(blocks)

    return text + "\n"


def verify_no_loops(text: str, name: str) -> None:
    hits = len(re.findall(r"(?:收束·|两站·|三糖·|四名·|旧区·|换皮·|二漏·|三帧·|成功·|妈妈·|笔录·|邻座·)\d+", text))
    if hits:
        print(f"WARN {name}: {hits} loop suffix remnants")
    if "playback" in text:
        print(f"WARN {name}: playback still present")


def main() -> None:
    bank = load_bank()
    for filename in CHAPTERS:
        ch_num = filename.split("-")[0]
        path = NOVEL / filename
        before = len(path.read_text(encoding="utf-8")) if path.exists() else 0
        text = build_chapter(ch_num, filename, bank)
        path.write_text(text, encoding="utf-8")
        verify_no_loops(text, filename)
        print(f"{filename}\t{before} -> {len(text)}")

    subprocess.run([sys.executable, str(TOOLS / "count_novel.py")], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
