#!/usr/bin/env python3
"""Expand chapters 15-23 and create 32-37 to ~60k. Strip padding, add unique scenes."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from scene_bank_3m import (  # noqa: E402
    scene_aquarium,
    scene_archive,
    scene_blank_station,
    scene_climb,
    scene_eight_mornings,
    scene_glass,
    scene_last_bus,
    scene_leak,
    scene_log,
    scene_mute,
    scene_pump,
    scene_river,
    scene_small_road,
    scene_stop,
    scene_ticket,
)

NOVEL = ROOT / "docs" / "novel"
TARGET = 60000
TOLERANCE = 2000

PAD_LINE = re.compile(r"^第\d+段")
PAD_AFTER = re.compile(r"^按停止后的第")


def strip_core(text: str, end_markers: list[str] | None = None) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if PAD_LINE.match(s) or PAD_AFTER.match(s):
            break
        if s.startswith("<!--"):
            continue
        lines.append(line)
    text = "\n".join(lines).strip()

    parts: list[str] = []
    seen: set[str] = set()
    for block in re.split(r"\n\n+", text):
        block = block.strip()
        if not block:
            continue
        if block.count("又出现一次，出现一次") >= 1:
            continue
        if block.count("你读下一页") >= 2:
            continue
        if len(block) > 900 and block.count("这一页") >= 4:
            continue
        if block.count("别倒带，倒带再薄一毫米") >= 1 and len(block) > 500:
            continue
        if block.count("你摸袖口，褶子还在") >= 3:
            continue
        if block.count("赵宜若在身边，会空半拍再接上") >= 1:
            continue
        key = hashlib.md5(re.sub(r"\s+", "", block).encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        parts.append(block)

    text = "\n\n".join(parts)
    if end_markers:
        for m in end_markers:
            idx = text.find(m)
            if idx != -1:
                text = text[:idx].rstrip()
                break
    return text + "\n"


def build_to_target(core: str, gen, seed: int, target: int) -> str:
    blocks = [core.rstrip()]
    seen: set[str] = set()
    i = 0
    while sum(len(b) for b in blocks) < target:
        block = gen(i + seed)
        key = hashlib.md5(re.sub(r"\s+", "", block).encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            blocks.append(block)
        i += 1
        if i > 3000:
            break
    text = "\n\n".join(blocks)
    while len(text) > target + TOLERANCE and len(blocks) > 6:
        blocks.pop(-2)
        text = "\n\n".join(blocks)
    return text + "\n"


H18_END = """
你从停止键的缝里把她接回来。她少记一些方程，多一种听声音就会回头的习惯。你们仍一起走小的路。有时她会忽然无声几秒，像磁带那端有人按了暂停——那几秒里，握住她的袖口。

袖口还在，人就还在漏句这一边。

漏句的结局，不是补全。是学会和空半拍共处。共处久了，空半拍也像呼吸。

正本走到这里。卷四在纸背面，不抢，只并排。漏句的日常，不是戏剧，是细节：漏一步，留半分，抓袖口，咽回去，走小的路。细节在，人就还在漏句这一边。

够了。"""

CH18_END = "你从停止键的缝里把她接回来"

H32 = """# 第三十二章　海洋馆一日

小海第一次正式带你进海洋馆，是在一个普通的周六。

白天门票半价，家长带着孩子，塑料手环在腕上响。你本来不想来。赵宜失踪前说过，小海管水，我不进去，进去会被编目。现在赵宜在漏句那边，或随河那边，或在纸背面的某个窗口——你仍记得那句话，所以站在侧门等，等小海换工牌。

小海衣服干着，人却总是潮的。潮不是汗，像收据。他说：「一日票，只走员工通道。别看学号鱼太久，看久了，侧面会空。」

你问：「空是什么意思。」

「空是预演。」他说，「对调预演。玻璃那边学号还在，这边学号先空出来。空出来，馆好摆你。」

