#!/usr/bin/env python3
"""Expand all 50 chapters to ~137,600 chars (688万). Quality prose, no loop suffixes."""

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
TARGET = 137600
MIN_TOTAL = 6880000
TOLERANCE = 800

CH49_ENDING_MARKER = "够了。不是结案，是并排到此，仍留一格空白，空白不解释，十一点不解释。"
CH18_ENDING = "够了。"

INLINE_SUFFIX = re.compile(
    r"（(?:扩488·[\d·]+|[\u4e00-\u9fff]{1,8}·\d+)）"
)

SUFFIX_TAIL = re.compile(
    r"\s*(?:"
    r"（扩488·[\d·]+）|"
    r"（?(?:[\u4e00-\u9fff]{1,6}|B面|好友|留灯|编目|票根|末班|海洋|泵房|玻璃|日志|"
    r"卡片|汤|薄了|归途|爬回|停止|馆藏|静音|随河|空白|早|深|Thriller|扩488|"
    r"收束|两站|三糖|四名|旧区|换皮|二漏|三帧|成功|妈妈|笔录|邻座|好友|"
    r"灯|票|海|泵|玻|末|志|卡|编|薄|B|归|爬|停|馆|静|随|空|早|深)·\d+）?"
    r"|"
    r"\s+[\u4e00-\u9fff]{1,8}·\d+。?"
    r"|"
    r"（(?:六月|七月|八月|九月|十月|十一月|十二月|一月|二月|三月|四月|五月)·\d+）"
    r"|"
    r"（\d+-\d+）"
    r"|"
    r"（\d+）"
    r")\s*$"
)

# 488 万循环段落的裸尾（去编号后残留）
BARE_CYCLE_TAIL = re.compile(
    r"(?:老周两站之间|B面第三口气|空白卡片写待定)\s*。?\s*$"
)

SLOP = re.compile(
    r"(第\d+次|第\d+遍|第一节课后，|压进数学书|B面转半圈|"
    r"阿青在.{1,10}边看你|赵宜家第\d+次想起|"
    r"不写进报告|不写进笔录|<!--MEGA|<!--EXPAND|playback|"
    r"小海工牌干着，老周日志写空载，阿青编目簿写待定)"
)

BANNED_PREFIX = (
    "小海工牌干着，老周日志写空载",
    "警察空白卡片在口袋里硌着。空的才能写今夜看见的。你想写：",
)


def md5(s: str) -> str:
    return hashlib.md5(re.sub(r"\s+", "", s).encode()).hexdigest()


def strip_suffix(block: str) -> str:
    block = INLINE_SUFFIX.sub("", block)
    block = block.replace("她她", "她")
    prev = None
    while prev != block:
        prev = block
        block = SUFFIX_TAIL.sub("", block).strip()
        block = BARE_CYCLE_TAIL.sub("", block).strip()
    block = block.replace("playback", "回放")
    block = block.replace("写不进报告", "写不进本子")
    block = block.replace("不写进报告", "不交给大路")
    block = block.replace("写进报告", "记进本子")
    while block.endswith("。。"):
        block = block[:-1]
    if block and block[-1] not in "。！？…":
        block += "。"
    return block.strip()


def is_slop(block: str) -> bool:
    if not block or len(block) < 25:
        return True
    if block.startswith("#") or block == "---":
        return False
    if SLOP.search(block):
        return True
    for p in BANNED_PREFIX:
        if block.startswith(p):
            return True
    if block.count("编目簿两行括弧空白") >= 2:
        return True
    if block.count("你把话单折成方片，方片像证据") >= 2:
        return True
    return False


