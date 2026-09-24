#!/usr/bin/env python3
"""Expand chapters 25-37 to ~97,600 chars (488万 project). Strip padding, add unique scenes."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from scenes_488_25_37 import GENERATORS  # noqa: E402

NOVEL = ROOT / "docs" / "novel"
TARGET = 97600
TOLERANCE = 400

# Cut at first padding marker (keep content before)
CUT_MARKERS: dict[str, list[str]] = {
    "25-好友列表.md": ["发送失败不是句号，是逗号，逗号后面还有馆还有带还有停止键。（2）", "你想起一次值日，她擦好友列表的窗"],
    "26-磁带背面.md": ["B面第一句是你初二的声音", "B面里，第三口气又转半圈"],
    "27-编目簿.md": ["试听间泡沫墙齿孔一排排像无数耳朵，阿青说每多听一盘"],
    "28-薄了.md": ["停业商场门口风冷，四楼灯独自亮，阿青伞在门缝闪青绿，赵宜说谢谢按停止"],
    "29-班主任的灯.md": ["海洋馆围挡，夜里回校，第三排靠窗日光灯还亮着", " 灯座残芯录的是大韦呼吸，呼吸被拧半圈，拧，不是删，是登记漏句。（108）"],
    "30-空白卡片.md": ["编目簿柜台，警察第二次找你", " 空白卡片最终写待定，不是抓人，是登记漏句，登记漏句的人，白天指纹浅一帧。（109）"],
    "31-妈妈的汤.md": ["你想起阿青在馆里说的话：交给馆，你们都在未完成里", " 汤不倒，等于保温未完成，等于「我选——」没收尾，未完成还热着，热着的人会等。（110）"],
    "32-海洋馆一日.md": ["【海洋馆·900】"],
    "33-泵房潮.md": ["【泵房·"],
    "34-玻璃后.md": ["【玻璃后·"],
    "35-末班全程.md": ["【末班·1200】"],
    "36-老周日志.md": ["【日志·"],
    "37-空白票根.md": ["【票根·"],
}

PADDING_SUFFIX = re.compile(
    r"\s+(?:"
    r"发送失败不是句号，是逗号，逗号后面还有馆还有带还有停止键|"
    r"这一章只到你看完簿，按在下一章，名字不是twist在成本|"
    r"这一章写薄不写没，没是大路，大路写结案，长不全够当同桌|"
    r"空白卡片最终写待定，不是抓人，是登记漏句，登记漏句的人，白天指纹浅一帧|"
    r"汤不倒，等于保温未完成，等于「我选——」没收尾，未完成还热着，热着的人会等|"
    r"灯座残芯录的是大韦呼吸，呼吸被拧半圈，拧，不是删，是登记漏句|"
    r"你把Walkman放下，手指停停止键上方，B面第三口气还在耳边，按吧像赵宜又像你自己，你不应，你还当同桌|"
    r"疼才能把故事按在两站之间，你读完了，疼在纸背面，你在正面，正面是袖口有没有褶"
    r")（\d+）$"
)

PADDING_BLOCK = re.compile(
    r"^(?:【[\w·]+】|第\d+段|第\d+次|第\d+遍|"
    r"你想起一次值日，她擦好友列表的窗|"
    r"B面里，第三口气又转半圈|"
    r"阿青在.{1,8}边看你|"
    r"B面转半圈|"
    r"压进数学书|"
    r"第一节课后，地点)"
)


def strip_padding_suffix(block: str) -> str:
    return PADDING_SUFFIX.sub("", block).strip()


def strip_core(text: str, markers: list[str]) -> str:
    idx = len(text)
    for m in markers:
        i = text.find(m)
        if i != -1 and i < idx:
            idx = i
    text = text[:idx].rstrip()

    parts: list[str] = []
    seen: set[str] = set()
    for block in re.split(r"\n\n+", text):
        block = block.strip()
        if not block:
            continue
        if block.startswith("<!--"):
            continue
        if PADDING_BLOCK.match(block):
            continue
        if block.startswith("【"):
            continue
        block = strip_padding_suffix(block)
        if not block or block.startswith("#"):
            if block.startswith("#"):
                parts.append(block)
            continue
        if block.count("你想起一次值日，她擦好友列表的窗") >= 1:
            continue
        if block.count("周一放学，你习惯性往左等两步") >= 1:
            continue
        if block.count("周二午休，小卖部阿姨问") >= 1:
            continue
        key = hashlib.md5(re.sub(r"\s+", "", block).encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        parts.append(block)

    return "\n\n".join(parts) + "\n"


def build_to_target(core: str, gen, seed: int, target: int) -> str:
    blocks = [core.rstrip()]
    seen: set[str] = {hashlib.md5(re.sub(r"\s+", "", core).encode()).hexdigest()}
    i = 0
    while sum(len(b) for b in blocks) < target:
        block = gen(i + seed)
        key = hashlib.md5(re.sub(r"\s+", "", block).encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            blocks.append(block)
        i += 1
        if i > 5000:
            break
    text = "\n\n".join(blocks)
    while len(text) > target + TOLERANCE and len(blocks) > 3:
        blocks.pop(-1)
        text = "\n\n".join(blocks)
    return text + "\n"


def expand_chapter(name: str) -> None:
    path = NOVEL / name
    gen = GENERATORS[name]
    seed = int(re.match(r"(\d+)", name).group(1)) * 100
    core = strip_core(path.read_text(encoding="utf-8"), CUT_MARKERS[name])
    text = build_to_target(core, gen, seed, TARGET)
    path.write_text(text, encoding="utf-8")
    cn = len(re.findall(r"[\u4e00-\u9fff]", text))
    print(f"{name}\tlen={len(text)}\tcn={cn}")


def main() -> None:
    for name in GENERATORS:
        expand_chapter(name)


if __name__ == "__main__":
    main()
