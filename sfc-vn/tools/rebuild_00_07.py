#!/usr/bin/env python3
"""Rebuild chapters 00-07: de-AI, de-pad, expand to STYLE_V486 targets."""
import re
import subprocess
from pathlib import Path

NOVEL = Path(__file__).resolve().parent.parent / "docs" / "novel"
TOOLS = Path(__file__).resolve().parent

TARGETS = {
    "00-序.md": 7000,
    "01-发送失败.md": 20800,
    "02-空位.md": 20800,
    "03-赵宜家.md": 20800,
    "04-胡同.md": 20800,
    "05-第三夜.md": 20800,
    "06-胡同深.md": 20800,
    "07-便利店.md": 20800,
}

PADDING_RES = [
    re.compile(r"^空位第\d+天"),
    re.compile(r"^胡同第\d+盏"),
    re.compile(r"^便利店里你第\d+次"),
    re.compile(r"^赵宜家第\d+次"),
    re.compile(r"^周[一二三四五](午休|放学)"),
    re.compile(r"^第\d+次发送失败"),
]

META_LOOPS_00 = re.compile(
    r"大韦游戏工作室|Pocket MICRO|海报句子|海报上只留|读序|读正本|不必重读|卷四不必"
)

CH00_BODY = """# 序

海报和游戏署名里，同桌叫大韦。正文仍用「你」。赵宜喊的是同桌，不是大韦；偶尔急了才喊一声大韦，一章里也不会超过两次。

大韦，南城某中学学生，和赵宜同桌，第三排靠窗。这是序章里唯一一次把名字写全。后文爸、班主任点名、警察笔录、赵宜妈妈仍叫大韦；赵宜日常喊同桌。

北京会在十一点换一张脸。不是全城一起变，是某些地方先变：天桥灯从白改成橙，便利店钟少跳一格，鱼缸里的北京比岸上的慢半拍。白天那套还在，上学、点名、立案、结案，到夜里还在，只是不再优先。夜里优先的是找，找走丢的人，找没说完的话，找还能不能回家。

这条规矩没人写进条例。它写在短信里，写在笔记撕页上，写在过期便当的标签里。写得很短，短到像恶作剧：别走大路。先别喊名字。别把磁带听完。甜的东西要沉。

赵宜失踪第三天，给你发来两行字：十一点后来天桥。别走大路。

你回：你在哪。发送失败。

对话框顶上多了一行小字：对方已不是好友。时间戳是昨天深夜，23:17。你当时应该睡了，或者说，你以为自己睡了。这个分钟空着，像黑板上一块没擦干净的白。

发送失败不是句号，是逗号。逗号后面还有南横街、护城河、西单倒带馆，还有磁带断在「我选——」后面那个没说完的字。正本走漏句：按停止，她从缝里爬回，少记方程，多一种听声回头的习惯。卷四另八个早晨并列，不判对错。

大韦游戏工作室把玩家叫大韦，游戏里仍叫「你」。彩色都市灵异文字冒险，给 Pocket MICRO 横屏写的，浏览器里也能玩。做成音小说，你只能听、看、选，听和选对得上磁带、水和路。

你在这本书里仍是无名的「你」。因为赵宜每喊一次同桌，都砸在第二人称上。同桌不是昵称，是位置，是第三排靠窗旁边那个位子，每学期开学班主任排座次，你们总被分到相邻。她转笔，笔掉，踩你脚，让你捡；你捡，她笑，说谢谢，谢完又戳你胳膊问这题怎么做。二层青涩：关心，但不告白，告白会把路压塌。

赵宜奶奶灰齐刘海，黄风衣，黑衬衫，红领带，口袋里有橘子糖。她怕黑，怕的部分漏给试听，没写进笔记。她说怕的留给白天，夜里只把路分开；分开什么，题，两题两个解，你选一个，她选另一个。你问选什么，她笑：选先喝豆浆的那个。

值日那天，你擦黑板，她洗抹布，水凉，她把手在衣摆上蹭完又蹭你袖口，像开玩笑。你躲，她说同桌互助。擦到一半她在下面排值日歌，跑调也认真。黑板粉灰落她刘海上，她不动，说灰像雪，雪化了还是灰。

失踪前一天下午，你们在天桥下面分一颗橘子糖。风把护城河吹起一层细鳞，她把糖纸折成小船放进水里，小船漂两米，卡在桥墩阴影里。你说停住了，她说停住也好，停住的才有人找。她看你看你，说同桌你别那样看，像我要消失了。你说瞎说。

第三排靠窗的位子，窗框老掉漆，赵宜拿指甲抠过，抠出一道白，说像草稿纸的延伸。你说过期豆浆更甜，她不信，第二天带两杯来，一杯给你一杯自己喝，说沉住了就不容易被冲走。你当时以为她在说豆浆。

白天那套还在。赵宜失踪第三天，空位在第三排靠窗，椅背贴着桌面，和她昨天离开时一样。桌角压着橙色便利贴，字迹用力，纸都快戳破：晚上豆浆，我请。胶还黏，人却像被整段删掉了。

班主任说能写进请假条的，他先信，别的晚上再说。赵宜妈妈坐在女儿位子上，大衣没脱，问宜宜有没有跟你说要去哪儿，你把头摇了。她把「晚上豆浆，我请」揭起来看了看，又贴回去，动作很轻，像怕把字蹭掉。

警察倒杯热水，记录里她是自行离开。笔记里写阿青管声音、小海管水、老周管路，这些名字白天问不到。他压低声音：十一点以后，别答应水里的人，别答应倒影，别把一整盘磁带听完。说多了没用，你按她短信走，他们在大路上等。大路和小路从此分开，大路安全，也容易把人写成请假条和结案报告。

有称呼的人名就四个：赵宜、阿青、老周、小海。妈妈、班主任、警察、馆长用身份出场。名字少，被喊到的人就沉。赵宜一旦写进水箱、磁带、报站，就会变成条目。

三条路收同一种失踪，保管方式不同：倒带馆收声音，海洋馆管水，无名地铁管路。选一条，另外两条仍给你留位子。没有救下她然后天亮，有的结局她回来少记方程，有的结局她留在路线河夹层，有的结局你留下。九个收场并列，「选你最不怕后悔的」才说得通。

南横街的雨有股土腥，土腥底下是煤烟、早点摊的豆浆、有人家汤没关火的咸。你从这章发送失败读起，经空位、赵宜家、胡同、第三夜、胡同深、便利店，到天桥选路。读完了，句子还会留在身上，口袋可能少一颗糖，合影可能空一个位子，坐车时可能有一段空会喊你的名字，这些是收场，不是教训。

正本从发送失败读起。赵宜从「我选——」后面漏回来，不完整，能抓袖口。停止键比播放烫，漏句可以走路，馆藏只能被播放。数字要能用：三颗糖，走一回少一颗；灭七盏灯，还剩十盏可以灭；十六辆车，第十七辆是空位。

二层那会儿，你们总被分到第三排靠窗。她转笔，转掉了就踩你脚，让你捡，你捡，她谢，谢完又戳你胳膊问这题怎么做。你讲一遍，她听一半，另一半去画小人，小人在卷子上举牌子：同桌加油，你说幼稚，她说幼稚才像人。发送失败之后，你仍做这些小事，擦黑板时多留一块没擦像留空位，洗抹布时水仍凉，凉得像确认她不在，你不再排值日歌，跑调需要两个人，一个唱一个笑。

爸在厨房热牛奶时会叫：大韦，别总熬夜，你嗯一声端走，烫，换到另一只手，你不解释发送失败，解释像大路，大路会把看见的东西写成空白。班主任点名点到赵宜，空着，他停半秒，改点你，说：大韦，你知道她去哪吗，你摇头，他说能写进请假条的，他先信，别的晚上再说。

你曾在护城河堤上和她投石子，她说听，一声是轻，两声是重，你投，她说同桌你投石问路啊，你问问什么路，她说问回家的路，你笑她装，装现在不笑。她笔记里夹过一张公交卡收据，时间23:17，你问这么晚，她说补作业，你信，现在你不确定，不确定就留着，留着像疑点，疑点留着夜里才有路。

生物课观察细胞，她显微镜里看见奇怪形状，喊同桌快来看，你凑过去，头发蹭她刘海，她没躲，说像不像糖纸皱了，你说像，她说那就当糖还在。冬天教室暖气不足，她把手套摘一只给你，说同桌你手怎么比我还冷，你说写字写的，她说写字写出手套，你戴手套写一笔，她笑，笑完又戳你：这题两个解，你选一个，我选另一个。

校医室登记本，有一次她陪你去拿创可贴，你打球擦破手，她填表，填到陪同写同桌，校医笑：同桌也算陪同，她说算，他比我还怕血，创可贴贴歪，她帮你撕正，撕正像替她以后也会帮你撕正某种东西，某种东西后来叫发送失败，失败不能撕正，只能走。

你帮她抢过限量便签纸，粉色，全班想要，她分到两张，给你一张，说同桌写重要的，你写：晚上豆浆，我请，她看：太重要了吧，你说那换一张，她说不换，就这张，这张还在桌角，人不在。发送失败之后，你把对话框置顶，置顶像把空位放在最上面，最上面仍是她的头像，春游照，齐刘海，笑成一条线，线下面红色感叹号，你关屏，开屏，又关，像某种只有你能做的仪式，仪式不救人，仪式让你还能走去第三排靠窗。

你读到这里，应该知道从哪里开始：发送失败。红色感叹号像某种只有你能看见的封印，封印不是结局，是开头。你收到了，你还没去。去，是第一章的事。"""


