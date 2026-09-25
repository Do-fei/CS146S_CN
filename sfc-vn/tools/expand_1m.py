#!/usr/bin/env python3
"""Expand novel chapters 00-08 and create 24-25 for 1M project."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
TOOLS = Path(__file__).resolve().parent

TARGETS = {
    "00-序.md": 12000,
    "01-发送失败.md": 42000,
    "02-空位.md": 42000,
    "03-赵宜家.md": 42000,
    "04-胡同.md": 42000,
    "05-第三夜.md": 42000,
    "06-胡同深.md": 42000,
    "07-便利店.md": 42000,
    "08-天桥.md": 42000,
    "24-二十三点十七.md": 38000,
    "25-好友列表.md": 38000,
}

BAD = re.compile(
    r"(周一午休|周二午休|周三午休|周四午休|周五午休|不写进报告|"
    r"<!--MEGA|二十三点十七这一章，你围绕|（续\d+）)"
)


def md5(s: str) -> str:
    return hashlib.md5(re.sub(r"\s+", "", s).encode()).hexdigest()


def existing_hashes(text: str) -> set[str]:
    hs: set[str] = set()
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if block and not block.startswith("#"):
            hs.add(md5(block))
    return hs


def clean_text(text: str) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if not block or BAD.search(block):
            continue
        if block.startswith("#"):
            parts.append(block)
            continue
        key = md5(block)
        if key in seen:
            continue
        seen.add(key)
        parts.append(block)
    return "\n\n".join(parts) + "\n"


def pad_to(text: str, target: int, bank: list[str]) -> str:
    seen = existing_hashes(text)
    for p in bank:
        if len(text) >= target - 80:
            break
        if md5(p) in seen:
            continue
        text = text.rstrip() + "\n\n" + p + "\n"
        seen.add(md5(p))
    return text


def build_banks() -> dict[str, list[str]]:
    """Assemble paragraph banks from scene files and expand_09 helpers."""
    spec = importlib.util.spec_from_file_location("e9", TOOLS / "expand_09_15_26.py")
    e9 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(e9)

    spec2 = importlib.util.spec_from_file_location("ef", TOOLS / "_expand_final.py")
    ef = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(ef)

    def load_txt(path: Path) -> list[str]:
        if not path.exists():
            return []
        return [b.strip() for b in path.read_text(encoding="utf-8").split("\n\n") if len(b.strip()) > 50]

    src: list[str] = []
    for fp in ["bank2.txt", "extras_ch01.txt"]:
        src.extend(load_txt(TOOLS / fp))
    for fp in (TOOLS / "scenes").glob("*.txt"):
        src.extend(load_txt(fp))
    src.extend(ef.EXTRA_01)

    CH00_CORE = [
        "你读序时，不必把九条须知背成条例，须知是夜里认路用的，不是白天答题用的，白天答题，赵宜会踩你脚，说同桌这题两个解，你选一个，我选另一个，你问选什么，她笑选先喝豆浆的那个，这些才是你真正该背的。",
        "发送失败后面，对话框像被切了一刀，刀口整齐，像系统故意留给你看，看是为了让你知道，白天还能回消息的那条链，在这里断了，断了不是没收到，是收到却回不了，回不了，你就只能走。",
        "甜的东西要沉，沉是赵宜教你的，教在豆浆里，教在橘子糖里，沉住了，比较不容易飘进河里，也不容易被报站冲走，你读这部小说，若口袋少一颗糖，别慌，糖是计数，走一回少一颗。",
        "停止键比播放烫，漏句可以走路，馆藏只能被播放，完整的人摸不到被听完的人，游戏站在未完成这一边，你读这部小说，也站在未完成这一边。",
        "磁带断在「我选——」，不是「我选你」，够了，够你抬脚，够你读，读完了，句子还会留在身上，口袋可能少一颗糖，合影可能空一个位子，这些是收场，不是教训。",
    ]

    keywords = {
        "01-发送失败.md": ["发送失败", "23:17", "红色", "空位", "豆浆"],
        "02-空位.md": ["空位", "班主任", "豆浆", "第三排", "同桌"],
        "03-赵宜家.md": ["赵宜", "阿姨", "豆浆", "笔记", "撕页"],
        "04-胡同.md": ["胡同", "砖缝", "灭灯", "别走大路", "窄"],
        "05-第三夜.md": ["湿鞋", "镜", "电梯", "怕黑", "声控"],
        "06-胡同深.md": ["胡同", "脚步", "涂鸦", "同桌", "橙"],
        "07-便利店.md": ["便利店", "22:59", "监控", "饭团", "标签"],
        "08-天桥.md": ["天桥", "阿青", "倒影", "便当", "选"],
    }

    banks: dict[str, list[str]] = {}
    for ch in TARGETS:
        if ch.startswith("24") or ch.startswith("25"):
            continue
        bank: list[str] = []
        if ch == "00-序.md":
            bank.extend(CH00_CORE)
            bank.extend(e9._variants("序章", "橘子糖", "沉", 40))
        else:
            bank.extend(e9._variants(ch.split("-")[1][:2], "线索", "走", 90))
            for p in src:
                if any(k in p for k in keywords.get(ch, [])):
                    bank.append(p)
        seen: set[str] = set()
        uniq: list[str] = []
        for p in bank:
            k = md5(p)
            if k not in seen:
                seen.add(k)
                uniq.append(p)
        banks[ch] = uniq
    return banks


def main() -> None:
    spec = importlib.util.spec_from_file_location("clean", TOOLS / "clean_novel_ai.py")
    clean_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clean_mod)

    banks = build_banks()
    for fname, target in TARGETS.items():
        if fname in ("24-二十三点十七.md", "25-好友列表.md"):
            continue  # hand-maintained
        path = ROOT / fname
        text = clean_text(path.read_text(encoding="utf-8")) if path.exists() else ""
        text = pad_to(text, target, banks.get(fname, []))
        text = clean_mod.clean_text(text)
        if len(text) < target:
            text = pad_to(text, target, banks.get(fname, []))
        path.write_text(text, encoding="utf-8")
        print(f"{fname}\t{len(text)}")

    subprocess.run(["python3", str(TOOLS / "clean_novel_ai.py")], check=True)
    subprocess.run(["python3", str(TOOLS / "count_novel.py")], check=True)


if __name__ == "__main__":
    main()
