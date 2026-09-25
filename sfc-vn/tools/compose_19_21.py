#!/usr/bin/env python3
"""Compose vol4 chapters 19-21 from hand-written scene modules (~30k each)."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
TOOLS = Path(__file__).resolve().parent
GEN = TOOLS / "_gen" / "hand_vol4"
TARGET = 30000
TOL = 900


def md5(s: str) -> str:
    return hashlib.md5(re.sub(r"\s+", "", s).encode()).hexdigest()


def load_scenes(name: str) -> list[str]:
    path = GEN / f"scenes_{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod.SCENES)


def load_bank(name: str) -> list[str]:
    banks = []
    for fname in (f"bank_{name}.py", f"bank2_{name}.py", f"extra_{name}.py"):
        path = GEN / fname
        if not path.exists():
            continue
        spec = importlib.util.spec_from_file_location(fname, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for attr in dir(mod):
            if attr.startswith(("BANK", "EXTRA")):
                val = getattr(mod, attr)
                if isinstance(val, list):
                    banks.extend(val)
    seen: set[str] = set()
    out: list[str] = []
    for p in banks:
        k = md5(p[:120])
        if k not in seen:
            seen.add(k)
            out.append(p)
    return out


def assemble(title: str, open_p: str, scenes: list[str], close_p: str, bank: list[str]) -> str:
    seen = {md5(open_p), md5(close_p)}
    body_parts = [open_p]
    for s in scenes:
        if md5(s) not in seen:
            seen.add(md5(s))
            body_parts.append(s)
    body = "\n\n".join(body_parts)
    marker = "够了。"
    # append unique bank paragraphs until target
    for p in bank:
        if len(body) + len(close_p) >= TARGET - TOL:
            break
        if md5(p) in seen:
            continue
        seen.add(md5(p))
        if marker in body:
            idx = body.rfind(marker)
            body = body[:idx].rstrip() + "\n\n" + p + "\n\n" + body[idx:]
        else:
            body = body.rstrip() + "\n\n" + p
    if not body.rstrip().endswith(marker):
        body = body.rstrip() + "\n\n" + close_p
    elif close_p not in body:
        body = body.rstrip() + "\n\n" + close_p
    return f"# {title}\n\n{body}\n"


OPEN = {
    "19": "若你把磁带交给阿青，故事会停在未完成里，不是停在你按停止的那条缝，是停在馆柜台最底层，两盘带并排，一盘写着赵宜，一盘空白，像等你填名，锁舌吞进喇叭，喇叭用你的声音说已收藏，这一次你不反感，反感需要你还想改主意。",
    "20": "若你听完整盘，赵宜会在第四层等你，你按下播放并且没有再停，她的声音一层一层叠上来，先是课堂再是天桥再是她对妈妈说我会回来，说到厨房的汤她吸吸鼻子，告诉她我没倒掉，她的等待，等待也是汤，会凉但还能热，她轻轻喊你的小名，磁带走完，卡座吐带像吐出一根骨头，你看自己的手指纹浅了，阿青闭着眼说第四层开了。",
    "21": "若你随小海去海洋馆，转动蓝色阀门，赵宜会跟着水走，泵房很潮，铁和橘子混在一起，观察窗里她站在河底的教室，课桌是锈，黑板是青苔，她按糖纸在玻璃上亮一下像信号，你转蓝阀像潮水倒抽，水位一寸寸降，她降，先是腰再是膝最后踮脚，她朝你挥手，动作被水流拉长变成一条发光的带子，带子上半句口型回家，回家两个字被水扯成一条河。",
}

CLOSE = {
    "19": "馆拆那天，阿青把编目簿最后一页撕下给你，页上只有一行，大韦（待定），赵宜（保管），她把页折成方片，塞你手心，说名写早了，别填，填了你就进喇叭，她在里面，你在标签上，并排就破了，你收方片，像收证据，证据在，人就还在某个未完成的格里，夜里路过停业商场旧址，卷帘门后空，四楼黑，黑里耳机灯闪一下，闪完没了，没了像夹层平安，也像馆搬走，搬走不是消失，是冷藏，冷藏里句子还热，热着的人会等，你站三秒，三秒像确认，确认还在，还在就够，并列，正本按停止，这里交带，不判对错，你路过也是守，够了。",
    "20": "你走出夹层，铁门把雨重新放进来，阿青没留你，她说路过四楼别抬头，抬头喇叭就会用你越来越浅的声音说欢迎光临，天台上有人把伞倒插在水里，透明柄上没有橘点，你没捡，城市的声音重新对齐口型，你数到十六辆车就停，第十七辆空着，班级合影里你的位置空着，像有人礼貌地让座，有时在很老的歌中间你会听见她喊你的小名，你把剩的糖含化，甜沉到舌根，浅了仍要活，活就算静音的一种答案，并列，正本按停止，这里你听了完整，够了。",
    "21": "你把糖纸叠成小船放进护城河，船走得很稳，稳像沉，沉不是坏事，后来你仍走小的路，仍不在二十三点以后数任何东西，仍会绕开密封的水，下雨时你去看护城河，水面普通偶尔有鱼纹，有一夜你站桥边22:59，水里闪一下橙色像校服又像糖纸，你眨眼没了，你当风，风也算，你保留习惯买两杯豆浆，一杯自己喝，一杯倒在桥栏外，不洒，慢慢倒像敬，敬岸敬水敬那个选随河的解，方程还是两个解，你选了排空的那一个，并列，正本按停止，这里你转蓝阀，她随河，够了。",
}

TITLES = {"19": "第十九章　馆藏", "20": "第二十章　静音", "21": "第二十一章　随河"}


def main() -> None:
    for num in ("19", "20", "21"):
        scenes = load_scenes(num)
        bank = load_bank(f"ch{num}")
        text = assemble(TITLES[num], OPEN[num], scenes, CLOSE[num], bank)
        fname = f"{num}-{'馆藏' if num=='19' else '静音' if num=='20' else '随河'}.md"
        (ROOT / fname).write_text(text, encoding="utf-8")
        print(f"{fname}\t{len(text)}\tscenes={len(scenes)}\tbank={len(bank)}")

    subprocess.run(["python3", str(TOOLS / "strip_vol4_templates.py")], check=True)
    subprocess.run(["python3", str(TOOLS / "clean_novel_ai.py")], check=True)
    subprocess.run(["python3", str(TOOLS / "count_novel.py")], check=True)


if __name__ == "__main__":
    main()
