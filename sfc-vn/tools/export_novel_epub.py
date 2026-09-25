#!/usr/bin/env python3
"""将 docs/novel 全书导出为 EPUB（UTF-8，按章分节）。"""

from __future__ import annotations

import html
import re
import sys
import time
from pathlib import Path

from ebooklib import epub

ROOT = Path(__file__).resolve().parents[1]
NOVEL = ROOT / "docs" / "novel"
DEFAULT_OUT = ROOT / "output" / "十一点的城市.epub"

BOOK_TITLE = "十一点的城市"
BOOK_AUTHOR = "大韦游戏工作室"
BOOK_LANG = "zh-CN"
BOOK_ID = "urn:do-fei:cs146s-cn:eleven-oclock-city"

CSS = """
body { font-family: "Noto Serif SC", "Source Han Serif SC", "SimSun", serif; line-height: 1.75; margin: 1em; }
h1 { font-size: 1.4em; text-align: center; margin: 2em 0 1.5em; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
p { text-indent: 2em; margin: 0.6em 0; }
strong { font-weight: bold; }
"""


def chapter_sort_key(path: Path) -> int:
    m = re.match(r"(\d+)", path.name)
    return int(m.group(1)) if m else 9999


def md_inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def md_to_html_body(text: str) -> str:
    parts: list[str] = []
    blocks = re.split(r"\n\n+", text.strip())
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith("# "):
            parts.append(f"<h1>{md_inline(block[2:].strip())}</h1>")
        elif block.startswith("## "):
            parts.append(f"<h2>{md_inline(block[3:].strip())}</h2>")
        elif block.startswith("---"):
            continue
        else:
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            para = "".join(lines)
            parts.append(f"<p>{md_inline(para)}</p>")
    return "\n".join(parts)


def chapter_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build_epub(out_path: Path) -> tuple[int, int]:
    files = sorted(NOVEL.glob("[0-9]*.md"), key=chapter_sort_key)
    if not files:
        raise SystemExit(f"no chapters in {NOVEL}")

    book = epub.EpubBook()
    book.set_identifier(BOOK_ID)
    book.set_title(BOOK_TITLE)
    book.set_language(BOOK_LANG)
    book.add_author(BOOK_AUTHOR)
    book.add_metadata("DC", "description", "赵宜失踪，发送失败，十一点的城市换皮。")

    style = epub.EpubItem(
        uid="style",
        file_name="style/default.css",
        media_type="text/css",
        content=CSS.encode("utf-8"),
    )
    book.add_item(style)

    spine: list = ["nav"]
    toc: list = []
    total_chars = 0

    for i, src in enumerate(files):
        text = src.read_text(encoding="utf-8")
        total_chars += len(text)
        ch_num = src.name.split("-")[0]
        title = chapter_title(text, src.stem)
        fname = f"ch{ch_num.zfill(2)}.xhtml"

        body = md_to_html_body(text)
        content = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<!DOCTYPE html>\n"
            '<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-CN">\n'
            "<head>"
            f'<title>{html.escape(title)}</title>'
            '<link rel="stylesheet" type="text/css" href="../style/default.css"/>'
            "</head>\n"
            f"<body>\n{body}\n</body>\n</html>"
        )

        chap = epub.EpubHtml(
            title=title,
            file_name=f"text/{fname}",
            lang=BOOK_LANG,
        )
        chap.content = content.encode("utf-8")
        chap.add_item(style)
        book.add_item(chap)
        spine.append(chap)
        toc.append(chap)

        if (i + 1) % 10 == 0 or i + 1 == len(files):
            print(f"  {i + 1}/{len(files)} {src.name} ({len(text):,} 字)")

    book.toc = toc
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    out_path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    epub.write_epub(str(out_path), book)
    elapsed = time.time() - t0
    size_mb = out_path.stat().st_size / (1024 * 1024)

    pages_copy = ROOT / "player" / "novel" / out_path.name
    pages_copy.parent.mkdir(parents=True, exist_ok=True)
    pages_copy.write_bytes(out_path.read_bytes())
    print(f"  also -> {pages_copy} (GitHub Pages)")

    return total_chars, size_mb, elapsed


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    print(f"Export EPUB -> {out}")
    chars, size_mb, elapsed = build_epub(out)
    print(f"Done: {chars:,} 字, {size_mb:.1f} MB, {elapsed:.1f}s")


if __name__ == "__main__":
    main()
