"""《月见桥》原创剧本：短篇文字冒险视觉小说。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextNode:
    scene: str
    lines: tuple[str, ...]
    next: str


@dataclass(frozen=True)
class ChoiceNode:
    scene: str
    prompt: str
    options: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class EndingNode:
    scene: str
    title: str
    lines: tuple[str, ...]


Node = TextNode | ChoiceNode | EndingNode


# 每页最多 4 行，每行最多 14 个全角字。用字尽量复用，好塞进 SFC 字库。
STORY: dict[str, Node] = {
    "open1": TextNode(
        "post",
        (
            "中秋前夜。",
            "海边小镇的邮局里，",
            "只剩一盏灯还亮着。",
        ),
        "open2",
    ),
    "open2": TextNode(
        "post",
        (
            "你替妈妈看店。",
            "窗外有潮声，",
            "像有人在说话。",
        ),
        "open3",
    ),
    "open3": TextNode(
        "post",
        (
            "柜台里掉出一封信。",
            "没有名字，",
            "折成小小的纸船。",
        ),
        "choice_letter",
    ),
    "choice_letter": ChoiceNode(
        "post",
        "这封没有名字的信——",
        (
            ("自己轻轻拆开", "open_a1"),
            ("先去问妈妈", "open_b1"),
            ("送到月见桥", "open_c1"),
        ),
    ),
    "open_a1": TextNode(
        "post",
        (
            "信纸旧了。",
            "上面只写一句：",
            "「若你想家，就看月。」",
        ),
        "open_a2",
    ),
    "open_a2": TextNode(
        "street",
        (
            "你把纸船重新折好。",
            "心里像有一盏",
            "还没点着的灯。",
        ),
        "mid1",
    ),
    "open_b1": TextNode(
        "home",
        (
            "妈妈在煮甜汤。",
            "她看见纸船，说：",
            "「这种信，桥上才收。」",
        ),
        "open_b2",
    ),
    "open_b2": TextNode(
        "home",
        (
            "她塞给你两块糖：",
            "「去吧。」",
            "月亮升起来了。",
        ),
        "mid1",
    ),
    "open_c1": TextNode(
        "street",
        (
            "石板路上有露水。",
            "远处桥灯一盏一盏",
            "亮起来。",
        ),
        "open_c2",
    ),
    "open_c2": TextNode(
        "bridge",
        (
            "月见桥横在河口。",
            "栏杆上系着红绳，",
            "风一过就轻轻响。",
        ),
        "mid1",
    ),
    "mid1": TextNode(
        "bridge",
        (
            "桥上站着一个旅人。",
            "纸灯照着她。",
            "她说自己叫阿岚。",
        ),
        "mid2",
    ),
    "mid2": TextNode(
        "bridge",
        (
            "「末班船要开了。」",
            "阿岚指指空灯：",
            "「我来取一封话说。」",
        ),
        "mid3",
    ),
    "mid3": TextNode(
        "bridge",
        (
            "桥下有猫叫。",
            "白猫小白跳上栏杆，",
            "眼睛圆圆的。",
        ),
        "choice_night",
    ),
    "choice_night": ChoiceNode(
        "bridge",
        "夜风把纸船吹动。",
        (
            ("把信交给阿岚", "path_travel1"),
            ("跟着小白走", "path_cat1"),
            ("自己投下河", "path_keep1"),
        ),
    ),
    "path_travel1": TextNode(
        "lantern",
        (
            "阿岚接过纸船。",
            "灯里忽然有了光，",
            "像有人轻轻点头。",
        ),
        "path_travel2",
    ),
    "path_travel2": TextNode(
        "lantern",
        (
            "「过海的人怕忘家。」",
            "她说。",
            "雾把声音接走了。",
        ),
        "choice_farewell",
    ),
    "choice_farewell": ChoiceNode(
        "lantern",
        "船要开了。",
        (
            ("送她到船边", "end_far"),
            ("请她再留一夜", "path_stay1"),
        ),
    ),
    "path_stay1": TextNode(
        "home",
        (
            "阿岚笑了，留下。",
            "你们把灯挂在门上。",
            "甜汤的香味出来。",
        ),
        "end_home",
    ),
    "path_cat1": TextNode(
        "street",
        (
            "小白跳下桥，",
            "钻进小巷。",
            "你跟着水花走。",
        ),
        "path_cat2",
    ),
    "path_cat2": TextNode(
        "home",
        (
            "妈妈坐在门前。",
            "小白跳进她怀里。",
            "她摸着旧信的折。",
        ),
        "path_cat3",
    ),
    "path_cat3": TextNode(
        "home",
        (
            "「你爸爸出海那年，",
            "也折过这样的船。」",
            "锅盖响了一下。",
        ),
        "end_home",
    ),
    "path_keep1": TextNode(
        "bridge",
        (
            "纸船落到水上。",
            "它没有沉，",
            "朝着月亮慢慢漂。",
        ),
        "path_keep2",
    ),
    "path_keep2": TextNode(
        "bridge",
        (
            "阿岚没有伸手。",
            "小白挨着你坐下。",
            "谁也不急着走。",
        ),
        "end_wait",
    ),
    "end_home": EndingNode(
        "home",
        "结局　灯火团圆",
        (
            "信在灯下慢慢开。",
            "想家的话一直在等",
            "回家的人。汤是甜的。",
        ),
    ),
    "end_far": EndingNode(
        "lantern",
        "结局　信去远方",
        (
            "船灯没进雾里。",
            "阿岚举起纸灯，",
            "像把一颗星带走。",
        ),
    ),
    "end_wait": EndingNode(
        "bridge",
        "结局　桥上守候",
        (
            "你把红绳又系紧。",
            "小白靠着你。",
            "月亮不走，信也不急。",
        ),
    ),
}

START_NODE = "open1"
TITLE_HINT = "按开始键"
ADVANCE_HINT = "按确定"
CHOICE_HINT = "上下选　确定"
MAX_GLYPHS = 250


def all_text_fragments() -> list[str]:
    chunks = [TITLE_HINT, ADVANCE_HINT, CHOICE_HINT, "　"]
    for node in STORY.values():
        if isinstance(node, TextNode):
            chunks.extend(node.lines)
        elif isinstance(node, ChoiceNode):
            chunks.append(node.prompt)
            chunks.extend(text for text, _ in node.options)
        else:
            chunks.append(node.title)
            chunks.extend(node.lines)
    return chunks


def collect_charset() -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    extra = "月见桥一封没有名字的信"
    for chunk in [*all_text_fragments(), extra]:
        for ch in chunk:
            if ch == "\n":
                continue
            if ch not in seen:
                seen.add(ch)
                ordered.append(ch)
    return ordered


def story_graph_errors() -> list[str]:
    errors: list[str] = []
    if START_NODE not in STORY:
        errors.append(f"missing start node {START_NODE}")
    charset = collect_charset()
    if len(charset) > MAX_GLYPHS:
        errors.append(f"too many glyphs: {len(charset)} > {MAX_GLYPHS}")
    for name, node in STORY.items():
        if isinstance(node, TextNode):
            if node.next not in STORY:
                errors.append(f"{name} -> missing {node.next}")
            if len(node.lines) > 4:
                errors.append(f"{name} has more than 4 lines")
            for line in node.lines:
                if len(line) > 14:
                    errors.append(f"{name} line too long: {line}")
        elif isinstance(node, ChoiceNode):
            if not (2 <= len(node.options) <= 3):
                errors.append(f"{name} needs 2-3 options")
            if len(node.prompt) > 14:
                errors.append(f"{name} prompt too long")
            for text, dest in node.options:
                if dest not in STORY:
                    errors.append(f"{name} option -> missing {dest}")
                if len(text) > 12:
                    errors.append(f"{name} option too long: {text}")
        else:
            if len(node.title) > 14:
                errors.append(f"{name} title too long")
            if len(node.lines) > 4:
                errors.append(f"{name} ending has more than 4 lines")
            for line in node.lines:
                if len(line) > 14:
                    errors.append(f"{name} ending line too long: {line}")
    return errors
