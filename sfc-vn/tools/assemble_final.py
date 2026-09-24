#!/usr/bin/env python3
"""Assemble clean chapters 00-07: dedupe, de-AI trim, expand, write."""

import re
from pathlib import Path

NOVEL = Path(__file__).resolve().parents[1] / "docs" / "novel"
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

# Paragraphs that belong in later chapters — strip from 01-07
LATER_SPOILERS = re.compile(
    r"阿青|倒带馆|停止键|三只键|西单停业|跟上阿青|选阿青|透明伞|"
    r"监控跳一帧|22:59|二十二点五十九|天桥写选|食街|三楼|"
    r"你还不按|按了，是后面的章|正本，从发送失败走到这里|"
    r"MEGA|BIG3|EXPAND|PASS2"
)

FORBIDDEN_META = re.compile(
    r"大韦游戏工作室把玩家|你读这部小说|读序|读正本|九个收场并列|"
    r"游戏站在未完成|卷四另八个|不必重读|气质朝|07th|Pocket MICRO|"
    r"画布钉死|十字键|APK|超任卡带"
)


def dedupe(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"^---\s*$", "", text, flags=re.M)
    title = ""
    paras = []
    seen = set()
    for p in re.split(r"\n\s*\n", text):
        p = p.strip()
        if not p:
            continue
        if p.startswith("#"):
            title = p
            continue
        key = re.sub(r"\s+", "", p)[:160]
        if key in seen:
            continue
        seen.add(key)
        paras.append(p)
    out = [title] if title else []
    out.extend(paras)
    return "\n\n".join(out)


def clean_para(p: str, chapter: str) -> str | None:
    if FORBIDDEN_META.search(p):
        return None
    if chapter in ("01-发送失败.md", "02-空位.md", "03-赵宜家.md", "04-胡同.md"):
        if LATER_SPOILERS.search(p) and chapter != "04-胡同.md":
            return None
    if chapter == "04-胡同.md" and re.search(r"你跟上阿青|选阿青|倒带馆", p):
        return None
    # merge obvious telegraph: many short fragments
    if p.count("。") >= 5 and sum(1 for s in p.split("。") if 0 < len(s.strip()) <= 6) >= 4:
        parts = [s.strip() for s in p.split("。") if s.strip()]
        if len(parts) >= 4 and all(len(x) <= 10 for x in parts[:5]):
            return "，".join(parts) + "。"
    return p


def load_extras(name: str) -> list[str]:
    p = TOOLS / "extras" / f"{name}"
    if not p.exists():
        return []
    return [x.strip() for x in p.read_text(encoding="utf-8").split("\n\n") if x.strip()]


def assemble_chapter(name: str, base: str | None = None) -> str:
    if base is None:
        base = (NOVEL / name).read_text(encoding="utf-8")
    # Always use in-repo draft; clean short variant is too thin for 20800 target.

    text = dedupe(base)
    title = ""
    kept = []
    for p in text.split("\n\n"):
        p = p.strip()
        if not p:
            continue
        if p.startswith("#"):
            title = p
            continue
        c = clean_para(p, name)
        if c:
            kept.append(c)

    extras = load_extras(name)
    seen = {re.sub(r"\s+", "", x)[:160] for x in kept}
    for ex in extras:
        k = re.sub(r"\s+", "", ex)[:160]
        if k not in seen:
            kept.append(ex)
            seen.add(k)

    body = (title + "\n\n" if title else "") + "\n\n".join(kept)
    return body.strip()


def load_ch00() -> str:
    return (NOVEL / "00-序.md").read_text(encoding="utf-8")


def main() -> None:
    # ensure extras dir
    (TOOLS / "extras").mkdir(exist_ok=True)

    outputs = {}
    for name in [
        "01-发送失败.md",
        "02-空位.md",
        "03-赵宜家.md",
        "04-胡同.md",
        "05-第三夜.md",
        "06-胡同深.md",
        "07-便利店.md",
    ]:
        outputs[name] = assemble_chapter(name)

    for name, body in outputs.items():
        path = NOVEL / name
        path.write_text(body.strip() + "\n", encoding="utf-8")
        n = len(body.strip())
        t = TARGETS[name]
        print(f"{name}\t{n}\t({100*n/t:.0f}% of {t})")


if __name__ == "__main__":
    main()
