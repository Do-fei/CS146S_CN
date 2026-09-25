#!/usr/bin/env python3
"""全书狐尾×远瞳融合：仅替换模板/标签段，再扩写维持688万字。"""

from __future__ import annotations

import importlib.util
import random
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOVEL = ROOT / "docs" / "novel"
TOOLS = Path(__file__).resolve().parent

spec = importlib.util.spec_from_file_location("expand_688", TOOLS / "expand_688.py")
e688 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e688)

TARGET = e688.TARGET
MIN_TOTAL = e688.MIN_TOTAL
TOLERANCE = e688.TOLERANCE

TAG_RE = re.compile(r"^【[^】]+】")

TEMPLATE_STARTS = (
    "老周在后视镜里看你：「小的路，懂？」",
    "赵宜忽然停，像磁带那端有人按暂停",
    "阿青短信无号码：「",
    "警察空白卡片在口袋里硌着，空的才能写今夜看见的",
    "像一枚没拆的糖，你想起她",
    "电信营业厅，",
    "试听间，",
    "广播室后排，",
    "末班车站台，",
    "赵宜家厨房，",
    "第三排靠窗，",
    "爸在厨房喊：「大韦，汤好了。」你应一声，端着碗走到",
    "化学实验室，",
    "护城河堤，",
    "派出所门口，",
    "西单围挡外，",
)

CYCLIC_SIG = (
    "按停止后第七天，九月夜",
    "残芯标签被汗渍晕开，只剩：第三排",
    "波形放慢，在拧的那一点",
    "残芯最后两秒，出现极轻一句",
    "阿青在馆里等你消息，你发：找到东西",
    "走出校门，听见身后极轻一声咳嗽",
)


def is_template(block: str) -> bool:
    if not block or block.startswith("#"):
        return False
    if TAG_RE.match(block):
        return True
    if e688.is_slop(block):
        return True
    s = block.strip()
    if any(s.startswith(t) for t in TEMPLATE_STARTS):
        return True
    if "当时你笑，现在不笑" in s and len(s) < 150:
        return True
    hits = sum(
        1
        for t in (
            "阿青耳机灯青绿，短信：缝还在",
            "编目簿缺页正是待定，括弧空白不是没写",
            "他把硬币弹起来又接住，线那面朝你",
            "你摸袖口，褶还在，褶像白天的证据",
        )
        if t in s
    )
    return hits >= 2


def cyclic_key(block: str) -> str | None:
    s = e688.strip_suffix(block)
    for sig in CYCLIC_SIG:
        if sig in s:
            return sig
    return None


def load_banks(chapter_file: str) -> list[str]:
    banks: list[str] = []
    for mod_name, rel in (
        ("fox_yuan", "_gen/scene_bank_fox_yuan.py"),
        ("bank688", "_gen/scene_bank_688_all.py"),
    ):
        spec2 = importlib.util.spec_from_file_location(mod_name, TOOLS / rel)
        mod = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(mod)
        banks.extend(mod.bank_for(chapter_file))
    rng = random.Random(sum(ord(c) for c in chapter_file) + 770000)
    rng.shuffle(banks)
    return banks


def pad_to_target(text: str, target: int, bank: list[str]) -> str:
    seen = e688.existing_hashes(text)
    prefix_count: dict[str, int] = defaultdict(int)
    for p in bank:
        if len(text) >= target - 40:
            break
        p = e688.strip_suffix(p.strip())
        if not p or len(p) < 35 or e688.is_slop(p):
            continue
        pk = re.sub(r"\s+", "", p)[:20]
        if prefix_count[pk] >= 3:
            continue
        key = e688.md5(p)
        if key in seen:
            continue
        seen.add(key)
        prefix_count[pk] += 1
        text = text.rstrip() + "\n\n" + p + "\n"
    return text


def transform(text: str, ch_num: str, bank: list[str]) -> str:
    body, protected = e688.extract_protected(text, ch_num)
    out: list[str] = []
    cyclic_seen: set[str] = set()
    bi = 0

    def next_scene() -> str | None:
        nonlocal bi
        while bi < len(bank):
            p = e688.strip_suffix(bank[bi].strip())
            bi += 1
            if p and len(p) >= 35 and not is_template(p):
                return p
        return None

    for block in e688.split_blocks(body):
        if block.startswith("#"):
            out.append(block)
            continue
        block = e688.strip_suffix(block)
        ck = cyclic_key(block)
        if ck is not None:
            if ck in cyclic_seen or is_template(block):
                repl = next_scene()
                out.append(repl if repl else block)
                if ck not in cyclic_seen:
                    cyclic_seen.add(ck)
                continue
            cyclic_seen.add(ck)
        if is_template(block):
            repl = next_scene()
            out.append(repl if repl else block)
            continue
        out.append(block)

    merged = "\n\n".join(out) + "\n"
    merged = pad_to_target(merged, TARGET, bank[bi:])
    if protected and protected not in merged:
        merged = merged.rstrip() + "\n\n" + protected + "\n"
    if protected:
        while len(merged) > TARGET + TOLERANCE and len(e688.split_blocks(merged)) > 14:
            parts = e688.split_blocks(merged)
            parts.pop(-2 if parts[-1] == protected else -1)
            merged = "\n\n".join(parts) + "\n"
    return merged


def chapter_files() -> list[Path]:
    return sorted(NOVEL.glob("[0-9]*.md"), key=lambda p: int(re.match(r"(\d+)", p.name).group(1)))


def main() -> None:
    for path in chapter_files():
        ch_num = path.name.split("-")[0]
        before = len(path.read_text(encoding="utf-8"))
        bank = load_banks(path.name)
        out = transform(path.read_text(encoding="utf-8"), ch_num, bank)
        path.write_text(out, encoding="utf-8")
        after = len(out)
        print(f"{path.name}\t{before} -> {after}\t{'OK' if after >= TARGET - TOLERANCE else 'LOW'}")

    total = sum(len(p.read_text(encoding="utf-8")) for p in chapter_files())
    if total < MIN_TOTAL:
        print(f"WARN total {total}, second pad pass...")
        for path in chapter_files():
            ch_num = path.name.split("-")[0]
            text = path.read_text(encoding="utf-8")
            if len(text) >= TARGET - 200:
                continue
            body, protected = e688.extract_protected(text, ch_num)
            bank = load_banks(path.name)
            padded = pad_to_target(body, TARGET + 500, bank)
            if protected and protected not in padded:
                padded = padded.rstrip() + "\n\n" + protected + "\n"
            path.write_text(padded, encoding="utf-8")
            print(f"PAD {path.name} -> {len(padded)}")

    subprocess.run([sys.executable, str(TOOLS / "count_novel.py")], check=True, cwd=ROOT)
    subprocess.run([sys.executable, str(TOOLS / "export_novel_web.py")], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
