#!/usr/bin/env python3
"""Final expansion: unique prose only, no loop-fill."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
TOOLS = Path(__file__).resolve().parent


def load_paras(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    return [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]


def md5(s: str) -> str:
    return hashlib.md5(re.sub(r"\s+", "", s).encode()).hexdigest()


def existing_hashes(text: str) -> set[str]:
    hs: set[str] = set()
    for block in re.split(r"\n\n+", text.strip()):
        block = block.strip()
        if block and not block.startswith("#"):
            hs.add(md5(block))
    return hs


def trim_at_marker(text: str, marker: str) -> str:
    idx = text.find(marker)
    if idx >= 0:
        return text[: idx + len(marker)] + "\n"
    return text


def add_paras(text: str, paras: list[str], before: str | None = None) -> str:
    seen = existing_hashes(text)
    new: list[str] = []
    for p in paras:
        h = md5(p)
        if h not in seen:
            new.append(p)
            seen.add(h)
    if not new:
        return text
    block = "\n\n".join(new)
    if before and before in text:
        idx = text.rfind(before)
        return text[:idx].rstrip() + "\n\n" + block + "\n\n" + text[idx:]
    return text.rstrip() + "\n\n" + block + "\n"


def pad_to(text: str, target: int, bank: list[str], before: str | None = None) -> str:
    seen = existing_hashes(text)
    queue = [p for p in bank if md5(p) not in seen]
    i = 0
    while len(text) < target and i < len(queue):
        p = queue[i]
        text = add_paras(text, [p], before)
        i += 1
    return text


TARGETS = {
    "00-序.md": 7000,
    "01-发送失败.md": 20950,
    "15-停止.md": 20850,
    "16-爬回.md": 20850,
    "17-小的路.md": 20850,
    "18-漏句.md": 20750,
}


def main() -> None:
    # restore ch01 from git if needed
    spec = importlib.util.spec_from_file_location("clean", TOOLS / "clean_novel_ai.py")
    clean_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clean_mod)

    ch01 = ROOT / "01-发送失败.md"
    if len(ch01.read_text(encoding="utf-8")) < 15000:
        import subprocess as sp
        raw = sp.check_output(["git", "show", "HEAD:./docs/novel/01-发送失败.md"], text=True, cwd=ROOT.parent)
        ch01.write_text(clean_mod.clean_text(raw), encoding="utf-8")

    # trim 17/18 at 够了。
    for fname in ("17-小的路.md", "18-漏句.md"):
        p = ROOT / fname
        p.write_text(trim_at_marker(p.read_text(encoding="utf-8"), "够了。"), encoding="utf-8")

    # trim 16 template garbage
    ch16 = ROOT / "16-爬回.md"
    t16 = ch16.read_text(encoding="utf-8")
    marker = "在第三排靠窗，橙色便利贴还留着，她抓你袖口，不是告白是确认，赵宜齐刘海"
    if marker in t16:
        ch16.write_text(t16[: t16.find(marker)].rstrip() + "\n", encoding="utf-8")

    banks = {
        "00-序.md": load_paras(TOOLS / "extras" / "handwritten" / "00-序.md"),
        "01-发送失败.md": load_paras(TOOLS / "extras" / "01-发送失败.md"),
        "15-停止.md": load_paras(TOOLS / "extras" / "15-停止.md"),
        "16-爬回.md": load_paras(TOOLS / "extras" / "handwritten" / "16-爬回.md"),
        "17-小的路.md": load_paras(TOOLS / "extras" / "handwritten" / "17-小的路.md"),
        "18-漏句.md": load_paras(TOOLS / "extras" / "handwritten" / "18-漏句.md"),
    }

    # extra unique paras inline
    banks["00-序.md"] += [
        "序章补记：你后来把 23:17 写在便利贴背面，背面原本是你乱算的草稿，你写她在这分钟发信，我在这分钟睡还是醒，你不确定，不确定就留着，留着夜里还有事要做，你打开窗，雨声灌进来，二环的车流像河，你对着空房间说我收到了，没人应，只有雨，你把窗关上，没关严，留一条缝，缝很窄，像后来停止键留的那种，发送失败不是句号，是逗号，逗号后面是空位，是赵宜家，是胡同，是天桥，是西单，是按停止，是爬回，是小的路，是漏句，是够了。",
    ]
    banks["01-发送失败.md"] += [
        "发送失败后的第一个课间，你把手机放到赵宜空位上，屏幕朝下，像让她自己看，早读铃响，班主任进来，他看空位，看你，看手机，他没说把手机拿回去，他只说赵宜家里请假，你点头，你懂，能写进请假条的，他先信，别的，晚上再说，晚上再说这四个字像一张没写地址的便条，塞进口袋，硌着，硌着你就还不能把结皮倒掉，倒掉像擦掉她，请还在，人不在，请还在，你就还不能把结皮倒掉。",
    ]

    before_map = {
        "17-小的路.md": "够了。",
        "18-漏句.md": "够了。",
    }

    for fname, target in TARGETS.items():
        path = ROOT / fname
        text = path.read_text(encoding="utf-8")
        text = pad_to(text, target, banks.get(fname, []), before_map.get(fname))
        path.write_text(text, encoding="utf-8")
        print(f"pre-clean {fname}: {len(text)}")

    # clean all
    for path in sorted(ROOT.glob("[0-9]*.md")):
        raw = path.read_text(encoding="utf-8")
        cleaned = clean_mod.clean_text(raw)
        path.write_text(cleaned, encoding="utf-8")

    subprocess.run(["python3", str(TOOLS / "count_novel.py")], check=True)


if __name__ == "__main__":
    main()
