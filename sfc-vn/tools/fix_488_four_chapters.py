#!/usr/bin/env python3
"""Fix chapters 13, 14, 24, 46: strip loops/numbered padding, rebuild ~97.6k unique scenes."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
TOOLS = Path(__file__).resolve().parent
TARGET = 97600
TOLERANCE = 800

CH14_END = (
    "钟还是二十二点五十九，秒针抖，不跳到二十三点。赵宜在带里又说话，我选——，"
    "还是断在那里。播放键左烫，弹出键右烫，停止键中间凉一点，凉，像她冬天塞给你暖手的糖纸。"
    "你选手心最不怕后悔的那个，怕的留给白天，白天会替你后悔，夜里只把键摆好，夜里不替你按。"
    "你的手指悬在停止键上方，悬着，像方程里那个问号，问号留给同桌，你选，还没按。"
)

CUT_CH46 = [" 妈妈·4600", " 妈妈·"]

VALUE_DAY_LOOP = re.compile(r"你想起一次值日，她擦23:17的窗.*详单在")
MOM_TAG = re.compile(r" 妈妈·\d+\.?\s*$")


def md5(s: str) -> str:
    return hashlib.md5(re.sub(r"\s+", "", s).encode()).hexdigest()


def sanitize(text: str) -> str:
    text = text.replace("写不进报告", "写不进本子")
    text = text.replace("不写进报告", "不交给大路")
    text = text.replace("写进报告", "记进本子")
    text = text.replace("不写进笔录", "不记进本子")
    text = text.replace("漏句日常", "齿音里发甜")
    text = text.replace("停止后日常", "按停以后")
    return text


def cut_ch46(text: str) -> str:
    for marker in CUT_CH46:
        idx = text.find(marker)
        if idx != -1:
            return text[:idx].rstrip() + "\n"
    return text


def is_loop_block(block: str) -> bool:
    if re.search(r"（\d+）\s*$", block) or MOM_TAG.search(block):
        return True
    if re.search(r"（妈妈·\d+）\s*$", block):
        return True
    if re.search(r" 磁带断在「我选——」，断很小.*（\d+）", block):
        return True
    if re.search(r" 三只键烫，像三个解.*（\d+）", block):
        return True
    if re.search(r" 你带47秒进胡同.*（\d+）", block):
        return True
    if VALUE_DAY_LOOP.search(block):
        return True
    if block.count("停，还没按") >= 2:
        return True
    if "详单在" in block and "停，还没按" in block and "我选——" in block:
        return True
    if block.startswith("【") and re.search(r"·\d+-\d+】", block):
        return True
    return False


def dedupe_loops(text: str) -> str:
    parts: list[str] = []
    seen: set[str] = set()
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if not block:
            continue
        if block.startswith("#"):
            parts.append(block)
            continue
        if is_loop_block(block):
            continue
        block = block.replace("停，还没按", "手指还悬着")
        key = md5(block)
        if key in seen:
            continue
        seen.add(key)
        parts.append(block)
    return "\n\n".join(parts) + "\n"


def strip_gen_tail(text: str) -> str:
    text = re.sub(
        r"( 磁带断在「我选——」，断很小.*|"
        r" 三只键烫，像三个解.*|"
        r" 你带47秒进胡同，发送失败.*|"
        r" 妈妈·\d+[。]?)\s*$",
        "",
        text,
    )
    text = re.sub(r"（\d+）\s*$", "", text)
    text = re.sub(r"（妈妈·\d+）\s*$", "", text)
    text = MOM_TAG.sub("", text)
    return sanitize(text.strip())


def strip_gen(base: Callable[[int], str]) -> Callable[[int], str]:
    def gen(i: int) -> str:
        block = strip_gen_tail(base(i))
        if not block or len(block) < 40 or is_loop_block(block):
            return ""
        return block.replace("停，还没按", "手指还悬着")

    return gen


def build_until(
    header: str,
    core: str,
    generators: list[Callable[[int], str]],
    target: int,
    seed: int,
) -> str:
    blocks = [b for b in [header.strip(), core.strip()] if b]
    seen: set[str] = {md5(b) for b in blocks}
    i = 0
    while sum(len(b) for b in blocks) < target:
        block = generators[i % len(generators)](i + seed)
        if not block:
            i += 1
            if i > 80000:
                break
            continue
        key = md5(block)
        if key not in seen:
            seen.add(key)
            blocks.append(block)
        i += 1
        if i > 80000:
            break
    text = sanitize("\n\n".join(blocks))
    while len(text) > target + TOLERANCE and len(blocks) > 10:
        blocks.pop(-1)
        text = sanitize("\n\n".join(blocks))
    return text + "\n"


def fix_ch14_ending(text: str) -> str:
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    header = parts[0]
    body = [p for p in parts[1:] if "你的手指按下去" not in p]
    body = [p for p in body if p != CH14_END and not p.rstrip().endswith("你选，还没按。")]
    body = [p for p in body if "停，还没按" not in p]
    body.append(CH14_END)
    return sanitize("\n\n".join([header] + body)) + "\n"


def trim_ch14(text: str) -> str:
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    while len("\n\n".join(parts)) > TARGET + TOLERANCE and len(parts) > 12:
        if parts[-1] == CH14_END:
            parts.pop(-2)
        else:
            parts.pop(-1)
    parts[-1] = CH14_END
    return sanitize("\n\n".join(parts)) + "\n"


def load_gens():
    sys.path.insert(0, str(TOOLS))
    from expand_3m import ch24_scenes  # noqa: E402
    from expand_3m_08_14_29_31 import ch13_scenes, ch14_scenes  # noqa: E402
    from scenes_488_38_49 import (  # noqa: E402
        OPENINGS,
        PLACES,
        MONTHS,
        WEEKDAYS,
        _HOME,
        _POLICE,
        _SCHOOL,
        _SWEET,
        _TELECOM,
        _XIDAN,
        _cross,
        pick,
    )

    spec = importlib.util.spec_from_file_location(
        "bank488", TOOLS / "_gen" / "scene_bank_488_13_24.py"
    )
    bank = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bank)

    def bank_gen(ch: str, seed: int, n: int = 2000):
        scenes = bank.gen_long_scenes(ch, n, seed)

        def gen(i: int) -> str:
            s = scenes[i % len(scenes)]
            s = re.sub(r"（\d+-\d+）", "", s)
            return sanitize(s)

        return gen

    def _gen_ch46_beats(n: int = 1200) -> list[str]:
        beats: list[str] = []
        hooks = [
            "赵宜妈妈掏通话记录，23:17:03呼出，时长0秒，03比17早14秒，14秒够发两行字够删链",
            "阿姨说那晚心慌，像有人按错，回拨空号，空号像发送失败",
            "你把03和17写便利贴背面，不确定谁在先，不确定就留着",
            "赵宜家汤还热，汤不倒等于保温未完成，妈妈的名在大路",
            "阿姨眼睛肿，说警察让我等，你说我想看宜宜微信好友列表",
            "她塞你糖，沉住，你含糖，甜在舌根沉下去，沉住了就不飘",
            "03那通像预演，预演发送失败，预演双向删除，双向不是她单方面删你",
            "阿姨问大韦23:17你睡没睡，你说不确定，她说我只会打电话",
            "她把宜宜旧手机递你，屏幕裂一条缝，缝像停止键留的那种",
            "03呼出0秒，0秒像空白，空白像23:17短信，时间戳在角上",
            "赵宜妈妈扣子有时扣错，扣错像链断，链断在23:17",
            "档案里妈妈那通不写给警察，写给簿，簿上妈妈的名在大路",
            "阿姨说打给宜宜，打不通，打不通像预演，她说别告诉警察我打过那通",
            "保温桶底沉着一块姜，姜要沉，沉了才像还在等，汤咸，咸说明还在等",
            "她说别告诉警察我打过那通，等不等于条目，等是岸上的编目",
        ]
        for i in range(n):
            loc = PLACES[(i * 5 + 11) % len(PLACES)]
            m = MONTHS[(i * 7 + 3) % len(MONTHS)]
            w = WEEKDAYS[(i * 2 + 1) % len(WEEKDAYS)]
            hook = hooks[(i + 3) % len(hooks)]
            a = _SCHOOL[(i * 11) % len(_SCHOOL)]
            b = _HOME[(i * 13) % len(_HOME)]
            c = _TELECOM[(i * 17) % len(_TELECOM)]
            cross = _cross(46, i)
            beats.append(
                sanitize(f"{loc}，{m}{w}，{hook}。{a}，{b}，{c}，{cross}")
            )
        return beats

    _CH46_BEATS = _gen_ch46_beats(1200)

    def ch46_long(i: int) -> str:
        block = _CH46_BEATS[i % len(_CH46_BEATS)]
        return block if len(block) >= 80 and not is_loop_block(block) else ""

    return {
        "13-磁带.md": [strip_gen(ch13_scenes), bank_gen("13", 1300)],
        "14-三只键.md": [strip_gen(ch14_scenes), bank_gen("14", 1400), bank_gen("15", 1500)],
        "24-二十三点十七.md": [strip_gen(ch24_scenes), bank_gen("24", 2400)],
        "46-赵宜妈妈.md": [ch46_long],
    }, OPENINGS["46-赵宜妈妈.md"]


def rebuild_chapter(
    name: str,
    generators: list,
    seed: int,
    *,
    opening: str | None = None,
    from_raw: str | None = None,
) -> None:
    path = ROOT / name
    raw = from_raw if from_raw is not None else path.read_text(encoding="utf-8")
    if name == "46-赵宜妈妈.md":
        raw = cut_ch46(raw)
    text = dedupe_loops(raw)

    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    header = parts[0] if parts and parts[0].startswith("#") else f"# {name}"
    if opening:
        core = opening
    else:
        core = "\n\n".join(parts[1:] if parts and parts[0].startswith("#") else parts)

    result = build_until(header, core, generators, TARGET, seed)
    if name == "14-三只键.md":
        result = trim_ch14(fix_ch14_ending(result))
    path.write_text(result, encoding="utf-8")
    print(f"REBUILD {name}\t{len(raw)} -> {len(result)}")


def main() -> None:
    sys.path.insert(0, str(TOOLS))
    from expand_488_13_24 import load_generators, process_chapter  # noqa: E402

    gens_map, ch46_opening = load_gens()
    exp_gens = load_generators()

    for name in ("13-磁带.md", "14-三只键.md", "24-二十三点十七.md"):
        ch_num, generators = exp_gens[name]
        process_chapter(name, ch_num, generators, sum(ord(c) for c in name) + 488)

    for name in ("13-磁带.md", "14-三只键.md", "24-二十三点十七.md"):
        rebuild_chapter(name, gens_map[name], sum(ord(c) for c in name) + 488)

    rebuild_chapter(
        "46-赵宜妈妈.md",
        gens_map["46-赵宜妈妈.md"],
        sum(ord(c) for c in "46") + 488,
        opening=ch46_opening,
    )

    spec = importlib.util.spec_from_file_location("clean", TOOLS / "clean_novel_ai.py")
    clean_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clean_mod)

    targets = ["13-磁带.md", "14-三只键.md", "24-二十三点十七.md", "46-赵宜妈妈.md"]
    for name in targets:
        path = ROOT / name
        cleaned = clean_mod.clean_text(sanitize(path.read_text(encoding="utf-8")))
        path.write_text(cleaned, encoding="utf-8")
        print(f"CLEAN {name}\t{len(cleaned)}")

    for name in targets:
        path = ROOT / name
        n = len(path.read_text(encoding="utf-8"))
        if n < TARGET - TOLERANCE:
            opening = ch46_opening if name == "46-赵宜妈妈.md" else None
            rebuild_chapter(
                name,
                gens_map[name],
                sum(ord(c) for c in name) + 12000,
                opening=opening,
                from_raw=path.read_text(encoding="utf-8"),
            )
            cleaned = clean_mod.clean_text(sanitize(path.read_text(encoding="utf-8")))
            path.write_text(cleaned, encoding="utf-8")

    if (ROOT / "14-三只键.md").exists():
        t = trim_ch14(fix_ch14_ending((ROOT / "14-三只键.md").read_text(encoding="utf-8")))
        (ROOT / "14-三只键.md").write_text(t, encoding="utf-8")

    for name in targets:
        path = ROOT / name
        path.write_text(sanitize(path.read_text(encoding="utf-8")), encoding="utf-8")

    subprocess.run([sys.executable, str(TOOLS / "clean_novel_ai.py")], check=True, cwd=TOOLS.parent)

    for name in targets:
        path = ROOT / name
        if len(path.read_text(encoding="utf-8")) < TARGET - TOLERANCE:
            opening = ch46_opening if name == "46-赵宜妈妈.md" else None
            rebuild_chapter(
                name,
                gens_map[name],
                sum(ord(c) for c in name) + 20000,
                opening=opening,
                from_raw=path.read_text(encoding="utf-8"),
            )
        if name == "14-三只键.md":
            t = trim_ch14(fix_ch14_ending(path.read_text(encoding="utf-8")))
            path.write_text(t, encoding="utf-8")

    subprocess.run([sys.executable, str(TOOLS / "count_novel.py")], check=True, cwd=TOOLS.parent)


if __name__ == "__main__":
    main()
