"""把段落编进节点图。"""

from __future__ import annotations

from game.nodes import ChoiceNode, EndingNode, Node, TextNode


def chain(
    prefix: str,
    pages: list[tuple[str, str, str, str]],
    final: str,
) -> dict[str, Node]:
    """pages: (scene, portrait, text, place)."""
    out: dict[str, Node] = {}
    for i, (scene, portrait, text, place) in enumerate(pages):
        name = f"{prefix}{i + 1:02d}"
        nxt = f"{prefix}{i + 2:02d}" if i + 1 < len(pages) else final
        out[name] = TextNode(scene, portrait, text, nxt, place)
    return out


def choice(
    name: str,
    scene: str,
    portrait: str,
    prompt: str,
    options: tuple[tuple[str, str], ...],
    place: str = "",
) -> dict[str, Node]:
    return {name: ChoiceNode(scene, portrait, prompt, options, place)}


def ending(
    name: str,
    scene: str,
    portrait: str,
    title: str,
    text: str,
    place: str = "",
) -> dict[str, Node]:
    return {name: EndingNode(scene, portrait, title, text, place)}
