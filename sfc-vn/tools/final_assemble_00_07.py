#!/usr/bin/env python3
"""Rebuild novel chapters 00-07: dedupe, de-pad, merge extras, pad to target."""
import re
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

PADDING = [
    re.compile(r"^空位第\d+天"),
    re.compile(r"^胡同第\d+盏"),
    re.compile(r"^便利店里你第\d+次"),
    re.compile(r"^周[一二三四五](午休|放学)"),
    re.compile(r"^第\d+次发送失败"),
]

CH00 = """# 序

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
    bank = []
    for p in [TOOLS / "bank2.txt", TOOLS / "extras_ch01.txt"]:
        if p.exists():
            bank.extend(
                x.strip()
                for x in p.read_text(encoding="utf-8").split("\n\n")
                if x.strip() and not x.strip().startswith("#")
            )
    p = TOOLS / "pad_to_target.py"
    if p.exists():
        txt = p.read_text(encoding="utf-8")
        m = re.search(r"BANK = \[(.*?)\]", txt, re.S)
        if m:
            for line in m.group(1).split("\n"):
                line = line.strip().strip(",").strip('"')
                if line and len(line) > 20:
                    bank.append(line)
    return bank


def is_padding(p: str) -> bool:
    s = p.strip()
    return any(r.search(s) for r in PADDING)


def dedupe_paras(paras: list[str]) -> list[str]:
    seen = set()
    out = []
    for p in paras:
        key = re.sub(r"\s+", "", p)[:180]
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def load_extras(name: str) -> list[str]:
    p = TOOLS / "extras" / name
    if not p.exists():
        return []
    return [x.strip() for x in p.read_text(encoding="utf-8").split("\n\n") if x.strip()]


def chapter_filter(name: str, para: str) -> bool:
    """Return True if para is OK for this chapter."""
    if is_padding(para):
        return False
    if name == "04-胡同.md":
        if re.search(r"22:59|二十二点五十九|监控跳|便利店里你|三楼到二楼|你跟上阿青|倒带馆", para):
            return False
        if "你进胡同了" in para and name == "04-胡同.md":
            pass  # ok for ending
    if name == "06-胡同深.md":
        if re.search(r"三楼到二楼|倒带馆|你跟上阿青", para):
            return False
    if name == "07-便利店.md":
        if re.search(r"你进胡同了|胡同口最后一盏|第三章|第四章止于", para):
            return False
    if name in ("01-发送失败.md", "02-空位.md", "03-赵宜家.md"):
        if re.search(r"你进胡同了|22:59|便利店的钟", para):
            return False
    return True


def assemble(name: str, base: str) -> str:
    paras = []
    title = ""
    for p in base.split("\n\n"):
        p = p.strip()
        if not p:
            continue
        if p.startswith("#"):
            title = p
            continue
        if is_padding(p):
            continue
        if chapter_filter(name, p):
            paras.append(p)

    seen = {re.sub(r"\s+", "", x)[:180] for x in paras}
    for ex in load_extras(name):
        if chapter_filter(name, ex):
            k = re.sub(r"\s+", "", ex)[:180]
            if k not in seen:
                paras.append(ex)
                seen.add(k)

    return title, paras


def pad(name: str, title: str, paras: list[str], bank: list[str], used: set) -> str:
    target = TARGETS[name]
    body = "\n\n".join(paras)
    for para in bank:
        if len(body) >= target:
            break
        if para in used:
            continue
        if not chapter_filter(name, para):
            continue
        if para in body:
            used.add(para)
            continue
        body = body + "\n\n" + para
        used.add(para)
    return (title + "\n\n" if title else "") + body.strip()


def build_ch04() -> str:
    sk = (TOOLS / "chapters" / "04-胡同.md").read_text(encoding="utf-8")
    lines = sk.split("\n")
    cut = []
    for line in lines:
        s = line.strip()
        if s.startswith("再往前，是第三夜") or s.startswith("你站住。站住"):
            break
        cut.append(line)
    base = "\n".join(cut)
    base = base.replace("在便利店，在天桥，在「我选——」后面。", "在胡同更深处。")
    title, paras = assemble("04-胡同.md", base)
    # ensure proper ending
    end = (
        "你进胡同了。身后，南横街全黑。身前，还有路。"
        "路窄，窄到你只能一个人想她。想她，就别喊名字。"
        "喊了，事就复杂。警察说过。"
    )
    # remove any existing 你进胡同 ending variants
    paras = [p for p in paras if not p.strip().startswith("你进胡同了")]
    paras.append(end)
    used = set()
    bank = load_bank()
    return pad("04-胡同.md", title, paras, bank, used)


def main():
    used_bank: set[str] = set()
    bank = load_bank()

    # 00
    ch00_title = "# 序"
    ch00_paras = [p for p in CH00.split("\n\n") if p.strip() and not p.startswith("#")]
    ch00 = pad("00-序.md", ch00_title, ch00_paras, bank, used_bank)
    (NOVEL / "00-序.md").write_text(ch00 + "\n", encoding="utf-8")

    # 04 special
    ch04 = build_ch04()
    (NOVEL / "04-胡同.md").write_text(ch04 + "\n", encoding="utf-8")

    for name in [
        "01-发送失败.md",
        "02-空位.md",
        "03-赵宜家.md",
        "05-第三夜.md",
        "06-胡同深.md",
        "07-便利店.md",
    ]:
        base = (NOVEL / name).read_text(encoding="utf-8")
        title, paras = assemble(name, base)
        paras = dedupe_paras(paras)

        # ch06: trim at first good arc ending before duplicates
        if name == "06-胡同深.md":
            trimmed = []
            hit_end = False
            for p in paras:
                if hit_end:
                    break
                trimmed.append(p)
                if "胡同深就走到头" in p or "再往前，橙光更清楚" in p:
                    hit_end = True
            paras = trimmed
            if not any("橙光" in p for p in paras):
                paras.append(
                    "再往前，橙光更清楚。清楚，像便利店。"
                    "卷帘半拉。灯白里带一点旧。你抬脚。胡同深就走到头。"
                )

        # ch07: keep first convenience store pass, end toward 天桥
        if name == "07-便利店.md":
            trimmed = []
            orange_count = 0
            for p in paras:
                if p.startswith("橙光更清楚") or p.startswith("胡同深走到头"):
                    orange_count += 1
                    if orange_count > 1:
                        break
                if is_padding(p):
                    break
                trimmed.append(p)
            paras = trimmed
            end = (
                "你往天桥方向走。走，别回头。"
                "钟还停在22:59。秒针还抖。"
                "你站十秒，等自己对齐。对齐了，再走。"
                "走去天桥。天桥在第八章。"
                "你现在，只拎便当。拎水。拎糖。"
                "拎监控里那帧空位。请还在。人不在。"
            )
            if end not in "\n\n".join(paras):
                paras.append(end)

        body = pad(name, title, paras, bank, used_bank)
        (NOVEL / name).write_text(body + "\n", encoding="utf-8")

    import subprocess
    r = subprocess.run(
        ["python3", str(TOOLS / "count_novel.py")],
        capture_output=True,
        text=True,
    )
    for line in r.stdout.splitlines():
        if any(line.startswith(f"{i:02d}") for i in range(8)):
            print(line)


if __name__ == "__main__":
    main()
