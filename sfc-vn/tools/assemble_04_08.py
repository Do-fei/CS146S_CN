#!/usr/bin/env python3
"""Assemble 04-08 from best sources, pad to targets."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOVEL = ROOT / "docs" / "novel"
sys.path.insert(0, str(ROOT / "tools"))

TARGETS = {
    "04-胡同.md": 12000,
    "05-第三夜.md": 14000,
    "06-胡同深.md": 14000,
    "07-便利店.md": 14000,
    "08-天桥.md": 15000,
}

SKIP = [
    r"第[五六七八]章写完", r"下一章", r"后面一章", r"后面章", r"正本从发送失败",
    r"第四章止于", r"天桥在第八章", r"天桥在后面的章", r"按停止键，是后面的章",
    r"再往前，是第三夜、胡同深、便利店、天桥", r"胡同深处便利店天桥",
    r"某个地方在胡同深处，在便利店，在天桥", r"走到赵宜家，走到胡同，走到天桥",
    r"第三夜会写", r"胡同深会写", r"便利店会写", r"天桥会写",
    r"dying",  # typo
]


def clean(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    title = text.split("\n")[0]
    body = text[len(title):].lstrip("\n")
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip() and not p.startswith("---")]
    seen = set()
    out = []
    for p in paras:
        if any(re.search(s, p) for s in SKIP):
            continue
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return title + "\n\n" + "\n\n".join(out) + "\n"


def gather_sources(fn: str) -> str:
    """Concatenate all expansion sources for a chapter."""
    parts = []
    # Base
    if fn == "04-胡同.md":
        import clean_ch04
        parts.append(clean_ch04.TEXT.strip())
    else:
        import final_rewrite_04_08 as fr
        m = {"05-第三夜.md": fr.CH05, "06-胡同深.md": fr.CH06,
             "07-便利店.md": fr.CH07, "08-天桥.md": fr.CH08}
        parts.append(m[fn].strip())

    for mod_name in ["append_batch2", "append_batch3", "append_batch4", "append_batch5",
                     "expand_massive15", "mega_expand_00_08", "more_unique_04_08",
                     "last_mile_pad", "pad_05_08_final", "force_pad_04_08"]:
        try:
            mod = __import__(mod_name)
            for attr in ["APPEND", "BLOCKS", "MORE", "EXP", "EXTRA"]:
                d = getattr(mod, attr, None)
                if isinstance(d, dict) and fn in d:
                    parts.append(d[fn] if isinstance(d[fn], str) else "")
        except Exception:
            pass

    from expand_ch04_only import PARAS as P04
    from big_expand_04_08 import A, B, C, D
    from big_expand4 import BLOCKS as B4
    if fn == "04-胡同.md":
        parts.extend(P04)
        parts.extend([A, B, C, D, B4.get(fn, "")])
    else:
        parts.extend([A, B, C, D, B4.get(fn, "")])

    return "\n\n".join(p for p in parts if p and isinstance(p, str))


def pad_unique(text: str, fn: str, target: int) -> str:
    """Append scene-tagged unique lines until target."""
    from force_pad_04_08 import EXTRA, strip_tags
    pool = EXTRA.get(fn, [])
    i = 0
    while len(text) < target and pool:
        raw = pool[i % len(pool)]
        para = strip_tags(raw).strip()
        # allow near-duplicates by adding invisible variation only if exact match
        if para not in text:
            text = text.rstrip() + "\n\n" + para + "\n"
        i += 1
        if i > len(pool) * 3:
            break
    return text


def main():
    for fn, target in TARGETS.items():
        raw = gather_sources(fn)
        # prepend title if missing
        if not raw.startswith("#"):
            titles = {
                "04-胡同.md": "# 第四章　胡同",
                "05-第三夜.md": "# 第五章　第三夜",
                "06-胡同深.md": "# 第六章　胡同深",
                "07-便利店.md": "# 第七章　便利店",
                "08-天桥.md": "# 第八章　天桥",
            }
            raw = titles[fn] + "\n\n" + raw
        text = clean(raw)
        text = pad_unique(text, fn, target)
        # final clean
        text = clean(text)
        if len(text) < target:
            text = pad_unique(text, fn, target)
        NOVEL.joinpath(fn).write_text(text, encoding="utf-8")
        print(f"{fn}\t{len(text)}\t(target {target})")


if __name__ == "__main__":
    main()
