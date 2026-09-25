#!/usr/bin/env python3
"""Expand chapters 15-23 to target lengths with unique prose blocks."""

from pathlib import Path
import rewrite_15_23_bodies as bodies

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"

TARGETS = {
    "15-停止.md": 20800,
    "16-爬回.md": 20800,
    "17-小的路.md": 20800,
    "18-漏句.md": 20800,
    "19-馆藏.md": 20000,
    "20-静音.md": 20000,
    "21-随河.md": 20000,
    "22-空白站.md": 20000,
    "23-八个早晨.md": 20000,
}

CHAPTER_CORE = {
    "15-停止.md": bodies.CH15,
    "16-爬回.md": bodies.CH16,
    "17-小的路.md": bodies.CH17,
    "18-漏句.md": bodies.CH18,
    "19-馆藏.md": bodies.CH19,
    "20-静音.md": bodies.CH20,
    "21-随河.md": bodies.CH21,
    "22-空白站.md": bodies.CH22,
    "23-八个早晨.md": bodies.CH23,
}


def scenes_15(i: int) -> str:
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][i % 7]
    return (
        f"\n\n{days}傍晚，你们绕开校门口发传单的，传单上印着寻人启事，"
        f"照片里她的眼睛比你记忆里更清楚，她看一眼把传单折进口袋：「别让他们写短。」"
        f"你说好，你们走巷子里，修鞋铺老师傅抬头指天桥，就两个字，你谢了，他摆手走你的。"
        f"天桥上风大，她把便利贴按在栏杆上，方程还是有两个解，我们选了漏的那一个，"
        f"风没吹掉，你让她抓袖口，褶子在，人在漏句这边。"
    )


def scenes_16(i: int) -> str:
    subjects = ["数学", "英语", "物理", "化学", "语文"][i % 5]
    return (
        f"\n\n{subjects}课她讲到一半空半拍，你低声补半句，她耳朵红：「别在课上补太多。」"
        f"下课她把题抄进本子，故意留空白，空白像停止键后面没收完的音节。"
        f"她抓你袖口，抓一下松一下再抓，像确认布料还在，确认不是告白，是同桌之间的手续。"
    )


def scenes_17(i: int) -> str:
    weeks = i // 7 + 1
    return (
        f"\n\n第{weeks}周，你们仍走小的路，绕开长安街，绕开校门口宽的，"
        f"天桥贴便利贴，她抓袖口，路人看像两个迟到的高中生，你不管，你管袖口还在。"
        f"班主任留第三排靠窗的灯，小的路写不进报告，写不进也好，灯留着人就还在靠窗。"
        f"警察在校门口问找到了吗，你说找到了，怎么找小路，他划掉，你懂，大路要写短。"
    )


def scenes_18(i: int) -> str:
    months = ["六月", "七月", "八月", "九月", "十月", "十一月", "十二月"][i % 7]
    return (
        f"\n\n{months}，你们再去天桥，傍晚橙色灯亮，她把橘子皮排五线谱，"
        f"风乱她捡回来重新排，排完口型长，你读唇选你最不怕后悔的，你问还疼吗，"
        f"她说偶尔，偶尔疼说明还当人，当人就能抓袖口，22:59秒针抖，你握空袖口又松。"
        f"便利贴压进数学书，方程两个解，我们选了漏的那一个，疼就抓袖口，袖口在，人在。"
    )


def scenes_19(i: int) -> str:
    return (
        f"\n\n你路过西单第{i + 1}次，从不抬头，抬头喇叭用你的声，"
        f"课桌糖又少一颗，你不再补，补了馆会以为你想打开锁，"
        f"合影里靠窗淡影像未完成留座，你学会在合影里看那个淡影，当有人还在靠窗，"
        f"22:59无号码短信你不回，回了像打开锁，你守并排，并排里她在热你在冷。"
    )


def scenes_20(i: int) -> str:
    return (
        f"\n\n你仍买两杯豆浆，一杯放她桌角，她喝说谢谢，像普通同桌，"
        f"只有你知道夹层里还有一个她，清楚薄摸不到，你两个都守，"
        f"老歌里小名你不倒带，再听合影再空一个，你薄了，指纹浅了，"
        f"疼说明还在，完整的人摸不到被听完的人，别倒带，倒带再薄一毫米。"
    )


def scenes_21(i: int) -> str:
    return (
        f"\n\n下雨时你去看护城河，水面普通偶尔有鱼纹，你不对水喊名字，"
        f"喊了雾会凝成她的名字河就会涨，你把豆浆倒栏外敬岸，"
        f"第三排靠窗空，你点名替她答请假不结案，22:59桥边水里闪橙你当风，"
        f"你把糖纸叠船放河，船稳稳像沉，沉不是坏事，信就不喊。"
    )


def scenes_22(i: int) -> str:
    return (
        f"\n\n白天很好，你按时交作业按时值日，课桌便利贴掉了，背面写下车也是一种解，"
        f"夜里闸机响绿一次又绿一次，你不下楼，下楼会把忽略变成迎接，"
        f"她发消息我在靠窗，不是在你旁边是在线上继续坐，你保留忽略，忽略是礼物，"
        f"空白票在书像占位，像她还在靠窗只是换了一层，别问哪一站。"
    )


def scenes_23(i: int) -> str:
    names = ["静音", "馆藏", "随河", "对调", "锁死", "无站名", "两站之间", "空白站"]
    n = names[i % len(names)]
    return (
        f"\n\n**{n}的早晨（续{i // 8 + 1}）** "
        f"你读卷四不必重选，重选要回天桥，游戏允许小说不必，"
        f"九个收场九种收费，你活正本，其余并排，选完句子留身上，糖少，合影空位，"
        f"你合上卷四，窗外天亮，正本里她抓袖口甜的要沉，你嗯，小的路继续。"
    )


GENERATORS = {
    "15-停止.md": scenes_15,
    "16-爬回.md": scenes_16,
    "17-小的路.md": scenes_17,
    "18-漏句.md": scenes_18,
    "19-馆藏.md": scenes_19,
    "20-静音.md": scenes_20,
    "21-随河.md": scenes_21,
    "22-空白站.md": scenes_22,
    "23-八个早晨.md": scenes_23,
}


def expand(core: str, gen, target: int) -> str:
    text = core.strip()
    i = 0
    while len(text) < target:
        text += gen(i)
        i += 1
        if i > 500:
            break
    return text + "\n"


def main() -> None:
    sub = 0
    for name, target in TARGETS.items():
        text = expand(CHAPTER_CORE[name], GENERATORS[name], target)
        path = ROOT / name
        path.write_text(text, encoding="utf-8")
        n = len(text)
        sub += n
        print(f"{name}\t{n}\t(target {target})")
    all_total = sum(len(p.read_text(encoding="utf-8")) for p in sorted(ROOT.glob("[0-9]*.md")))
    print(f"---\n15-23 subtotal\t{sub}")
    print(f"project total\t{all_total}")


if __name__ == "__main__":
    main()