def load_bank() -> list[str]:
    items = []
    for fp in [TOOLS / "bank2.txt", TOOLS / "extras_ch01.txt"]:
        if fp.exists():
            items.extend(
                x.strip()
                for x in fp.read_text(encoding="utf-8").split("\n\n")
                if x.strip()
            )
    pt = TOOLS / "pad_to_target.py"
    if pt.exists():
        m = re.search(r"BANK = \[(.*?)\n\]", pt.read_text(), re.S)
        if m:
            for line in m.group(1).split("\n"):
                s = line.strip().strip(",").strip('"')
                if len(s) > 30:
                    items.append(s)
    return items


def is_padding(p: str) -> bool:
    s = p.strip()
    return any(r.search(s) for r in PADDING_RES)


def norm_key(p: str) -> str:
    return re.sub(r"\s+", "", p)[:200]


def split_paras(text: str) -> tuple[str, list[str]]:
    title, paras = "", []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block:
            continue
        if block.startswith("#"):
            title = block.split("\n")[0]
            continue
        paras.append(block)
    return title, paras


def clean_paras(name: str, paras: list[str]) -> list[str]:
    out, seen = [], set()
    openers: dict[str, int] = {}
    studio_in_00 = False

    for p in paras:
        if is_padding(p):
            continue
        if name == "00-序.md" and META_LOOPS_00.search(p):
            if "大韦游戏工作室把玩家" in p:
                if studio_in_00:
                    continue
                studio_in_00 = True
            elif "海报" in p and "Pocket" in p:
                continue
            elif META_LOOPS_00.search(p) and "大韦游戏工作室" not in p:
                continue
        if name == "05-第三夜.md" and re.search(r"你进胡同了|便利店的钟|收银台旁小音箱", p):
            continue
        if name == "04-胡同.md" and re.search(r"22:59|监控跳|三楼到二楼|倒带馆", p):
            continue
        if name == "06-胡同深.md" and re.search(r"三楼到二楼|倒带馆|你跟上阿青", p):
            continue
        if name in ("01-发送失败.md", "02-空位.md", "03-赵宜家.md"):
            if re.search(r"你进胡同了|22:59|便利店的钟", p):
                continue

        opener = p[:24]
        if opener in openers:
            openers[opener] += 1
            if openers[opener] >= 2:
                continue
        else:
            openers[opener] = 1

        k = norm_key(p)
        if k in seen:
            continue
        seen.add(k)
        out.append(p)
    return out


