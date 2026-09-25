#!/usr/bin/env python3
"""Remove numbered-loop padding and cross-chapter leakage."""

import re
from pathlib import Path

NOVEL = Path(__file__).resolve().parents[1] / "docs" / "novel"

RULES = {
    "04-胡同.md": {
        "drop_if": re.compile(
            r"便利店里你第|赵宜家第\d+次|第\d+次发送失败|"
            r"22:59|二十二点五十九|监控雪花|店员指门：天桥|"
            r"门槛外多一双湿鞋|镜子里你晚|声控灯懒|抽屉多便条：别数错|"
            r"胡同深就走到头|橙光更清楚，像便利店"
        ),
        "end_markers": [
            "你进胡同了。身后，南横街全黑",
            "你进胡同了。灯开始一盏盏灭",
            "第四章，止于这里",
            "你站住。站住，像还某种同桌的约",
        ],
    },
    "05-第三夜.md": {
        "drop_if": re.compile(
            r"便利店里你第|赵宜家第\d+次|第\d+次发送失败|"
            r"22:59|监控雪花|店员|冰柜|饭团|便当袋发热"
        ),
    },
    "06-胡同深.md": {
        "drop_if": re.compile(
            r"便利店里你第|赵宜家第\d+次|第\d+次发送失败|"
            r"22:59|监控雪花|店员指门|冰柜|饭团"
        ),
    },
    "07-便利店.md": {
        "drop_if": re.compile(r"赵宜家第\d+次|第\d+次发送失败|第15次"),
    },
    "01-发送失败.md": {
        "drop_if": re.compile(r"第\d+次发送失败|便利店里你第|赵宜家第\d+次|胡同第\d+盏"),
    },
    "02-空位.md": {
        "drop_if": re.compile(r"第\d+次发送失败|便利店里你第|赵宜家第\d+次|胡同第\d+盏"),
    },
    "03-赵宜家.md": {
        "drop_if": re.compile(r"第\d+次发送失败|便利店里你第|赵宜家第\d+次|胡同第\d+盏"),
    },
}


def strip_file(name: str) -> None:
    path = NOVEL / name
    text = path.read_text(encoding="utf-8")
    title = ""
    paras = []
    seen = set()
    rules = RULES.get(name, {})
    drop = rules.get("drop_if")
    for p in re.split(r"\n\s*\n", text):
        p = p.strip()
        if not p:
            continue
        if p.startswith("#"):
            title = p
            continue
        if drop and drop.search(p):
            continue
        if re.match(r"第\d+次", p):
            continue
        key = re.sub(r"\s+", "", p)
        if key in seen:
            continue
        seen.add(key)
        paras.append(p)

    # Trim 04 at hutong entry
    if name == "04-胡同.md":
        cut = None
        for i, p in enumerate(paras):
            if "你进胡同了" in p and "身后" in p:
                cut = i + 1
                break
        if cut:
            paras = paras[:cut]

    body = (title + "\n\n" if title else "") + "\n\n".join(paras)
    path.write_text(body.strip() + "\n", encoding="utf-8")
    print(f"{name}\t{len(body.strip())}")


def main():
    for f in RULES:
        strip_file(f)


if __name__ == "__main__":
    main()