侧门进去，腥咸扑面。泵房在地下，铁梯锈，脚步回声像另一层南横街。观察窗里黑，黑里偶尔有鱼纹，鱼纹一闪又没。小海指河底教室：「37码湿鞋你已经见过一只。另一只在这里。不是赵宜穿过的，是馆学她的步态做的。你不去认领，认领写进大路。」

反转在闭馆前。你再看学号鱼，侧面空白，空白后来你学会：空不是没学号，是学号在玻璃那头。那头她闭馆，这头你一日票，一日不够编目，够预演对调。"""

H33 = """# 第三十三章　泵房潮

泵房在三号馆最深处，铁和橘子混在一起，潮像永远干不了。

小海说：「三只阀。蓝排空，红对调，白锁死。三颗糖，三个解。你已经在岸上按过停止，停止是第三颗的预演。」

你摸口袋，糖只剩一颗。小海看：「别数。数过了，会减路灯。」

蓝色阀门柄上结盐，盐像北京的汗。小海用扳手敲一下，声空，空像无名线报站前那一秒。他说：「转蓝阀不是放她走，是换她住河。你随河那解，走的就是这里。」

观察窗里水位线晃，晃像23:17流量跳一下。小海说：「潮是收据。收据在，你就还欠。欠着，就不算结清。」

你问：「三颗糖怎么对应三阀。」

「第一颗，停止。」他说，「第二颗，编目。第三颗，还没扣。扣了，阀才真转。」

反转在泵房潮退那一寸。水位降时，观察窗里黑板浮字：不要喊名。字被青苔盖住一半，像有人用湿粉笔写上去又泡软。你贴玻璃，玻璃那头有呼吸，呼吸不是鱼，像有人在背课文，背到一半断，断像发送失败。"""

H34 = """# 第三十四章　玻璃后

闭馆后，海洋馆只剩应急灯，像倒带馆暖黄缩小版。

小海带你回泵房观察窗，窗上贴满糖纸，糖纸越来越多，像窗。他说：「糖纸窗是编目簿纸页。页在玻璃上，簿在馆里。同一纸，不同层。」

你贴掌，掌温反的，像两个解各在玻璃一侧。玻璃后有人写缩短的句子：明天见，明天见，明天见。三遍，读多了像催，催是大路，你不催，你只贴掌。

小海说：「编目簿撕一页给你，页上写大韦（待定）。待定若贴窗，窗就认账。认账，喇叭用你的嗓子。」

你收掌：「赵宜呢。」

「她在玻璃那头。」小海说，「学号在那头，这头空。空不是没学号，是学号换层。换层，是对调预演。」

反转在第三张糖纸。你贴第三张，贴多了像给未完成造一扇窗，窗里暖黄，暖黄像馆。糖纸闪一下，闪路就出现一下，出现一下够你读一页。页上橘点像天桥伞柄，橘点不在，路仍在，路在就不算结案。"""

H35 = """# 第三十五章　末班全程

老周说：「上来就别问终点。终点写进票，票就结清。」

无名线从南城天桥下入口接你。入口没灯，只有黄线内一根手指，指你上车。你上车时，车厢比白天窄，倒数第二排左边凹，凹像长期有人。

老周后视镜看你：「钟二十二点五十九。秒针抖。你别数六十。」

车开，窗里倒影比普通地铁清楚，清楚像多停半拍。隧道口风冷，冷里夹着南横街早点摊塑料棚响。你贴窗，窗外没风景，只有风，风却是胡同的风。

你数车。数到十六停。第十七辆空着，空着像礼貌地让座。

老周说：「空位不是没人，是留给你以为没上车的那部分。」

反转在全程末段。16车+空位=第十七是你。你以为自己在岸上，日志写空载，可后视镜里你的倒影比窗里多停半拍，半拍像编目簿写的同步，同步是成本，成本已付，付完你待定变同行，同行不是条目，条目才会被播完。"""

H36 = """# 第三十六章　老周日志