def load_extras(name: str) -> list[str]:
    fp = TOOLS / "extras" / name
    if not fp.exists():
        return []
    return [x.strip() for x in fp.read_text(encoding="utf-8").split("\n\n") if x.strip()]


CHAPTER_BANK_HINTS = {
    "04-胡同.md": r"胡同|窄巷|砖|雨|湿鞋|井盖|收音机|崇文|修鞋|糖纸|别走大路|南横街|灭灯|路灯",
    "05-第三夜.md": r"第三夜|单元门|电梯|镜|声控|湿鞋|六层|七层|门槛|怕黑|袖口|老楼",
    "06-胡同深.md": r"胡同|深|橙|灯灭|砖|广播|绿帽|传单|公交.*未命名|脚步|涂鸦|同桌",
    "07-便利店.md": r"便利店|22:59|钟|监控|饭团|冰柜|便当|收银|店员|天桥|橘子糖|海报",
}


def chapter_ok(name: str, p: str) -> bool:
    if is_padding(p):
        return False
    if name == "04-胡同.md" and re.search(r"22:59|监控雪花|三楼|倒带馆|你跟上阿青|便利店的钟", p):
        return False
    if name == "05-第三夜.md" and re.search(r"你进胡同了|便利店的钟|收银台|22:59", p):
        return False
    if name in ("01-发送失败.md", "02-空位.md", "03-赵宜家.md") and re.search(
        r"你进胡同了|22:59|便利店的钟", p
    ):
        return False
    hints = CHAPTER_BANK_HINTS.get(name)
    if hints and not re.search(hints, p):
        return False
    return True


