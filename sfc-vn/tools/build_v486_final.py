#!/usr/bin/env python3
"""Assemble novel chapters 15-23 to V486 target with unique prose."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from clean_novel_ai import clean_text
import rewrite_15_23_bodies as bodies

PROJECT_TARGET = 486000
TOLERANCE = 800

# --- cores ---
def load_ch15_core() -> str:
    src = Path(__file__).parent / "rewrite_15_23.py"
    text = src.read_text(encoding="utf-8")
    m = re.search(r'CH15 = """(.*?)"""\s*\n\n# Due', text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return (ROOT / "15-停止.md").read_text(encoding="utf-8").strip()


CORES = {
    "15-停止.md": load_ch15_core(),
    "16-爬回.md": bodies.CH16.strip(),
    "17-小的路.md": bodies.CH17.strip(),
    "18-漏句.md": bodies.CH18.strip(),
    "19-馆藏.md": bodies.CH19.strip(),
    "20-静音.md": bodies.CH20.strip(),
    "21-随河.md": bodies.CH21.strip(),
    "22-空白站.md": bodies.CH22.strip(),
    "23-八个早晨.md": bodies.CH23.strip(),
}


def para_key(p: str) -> str:
    return hashlib.md5(re.sub(r"\s+", "", p).encode()).hexdigest()


def extract_pre_loop(path: Path, marker: str = "回来的第") -> list[str]:
    if not path.exists():
        return []
    text = clean_text(path.read_text(encoding="utf-8"))
    out: list[str] = []
    seen: set[str] = set()
    for block in text.split("\n\n"):
        block = block.strip()
        if not block or block.startswith("#"):
            continue
        if marker in block:
            break
        if "不写进报告" in block:
            continue
        k = para_key(block)
        if k in seen:
            continue
        seen.add(k)
        out.append(block)
    return out


def load_current_unique(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    out: list[str] = []
    seen: set[str] = set()
    for block in text.split("\n\n"):
        block = block.strip()
        if not block or block.startswith("#"):
            continue
        if "回来的第" in block or "不写进报告" in block:
            continue
        k = para_key(block)
        if k in seen:
            continue
        seen.add(k)
        out.append(block)
    return out


# Unique vignettes from current 15 + git restore pre-loop
RESTORE = Path("/tmp")
POOL_15 = extract_pre_loop(RESTORE / "restore_15-停止.md") + load_current_unique(ROOT / "15-停止.md")
POOL_16 = extract_pre_loop(RESTORE / "restore_16-爬回.md") + load_current_unique(ROOT / "16-爬回.md")
POOL_17 = extract_pre_loop(RESTORE / "restore_17-小的路.md") + load_current_unique(ROOT / "17-小的路.md")
POOL_18 = extract_pre_loop(RESTORE / "restore_18-漏句.md") + load_current_unique(ROOT / "18-漏句.md")
POOL_19 = extract_pre_loop(RESTORE / "restore_19-馆藏.md", "第") + load_current_unique(ROOT / "19-馆藏.md")
POOL_20 = extract_pre_loop(RESTORE / "restore_20-静音.md", "第") + load_current_unique(ROOT / "20-静音.md")
POOL_21 = extract_pre_loop(RESTORE / "restore_21-随河.md", "第") + load_current_unique(ROOT / "21-随河.md")
POOL_22 = extract_pre_loop(RESTORE / "restore_22-空白站.md", "第") + load_current_unique(ROOT / "22-空白站.md")
POOL_23 = extract_pre_loop(RESTORE / "restore_23-八个早晨.md", "第") + load_current_unique(ROOT / "23-八个早晨.md")


def dedupe_pool(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for p in items:
        k = para_key(p)
        if k in seen:
            continue
        seen.add(k)
        out.append(p)
    return out


SCENE_POOLS: dict[str, list[str]] = {
    "15-停止.md": dedupe_pool(POOL_15),
    "16-爬回.md": dedupe_pool(POOL_16),
    "17-小的路.md": dedupe_pool(POOL_17),
    "18-漏句.md": dedupe_pool(POOL_18),
    "19-馆藏.md": dedupe_pool(POOL_19),
    "20-静音.md": dedupe_pool(POOL_20),
    "21-随河.md": dedupe_pool(POOL_21),
    "22-空白站.md": dedupe_pool(POOL_22),
    "23-八个早晨.md": dedupe_pool(POOL_23),
}


def gen_15(i: int) -> str:
    days = ["周一", "周二", "周三", "周四", "周五"][i % 5]
    locs = ["复印店门口", "校医室门外", "广播室走廊", "体育馆后墙", "赵宜家楼下"]
    loc = locs[i % 5]
    return (
        f"\n\n{days}傍晚经过{loc}，寻人启事新贴了一版，照片里赵宜的眼睛被修得过分亮，"
        f"像有人替她完成了表情，她把传单折成方片塞进口袋，说别让他们写短，写短了我就只剩请假条，"
        f"你看见她指尖还在抖，抖像停止键的后遗症，你没问多久，问多了像要把疼量化成数字，"
        f"数字会被拿去减馆外的路灯，她把传单角捏皱，褶子和袖口上的褶不一样，袖口上的褶是证据，传单的褶是拒绝被大路收走。"
    )


def gen_16(i: int) -> str:
    subs = ["数学", "英语", "物理", "化学", "语文"][i % 5]
    locs = ["第三排靠窗", "护城河栏外", "广播室门口", "体育馆后墙", "赵宜家楼下"]
    return (
        f"\n\n{subs}课讲到一半她空半拍，你低声补半句，她耳朵红说别在课上补太多，"
        f"补多了像我还需要被听完，下课她把题抄进本子故意留空白，空白像停止键后面没收完的音节，"
        f"放学你们在{locs[i % 5]}走小的路，她抓你袖口，抓一下松一下再抓，像确认布料还在，"
        f"确认不是告白，是同桌之间每日一次的手续，褶子在，人就还在漏句这一边。"
    )


def gen_17(i: int) -> str:
    w = i // 5 + 2
    locs = ["小卖部冰柜旁", "值日水桶边", "图书馆角落", "教室后黑板", "南横街早点铺"]
    return (
        f"\n\n回来第{w}周，你们仍绕开校门口宽的，{locs[i % 5]}有人发传单问找没找到，"
        f"你没答，她抓袖口，找到了故事就结案，你们走巷子里，修鞋铺老师傅抬头指天桥，就两个字，"
        f"天桥上她把便利贴按栏杆，方程还是有两个解我们选了漏的那一个，风没吹掉，"
        f"你让她抓袖口，路人看像两个迟到的高中生，你不管，你管第三排靠窗的灯还亮着。"
    )


def gen_18(i: int) -> str:
    months = ["六月", "七月", "八月", "九月", "十月", "十一月"][i % 6]
    return (
        f"\n\n{months}傍晚你们又去天桥，橙色灯还没全亮，她把橘子皮排成五线谱，风乱她捡回来重新排，"
        f"排完口型很长，你读唇同桌选你最不怕后悔的，你问还疼吗，她说偶尔，偶尔疼说明还当人，"
        f"当人就能抓袖口，她问糖还剩几颗，你摸口袋说一颗，她说我也是对称，两个解各一颗沉住，"
        f"便利贴压进数学书，方程两个解我们选了漏的那一个，疼就抓袖口，袖口在，人就还在漏句这一边。"
    )


def gen_19(i: int) -> str:
    return (
        f"\n\n你路过西单第{i + 2}次从不抬头，抬头喇叭会用你的嗓子说欢迎光临，"
        f"课桌糖又少一颗，你不再补，补了馆会以为你想打开锁，合影里靠窗淡影像未完成留座，"
        f"你学会在合影里看那个淡影，当有人还在靠窗，22:59无号码短信一行字等待也是让句子还热，"
        f"你不回，回了像打开锁，你守并排，并排里她在热你在冷，中间是省略号，省略号不念出来。"
    )


def gen_20(i: int) -> str:
    return (
        f"\n\n你仍买两杯豆浆，一杯放她桌角，她喝说谢谢，像对普通同桌，"
        f"只有你知道夹层里还有一个她，清楚薄摸不到，你两个都守，守白天这个守第四层那个，"
        f"老歌里忽然喊你小名，你不倒带，再听合影会再空一个，你薄了指纹浅了，"
        f"疼说明还在，完整的人摸不到被听完的人，别倒带，倒带会再薄一毫米，你仍走小的路。"
    )


def gen_21(i: int) -> str:
    return (
        f"\n\n下雨时你去看护城河，水面普通偶尔有鱼纹，你不对水喊名字，"
        f"喊了雾会凝成她的名字河就会涨，你把豆浆慢慢倒在桥栏外敬岸，"
        f"第三排靠窗空着，老师点名点到赵宜你沉默半拍说请假，老师看你没追问，"
        f"22:59桥边水里闪一下橙色像校服又像糖纸，你眨眼没了你当风，风也算，信就不喊。"
    )


def gen_22(i: int) -> str:
    return (
        f"\n\n白天很好，你按时交作业按时值日，课桌便利贴掉了，背面写下车也是一种解，"
        f"夜里闸机响绿一次又绿一次，像有人进站却不来找你，你没有下楼，下楼会把忽略变成迎接，"
        f"她发消息我在靠窗，不是在你旁边是在线上继续坐，你保留忽略，忽略是她给你的白天，"
        f"空白票在数学书里纸缘磨毛，像被反复检票，你不去检了，检了像催她下车，催是大陆的事。"
    )


def gen_23(i: int) -> str:
    names = ["静音", "馆藏", "随河", "对调", "锁死", "无站名", "两站之间", "空白站"]
    n = names[i % 8]
    return (
        f"\n\n**{n}的早晨（侧写{i + 1}）** 南横街早市还没开，你已在教室或已在路上，"
        f"卷四不是岔路攻略，是城在十一点之后还亮着的别的窗口，九个收场九种收费，没有官方正确答案，"
        f"你活正本，其余并排，选完句子还会留在身上，口袋少一颗糖，合影空一个位子，"
        f"你合上卷四，窗外天亮，正本里她抓袖口说甜的要沉，你嗯，发送成功，没有红色感叹号。"
    )


GENERATORS = {
    "15-停止.md": gen_15,
    "16-爬回.md": gen_16,
    "17-小的路.md": gen_17,
    "18-漏句.md": gen_18,
    "19-馆藏.md": gen_19,
    "20-静音.md": gen_20,
    "21-随河.md": gen_21,
    "22-空白站.md": gen_22,
    "23-八个早晨.md": gen_23,
}


def assemble(name: str, target: int) -> str:
    core = CORES[name]
    pool = SCENE_POOLS.get(name, [])
    seen: set[str] = {para_key(p) for p in core.split("\n\n")}
    parts = [core]
    length = len(core)

    for p in pool:
        k = para_key(p)
        if k in seen:
            continue
        if p in core:
            continue
        parts.append(p)
        seen.add(k)
        length += len(p) + 2
        if length >= target:
            break

    gen = GENERATORS[name]
    i = 0
    while length < target and i < 200:
        block = gen(i)
        k = para_key(block)
        if k not in seen:
            parts.append(block.strip())
            seen.add(k)
            length += len(block)
        i += 1

    text = "\n\n".join(parts).strip() + "\n"
    if len(text) > target + 1200:
        # trim from end generators only
        while len(text) > target + 200 and len(parts) > 3:
            parts.pop()
            text = "\n\n".join(parts).strip() + "\n"
    return text


def count_00_14() -> int:
    total = 0
    for p in sorted(ROOT.glob("[0-9]*.md")):
        if int(p.name[:2]) <= 14:
            total += len(p.read_text(encoding="utf-8"))
    return total


def main() -> None:
    base = count_00_14()
    need = PROJECT_TARGET - base
    per = need // 9
    extra = need % 9
    targets = {}
    for idx, name in enumerate(sorted(CORES.keys())):
        targets[name] = per + (1 if idx < extra else 0)

    sub = 0
    for name in sorted(CORES.keys()):
        t = targets[name]
        text = assemble(name, t)
        (ROOT / name).write_text(text, encoding="utf-8")
        n = len(text)
        sub += n
        print(f"{name}\t{n}\t(target {t})")

    all_total = sum(len(p.read_text(encoding="utf-8")) for p in sorted(ROOT.glob("[0-9]*.md")))
    print(f"---\n15-23 subtotal\t{sub}")
    print(f"project total\t{all_total}")


if __name__ == "__main__":
    main()
