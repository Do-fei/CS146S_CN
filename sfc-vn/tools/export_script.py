#!/usr/bin/env python3
"""把游戏节点图导出为可读的完整剧本文档。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.nodes import ChoiceNode, EndingNode, TextNode
from game.story import PORTRAITS, START_NODE, STORY, TITLE, estimate_minutes
from tools.deslop_export import deslop_export

OUT = ROOT / "docs" / "完整剧本.md"


def speaker(portrait: str) -> str:
    name = PORTRAITS.get(portrait, "")
    return name if name and name != "无" else "旁白"


def walk_linear(start: str) -> tuple[list, str | None]:
    """沿唯一后继走到选择或结局。返回（文本节点列表，终点节点名）。"""
    pages: list = []
    name = start
    seen: set[str] = set()
    while name and name not in seen:
        seen.add(name)
        node = STORY[name]
        if isinstance(node, TextNode):
            pages.append((name, node))
            name = node.next
            continue
        return pages, name
    return pages, name


def emit_pages(lines: list[str], pages: list) -> None:
    last_place = None
    for _name, node in pages:
        if node.place and node.place != last_place:
            lines.append(f"**〔{node.place}〕**")
            lines.append("")
            last_place = node.place
        who = speaker(node.portrait)
        lines.append(f"**{who}**")
        lines.append("")
        for para in node.text.split("\n"):
            lines.append(para)
        lines.append("")


def emit_choice(lines: list[str], name: str) -> ChoiceNode:
    node = STORY[name]
    assert isinstance(node, ChoiceNode)
    if node.place:
        lines.append(f"**〔{node.place}〕**")
        lines.append("")
    who = speaker(node.portrait)
    if who != "旁白":
        lines.append(f"**{who}**")
        lines.append("")
    lines.append(f"> **选择**　{node.prompt}")
    lines.append(">")
    for i, (text, dest) in enumerate(node.options, 1):
        lines.append(f"> {i}. {text}")
    lines.append("")
    return node


def emit_ending(lines: list[str], name: str) -> None:
    node = STORY[name]
    assert isinstance(node, EndingNode)
    lines.append(f"### {node.title}")
    lines.append("")
    if node.place:
        lines.append(f"**〔{node.place}〕**")
        lines.append("")
    who = speaker(node.portrait)
    lines.append(f"**{who}**")
    lines.append("")
    lines.append(node.text)
    lines.append("")


def emit_branch(lines: list[str], start: str, heading: str) -> None:
    lines.append(f"### {heading}")
    lines.append("")
    pages, end = walk_linear(start)
    emit_pages(lines, pages)
    if end and isinstance(STORY[end], EndingNode):
        emit_ending(lines, end)


def build() -> str:
    minutes = estimate_minutes(STORY)
    lines: list[str] = [
        f"# 《{TITLE}》完整剧本",
        "",
        "按游戏节点顺序收录对白、旁白、分支选择和九个结局。",
        f"全文大约 {minutes:.0f} 分钟阅读量（按每分钟 260 字）。一条线从开场走到一个结局，就是完整的一次。",
        "",
        "阅读稿改过个别对比句和破折号，剧情、选择、结局不变。游戏程序仍读 `game/route_*.py`。",
        "",
        "重生成：`python3 tools/export_script.py`",
        "",
        "## 目录",
        "",
        "- [人物](#人物)",
        "- [路线图](#路线图)",
        "- [第一幕　开场](#第一幕开场)",
        "- [选择　三条路](#选择三条路)",
        "- [第二幕甲　西单倒带馆](#第二幕甲西单倒带馆)",
        "- [第二幕乙　北京海洋馆](#第二幕乙北京海洋馆)",
        "- [第二幕丙　无名地铁](#第二幕丙无名地铁)",
        "- [九个结局速查](#九个结局速查)",
        "",
        "## 人物",
        "",
        "| 称呼 | 身份 |",
        "| --- | --- |",
        "| 你 | 赵宜的同桌。海报与工作室署名里叫大韦。游戏正文以第二人称「你」推进。 |",
        "| 赵宜 | 失踪第三天的女孩。奶奶灰齐刘海短发，口袋里有橘子糖。 |",
        "| 阿青 | 西单倒带馆。管声音。 |",
        "| 老周 | 夜班出租。管路。 |",
        "| 小海 | 北京海洋馆夜班。管水。 |",
        "| 店员 | 二十四小时便利店。没有名字。 |",
        "| 妈妈 | 赵宜的母亲。 |",
        "| 班主任 | 白天的教室。 |",
        "| 警察 | 南城派出所夜班。 |",
        "| 馆长 | 北京海洋馆。 |",
        "",
        "## 路线图",
        "",
        "```",
        "开场（南横街 → 学校 → 赵宜家 → 派出所 → 便利店 → 天桥）",
        "        │",
        "        ├─ 跟阿青去倒带馆",
        "        │       ├─ 听完整盘　　→ 结局　静音",
        "        │       ├─ 把磁带交给阿青 → 结局　馆藏",
        "        │       └─ 按下停止　　→ 结局　漏句",
        "        │",
        "        ├─ 随小海去海洋馆",
        "        │       ├─ 蓝色阀门：排空 → 结局　随河",
        "        │       ├─ 红色阀门：对调 → 结局　对调",
        "        │       └─ 白色阀门：锁死 → 结局　锁死",
        "        │",
        "        └─ 上老周的夜班车",
        "                ├─ 坐到终点　　　→ 结局　无站名的早晨",
        "                ├─ 在下一站下车　→ 结局　空白站",
        "                └─ 拉下紧急制动　→ 结局　两站之间",
        "```",
        "",
        "三条线互不交叉。选完只能走到该线的三个结局之一。另外两条路还在窗外或水箱里，不汇合。",
        "",
        "---",
        "",
        "## 第一幕　开场",
        "",
    ]

    open_pages, route_choice = walk_linear(START_NODE)
    emit_pages(lines, open_pages)

    lines.append("## 选择　三条路")
    lines.append("")
    route = emit_choice(lines, route_choice or "choice_route")

    tape_start, rail_start, aqua_start = None, None, None
    for text, dest in route.options:
        if dest.startswith("t"):
            tape_start = dest
        elif dest.startswith("r"):
            rail_start = dest
        elif dest.startswith("a"):
            aqua_start = dest

    lines.append("---")
    lines.append("")
    lines.append("## 第二幕甲　西单倒带馆")
    lines.append("")
    tape_pages, tape_choice = walk_linear(tape_start or "t01")
    emit_pages(lines, tape_pages)
    tape = emit_choice(lines, tape_choice or "choice_tape")

    tape_heads = {
        "tl": "甲－1　听完整盘",
        "tg": "甲－2　把磁带交给阿青",
        "ts": "甲－3　按下停止",
    }
    for text, dest in tape.options:
        key = "".join(ch for ch in dest if ch.isalpha())[:2]
        emit_branch(lines, dest, tape_heads.get(key, text))

    lines.append("---")
    lines.append("")
    lines.append("## 第二幕乙　北京海洋馆")
    lines.append("")
    aqua_pages, aqua_choice = walk_linear(aqua_start or "a01")
    emit_pages(lines, aqua_pages)
    aqua = emit_choice(lines, aqua_choice or "choice_aqua")

    aqua_heads = {
        "ad": "乙－1　转动蓝色：排空",
        "ax": "乙－2　转动红色：对调",
        "ak": "乙－3　按下白色：锁死",
    }
    for text, dest in aqua.options:
        key = "".join(ch for ch in dest if ch.isalpha())[:2]
        emit_branch(lines, dest, aqua_heads.get(key, text))

    lines.append("---")
    lines.append("")
    lines.append("## 第二幕丙　无名地铁")
    lines.append("")
    rail_pages, rail_choice = walk_linear(rail_start or "r01")
    emit_pages(lines, rail_pages)
    rail = emit_choice(lines, rail_choice or "choice_rail")

    rail_heads = {
        "re": "丙－1　坐到终点",
        "rd": "丙－2　在下一站下车",
        "rb": "丙－3　拉下紧急制动",
    }
    for text, dest in rail.options:
        key = "".join(ch for ch in dest if ch.isalpha())[:2]
        emit_branch(lines, dest, rail_heads.get(key, text))

    lines += [
        "---",
        "",
        "## 九个结局速查",
        "",
        "| 线 | 选择 | 结局名 | 一句话 |",
        "| --- | --- | --- | --- |",
        "| 倒带馆 | 听完整盘 | 静音 | 她被听完整。你在合影里让座。 |",
        "| 倒带馆 | 交给阿青 | 馆藏 | 未完成被保管，谁也不往前走。 |",
        "| 倒带馆 | 按下停止 | 漏句 | 她从停止键的缝里回来。 |",
        "| 海洋馆 | 蓝色排空 | 随河 | 水位退回规矩，她去了护城河。 |",
        "| 海洋馆 | 红色对调 | 对调 | 她上岸，你留在夜场。 |",
        "| 海洋馆 | 白色锁死 | 锁死 | 两岸维持原样。 |",
        "| 无名地铁 | 坐到终点 | 无站名的早晨 | 她留在路线里，你用硬币换回白天。 |",
        "| 无名地铁 | 下一站下车 | 空白站 | 白天还给你，她继续坐。 |",
        "| 无名地铁 | 紧急制动 | 两站之间 | 故事停在隧道中段。 |",
        "",
        "三条线、九个收场并列。没有隐藏结局。",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    text = deslop_export(build())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT} ({len(text)} chars, {text.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