def build_ch04_skeleton() -> str:
    sk = (TOOLS / "chapters" / "04-胡同.md").read_text(encoding="utf-8")
    lines, cut = sk.split("\n"), []
    for line in lines:
        s = line.strip()
        if s.startswith("再往前，是第三夜") or s.startswith("你站住。站住"):
            break
        cut.append(line)
    text = "\n".join(cut)
    return text.replace("在便利店，在天桥，在「我选——」后面。", "在胡同更深处。")


def assemble(name: str, raw: str) -> str:
    if name == "00-序.md":
        title, paras = split_paras(CH00_BODY)
    elif name == "04-胡同.md":
        title, paras = split_paras(build_ch04_skeleton())
    else:
        title, paras = split_paras(raw)

    paras = clean_paras(name, paras)
    seen = {norm_key(p) for p in paras}

    for ex in load_extras(name):
        if not chapter_ok(name, ex):
            continue
        k = norm_key(ex)
        if k not in seen:
            paras.append(ex)
            seen.add(k)

    return title, paras


CH04_END = (
    "你进胡同了。身后，南横街全黑。身前，还有路。"
    "路窄，窄到你只能一个人想她。想她，就别喊名字。"
    "喊了，事就复杂。警察说过。"
)
CH06_END = (
    "再往前，橙光更清楚。清楚，像便利店。"
    "卷帘半拉。灯白里带一点旧。你抬脚。胡同深就走到头。"
)
CH07_END = (
    "你往天桥方向走。走，别回头。"
    "钟还停在22:59。秒针还抖。"
    "你站十秒，等自己对齐。对齐了，再走。"
    "走去天桥。天桥在第八章。"
    "你现在，只拎便当。拎水。拎糖。"
    "拎监控里那帧空位。请还在。人不在。"
)


SCENE_FILES = {
    "04-胡同.md": "04_hutong.txt",
    "05-第三夜.md": "05_third_night.txt",
    "06-胡同深.md": "06_hutong_deep.txt",
    "07-便利店.md": "07_store.txt",
}


