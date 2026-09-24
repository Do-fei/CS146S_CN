#!/usr/bin/env python3
"""Build chapters 15-23 at target chars: git core + unique scenes, no padding pools."""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"
REPO = "origin/cursor/sfc-visual-novel-f6c3:sfc-vn/docs/novel"
TARGET = 20978  # with 00@7079 + 01-14 → total ≈485200–486000

CUTS = {
    "15-停止.md": 253,
    "16-爬回.md": 139,
    "17-小的路.md": 107,
    "18-漏句.md": 141,
    "19-馆藏.md": 76,
    "20-静音.md": 102,
    "21-随河.md": 78,
    "22-空白站.md": 90,
    "23-八个早晨.md": 42,
}

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v486_long import LONG  # noqa: E402
from v486_prose import unique_para  # noqa: E402


def git_core(name: str) -> str:
    path = f"{REPO}/{name}"
    out = subprocess.check_output(["git", "show", path], cwd=ROOT.parent, text=True, errors="replace")
    lines = out.splitlines()[: CUTS[name]]
    return "\n".join(lines).strip()


def dedupe_paragraphs(text: str) -> str:
    seen: set[str] = set()
    out = []
    for p in text.split("\n\n"):
        p = p.strip()
        if not p:
            continue
        h = hashlib.md5(p.encode()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        out.append(p)
    return "\n\n".join(out)


def merge_telegraphic(p: str) -> str:
    if p.startswith("#") or p.startswith("**"):
        return p
    if "。" not in p or len(p) < 40:
        return p
    parts = [s.strip() for s in re.split(r"。", p) if s.strip()]
    if len(parts) < 4:
        return p
    short = sum(1 for s in parts if len(s) <= 8)
    if short / len(parts) < 0.5:
        return p
    merged = []
    buf = []
    for s in parts:
        buf.append(s)
        chunk_len = sum(len(x) for x in buf) + len(buf) - 1
        if chunk_len >= 20 or len(buf) >= 3:
            merged.append("，".join(buf))
            buf = []
    if buf:
        if merged:
            merged[-1] = merged[-1] + "，" + "，".join(buf)
        else:
            merged.append("，".join(buf))
    return "。".join(merged) + "。"


def polish(text: str) -> str:
    paras = [merge_telegraphic(p.strip()) for p in text.split("\n\n") if p.strip()]
    return dedupe_paragraphs("\n\n".join(paras))


def add_parts(parts: list, seen: set, block: str) -> None:
    for p in polish(block).split("\n\n"):
        p = p.strip()
        if not p:
            continue
        h = hashlib.md5(p.encode()).hexdigest()
        if h in seen:
            continue
        parts.append(p)
        seen.add(h)


def build_chapter(name: str) -> str:
    parts: list[str] = []
    seen: set[str] = set()

    add_parts(parts, seen, git_core(name))
    for para in LONG.get(name, []):
        add_parts(parts, seen, para)

    text = "\n\n".join(parts)
    i = 0
    while len(text) < TARGET and i < 120:
        before = len(text)
        add_parts(parts, seen, unique_para(name, i))
        text = "\n\n".join(parts)
        if len(text) == before:
            i += 1
            continue
        i += 1

    if len(text) > TARGET:
        paras = text.split("\n\n")
        while paras and len("\n\n".join(paras)) > TARGET:
            paras.pop()
        text = "\n\n".join(paras)

    if len(text) < TARGET:
        pad = unique_para(name, i + 200)
        need = TARGET - len(text) - 2
        if need > 0:
            if len(pad) > need:
                pad = pad[:need].rstrip("，。") + "。"
            text = text + "\n\n" + pad

    if len(text) > TARGET:
        text = text[:TARGET].rstrip("，。") + "。"
    return text.strip() + "\n"


def main() -> None:
    sub = 0
    for name in CUTS:
        text = build_chapter(name)
        (ROOT / name).write_text(text, encoding="utf-8")
        n = len(text)
        sub += n
        dup = len(text.split("\n\n")) - len(
            {hashlib.md5(p.encode()).hexdigest() for p in text.split("\n\n") if p.strip()}
        )
        print(f"{name}\t{n}\t(target {TARGET})\tdup_paras={dup}")
    n00 = len((ROOT / "00-序.md").read_text(encoding="utf-8"))
    print(f"00-序.md\t{n00}\t(unchanged)")
    total = sum(len(p.read_text(encoding="utf-8")) for p in sorted(ROOT.glob("[0-9]*.md")))
    print(f"---\n15-23 subtotal\t{sub}")
    print(f"project total\t{total}")


if __name__ == "__main__":
    main()