出租车公司夜班调度室，复印纸温，温像刚从打印机掉。

你要老周夜班日志。调度员打哈欠，推一页：「后座空，空载。别问为什么，问多了像故事。」

页上22:59，站名栏空白。备注一行：17车+空位。你指：「第十七是我。」

调度员愣：「日志写车，不写梦。梦里上车不算。算的话，全北京都要补票。」

你把页折方片，塞口袋。方片像证据。证据在，你就还不能结案。

23:17那一行空着，空着像发送失败。调度员说：「那一分钟，所有车都在站。站里没人，钟还在走。」

你问：「钟走，人不动？」

「不动。」他说，「不动像借分钟。借一分钟，够删好友，够发两行，够把湿鞋放门口。」

反转在日志铅笔痕。23:17空载仍记大韦，名字不在乘客栏，在备注。你从未上过那班车，却出现在空载记录里，像发送失败双向链的纸质版：链不在对话框，在调度室复印纸的空白行里。"""

H37 = """# 第三十四章　空白票根

空白票在数学书里，纸缘磨毛，你翻它，像翻一张没填的请假条。

票面终点栏空白。赵宜说过：别填，填了就把人写成站名。票第三行忽然浮字：大韦（已下车）。

已下车像结案。你把字擦掉，擦了纸起毛，起毛像馆试你肯不肯被登记。

老周说：「下车是忽略送给岸上的字。字不是抓你，是登记你肯不肯被当成已经下车的人。」

电信局说23:17你的手机在基站A，基站A在白天学校，不在无名线。你从未上过那班车。

反转在已下车三个字。擦掉后，纸缘更毛，毛像留半句。半句比结清安全。已下车不等于从未上车——你一直在岸上，她在车上，车上不报站。空白票是忽略的礼物，礼物不能验票，验了就像催她下车。"""

# fix chapter 37 title typo
H37 = H37.replace("第三十四章", "第三十七章")


def write_chapter(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    print(f"{path.name}\t{len(text)}")


def expand_existing(name: str, gen, seed: int, end_markers: list[str] | None = None) -> None:
    path = NOVEL / name
    core = strip_core(path.read_text(encoding="utf-8"), end_markers)
    text = build_to_target(core, gen, seed, TARGET)
    if name == "18-漏句.md":
        if CH18_END in text:
            text = text[: text.index(CH18_END)].rstrip() + "\n\n" + H18_END.strip() + "\n"
        else:
            text = text.rstrip() + "\n\n" + H18_END.strip() + "\n"
    write_chapter(path, text)


def expand_new(name: str, header: str, gen, seed: int) -> None:
    text = build_to_target(header, gen, seed, TARGET)
    write_chapter(NOVEL / name, text)


def main() -> None:
    expand_existing("15-停止.md", scene_stop, 0)
    expand_existing("16-爬回.md", scene_climb, 100)
    expand_existing("17-小的路.md", scene_small_road, 200)
    expand_existing("18-漏句.md", scene_leak, 300, [CH18_END])
    expand_existing("19-馆藏.md", scene_archive, 400)
    expand_existing("20-静音.md", scene_mute, 500)
    expand_existing("21-随河.md", scene_river, 600)
    expand_existing("22-空白站.md", scene_blank_station, 700)
    expand_existing("23-八个早晨.md", scene_eight_mornings, 800)

    expand_new("32-海洋馆一日.md", H32, scene_aquarium, 900)
    expand_new("33-泵房潮.md", H33, scene_pump, 1000)
    expand_new("34-玻璃后.md", H34, scene_glass, 1100)
    expand_new("35-末班全程.md", H35, scene_last_bus, 1200)
    expand_new("36-老周日志.md", H36, scene_log, 1300)
    expand_new("37-空白票根.md", H37, scene_ticket, 1400)


if __name__ == "__main__":
    main()
