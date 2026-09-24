#!/usr/bin/env python3
"""Full rebuild of chapters 08-14 from clean cores + unique pools."""

import importlib.util
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
TARGET = 20800
TOLERANCE = 350

META_RE = re.compile(
    r"^(下一步|现在，你只|停\.?$|够了\.?\.?|赵宜（未完成）|进门，暖黄|读到这里|正本，按停止|大韦游戏|不是这一章|下一章|后面章|第十五章|你站键前|后面的章|按是下一章|这一章只|按了，是后面|imaginary )"
)

META_SUBS = [
    r"后面的章才轮到",
    r"不是这一章",
    r"下一章",
    r"按了，是第\S*",
    r"这一章只到",
    r"按是下一章",
    r"imaginary 登记簿",
    r"你还不按，按了",
    r"站成还愿意听但未完的人",
    r"现在，你只站在\S+",
    r"现在，你只离开天桥",
    r"是后面的章",
    r"是第十五章",
    r"后面章",
    r"再下一章",
    r"再，磁带响",
    r"再，三只键烫",
    r"规则讲清楚",
    r"你的手指慢慢按下去",
    r"你的手指，在，按下去",
    r"你慢慢按，",
    r"你按停止，三只键开始发热",
]

BANNED_CONTAINS = [
    "后面的章",
    "是第十五章",
    "这一章只",
    "站成还愿意",
    "下一步，是第",
    "imaginary ",
    "你的手指慢慢按下去",
    "你的手指，在，按下去",
    "你的手指，慢慢按下去",
    "你慢慢按，",
    "慢慢按下去",
    "这一章停",
    "还没按下去",
]

EXCLUDE_IF_IN = {
    "08": ("食街深处", "三楼没有灯", "台式卡座开始发热", "试听间里，隔音"),
    "09": ("三楼没有灯", "台式卡座开始发热", "试听间里，隔音", "三只键并排"),
    "10": ("三楼没有灯", "台式卡座开始发热", "试听间里，隔音", "三只键并排"),
    "11": ("食街深处", "台式卡座开始发热", "试听间里，隔音", "三只键并排"),
    "12": ("食街深处", "三楼没有灯", "三只键并排"),
    "13": ("食街深处", "三楼没有灯", "食街椅子倒扣"),
    "14": ("食街椅子倒扣", "侧身穿缝之前", "童装区打折"),
}

_spec = importlib.util.spec_from_file_location(
    "fr0408", Path(__file__).parent / "final_rewrite_04_08.py"
)
_fr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fr)

from bulk_extra_0814 import BULK  # noqa: E402
from final_rewrite_08_14 import E08, E09  # noqa: E402
from mega_0814 import M08, M09, M10, M11, M12, M13, M14  # noqa: E402
from pads_08_14_rest import E10, E11, E12, E13, E14  # noqa: E402

try:
    from mega_blocks import BLOCKS as MEGA  # noqa: E402

    EXTRA_SHARED = [
        p.strip()
        for p in MEGA
        if "正本，按停止" not in p and "读到这里" not in p and "大韦游戏" not in p
    ]
except ImportError:
    EXTRA_SHARED = []

SHARED_BASE = _fr.PAD05 + _fr.PAD06 + _fr.PAD07 + _fr.PAD08 + EXTRA_SHARED

BULK_BY_CH = {
    "08": [b for b in BULK if any(k in b for k in ("天桥", "选路", "桥栏", "透明伞", "老周", "小海"))],
    "09": [b for b in BULK if any(k in b for k in ("西单", "侧身穿", "中庭", "缝", "扶梯"))],
    "10": [b for b in BULK if any(k in b for k in ("食街", "豆浆", "省略", "点餐屏"))],
    "11": [b for b in BULK if any(k in b for k in ("三楼", "模特", "霓虹", "眼窝"))],
    "12": [b for b in BULK if any(k in b for k in ("倒带馆", "试听", "登记", "宝丽来", "后仓"))],
    "13": [b for b in BULK if any(k in b for k in ("磁带", "卡座", "倒带", "播放", "我选——"))],
    "14": [b for b in BULK if any(k in b for k in ("三只键", "停止键", "弹出", "键热", "键烫"))],
}

