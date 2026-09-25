#!/usr/bin/env python3
"""Expand chapters 00-12 to ~97,600 chars for 488万 project. No loc-time loop generators."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
TOOLS = Path(__file__).resolve().parent
TARGET = 97600

SLOP_BLOCK = re.compile(
    r"(阿青在.{1,10}边看你|"
    r"你想起一次值日，她擦.{1,10}的窗|"
    r"发送失败里红色感叹号又|"
    r"序章里橘子糖又|"
    r"便利店里你第\d+次|"
    r"第\d+次发送失败|"
    r"第\d+次|第\d+遍|"
    r"第一节课后|"
    r"周[一二三四五](午休|放学)|"
    r"赵宜家第\d+次想起|"
    r"胡同第\d+盏灯灭|"
    r"空位第\d+天|"
    r"压进数学书|"
    r"B面.*转半圈|"
    r"这一边，才配在.{1,10}里继续|"
    r"悬着，像方程里那个问号，问号留给同桌，你选，停，还没按，断，在「我选——」|"
    r"发送失败之后，你仍记得这些小事，记得不是浪漫，是位置|"
    r"倒带馆收未完成，不收完整，完整好编目，编目了，人就变成格子。\（\d+\）|"
    r"<!--MEGA|<!--EXPAND)"
)

BAD_LINE = re.compile(
    r"(大韦，第\d+次守|第一节课后|不写进报告|故事下一段是天桥，天桥在第八章，你现在只站在22:59里|"
    r"发送失败之后，你仍记得这些小事，记得不是浪漫，是位置|"
    r"归途·\d+|爬回·\d+|漏句日常·\d+|【小的路·\d+】|【馆藏·\d+】|【静音·\d+】)"
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
    if block.count("橘子皮排五线谱") and block.count("偶尔疼说明还当人"):
        return True
    if block.count("她抓你袖口，褶子在，你说在，她重复同桌在") > 0 and len(block) < 400:
        return True
    return False


def clean_chapter(text: str) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if not block:
            continue
        if block.startswith("<!--"):
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
        if len(text) >= target - 80:
            break
        p = p.strip()
        if not p or md5(p) in seen or is_slop(p):
            continue
        text = text.rstrip() + "\n\n" + p + "\n"
        seen.add(md5(p))
    return text


def _load_banks_488() -> dict[str, list[str]]:
    spec = importlib.util.spec_from_file_location(
        "banks488", TOOLS / "_gen" / "ch00_12_488_banks.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {ch: mod.bank_for(ch) for ch in mod.CHAPTER_FILES}


def _load_banks_007() -> dict[str, list[str]]:
    spec = importlib.util.spec_from_file_location(
        "banks007", TOOLS / "_gen" / "ch00_07_banks.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out: dict[str, list[str]] = {}
    for ch in [
        "00-序.md", "01-发送失败.md", "02-空位.md", "03-赵宜家.md",
        "04-胡同.md", "05-第三夜.md", "06-胡同深.md", "07-便利店.md",
    ]:
        out[ch] = mod.bank_for(ch)
    return out


def _load_extras() -> list[str]:
    items: list[str] = []
    for fp in sorted((TOOLS / "extras").glob("*.md")):
        for block in fp.read_text(encoding="utf-8").split("\n\n"):
            block = block.strip()
            if len(block) > 50 and not block.startswith("#"):
                items.append(block)
    for fp in [TOOLS / "bank2.txt", TOOLS / "extras_ch01.txt"]:
        if fp.exists():
            for block in fp.read_text(encoding="utf-8").split("\n\n"):
                block = block.strip()
                if len(block) > 50:
                    items.append(block)
    return items


def _load_supplement() -> tuple[dict[str, list[str]], list[str]]:
    spec = importlib.util.spec_from_file_location(
        "supp488", TOOLS / "_gen" / "ch488_supplement.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ch12 = mod.ch12_extra()
    topup: dict[str, list[str]] = {}
    for ch in [
        "00-序.md", "01-发送失败.md", "02-空位.md", "03-赵宜家.md",
        "04-胡同.md", "05-第三夜.md", "06-胡同深.md", "07-便利店.md",
        "08-天桥.md", "09-西单.md", "10-食街.md", "11-三楼.md", "12-倒带馆.md",
    ]:
        topup[ch] = mod.topup_for(ch)
    return topup, ch12


def merge_banks() -> dict[str, list[str]]:
    b488 = _load_banks_488()
    b007 = _load_banks_007()
    extras = _load_extras()
    topup, ch12_extra = _load_supplement()
    out: dict[str, list[str]] = {}
    for ch in b488:
        bank: list[str] = []
        seen: set[str] = set()
        sources = [b488.get(ch, []), b007.get(ch, []), topup.get(ch, []), extras]
        if ch == "12-倒带馆.md":
            sources.insert(0, ch12_extra)
        for source in sources:
            for p in source:
                k = md5(p)
                if k in seen or is_slop(p):
                    continue
                seen.add(k)
                bank.append(p)
        out[ch] = bank
    return out


def main() -> None:
    chapters = [
        "00-序.md", "01-发送失败.md", "02-空位.md", "03-赵宜家.md",
        "04-胡同.md", "05-第三夜.md", "06-胡同深.md", "07-便利店.md",
        "08-天桥.md", "09-西单.md", "10-食街.md", "11-三楼.md", "12-倒带馆.md",
    ]
    banks = merge_banks()

    for name in chapters:
        path = ROOT / name
        raw = path.read_text(encoding="utf-8")
        cleaned = clean_chapter(raw)
        padded = pad_unique(cleaned, TARGET, banks.get(name, []))
        path.write_text(padded, encoding="utf-8")
        n = len(padded)
        status = "OK" if n >= TARGET - 500 else "LOW"
        print(f"{name}\t{len(raw)} -> {n}\t{status}")

    for script in ["clean_novel_ai.py", "count_novel.py"]:
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
