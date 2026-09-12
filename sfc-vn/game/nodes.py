"""剧本节点。对白按段落存储，显示时再折行分页。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextNode:
    scene: str
    portrait: str
    text: str
    next: str
    place: str = ""


@dataclass(frozen=True)
class ChoiceNode:
    scene: str
    portrait: str
    prompt: str
    options: tuple[tuple[str, str], ...]
    place: str = ""


@dataclass(frozen=True)
class EndingNode:
    scene: str
    portrait: str
    title: str
    text: str
    place: str = ""


Node = TextNode | ChoiceNode | EndingNode


def paginate(text: str, width: int, rows: int) -> list[list[str]]:
    """按全角宽度折行，再切成多页。"""
    lines: list[str] = []
    for para in text.replace("\r", "").split("\n"):
        if para == "":
            lines.append("")
            continue
        buf = ""
        for ch in para:
            if len(buf) >= width:
                lines.append(buf)
                buf = ch
            else:
                buf += ch
        if buf:
            lines.append(buf)
    pages: list[list[str]] = []
    chunk: list[str] = []
    for line in lines:
        chunk.append(line)
        if len(chunk) >= rows:
            pages.append(chunk)
            chunk = []
    if chunk:
        pages.append(chunk)
    return pages or [[]]


def estimate_minutes(nodes: dict[str, Node], chars_per_min: int = 260) -> float:
    total = 0
    for node in nodes.values():
        if isinstance(node, ChoiceNode):
            total += len(node.prompt) + sum(len(t) for t, _ in node.options)
        elif isinstance(node, EndingNode):
            total += len(node.title) + len(node.text)
        else:
            total += len(node.text)
    return total / chars_per_min