CH09_CORE = """# 第九章　西单

跟阿青离开天桥之后，你们没再说话，雨把霓虹拉成湿线，她把透明伞往你这边偏一点，伞骨咔咔响，像某种计时，你口袋里的便当已经不烫，仍有余温，三颗糖在另一头口袋，分开存放，阿青说过，别把岸上的甜和夜里的甜走混，西单方向的风更硬，硬风里夹着旧塑料、橘子皮、还有磁带放久了的微甜。

路过一家还亮着灯的复印店，卷帘半开，机器空转，老板趴在柜台上睡，没醒，玻璃上有人用指节写过一行字，被雨冲得只剩十一点，你停了一秒，阿青拉你，别读，读了，你会想停下来等，再往前，西单那座停业商场出现在街角，白天写改造中，夜里却留着一人宽的缝，缝里的光比外面黄。

你站在缝前，没立刻进，侧身穿过去之前，你先看缝里的扶梯，空转，阶梯往上，脚却觉得在往下，你想起笔记里那句，电梯只到三，四楼得走漏的，便当袋在手里换了一次，油渍没沾到门边，袋绳勒出红印，你换一只手，阿青看你，还走得动吗，你点头，其实腿有点软，软不是因为累，是因为缝太窄。

侧身穿进去，卷帘在身后轻轻响，外面雨声一下子远了，远得像被关进另一个频道，里面干，干得像档案室，像试卷堆久了的房间，阿青说，停业是白天的说法，夜里它开给听得见的人，你问，听得见什么，她看你一眼，听得见句子还没说完，人又不肯走。"""

CH10_CORE = """# 第十章　食街

倒带馆在四楼，到馆之前，阿青在食街又停了一次，不是休息，她说，她请我在这儿喝过豆浆，你最好先知道豆浆是什么味道，食街椅子倒扣在桌上，腿朝天，像一群被翻过去的龟，应急灯把桌面照白，白得能看清灰，灰里有人用手指写过回家，字已经被后来的灰盖住，只剩笔画深处一点凹痕。

你跟着阿青往里，食街的应急灯白得刺眼，你经过一张倒扣的桌子，桌腿在地面投出四根细影，像某种未完成的符号，符号还没写完，写完，就不是你了，阿青说，别在食街答应请客，答应了，你会坐到打烊，打烊没有钟，钟停在二十二点五十九，秒针抖，不跳到二十三点。

食街深处，点餐屏亮着雪花，屏幕里没有字，只有橙色方块，一块，两块，三块，阿青用吸管在空气里点了一下，像点杯壁，省略号，她不敢寄回家的那句，省略在这儿，你没问那句是什么，问出来，像要替她把句子说完，而她停在了「我选」。"""

CH11_CORE = """# 第十一章　三楼

三楼没有灯，只有霓虹在自己闪，粉和青，交替，像呼吸，模特站在橱窗里，站在走廊两侧，站在扶梯口，它们没有脸，有的连眼窝都空着，空得像喇叭，风从眼窝穿过，发出极轻的哨声，节奏和你心跳错半拍，阿青走在你前面半步，别应广播，三楼会把你收成一句，一句能循环的，循环久了，你就不是同桌，是背景音。

你停住，喊声也停住，阿青按住你的肘，没说话，她的手指凉，透过校服袖，你低头看模特，模特手指都指向四楼，指得整齐，像被训练过，指向馆，指向未完成，赵宜的声音又来一次，近到像贴在你耳后，同桌，电梯只到三，楼梯在模特后面，别怕黑，馆里的黑是没有下一句，你喉咙动了一下，差点应，你想起警察的空白卡片，把那个嗯咽回去，咽得喉头发紧。

有一尊模特穿黄风衣，齐刘海，像某个夜里一眼能认出的轮廓，你多看一秒，阿青用伞骨挡你的视线，别对视，对视了，它会学你的步态，学了，四楼会以为你已经上来过，楼梯在模特后面，窄，黑，没有扶手，阿青打开手机灯，青绿，和耳机灯同色，馆里的黑是没有下一句，下一句在带里，带里停在「我选——」。"""

