"""《十一点的城市》剧本入口。"""

from __future__ import annotations

from game.nodes import ChoiceNode, EndingNode, Node, TextNode, estimate_minutes, paginate
from game.route_aqua import AQUA
from game.route_opening import OPEN
from game.route_rail import RAIL
from game.route_tape import TAPE

TITLE = "十一点的城市"
SUBTITLE = "三条不该存在的路"
TITLE_HINT = "按开始　或读取"
START_NODE = "o01"

STORY: dict[str, Node] = {}
STORY.update(OPEN)
STORY.update(TAPE)
STORY.update(AQUA)
STORY.update(RAIL)

PORTRAITS = {
    "": "无",
    "linxia": "赵宜",
    "qing": "阿青",
    "zhou": "老周",
    "hai": "小海",
    "clerk": "店员",
}

SCENE_TITLES = {
    "title": "十一点的城市",
    "apartment": "南横街老楼",
    "elevator": "电梯",
    "street_rain": "雨街",
    "store": "便利店",
    "overpass": "天桥",
    "mall": "西单商场",
    "tape_shop": "倒带馆",
    "tape_back": "后仓",
    "aquarium": "海洋馆",
    "tank": "水箱",
    "pump": "泵房",
    "bus": "夜班车",
    "subway": "地铁",
    "platform": "站台",
    "rooftop": "屋顶",
    "hutong": "胡同",
    "avenue": "珠市口",
    "xidan_road": "去西单",
    "aqua_road": "去海洋馆",
    "dawn_apt": "黎明老楼",
    "mall_mid": "商场夹层",
    "aqua_tunnel": "海底隧道",
    "riverbank": "河岸",
    "nameless_lane": "无名巷",
    "metro_gate": "无名地铁口",
    "gap_tunnel": "两站之间",
    "pale_dawn": "无太阳的早晨",
    "morning_st": "清晨大街",
    "home_rain": "回家的雨",
    "duty_room": "值班室",
    "wave_plat": "挥手的站",
}


def collect_charset() -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    extras = TITLE + SUBTITLE + TITLE_HINT + "存档读档继续空槽确认返回上下开始"
    blobs = [extras]
    for node in STORY.values():
        if isinstance(node, TextNode):
            blobs.append(node.text)
            blobs.append(node.place)
        elif isinstance(node, ChoiceNode):
            blobs.append(node.prompt)
            blobs.append(node.place)
            blobs.extend(t for t, _ in node.options)
        else:
            blobs.append(node.title)
            blobs.append(node.text)
            blobs.append(node.place)
    blobs.extend(PORTRAITS.values())
    blobs.extend(SCENE_TITLES.values())
    for blob in blobs:
        for ch in blob:
            if ch not in seen and ch not in "\n\r":
                seen.add(ch)
                ordered.append(ch)
    return ordered


def story_graph_errors() -> list[str]:
    errors: list[str] = []
    if START_NODE not in STORY:
        errors.append(f"missing start {START_NODE}")
    for name, node in STORY.items():
        if isinstance(node, TextNode) and node.next not in STORY:
            errors.append(f"{name} -> {node.next}")
        elif isinstance(node, ChoiceNode):
            if not (2 <= len(node.options) <= 3):
                errors.append(f"{name} options")
            for text, dest in node.options:
                if dest not in STORY:
                    errors.append(f"{name} -> {dest}")
                if len(text) > 14:
                    errors.append(f"{name} option long: {text}")
    endings = [n for n, v in STORY.items() if isinstance(v, EndingNode)]
    if len(endings) < 3:
        errors.append("need at least 3 endings")
    return errors


def story_to_plain() -> dict:
    """给网页玩家用的纯数据。"""
    nodes = {}
    for name, node in STORY.items():
        if isinstance(node, TextNode):
            nodes[name] = {
                "type": "text",
                "scene": node.scene,
                "portrait": node.portrait,
                "text": node.text,
                "next": node.next,
                "place": node.place,
            }
        elif isinstance(node, ChoiceNode):
            nodes[name] = {
                "type": "choice",
                "scene": node.scene,
                "portrait": node.portrait,
                "prompt": node.prompt,
                "options": [{"text": t, "next": d} for t, d in node.options],
                "place": node.place,
            }
        else:
            nodes[name] = {
                "type": "ending",
                "scene": node.scene,
                "portrait": node.portrait,
                "title": node.title,
                "text": node.text,
                "place": node.place,
            }
    return {
        "title": TITLE,
        "subtitle": SUBTITLE,
        "hint": TITLE_HINT,
        "start": START_NODE,
        "portraits": PORTRAITS,
        "scenes": SCENE_TITLES,
        "nodes": nodes,
        "minutes": round(estimate_minutes(STORY), 1),
    }


def screen_count(width: int = 16, rows: int = 4) -> int:
    n = 0
    for node in STORY.values():
        if isinstance(node, TextNode):
            n += len(paginate(node.text, width, rows))
        elif isinstance(node, EndingNode):
            n += 1 + len(paginate(node.text, width, rows))
        else:
            n += 1
    return n