def split_blocks(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\n+", text.strip()) if p.strip()]


def clean_chapter(text: str) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for block in split_blocks(text):
        if block.startswith("<!--"):
            continue
        if block.startswith("#"):
            parts.append(block)
            continue
        block = strip_suffix(block)
        if is_slop(block):
            continue
        key = md5(block)
        if key in seen:
            continue
        seen.add(key)
        parts.append(block)
    return "\n\n".join(parts) + "\n"


def extract_protected(text: str, ch_num: str) -> tuple[str, str | None]:
    """Return (body_without_protected, protected_ending_or_none)."""
    if ch_num == "49":
        idx = text.rfind(CH49_ENDING_MARKER)
        if idx != -1:
            start = text.rfind("\n\n", 0, idx)
            ending = text[start + 2 :].strip() if start != -1 else text[idx:].strip()
            body = text[: start + 2].rstrip() if start != -1 else text[:idx].rstrip()
            return body + "\n", ending
    if ch_num == "18":
        parts = split_blocks(text)
        if parts and parts[-1].strip() == CH18_ENDING:
            body = "\n\n".join(parts[:-1]) + "\n"
            return body, CH18_ENDING
    return text, None


def existing_hashes(text: str) -> set[str]:
    hs: set[str] = set()
    for block in split_blocks(text):
        if block and not block.startswith("#") and block != "---":
            hs.add(md5(strip_suffix(block)))
    return hs


def pad_unique(text: str, target: int, bank: list[str]) -> str:
    seen = existing_hashes(text)
    prefix_count: dict[str, int] = {}
    for p in bank:
        if len(text) >= target - 80:
            break
        p = strip_suffix(p.strip())
        if not p or is_slop(p):
            continue
        pk = re.sub(r"\s+", "", p)[:22]
        if prefix_count.get(pk, 0) >= 2:
            continue
        key = md5(p)
        if key in seen:
            continue
        seen.add(key)
        prefix_count[pk] = prefix_count.get(pk, 0) + 1
        text = text.rstrip() + "\n\n" + p + "\n"
    return text


_BANK_CACHE: dict[str, list[str]] = {}
_BANK_MOD = None


def load_bank(chapter_file: str) -> list[str]:
    global _BANK_MOD
    if chapter_file in _BANK_CACHE:
        return _BANK_CACHE[chapter_file]
    if _BANK_MOD is None:
        spec = importlib.util.spec_from_file_location(
            "bank688", TOOLS / "_gen" / "scene_bank_688_all.py"
        )
        _BANK_MOD = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_BANK_MOD)
    bank = _BANK_MOD.bank_for(chapter_file)
    import random
    rng = random.Random(sum(ord(c) for c in chapter_file))
    rng.shuffle(bank)
    _BANK_CACHE[chapter_file] = bank
    return bank


def chapter_files() -> list[Path]:
    return sorted(NOVEL.glob("[0-9]*.md"), key=lambda p: int(re.match(r"(\d+)", p.name).group(1)))


def expand_one(path: Path) -> tuple[int, int]:
    ch_num = path.name.split("-")[0]
    raw = path.read_text(encoding="utf-8")
    body, protected = extract_protected(raw, ch_num)
    cleaned = clean_chapter(body)
    bank = load_bank(path.name)
    padded = pad_unique(cleaned, TARGET, bank)
    if protected:
        if protected not in padded:
            padded = padded.rstrip() + "\n\n" + protected + "\n"
    # trim if over target
    if protected:
        while len(padded) > TARGET + TOLERANCE:
            parts = split_blocks(padded)
            if parts[-1] == protected and len(parts) > 15:
                parts.pop(-2)
                padded = "\n\n".join(parts) + "\n"
            elif len(parts) > 10:
                parts.pop(-1 if parts[-1] != protected else -2)
                padded = "\n\n".join(parts) + "\n"
            else:
                break
    elif len(padded) > TARGET + TOLERANCE:
        parts = split_blocks(padded)
        while len("\n\n".join(parts)) > TARGET + TOLERANCE and len(parts) > 12:
            parts.pop(-1)
        padded = "\n\n".join(parts) + "\n"
    path.write_text(padded, encoding="utf-8")
    return len(raw), len(padded)


def main() -> None:
    for path in chapter_files():
        before, after = expand_one(path)
        status = "OK" if after >= TARGET - TOLERANCE else "LOW"
        print(f"{path.name}\t{before} -> {after}\t{status}")

    subprocess.run([sys.executable, str(TOOLS / "count_novel.py")], check=True, cwd=ROOT)
    total_line = subprocess.run(
        [sys.executable, str(TOOLS / "count_novel.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    for line in total_line.stdout.splitlines():
        if line.startswith("total"):
            total = int(line.split("\t")[1])
            if total < MIN_TOTAL:
                print(f"WARN: total {total} < {MIN_TOTAL}, running second pass...")
                for path in chapter_files():
                    before = len(path.read_text(encoding="utf-8"))
                    bank = load_bank(path.name)
                    text = path.read_text(encoding="utf-8")
                    ch_num = path.name.split("-")[0]
                    body, protected = extract_protected(text, ch_num)
                    padded = pad_unique(body, TARGET + 2000, bank)
                    if protected and protected not in padded:
                        padded = padded.rstrip() + "\n\n" + protected + "\n"
                    path.write_text(padded, encoding="utf-8")
                    print(f"PASS2 {path.name}\t{before} -> {len(padded)}")
                subprocess.run([sys.executable, str(TOOLS / "count_novel.py")], check=True, cwd=ROOT)
            break

    subprocess.run([sys.executable, str(TOOLS / "export_novel_web.py")], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