CH12_CORE = """# 第十二章　倒带馆

暖黄灯，木架子顶到烟渍天花板，空气里是旧塑料、橘子皮、还有磁带放久了的微甜，架子上的带大多没歌名，有的写日期，有的写天气，有的只写姓，你看见一排与教室座位表相同的顺序，第三排靠窗空着，标签铅笔写，赵宜（未完成），你的手指在那盘上方停住，带壳温的，像刚从谁口袋里拿出来，阿青说，这里收人还来不及说出口、又不肯死掉的那一句，放一次，句子短一点，放到最后，说话的人从照片上变淡，别贪听，贪听的人，会把自己也录进去，当背景噪音。

你问，为什么还开着馆，有人把句子寄存在这儿，抛弃是把带子扔进护城河，寄存是说，等一个肯按停止、也肯按播放的人，赵宜选了你，柜台后没有店员，喇叭嵌在墙里，网罩积灰，你走近，喇叭极轻地响，欢迎光临，用的是你自己的嗓子，你没说过这句话，墙上的钟不肯往前，阿青敲柜台，它在试探你肯不肯成为馆的一部分，别回欢迎，你没回。

她把赵宜那盘未完成抽出来，放进台式卡座，先是电流，然后是雨，然后是她的声音，比回忆更近，我算到一半，方程有两个解，一个是回家，一个是继续往前，我选——，咔哒，磁带断了，卡座数字窗停在一个不该有的日期，明天，喇叭沉默了一秒，又用你自己的声音说，要试听吗，今日推荐，你的名字，你把手缩回，阿青把那盘推远，它在长，话一完整，你也会薄。"""

CH13_CORE = """# 第十三章　磁带

你按下播放，还是同一句，停在同一处，电流，雨，赵宜的声音，我算到一半，方程有两个解，一个是回家，一个是继续往前，我选——，咔哒，断了，阿青按倒带，数字窗往回跳，磁带里赵宜忽然笑出来，你真的来了，我就知道橘子糖能把你喊到，便当呢，过期也行，过期的比较甜，你看了眼柜台上的袋子，袋子轻轻震了一下，像被点名。

她说：「别相信大路。大路会把你送回白天，白天的人会劝你忘记。你要是想找到我，就听完整盘。听到最后，你会知道我站在哪一层。」

电流里，赵宜压低声音：「同桌，我怕黑。别告诉阿青。馆里的黑是没有下一句。我怕自己变成一句被剪掉的呼吸。你要是把整盘听完，我会在第四层等你。你要是按停止，我会试着自己走回来。我不确定哪一种更疼。」

试听间那边，那盘「你的名字」还在发热。阿青把它推更远：「别碰。碰了，你会想把自己的名字也录进去。」"""

CH14_CORE = """# 第十四章　三只键

台式卡座开始发热，播放、停止、弹出，三只键并排，烫得像刚晒过，阿青退开一步，把选择留给你，青绿耳机灯一闪一闪，像在倒数，喇叭沉默，沉默比欢迎光临更像一句完整的话，你站在柜台前，手插进口袋又拿出来，拿出来，是因为停止键需要手指，插进去，是因为糖需要确认还在，三颗，走一回少一颗，别一次吃完。

阿青把规则讲第三遍，这一遍最短，听完整盘，她在第四层，你在合影里让座，把磁带交给我，你们都停在未完成，按停止，她可能爬回来，带着漏句和疼，三种都是爱，收费不同，你问，有没有对的选项，阿青摇头，没有官方正确答案，只有收费不同。

你怕她回不来，也怕她回来了，却不完整，也怕她完整了，你薄了，怕的太多，你就站在三只键前，像站在方程中间，播放键在左边，烫，弹出键在右边，更烫，停止键在中间，凉一点，你想起她说过，停止是疼的，疼的人会回来，播放是完整的，完整的人摸不到被听完的人，赵宜在带里又说话，我选——，还是断在那里，你的手指，停在停止键上方，停，还没按。"""

END13 = (
    "钟还是二十二点五十九，秒针抖，不跳到二十三点，你没数六十，六十会把人交还给点名册，"
    "磁带里电流和雨声交替，赵宜的声音又落到同一处，我算到一半，方程有两个解，"
    "一个是回家，一个是继续往前，我选——，咔哒，断了，你的手指停在停止键上方，"
    "停，还没按，阿青在帘外没催，催是大路的事，大路要你在三秒内改主意，"
    "你不改，你只等，等带里那个空，空很小，小得像半个音节，半个音节后面，"
    "才轮到你选怎么疼，你抓紧袖口，布料潮，真实，真实在，你就还在同桌这一边，"
    "这一边，才配悬在停止键上，悬着，像方程里那个问号，问号留给同桌，你选，"
    "停，还没按，断，在「我选——」。"
)

END14 = (
    "键热着，阿青退开一步，把选择留给你，青绿耳机灯一闪一闪，像在倒数，"
    "喇叭沉默，沉默比欢迎光临更像一句完整的话，你站在三只键前，"
    "播放键在左边，烫，弹出键在右边，更烫，停止键在中间，凉一点，"
    "凉，像她冬天塞给你暖手的糖纸，赵宜在带里又说话，我选——，还是断在那里，"
    "你的手指停在停止键上方，停，还没按，你还不急，急的人，容易被馆代选，"
    "代选，就不是你的疼，你拒绝被代选，你当同桌，同桌是作业、便当和袖口，"
    "你选手心最不怕后悔的那个，怕的留给白天，白天会替你后悔，夜里只把键摆好，"
    "夜里不替你按，按下去会疼，疼是你的，那是之后的事，"
    "现在，你只悬在停止键上方，悬着，像方程里那个问号，问号留给同桌，你选，"
    "停，还没按，断，在「我选——」。"
)