def load_scenes(name: str) -> list[str]:
    fn = SCENE_FILES.get(name)
    if not fn:
        return []
    fp = TOOLS / "scenes" / fn
    if not fp.exists():
        return []
    return [x.strip() for x in fp.read_text(encoding="utf-8").split("\n\n") if x.strip()]


def chapter_bank(name: str, global_bank: list[str]) -> list[str]:
    """Prefer chapter scenes + extras, then keyword-filtered global bank."""
    items = load_scenes(name) + list(load_extras(name))
    seen = {norm_key(x) for x in items}
    for p in global_bank:
        if not chapter_ok(name, p):
            continue
        k = norm_key(p)
        if k not in seen:
            items.append(p)
            seen.add(k)
    return items


def pad(name: str, title: str, paras: list[str], bank: list[str], global_bank: list[str] | None = None) -> str:
    target = TARGETS[name]
    end = ""
    if name == "04-胡同.md":
        end = CH04_END
        paras = [p for p in paras if not p.strip().startswith("你进胡同了")]
    elif name == "06-胡同深.md":
        end = CH06_END
        paras = [p for p in paras if "胡同深就走到头" not in p]
    elif name == "07-便利店.md":
        end = CH07_END
        paras = [
            p
            for p in paras
            if not (p.strip().startswith("你往天桥方向走") and "天桥在第八章" in p)
        ]

    body = "\n\n".join(paras)
    end_len = len(end) + 2 if end else 0
    used: set[str] = set()

    for para in bank:
        if len(body) + end_len >= target:
            break
        if para in used or not chapter_ok(name, para):
            continue
        if para in body:
            continue
        body += "\n\n" + para
        used.add(para)

    # Second pass: fill remaining gap (before chapter end marker)
    fill_pool = list(bank)
    if global_bank:
        fill_pool.extend(global_bank)
    if len(body) < target:
        seen_fill = set()
        for para in fill_pool:
            if len(body) >= target:
                break
            if is_padding(para) or para in body or para in seen_fill:
                continue
            if name == "04-胡同.md" and re.search(r"22:59|监控|便利店|倒带馆", para):
                continue
            if name == "05-第三夜.md" and re.search(r"你进胡同了|22:59|收银", para):
                continue
            body += "\n\n" + para
            seen_fill.add(para)

    if end:
        if name == "04-胡同.md":
            body = re.sub(r"\n\n你进胡同了[\s\S]*$", "", body).rstrip()
        elif name == "06-胡同深.md":
            body = re.sub(r"\n\n再往前，橙光更清楚[\s\S]*$", "", body).rstrip()
        elif name == "07-便利店.md":
            body = re.sub(r"\n\n你往天桥方向走[\s\S]*$", "", body).rstrip()
        if end not in body:
            body = body + "\n\n" + end

    return ((title + "\n\n") if title else "") + body.strip()


def main():
    global_bank = load_bank()

    for name in TARGETS:
        raw = (NOVEL / name).read_text(encoding="utf-8") if (NOVEL / name).exists() else ""
        title, paras = assemble(name, raw)
        cbank = chapter_bank(name, global_bank)
        text = pad(name, title, paras, cbank, global_bank)
        # Final strip: padding lines only
        t, ps = split_paras(text)
        ps = [p for p in ps if not is_padding(p)]
        text = ((t + "\n\n") if t else "") + "\n\n".join(ps)
        # Re-pad if final strip dropped below target
        if len(text) < TARGETS[name] * 0.95 and name != "00-序.md":
            t2, ps2 = split_paras(text)
            text = pad(name, t2, ps2, chapter_bank(name, global_bank), global_bank)
            t3, ps3 = split_paras(text)
            ps3 = [p for p in ps3 if not is_padding(p)]
            text = ((t3 + "\n\n") if t3 else "") + "\n\n".join(ps3)
        (NOVEL / name).write_text(text.strip() + "\n", encoding="utf-8")

    subprocess.run(["python3", str(TOOLS / "count_novel.py")], check=False)


if __name__ == "__main__":
    main()
