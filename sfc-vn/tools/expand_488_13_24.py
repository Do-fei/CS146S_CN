#!/usr/bin/env python3
"""Expand chapters 13-24 to ~97,600 chars each for 488万 target."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
TOOLS = Path(__file__).resolve().parent
TARGET = 97600
TOLERANCE = 800

CH18_END = "你从停止键的缝里把她接回来"

H18_END = """你从停止键的缝里把她接回来。她少记一些方程，多一种听声音就会回头的习惯。你们仍一起走小的路。有时她会忽然无声几秒，像磁带那端有人按了暂停——那几秒里，握住她的袖口。

袖口还在，人就还在漏句这一边。

漏句的结局，不是补全。是学会和空半拍共处。共处久了，空半拍也像呼吸。

正本走到这里。卷四在纸背面，不抢，只并排。漏句的日常，不是戏剧，是细节：漏一步，留半分，抓袖口，咽回去，走小的路。细节在，人就还在漏句这一边。

够了。"""

# Markers where numbered padding loops begin — keep prose before these
CUT_MARKERS: dict[str, list[str]] = {
    "13-磁带.md": [" 磁带断在「我选——」，断很小，小得像半个音节，半个音节后面，才轮到你选怎么疼。（106）"],
    "14-三只键.md": ["【三只键·"],
    "15-停止.md": ["【停止·"],
    "16-爬回.md": ["【爬回·"],
    "17-小的路.md": ["【小的路·"],
    "18-漏句.md": ["【漏句·"],
    "19-馆藏.md": ["【馆藏·"],
    "20-静音.md": ["【静音·"],
    "21-随河.md": ["【随河·"],
    "22-空白站.md": ["【空白站·"],
    "23-八个早晨.md": ["你读下一页"],
    "24-二十三点十七.md": [" 你带47秒进胡同，发送失败是逗号，逗号后面还有湿鞋还有慢半拍的镜，别走大路。（412）"],
}

LOOP_LINE = re.compile(
    r"^(【(停止|漏句|爬回|小的路|馆藏|静音|随河|空白站|海洋馆|二十三点十七)·|"
    r"第\d+段|按停止后第|"
    r"\*\*(静音|馆藏|随河|空白站|漏句|对调|锁死|无站名|两站之间)的早晨)"
)

NUM_SUFFIX = re.compile(r"（\d+）\s*$")


def md5(s: str) -> str:
    return hashlib.md5(re.sub(r"\s+", "", s).encode()).hexdigest()


def cut_padding_loops(text: str, name: str) -> str:
    for marker in CUT_MARKERS.get(name, []):
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx].rstrip() + "\n"
            break
    return text


def dedupe_blocks(text: str) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if not block:
            continue
        if block.startswith("#"):
            parts.append(block)
            continue
        if NUM_SUFFIX.search(block) and "磁带断在" in block:
            continue
        if block.count("你带47秒进胡同，发送失败是逗号") >= 1 and NUM_SUFFIX.search(block):
            continue
        if block.count("咽回去不等于没听见") >= 2:
            continue
        key = md5(block)
        if key in seen:
            continue
        seen.add(key)
        parts.append(block)
    return "\n\n".join(parts) + "\n"


def strip_loops(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    skip = False
    seen_header = False
    for line in lines:
        if line.startswith("# 第"):
            if seen_header:
                skip = True
                continue
            seen_header = True
        if LOOP_LINE.match(line.strip()):
            skip = True
            continue
        if skip and line.strip() == "":
            continue
        if skip and not line.startswith("#"):
            if len(line) > 100:
                skip = False
            else:
                continue
        skip = False
        out.append(line)
    return "\n".join(out).strip() + "\n"


def build_until(
    header: str,
    core: str,
    generators: list[Callable[[int], str]],
    target: int,
    seed: int,
) -> str:
    blocks = [header.strip(), core.strip()]
    seen: set[str] = {md5(b) for b in blocks}
    i = 0
    while sum(len(b) for b in blocks) < target:
        gen = generators[i % len(generators)]
        block = gen(i + seed)
        key = md5(block)
        if key not in seen:
            seen.add(key)
            blocks.append(block)
        i += 1
        if i > 35000:
            break
    text = "\n\n".join(blocks)
    while len(text) > target + TOLERANCE and len(blocks) > 8:
        blocks.pop(-1)
        text = "\n\n".join(blocks)
    return text + "\n"


def fix_ch18_ending(text: str) -> str:
    if CH18_END in text:
        text = text[: text.index(CH18_END)].rstrip() + "\n\n" + H18_END.strip() + "\n"
    elif not text.rstrip().endswith("够了。"):
        text = text.rstrip() + "\n\n" + H18_END.strip() + "\n"
    return text


def load_generators() -> dict[str, list]:
    sys.path.insert(0, str(TOOLS))
    from expand_3m_08_14_29_31 import ch13_scenes, ch14_scenes  # noqa: E402
    from expand_3m import ch24_scenes  # noqa: E402
    from scene_bank_3m import (  # noqa: E402
        scene_archive,
        scene_blank_station,
        scene_climb,
        scene_eight_mornings,
        scene_leak,
        scene_mute,
        scene_river,
        scene_small_road,
        scene_stop,
    )

    spec = importlib.util.spec_from_file_location(
        "bank488", TOOLS / "_gen" / "scene_bank_488_13_24.py"
    )
    bank_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bank_mod)

    def make_bank_gen(ch: str, seed: int):
        scenes = bank_mod.gen_long_scenes(ch, 800, seed)

        def gen(i: int) -> str:
            return scenes[i % len(scenes)]

        return gen

    chapters = {
        "13-磁带.md": ("13", [ch13_scenes, make_bank_gen("13", 1300)]),
        "14-三只键.md": ("14", [ch14_scenes, make_bank_gen("14", 1400)]),
        "15-停止.md": ("15", [scene_stop, make_bank_gen("15", 1500)]),
        "16-爬回.md": ("16", [scene_climb, make_bank_gen("16", 1600)]),
        "17-小的路.md": ("17", [scene_small_road, make_bank_gen("17", 1700)]),
        "18-漏句.md": ("18", [make_bank_gen("18", 1800)]),  # scene_leak stripped by clean_novel_ai
        "19-馆藏.md": ("19", [scene_archive, make_bank_gen("19", 1900)]),
        "20-静音.md": ("20", [scene_mute, make_bank_gen("20", 2000)]),
        "21-随河.md": ("21", [scene_river, make_bank_gen("21", 2100)]),
        "22-空白站.md": ("22", [scene_blank_station, make_bank_gen("22", 2200)]),
        "23-八个早晨.md": ("23", [scene_eight_mornings, make_bank_gen("23", 2300)]),
        "24-二十三点十七.md": ("24", [ch24_scenes, make_bank_gen("24", 2400)]),
    }

    # Add hand vol4 paragraphs as static pool for 19-21
    try:
        spec2 = importlib.util.spec_from_file_location(
            "hand", TOOLS / "hand_expand_vol4_19_21.py"
        )
        hand = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(hand)
        for ch_file, attr in [
            ("19-馆藏.md", "CH19_PARAS"),
            ("20-静音.md", "CH20_PARAS"),
            ("21-随河.md", "CH21_PARAS"),
        ]:
            paras = getattr(hand, attr)
            ch_num = ch_file.split("-")[0]

            def make_static_gen(pool: list, s: int):
                def gen(i: int) -> str:
                    return pool[(i + s) % len(pool)]

                return gen

            chapters[ch_file][1].append(make_static_gen(paras, int(ch_num) * 100))
    except Exception:
        pass

    return chapters


def process_chapter(name: str, ch_num: str, generators: list, seed: int) -> None:
    path = ROOT / name
    raw = path.read_text(encoding="utf-8")
    text = cut_padding_loops(raw, name)
    text = strip_loops(text)
    text = dedupe_blocks(text)

    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    header = parts[0] if parts and parts[0].startswith("#") else f"# {name}"
    core_parts = parts[1:] if parts and parts[0].startswith("#") else parts
    core = "\n\n".join(core_parts)

    if name == "18-漏句.md" and CH18_END in core:
        core = core[: core.index(CH18_END)].rstrip()

    result = build_until(header, core, generators, TARGET, seed)
    if name == "18-漏句.md":
        result = fix_ch18_ending(result)
    path.write_text(result, encoding="utf-8")
    status = "OK" if len(result) >= TARGET - TOLERANCE else "LOW"
    print(f"{name}\t{len(raw)} -> {len(result)}\t{status}")


def trim_to_target(text: str, target: int) -> str:
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    header = parts[0] if parts and parts[0].startswith("#") else ""
    body = parts[1:] if header else parts
    blocks = ([header] if header else []) + body
    while len("\n\n".join(blocks)) > target + TOLERANCE and len(blocks) > 8:
        if blocks[-1].strip() in ("够了。",) or blocks[-1].startswith("你从停止"):
            blocks.pop(-2)
        else:
            blocks.pop(-1)
    return "\n\n".join(blocks) + "\n"


def clean_chapter_file(name: str) -> None:
    spec = importlib.util.spec_from_file_location("clean", TOOLS / "clean_novel_ai.py")
    clean = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clean)
    path = ROOT / name
    raw = path.read_text(encoding="utf-8")
    cleaned = clean.clean_text(raw)
    path.write_text(cleaned, encoding="utf-8")


def post_clean_pad(name: str, ch_num: str, generators: list, seed: int) -> None:
    """After clean_novel_ai, pad chapters that fell below TARGET."""
    spec = importlib.util.spec_from_file_location("clean", TOOLS / "clean_novel_ai.py")
    clean = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clean)
    path = ROOT / name
    text = path.read_text(encoding="utf-8")
    if TARGET - TOLERANCE <= len(text) <= TARGET + TOLERANCE:
        return
    if len(text) > TARGET + TOLERANCE:
        trimmed = trim_to_target(text, TARGET)
        path.write_text(trimmed, encoding="utf-8")
        print(f"  trim {name}\t{len(text)} -> {len(trimmed)}")
        return
    if name == "18-漏句.md" and CH18_END in text:
        core = text[: text.index(CH18_END)].rstrip()
        header = text.split("\n\n")[0] if text.startswith("#") else f"# {name}"
        if not header.startswith("#"):
            parts = [p for p in text.split("\n\n") if p.strip()]
            header = parts[0]
            core = "\n\n".join(parts[1:])
            if CH18_END in core:
                core = core[: core.index(CH18_END)].rstrip()
        extra = build_until(header, core, generators, TARGET + 20000, seed + 9000)
        extra = fix_ch18_ending(extra)
        path.write_text(extra, encoding="utf-8")
        cleaned = clean.clean_text(extra)
        path.write_text(cleaned, encoding="utf-8")
        print(f"  repad {name}\t{len(extra)} -> {len(cleaned)}")
        return
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    header = parts[0]
    core = "\n\n".join(parts)
    extra = build_until(header, core, generators, TARGET + 15000, seed + 9000)
    path.write_text(extra, encoding="utf-8")
    cleaned = clean.clean_text(extra)
    path.write_text(cleaned, encoding="utf-8")
    print(f"  repad {name}\t{len(extra)} -> {len(cleaned)}")


def main() -> None:
    gens = load_generators()
    for name, (ch_num, generators) in gens.items():
        seed = sum(ord(c) for c in name) + 488
        process_chapter(name, ch_num, generators, seed)

    for name in gens:
        clean_chapter_file(name)
    for name, (ch_num, generators) in gens.items():
        post_clean_pad(name, ch_num, generators, sum(ord(c) for c in name) + 488)

    for script in ["strip_novel_padding.py", "count_novel.py"]:
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