def is_telegraphic(p: str) -> bool:
    parts = re.split(r"[。！？]", p)
    parts = [x.strip() for x in parts if len(x.strip()) > 1]
    if len(parts) < 3:
        return False
    short = sum(1 for x in parts if len(x) <= 8)
    return short / len(parts) > 0.65


def clean_para(p: str) -> str:
    for pat in META_SUBS:
        p = re.sub(pat, "", p)
    p = re.sub(r"[ \t]+", "", p)
    p = re.sub(r"，{2,}", "，", p)
    p = re.sub(r"，，+", "，", p)
    return p.strip()


def is_banned(p: str) -> bool:
    return any(b in p for b in BANNED_CONTAINS)


def dedupe_paras(paras: list[str]) -> list[str]:
    seen: set[str] = set()
    kept: list[str] = []
    for p in paras:
        p = clean_para(p)
        if not p or len(p) < 45:
            continue
        if META_RE.match(p) or is_banned(p):
            continue
        if is_telegraphic(p):
            continue
        if p in seen:
            continue
        seen.add(p)
        kept.append(p)
    return kept


def split_core(core: str) -> tuple[str, list[str]]:
    lines = core.strip().split("\n\n")
    title = lines[0] if lines[0].startswith("#") else ""
    body = lines[1:] if title else lines
    return title, body


def assemble(
    title: str,
    core_body: list[str],
    chapter_pool: list[str],
    generic_pool: list[str],
    end_para: str | None = None,
) -> str:
    base = dedupe_paras(core_body + chapter_pool)
    used = set(base)
    generic: list[str] = []
    for p in dedupe_paras(generic_pool):
        if p in used:
            continue
        generic.append(p)
        used.add(p)

    ep = clean_para(end_para) if end_para else ""
    if ep and (ep in used or is_banned(ep)):
        ep = ""

    def build(gens: list[str]) -> str:
        parts = base + gens
        if ep:
            parts = [x for x in parts if x != ep] + [ep]
        return title + "\n\n" + "\n\n".join(parts) + "\n"

    # Add generic paragraphs until near target; keep ending paragraph last.
    keep = 0
    for i in range(len(generic) + 1):
        text = build(generic[:i])
        if len(text) >= TARGET - TOLERANCE:
            keep = i
            break
        keep = i

    text = build(generic[:keep])
    if len(text) > TARGET + TOLERANCE:
        # Trim generic from the end, never drop base or ending.
        while keep > 0 and len(text) > TARGET + TOLERANCE:
            keep -= 1
            text = build(generic[:keep])
    return text


def generic_pool(ch: str) -> list[str]:
    ex = EXCLUDE_IF_IN.get(ch, ())
    primary = set(BULK_BY_CH[ch])

    def ok(p: str) -> bool:
        return not any(x in p for x in ex)

    rest = [b for b in BULK if b not in primary and ok(b)]
    shared = [p for p in SHARED_BASE if ok(p)]
    bulk_ch = [b for b in BULK_BY_CH[ch] if ok(b)]
    return bulk_ch + shared + rest


CHAPTERS = [
    ("08-天桥.md", _fr.CH08, M08 + E08, generic_pool("08"), None),
    ("09-西单.md", CH09_CORE, M09 + E09, generic_pool("09"), None),
    ("10-食街.md", CH10_CORE, M10 + E10, generic_pool("10"), None),
    ("11-三楼.md", CH11_CORE, M11 + E11, generic_pool("11"), None),
    ("12-倒带馆.md", CH12_CORE, M12 + E12, generic_pool("12"), None),
    ("13-磁带.md", CH13_CORE, M13 + E13, generic_pool("13"), END13),
    ("14-三只键.md", CH14_CORE, M14 + E14, generic_pool("14"), END14),
]


def main():
    for fname, core, ch_pool, gen_pool, end_para in CHAPTERS:
        title, core_body = split_core(core)
        text = assemble(title, core_body, ch_pool, gen_pool, end_para)
        (ROOT / fname).write_text(text, encoding="utf-8")
        print(f"{fname}\t{len(text)}")


if __name__ == "__main__":
    main()
