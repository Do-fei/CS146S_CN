#!/usr/bin/env python3
"""Targeted cleanup of 488 cyclic remnants; preserve 688万 volume."""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

spec = importlib.util.spec_from_file_location("expand_688", TOOLS / "expand_688.py")
e688 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e688)

TARGET = e688.TARGET
MIN_TOTAL = e688.MIN_TOTAL
TOLERANCE = e688.TOLERANCE

CYCLIC_ONCE = (
    "按停止后第七天，九月夜",
    "残芯标签被汗渍晕开，只剩：第三排",
    "波形放慢，在拧的那一点",
    "残芯最后两秒，出现极轻一句",
    "阿青在馆里等你消息",
    "走出校门，听见身后极轻一声咳嗽",
    "英语课她借你耳机，说听听这句怎么读",
    "班主任第二天没提灯，只提作业",
    "值日那天你擦黑板，她洗抹布",
)

PREFIX_MAX_CLEAN = 2
REP_THRESHOLD = 6  # chapter needs deep clean if any opener repeats this many times


def prefix_key(block: str) -> str:
    s = e688.strip_suffix(block)
    m = re.match(r"^(.{8,28}?)[，。：]", s)
    return m.group(1) if m else s[:20]


def cyclic_once_key(block: str) -> str | None:
    s = e688.strip_suffix(block)
    for pat in CYCLIC_ONCE:
        if pat in s:
            return pat
    return None


def repetition_score(text: str) -> int:
    counts: Counter[str] = Counter()
    for block in e688.split_blocks(text):
        if block.startswith("#"):
            continue
        counts[prefix_key(block)] += 1
    return max(counts.values()) if counts else 0


def strip_tails_only(text: str) -> str:
    parts: list[str] = []
    for block in e688.split_blocks(text):
        if block.startswith("#"):
            parts.append(block)
        else:
            parts.append(e688.strip_suffix(block))
    return "\n\n".join(parts) + "\n"


def aggressive_clean(text: str) -> str:
    parts: list[str] = []
    seen_full: set[str] = set()
    prefix_count: dict[str, int] = defaultdict(int)
    cyclic_seen: set[str] = set()

    for block in e688.split_blocks(text):
        if block.startswith("<!--"):
            continue
        if block.startswith("#"):
            parts.append(block)
            continue
        block = e688.strip_suffix(block)
        if e688.is_slop(block):
            continue
        fk = e688.md5(block)
        if fk in seen_full:
            continue
        ckey = cyclic_once_key(block)
        if ckey is not None:
            if ckey in cyclic_seen:
                continue
            cyclic_seen.add(ckey)
        pk = prefix_key(block)
        if prefix_count[pk] >= PREFIX_MAX_CLEAN:
            continue
        prefix_count[pk] += 1
        seen_full.add(fk)
        parts.append(block)
    return "\n\n".join(parts) + "\n"


def pad_relaxed(text: str, target: int, bank: list[str], prefix_cap: int = 4) -> str:
    seen = e688.existing_hashes(text)
    prefix_count: dict[str, int] = defaultdict(int)
    for p in bank:
        if len(text) >= target - 60:
            break
        p = e688.strip_suffix(p.strip())
        if not p or e688.is_slop(p):
            continue
        pk = prefix_key(p)[:22]
        if prefix_count[pk] >= prefix_cap:
            continue
        key = e688.md5(p)
        if key in seen:
            continue
        seen.add(key)
        prefix_count[pk] += 1
        text = text.rstrip() + "\n\n" + p + "\n"
    return text


def fix_one(path: Path, force_deep: bool = False) -> tuple[int, int, str]:
    ch_num = path.name.split("-")[0]
    raw = path.read_text(encoding="utf-8")
    body, protected = e688.extract_protected(raw, ch_num)
    score = repetition_score(body)
    deep = force_deep or score >= REP_THRESHOLD
    cleaned = aggressive_clean(body) if deep else strip_tails_only(body)
    bank = e688.load_bank(path.name)
    cap = 3 if deep else 5
    padded = pad_relaxed(cleaned, TARGET, bank, prefix_cap=cap)
    if protected and protected not in padded:
        padded = padded.rstrip() + "\n\n" + protected + "\n"
    if protected:
        while len(padded) > TARGET + TOLERANCE and len(e688.split_blocks(padded)) > 15:
            parts = e688.split_blocks(padded)
            parts.pop(-2 if parts[-1] == protected else -1)
            padded = "\n\n".join(parts) + "\n"
    elif len(padded) > TARGET + TOLERANCE:
        parts = e688.split_blocks(padded)
        while len("\n\n".join(parts)) > TARGET + TOLERANCE and len(parts) > 12:
            parts.pop(-1)
        padded = "\n\n".join(parts) + "\n"
    path.write_text(padded, encoding="utf-8")
    mode = "DEEP" if deep else "TAIL"
    return len(raw), len(padded), mode


def main() -> None:
    files = e688.chapter_files()
    for path in files:
        before, after, mode = fix_one(path)
        status = "OK" if after >= TARGET - TOLERANCE else "LOW"
        print(f"{path.name}\t{before} -> {after}\t{status}\t{mode}")

    total = sum(len(p.read_text(encoding="utf-8")) for p in files)
    if total < MIN_TOTAL:
        print(f"WARN total {total} < {MIN_TOTAL}, padding low chapters...")
        for path in files:
            text = path.read_text(encoding="utf-8")
            if len(text) >= TARGET - TOLERANCE:
                continue
            ch_num = path.name.split("-")[0]
            body, protected = e688.extract_protected(text, ch_num)
            bank = e688.load_bank(path.name)
            before = len(text)
            padded = pad_relaxed(body, TARGET + 800, bank, prefix_cap=6)
            if protected and protected not in padded:
                padded = padded.rstrip() + "\n\n" + protected + "\n"
            path.write_text(padded, encoding="utf-8")
            print(f"PAD {path.name}\t{before} -> {len(padded)}")

    subprocess.run([sys.executable, str(TOOLS / "count_novel.py")], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(TOOLS / "export_novel_web.py")], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
